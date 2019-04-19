<template>
  <main v-title="labels.title">
    <div v-if="isLoading" class="ui vertical segment">
      <div :class="['ui', 'centered', 'active', 'inline', 'loader']"></div>
    </div>
    <template v-if="object">
      <section :class="['ui', 'head', {'with-background': cover}, 'vertical', 'center', 'aligned', 'stripe', 'segment']" :style="headerStyle" v-title="object.name">
        <div class="segment-content">
          <h2 class="ui center aligned icon header">
            <i class="circular inverted users violet icon"></i>
            <div class="content">
              {{ object.name }}
              <div class="sub header" v-if="albums">
                <translate translate-context="Content/Artist/Paragraph"
                  tag="div"
                  translate-plural="%{ count } tracks in %{ albumsCount } albums"
                  :translate-n="totalTracks"
                  :translate-params="{count: totalTracks, albumsCount: totalAlbums}">
                  %{ count } track in %{ albumsCount } albums
                </translate>
              </div>
            </div>
          </h2>
          <div class="ui hidden divider"></div>
          <div class="header-buttons">
            <div class="ui buttons">
              <radio-button type="artist" :object-id="object.id"></radio-button>

            </div>
            <div class="ui buttons">
              <play-button :is-playable="isPlayable" class="orange" :artist="object">
                <translate translate-context="Content/Artist/Button.Label/Verb">Play all albums</translate>
              </play-button>
            </div>

            <modal :show.sync="showEmbedModal" v-if="publicLibraries.length > 0">
              <div class="header">
                <translate translate-context="Popup/Artist/Title/Verb">Embed this artist work on your website</translate>
              </div>
              <div class="content">
                <div class="description">
                  <embed-wizard type="artist" :id="object.id" />

                </div>
              </div>
              <div class="actions">
                <div class="ui deny button">
                  <translate translate-context="*/*/Button.Label/Verb">Cancel</translate>
                </div>
              </div>
            </modal>
            <div class="ui buttons">
              <button class="ui button" @click="$refs.dropdown.click()">
                <translate translate-context="*/*/Button.Label/Noun">More…</translate>
              </button>
              <div class="ui floating dropdown icon button" ref="dropdown" v-dropdown>
                <i class="dropdown icon"></i>
                <div class="menu">
                  <div
                    role="button"
                    v-if="publicLibraries.length > 0"
                    @click="showEmbedModal = !showEmbedModal"
                    class="basic item">
                    <i class="code icon"></i>
                    <translate translate-context="Content/*/Button.Label/Verb">Embed</translate>
                  </div>
                  <a :href="wikipediaUrl" target="_blank" rel="noreferrer noopener" class="basic item">
                    <i class="wikipedia w icon"></i>
                    <translate translate-context="Content/*/Button.Label/Verb">Search on Wikipedia</translate>
                  </a>
                  <a v-if="musicbrainzUrl" :href="musicbrainzUrl" target="_blank" rel="noreferrer noopener" class="basic item">
                    <i class="external icon"></i>
                    <translate translate-context="Content/*/*/Clickable, Verb">View on MusicBrainz</translate>
                  </a>
                  <router-link
                    v-if="object.is_local"
                    :to="{name: 'library.artists.edit', params: {id: object.id }}"
                    class="basic item">
                    <i class="edit icon"></i>
                    <translate translate-context="Content/*/Button.Label/Verb">Edit</translate>
                  </router-link>
                  <div class="divider"></div>
                  <router-link class="basic item" v-if="$store.state.auth.availablePermissions['library']" :to="{name: 'manage.library.artists.detail', params: {id: object.id}}">
                    <i class="wrench icon"></i>
                    <translate translate-context="Content/Moderation/Link">Open in moderation interface</translate>
                  </router-link>
                  <a
                    v-if="$store.state.auth.profile.is_superuser"
                    class="basic item"
                    :href="$store.getters['instance/absoluteUrl'](`/api/admin/music/artist/${object.id}`)"
                    target="_blank" rel="noopener noreferrer">
                    <i class="wrench icon"></i>
                    <translate translate-context="Content/Moderation/Link/Verb">View in Django's admin</translate>&nbsp;
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
      <router-view v-if="object" :tracks="tracks" :albums="albums" :is-loading-albums="isLoadingAlbums" @libraries-loaded="libraries = $event" :object="object" object-type="artist" :key="$route.fullPath"></router-view>
    </template>
  </main>
</template>

<script>
import axios from "axios"
import logger from "@/logging"
import backend from "@/audio/backend"
import PlayButton from "@/components/audio/PlayButton"
import EmbedWizard from "@/components/audio/EmbedWizard"
import Modal from '@/components/semantic/Modal'
import RadioButton from "@/components/radios/Button"

const FETCH_URL = "albums/"


export default {
  props: ["id"],
  components: {
    PlayButton,
    EmbedWizard,
    Modal,
    RadioButton
  },
  data() {
    return {
      isLoading: true,
      isLoadingAlbums: true,
      object: null,
      albums: null,
      libraries: [],
      showEmbedModal: false,
      tracks: [],
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      var self = this
      this.isLoading = true
      logger.default.debug('Fetching artist "' + this.id + '"')
      axios.get("tracks/", { params: { artist: this.id, hidden: '' } }).then(response => {
        self.tracks = response.data.results
        self.totalTracks = response.data.count
      })
      axios.get("artists/" + this.id + "/").then(response => {
        self.object = response.data
        self.isLoading = false
        self.isLoadingAlbums = true
        axios
          .get("albums/", {
            params: { artist: self.id, ordering: "-release_date", hidden: '' }
          })
          .then(response => {
            self.totalAlbums = response.data.count
            let parsed = JSON.parse(JSON.stringify(response.data.results))
            self.albums = parsed.map(album => {
              return backend.Album.clean(album)
            })

            self.isLoadingAlbums = false
          })
      })
    }
  },
  computed: {
    isPlayable() {
      return (
        this.object.albums.filter(a => {
          return a.is_playable
        }).length > 0
      )
    },
    labels() {
      return {
        title: this.$pgettext('*/*/*', 'Album')
      }
    },
    wikipediaUrl() {
      return (
        "https://en.wikipedia.org/w/index.php?search=" +
        encodeURI(this.object.name)
      )
    },
    musicbrainzUrl() {
      if (this.object.mbid) {
        return "https://musicbrainz.org/artist/" + this.object.mbid
      }
    },
    cover() {
      return this.object.albums
        .filter(album => {
          return album.cover
        })
        .map(album => {
          return album.cover
        })[0]
    },

    publicLibraries () {
      return this.libraries.filter(l => {
        return l.privacy_level === 'everyone'
      })
    },
    headerStyle() {
      if (!this.cover || !this.cover.original) {
        return ""
      }
      return (
        "background-image: url(" +
        this.$store.getters["instance/absoluteUrl"](this.cover.original) +
        ")"
      )
    },
    contentFilter () {
      let self = this
      return this.$store.getters['moderation/artistFilters']().filter((e) => {
        return e.target.id === this.object.id
      })[0]
    }
  },
  watch: {
    id() {
      this.fetchData()
    }
  }
}
</script>