import urllib.parse

from django.db import transaction
from django import urls
from django.conf import settings
from rest_framework import serializers

from funkwhale_api.activity import serializers as activity_serializers
from funkwhale_api.audio import serializers as audio_serializers
from funkwhale_api.common import serializers as common_serializers
from funkwhale_api.common import utils as common_utils
from funkwhale_api.federation import routes
from funkwhale_api.federation import utils as federation_utils
from funkwhale_api.playlists import models as playlists_models
from funkwhale_api.tags.models import Tag
from funkwhale_api.tags import serializers as tags_serializers

from . import filters, models, tasks


class CoverField(
    common_serializers.NullToEmptDict, common_serializers.AttachmentSerializer
):
    # XXX: BACKWARD COMPATIBILITY
    pass


cover_field = CoverField()


def serialize_attributed_to(self, obj):
    # Import at runtime to avoid a circular import issue
    from funkwhale_api.federation import serializers as federation_serializers

    if not obj.attributed_to_id:
        return

    return federation_serializers.APIActorSerializer(obj.attributed_to).data


class OptionalDescriptionMixin(object):
    def to_representation(self, obj):
        repr = super().to_representation(obj)
        if self.context.get("description", False):
            description = obj.description
            repr["description"] = (
                common_serializers.ContentSerializer(description).data
                if description
                else None
            )

        return repr


class LicenseSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    url = serializers.URLField()
    code = serializers.CharField()
    name = serializers.CharField()
    redistribute = serializers.BooleanField()
    derivative = serializers.BooleanField()
    commercial = serializers.BooleanField()
    attribution = serializers.BooleanField()
    copyleft = serializers.BooleanField()

    def get_id(self, obj):
        return obj["identifiers"][0]

    class Meta:
        model = models.License


class ArtistAlbumSerializer(serializers.Serializer):
    tracks_count = serializers.SerializerMethodField()
    cover = cover_field
    is_playable = serializers.SerializerMethodField()
    is_local = serializers.BooleanField()
    id = serializers.IntegerField()
    fid = serializers.URLField()
    mbid = serializers.UUIDField()
    title = serializers.CharField()
    artist = serializers.SerializerMethodField()
    release_date = serializers.DateField()
    creation_date = serializers.DateTimeField()

    def get_artist(self, o):
        return o.artist_id

    def get_tracks_count(self, o):
        return o._tracks_count

    def get_is_playable(self, obj):
        try:
            return bool(obj.is_playable_by_actor)
        except AttributeError:
            return None


DATETIME_FIELD = serializers.DateTimeField()


class ArtistWithAlbumsSerializer(OptionalDescriptionMixin, serializers.Serializer):
    albums = ArtistAlbumSerializer(many=True)
    tags = serializers.SerializerMethodField()
    attributed_to = serializers.SerializerMethodField()
    tracks_count = serializers.SerializerMethodField()
    id = serializers.IntegerField()
    fid = serializers.URLField()
    mbid = serializers.UUIDField()
    name = serializers.CharField()
    content_category = serializers.CharField()
    creation_date = serializers.DateTimeField()
    is_local = serializers.BooleanField()
    cover = cover_field

    def get_tags(self, obj):
        tagged_items = getattr(obj, "_prefetched_tagged_items", [])
        return [ti.tag.name for ti in tagged_items]

    get_attributed_to = serialize_attributed_to

    def get_tracks_count(self, o):
        tracks = getattr(o, "_prefetched_tracks", None)
        return len(tracks) if tracks else None


def serialize_artist_simple(artist):
    data = {
        "id": artist.id,
        "fid": artist.fid,
        "mbid": str(artist.mbid),
        "name": artist.name,
        "creation_date": DATETIME_FIELD.to_representation(artist.creation_date),
        "is_local": artist.is_local,
        "content_category": artist.content_category,
    }
    if "description" in artist._state.fields_cache:
        data["description"] = (
            common_serializers.ContentSerializer(artist.description).data
            if artist.description
            else None
        )

    return data


def serialize_album_track(track):
    return {
        "id": track.id,
        "fid": track.fid,
        "mbid": str(track.mbid),
        "title": track.title,
        "artist": serialize_artist_simple(track.artist),
        "album": track.album_id,
        "creation_date": DATETIME_FIELD.to_representation(track.creation_date),
        "position": track.position,
        "disc_number": track.disc_number,
        "uploads": [
            serialize_upload(u) for u in getattr(track, "playable_uploads", [])
        ],
        "listen_url": track.listen_url,
        "duration": getattr(track, "duration", None),
        "copyright": track.copyright,
        "license": track.license_id,
        "is_local": track.is_local,
    }


