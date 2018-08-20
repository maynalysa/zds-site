from django.core.cache import caches
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_extensions.settings import extensions_api_settings

from zds.gallery.factories import UserGalleryFactory, GalleryFactory, ImageFactory
from zds.gallery.models import Gallery, UserGallery, GALLERY_WRITE
from zds.member.factories import ProfileFactory
from zds.member.api.tests import create_oauth2_client, authenticate_client


class GalleryListAPITest(APITestCase):
    def setUp(self):
        self.profile = ProfileFactory()
        self.client = APIClient()
        client_oauth2 = create_oauth2_client(self.profile.user)
        authenticate_client(self.client, client_oauth2, self.profile.user.username, 'hostel77')

        caches[extensions_api_settings.DEFAULT_USE_CACHE].clear()

    def test_get_list_of_gallery_empty(self):
        response = self.client.get(reverse('api:gallery:list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 0)
        self.assertEqual(response.data.get('results'), [])
        self.assertIsNone(response.data.get('next'))
        self.assertIsNone(response.data.get('previous'))

    def test_get_list_of_gallery(self):

        gallery = GalleryFactory()
        UserGalleryFactory(user=self.profile.user, gallery=gallery)
        response = self.client.get(reverse('api:gallery:list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)
        self.assertIsNone(response.data.get('next'))
        self.assertIsNone(response.data.get('previous'))

    def test_post_create_gallery(self):
        title = 'Ma super galerie'
        subtitle = 'Comment que ça va être bien'

        response = self.client.post(
            reverse('api:gallery:list'),
            {
                'title': title,
                'subtitle': subtitle
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Gallery.objects.count(), 1)
        self.assertEqual(UserGallery.objects.count(), 1)

        gallery = Gallery.objects.first()
        self.assertEqual(gallery.title, title)
        self.assertEqual(gallery.subtitle, subtitle)

        user_gallery = UserGallery.objects.first()
        self.assertEqual(user_gallery.user, self.profile.user)
        self.assertEqual(user_gallery.gallery, gallery)
        self.assertEqual(user_gallery.mode, GALLERY_WRITE)

        self.assertEqual(response.data.get('id'), gallery.pk)
        self.assertEqual(response.data.get('title'), gallery.title)
        self.assertEqual(response.data.get('subtitle'), gallery.subtitle)
        self.assertIsNone(response.data.get('linked_content'))
        self.assertEqual(response.data.get('image_count'), 0)


class GalleryDetailAPITest(APITestCase):
    def setUp(self):
        self.profile = ProfileFactory()
        self.other = ProfileFactory()
        self.client = APIClient()
        client_oauth2 = create_oauth2_client(self.profile.user)
        authenticate_client(self.client, client_oauth2, self.profile.user.username, 'hostel77')

        self.gallery = GalleryFactory()

        caches[extensions_api_settings.DEFAULT_USE_CACHE].clear()

    def test_get_gallery(self):
        UserGalleryFactory(user=self.profile.user, gallery=self.gallery)

        response = self.client.get(reverse('api:gallery:detail', kwargs={'pk': self.gallery.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), self.gallery.pk)
        self.assertEqual(response.data.get('title'), self.gallery.title)
        self.assertEqual(response.data.get('subtitle'), self.gallery.subtitle)
        self.assertIsNone(response.data.get('linked_content'))
        self.assertEqual(response.data.get('image_count'), 0)

    def test_get_fail_non_existing(self):
        response = self.client.get(reverse('api:gallery:detail', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_fail_no_right(self):
        UserGalleryFactory(user=self.other.user, gallery=self.gallery)

        response = self.client.get(reverse('api:gallery:detail', kwargs={'pk': self.gallery.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_update_gallery(self):
        title = 'Ma super galerie'
        subtitle = '... A été mise à jour !'

        UserGalleryFactory(user=self.profile.user, gallery=self.gallery)

        response = self.client.put(
            reverse('api:gallery:detail', kwargs={'pk': self.gallery.pk}),
            {
                'title': title,
                'subtitle': subtitle
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        gallery = Gallery.objects.get(pk=self.gallery.pk)
        self.assertEqual(gallery.title, title)
        self.assertEqual(gallery.subtitle, subtitle)

        self.assertEqual(response.data.get('title'), gallery.title)
        self.assertEqual(response.data.get('subtitle'), gallery.subtitle)

    def test_put_fail_no_right(self):
        title = 'Ma super galerie'
        subtitle = '... A été mise à jour !'

        UserGalleryFactory(user=self.other.user, gallery=self.gallery)

        response = self.client.put(
            reverse('api:gallery:detail', kwargs={'pk': self.gallery.pk}),
            {
                'title': title,
                'subtitle': subtitle
            }
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        gallery = Gallery.objects.get(pk=self.gallery.pk)
        self.assertNotEqual(gallery.title, title)
        self.assertNotEqual(gallery.subtitle, subtitle)

    def test_delete(self):
        UserGalleryFactory(user=self.profile.user, gallery=self.gallery)

        response = self.client.delete(
            reverse('api:gallery:detail', kwargs={'pk': self.gallery.pk}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(Gallery.objects.count(), 0)
        self.assertEqual(UserGallery.objects.count(), 0)

    def test_delete_fail_no_right(self):
        UserGalleryFactory(user=self.other.user, gallery=self.gallery)

        response = self.client.delete(
            reverse('api:gallery:detail', kwargs={'pk': self.gallery.pk}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(Gallery.objects.count(), 1)
        self.assertEqual(UserGallery.objects.count(), 1)


class ImageListAPITest(APITestCase):
    def setUp(self):
        self.profile = ProfileFactory()
        self.other = ProfileFactory()
        self.client = APIClient()
        client_oauth2 = create_oauth2_client(self.profile.user)
        authenticate_client(self.client, client_oauth2, self.profile.user.username, 'hostel77')

        self.gallery = GalleryFactory()
        UserGalleryFactory(user=self.profile.user, gallery=self.gallery)
        self.image = ImageFactory(gallery=self.gallery)

        self.gallery_other = GalleryFactory()
        UserGalleryFactory(user=self.other.user, gallery=self.gallery_other)
        self.image_other = ImageFactory(gallery=self.gallery_other)

    def test_get_list(self):
        response = self.client.get(reverse('api:gallery:list-images', kwargs={'pk_gallery': self.gallery.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data.get('count'), 1)
        self.assertEqual(response.data.get('results')[0].get('id'), self.image.pk)

    def test_get_list_fail_no_permissions(self):
        response = self.client.get(reverse('api:gallery:list-images', kwargs={'pk_gallery': self.gallery_other.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
