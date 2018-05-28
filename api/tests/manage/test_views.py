import pytest

from django.urls import reverse

from funkwhale_api.manage import serializers
from funkwhale_api.manage import views


@pytest.mark.parametrize('view,permissions,operator', [
    (views.ManageTrackFileViewSet, ['library'], 'and'),
])
def test_permissions(assert_user_permission, view, permissions, operator):
    assert_user_permission(view, permissions, operator)


def test_track_file_view(factories, superuser_api_client):
    tfs = factories['music.TrackFile'].create_batch(size=5)
    qs = tfs[0].__class__.objects.order_by('-creation_date')
    url = reverse('api:v1:manage:library:track-files-list')

    response = superuser_api_client.get(url, {'sort': '-creation_date'})
    expected = serializers.ManageTrackFileSerializer(qs, many=True).data

    assert response.data['count'] == len(tfs)
    assert response.data['results'] == expected