class AlbumSerializer(OptionalDescriptionMixin, serializers.Serializer):
    tracks = serializers.SerializerMethodField()
    artist = serializers.SerializerMethodField()
    cover = cover_field
    is_playable = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    attributed_to = serializers.SerializerMethodField()
    id = serializers.IntegerField()
    fid = serializers.URLField()
    mbid = serializers.UUIDField()
    title = serializers.CharField()
    artist = serializers.SerializerMethodField()
    release_date = serializers.DateField()
    creation_date = serializers.DateTimeField()
    is_local = serializers.BooleanField()
    is_playable = serializers.SerializerMethodField()

    get_attributed_to = serialize_attributed_to

    def get_artist(self, o):
        return serialize_artist_simple(o.artist)

    def get_tracks(self, o):
        ordered_tracks = o.tracks.all()
        return [serialize_album_track(track) for track in ordered_tracks]

    def get_is_playable(self, obj):
        try:
            return any(
                [bool(getattr(t, "playable_uploads", [])) for t in obj.tracks.all()]
            )
        except AttributeError:
            return None

    def get_tags(self, obj):
        tagged_items = getattr(obj, "_prefetched_tagged_items", [])
        return [ti.tag.name for ti in tagged_items]


class TrackAlbumSerializer(serializers.ModelSerializer):
    artist = serializers.SerializerMethodField()
    cover = cover_field

    class Meta:
        model = models.Album
        fields = (
            "id",
            "fid",
            "mbid",
            "title",
            "artist",
            "release_date",
            "cover",
            "creation_date",
            "is_local",
        )

    def get_artist(self, o):
        return serialize_artist_simple(o.artist)


def serialize_upload(upload):
    return {
        "uuid": str(upload.uuid),
        "listen_url": upload.listen_url,
        "size": upload.size,
        "duration": upload.duration,
        "bitrate": upload.bitrate,
        "mimetype": upload.mimetype,
        "extension": upload.extension,
    }


class TrackSerializer(OptionalDescriptionMixin, serializers.Serializer):
    artist = serializers.SerializerMethodField()
    album = TrackAlbumSerializer(read_only=True)
    uploads = serializers.SerializerMethodField()
    listen_url = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    attributed_to = serializers.SerializerMethodField()

    id = serializers.IntegerField()
    fid = serializers.URLField()
    mbid = serializers.UUIDField()
    title = serializers.CharField()
    artist = serializers.SerializerMethodField()
    creation_date = serializers.DateTimeField()
    is_local = serializers.BooleanField()
    position = serializers.IntegerField()
    disc_number = serializers.IntegerField()
    copyright = serializers.CharField()
    license = serializers.SerializerMethodField()
    cover = cover_field
    get_attributed_to = serialize_attributed_to

    def get_artist(self, o):
        return serialize_artist_simple(o.artist)

    def get_listen_url(self, obj):
        return obj.listen_url

    def get_uploads(self, obj):
        return [serialize_upload(u) for u in getattr(obj, "playable_uploads", [])]

    def get_tags(self, obj):
        tagged_items = getattr(obj, "_prefetched_tagged_items", [])
        return [ti.tag.name for ti in tagged_items]

    def get_license(self, o):
        return o.license_id


@common_serializers.track_fields_for_update("name", "description", "privacy_level")
class LibraryForOwnerSerializer(serializers.ModelSerializer):
    uploads_count = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()

    class Meta:
        model = models.Library
        fields = [
            "uuid",
            "fid",
            "name",
            "description",
            "privacy_level",
            "uploads_count",
            "size",
            "creation_date",
        ]
        read_only_fields = ["fid", "uuid", "creation_date", "actor"]

    def get_uploads_count(self, o):
        return getattr(o, "_uploads_count", o.uploads_count)

    def get_size(self, o):
        return getattr(o, "_size", 0)

    def on_updated_fields(self, obj, before, after):
        routes.outbox.dispatch(
            {"type": "Update", "object": {"type": "Library"}}, context={"library": obj}
        )


class UploadSerializer(serializers.ModelSerializer):
    track = TrackSerializer(required=False, allow_null=True)
    library = common_serializers.RelatedField(
        "uuid",
        LibraryForOwnerSerializer(),
        required=False,
        filters=lambda context: {"actor": context["user"].actor},
    )
    channel = common_serializers.RelatedField(
        "uuid",
        audio_serializers.ChannelSerializer(),
        required=False,
        filters=lambda context: {"attributed_to": context["user"].actor},
    )

    class Meta:
        model = models.Upload
        fields = [
            "uuid",
            "filename",
            "creation_date",
            "mimetype",
            "track",
            "library",
            "channel",
            "duration",
            "mimetype",
            "bitrate",
            "size",
            "import_date",
            "import_status",
        ]

        read_only_fields = [
            "uuid",
            "creation_date",
            "duration",
            "mimetype",
            "bitrate",
            "size",
            "track",
            "import_date",
        ]


class ImportMetadataSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=500, required=True)
    mbid = serializers.UUIDField(required=False, allow_null=True)
    copyright = serializers.CharField(max_length=500, required=False, allow_null=True)
    position = serializers.IntegerField(min_value=1, required=False, allow_null=True)
    tags = tags_serializers.TagsListField(required=False)
    license = common_serializers.RelatedField(
        "code", LicenseSerializer(), required=False, allow_null=True
    )


class ImportMetadataField(serializers.JSONField):
    def to_internal_value(self, v):
        v = super().to_internal_value(v)
        s = ImportMetadataSerializer(data=v)
        s.is_valid(raise_exception=True)
        return v


class UploadForOwnerSerializer(UploadSerializer):
    import_status = serializers.ChoiceField(
        choices=["draft", "pending"], default="pending"
    )
    import_metadata = ImportMetadataField(required=False)

    class Meta(UploadSerializer.Meta):
        fields = UploadSerializer.Meta.fields + [
            "import_details",
            "import_metadata",
            "import_reference",
            "metadata",
            "source",
            "audio_file",
        ]
        write_only_fields = ["audio_file"]
        read_only_fields = UploadSerializer.Meta.read_only_fields + [
            "import_details",
            "metadata",
        ]

    def to_representation(self, obj):
        r = super().to_representation(obj)
        if "audio_file" in r:
            del r["audio_file"]
        return r

    def validate(self, validated_data):
        if (
            not self.instance
            and "library" not in validated_data
            and "channel" not in validated_data
        ):
            raise serializers.ValidationError(
                "You need to specify a channel or a library"
            )
        if (
            not self.instance
            and "library" in validated_data
            and "channel" in validated_data
        ):
            raise serializers.ValidationError(
                "You may specify a channel or a library, not both"
            )
        if "audio_file" in validated_data:
            self.validate_upload_quota(validated_data["audio_file"])

        if "channel" in validated_data:
            validated_data["library"] = validated_data.pop("channel").library
        return super().validate(validated_data)

    def validate_upload_quota(self, f):
        quota_status = self.context["user"].get_quota_status()
        if (f.size / 1000 / 1000) > quota_status["remaining"]:
            raise serializers.ValidationError("upload_quota_reached")

        return f


class UploadActionSerializer(common_serializers.ActionSerializer):
    actions = [
        common_serializers.Action("delete", allow_all=True),
        common_serializers.Action("relaunch_import", allow_all=True),
    ]
    filterset_class = filters.UploadFilter
    pk_field = "uuid"

    @transaction.atomic
    def handle_delete(self, objects):
        libraries = sorted(set(objects.values_list("library", flat=True)))
        for id in libraries:
            # we group deletes by library for easier federation
            uploads = objects.filter(library__pk=id).select_related("library__actor")
            for chunk in common_utils.chunk_queryset(uploads, 100):
                routes.outbox.dispatch(
                    {"type": "Delete", "object": {"type": "Audio"}},
                    context={"uploads": chunk},
                )

        return objects.delete()

    @transaction.atomic
    def handle_relaunch_import(self, objects):
        qs = objects.filter(import_status__in=["pending", "skipped", "errored"])
        pks = list(qs.values_list("id", flat=True))
        qs.update(import_status="pending")
        for pk in pks:
            common_utils.on_commit(tasks.process_upload.delay, upload_id=pk)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "creation_date")


class SimpleAlbumSerializer(serializers.ModelSerializer):
    cover = cover_field

    class Meta:
        model = models.Album
        fields = ("id", "mbid", "title", "release_date", "cover")


class TrackActivitySerializer(activity_serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    name = serializers.CharField(source="title")
    artist = serializers.CharField(source="artist.name")
    album = serializers.CharField(source="album.title")

    class Meta:
        model = models.Track
        fields = ["id", "local_id", "name", "type", "artist", "album"]

    def get_type(self, obj):
        return "Audio"


def get_embed_url(type, id):
    return settings.FUNKWHALE_EMBED_URL + "?type={}&id={}".format(type, id)


class OembedSerializer(serializers.Serializer):
    format = serializers.ChoiceField(choices=["json"])
    url = serializers.URLField()
    maxheight = serializers.IntegerField(required=False)
    maxwidth = serializers.IntegerField(required=False)

    def validate(self, validated_data):
        try:
            match = common_utils.spa_resolve(
                urllib.parse.urlparse(validated_data["url"]).path
            )
        except urls.exceptions.Resolver404:
            raise serializers.ValidationError(
                "Invalid URL {}".format(validated_data["url"])
            )
        data = {
            "version": "1.0",
            "type": "rich",
            "provider_name": settings.APP_NAME,
            "provider_url": settings.FUNKWHALE_URL,
            "height": validated_data.get("maxheight") or 400,
            "width": validated_data.get("maxwidth") or 600,
        }
        embed_id = None
        embed_type = None
        if match.url_name == "library_track":
            qs = models.Track.objects.select_related("artist", "album__artist").filter(
                pk=int(match.kwargs["pk"])
            )
            try:
                track = qs.get()
            except models.Track.DoesNotExist:
                raise serializers.ValidationError(
                    "No track matching id {}".format(match.kwargs["pk"])
                )
            embed_type = "track"
            embed_id = track.pk
            data["title"] = "{} by {}".format(track.title, track.artist.name)
            if track.album.attachment_cover:
                data[
                    "thumbnail_url"
                ] = track.album.attachment_cover.download_url_medium_square_crop
                data["thumbnail_width"] = 200
                data["thumbnail_height"] = 200
            data["description"] = track.full_name
            data["author_name"] = track.artist.name
            data["height"] = 150
            data["author_url"] = federation_utils.full_url(
                common_utils.spa_reverse(
                    "library_artist", kwargs={"pk": track.artist.pk}
                )
            )
        elif match.url_name == "library_album":
            qs = models.Album.objects.select_related("artist").filter(
                pk=int(match.kwargs["pk"])
            )
            try:
                album = qs.get()
            except models.Album.DoesNotExist:
                raise serializers.ValidationError(
                    "No album matching id {}".format(match.kwargs["pk"])
                )
            embed_type = "album"
            embed_id = album.pk
            if album.attachment_cover:
                data[
                    "thumbnail_url"
                ] = album.attachment_cover.download_url_medium_square_crop
                data["thumbnail_width"] = 200
                data["thumbnail_height"] = 200
            data["title"] = "{} by {}".format(album.title, album.artist.name)
            data["description"] = "{} by {}".format(album.title, album.artist.name)
            data["author_name"] = album.artist.name
            data["height"] = 400
            data["author_url"] = federation_utils.full_url(
                common_utils.spa_reverse(
                    "library_artist", kwargs={"pk": album.artist.pk}
                )
            )
        elif match.url_name == "library_artist":
            qs = models.Artist.objects.filter(pk=int(match.kwargs["pk"]))
            try:
                artist = qs.get()
            except models.Artist.DoesNotExist:
                raise serializers.ValidationError(
                    "No artist matching id {}".format(match.kwargs["pk"])
                )
            embed_type = "artist"
            embed_id = artist.pk
            album = artist.albums.exclude(attachment_cover=None).order_by("-id").first()

            if album and album.attachment_cover:
                data[
                    "thumbnail_url"
                ] = album.attachment_cover.download_url_medium_square_crop
                data["thumbnail_width"] = 200
                data["thumbnail_height"] = 200
            data["title"] = artist.name
            data["description"] = artist.name
            data["author_name"] = artist.name
            data["height"] = 400
            data["author_url"] = federation_utils.full_url(
                common_utils.spa_reverse("library_artist", kwargs={"pk": artist.pk})
            )
        elif match.url_name == "library_playlist":
            qs = playlists_models.Playlist.objects.filter(
                pk=int(match.kwargs["pk"]), privacy_level="everyone"
            )
            try:
                obj = qs.get()
            except playlists_models.Playlist.DoesNotExist:
                raise serializers.ValidationError(
                    "No artist matching id {}".format(match.kwargs["pk"])
                )
            embed_type = "playlist"
            embed_id = obj.pk
            playlist_tracks = obj.playlist_tracks.exclude(
                track__album__attachment_cover=None
            )
            playlist_tracks = playlist_tracks.select_related(
                "track__album__attachment_cover"
            ).order_by("index")
            first_playlist_track = playlist_tracks.first()

            if first_playlist_track:
                data[
                    "thumbnail_url"
                ] = (
                    first_playlist_track.track.album.attachment_cover.download_url_medium_square_crop
                )
                data["thumbnail_width"] = 200
                data["thumbnail_height"] = 200
            data["title"] = obj.name
            data["description"] = obj.name
            data["author_name"] = obj.name
            data["height"] = 400
            data["author_url"] = federation_utils.full_url(
                common_utils.spa_reverse("library_playlist", kwargs={"pk": obj.pk})
            )
        else:
            raise serializers.ValidationError(
                "Unsupported url: {}".format(validated_data["url"])
            )
        data[
            "html"
        ] = '<iframe width="{}" height="{}" scrolling="no" frameborder="no" src="{}"></iframe>'.format(
            data["width"], data["height"], get_embed_url(embed_type, embed_id)
        )
        return data

    def create(self, data):
        return data
