from rest_framework import filters
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_extensions.cache.decorators import cache_response
from rest_framework_extensions.etag.decorators import etag
from rest_framework_extensions.key_constructor import bits
from dry_rest_permissions.generics import DRYPermissions

from zds.api.bits import UpdatedAtKeyBit
from zds.api.key_constructor import PagingListKeyConstructor, DetailKeyConstructor
from zds.gallery.models import Gallery
from zds.gallery.mixins import GalleryUpdateOrDeleteMixin

from .serializers import GallerySerializer


class PagingGalleryListKeyConstructor(PagingListKeyConstructor):
    search = bits.QueryParamsKeyBit(['search', 'ordering'])
    user = bits.UserKeyBit()
    updated_at = UpdatedAtKeyBit('api_updated_gallery')


class GalleryListView(ListCreateAPIView):

    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('title',)
    ordering_fields = ('title', 'update', 'pubdate')
    list_key_func = PagingGalleryListKeyConstructor()

    @etag(list_key_func)
    @cache_response(key_func=list_key_func)
    def get(self, request, *args, **kwargs):
        """
        Lists an authenticated member's galleries
        ---

        parameters:
            - name: Authorization
              description: Bearer token to make an authenticated request.
              required: true
              paramType: header
            - name: page
              description: Restricts output to the given page number.
              required: false
              paramType: query
            - name: page_size
              description: Sets the number of private topics per page.
              required: false
              paramType: query
            - name: search
              description: Filters by title.
              required: false
              paramType: query
            - name: ordering
              description: Sorts the results. You can order by (-)title, (-)update, (-)pubdate.
              paramType: query
        responseMessages:
            - code: 401
              message: Not Authenticated
        """
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Create a new gallery
        ---

        parameters:
            - name: Authorization
              description: Bearer token to make an authenticated request.
              required: true
              paramType: header
            - name: title
              description: Private topic title.
              required: true
              paramType: form
            - name: subtitle
              description: Private topic subtitle.
              required: false
              paramType: form
        """
        return self.create(request, *args, **kwargs)

    def get_current_user(self):
        return self.request.user

    def get_serializer_class(self):
        return GallerySerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return Gallery.objects.galleries_of_user(self.get_current_user()).order_by('pk')


class GalleryDetailKeyConstructor(DetailKeyConstructor):
    user = bits.UserKeyBit()
    updated_at = UpdatedAtKeyBit('api_updated_gallery')


class GalleryDetailView(RetrieveUpdateDestroyAPIView, GalleryUpdateOrDeleteMixin):

    queryset = Gallery.objects.annotated_gallery()
    list_key_func = DetailKeyConstructor()

    @etag(list_key_func)
    @cache_response(key_func=list_key_func)
    def get(self, request, *args, **kwargs):
        """
        Gets a gallery by identifier.
        ---

        parameters:
            - name: Authorization
              description: Bearer token to make an authenticated request.
              required: true
              paramType: header
            - name: expand
              description: Returns an object instead of an identifier representing the given field.
              required: false
              paramType: query
        responseMessages:
            - code: 401
              message: Not Authenticated
            - code: 403
              message: Permission Denied
            - code: 404
              message: Not Found
        """

        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """
        Update the gallery
        ---

        parameters:
            - name: Authorization
              description: Bearer token to make an authenticated request.
              required: true
              paramType: header
            - name: title
              description: Private topic title.
              required: true
              paramType: form
            - name: subtitle
              description: Private topic subtitle.
              required: false
              paramType: form
        responseMessages:
            - code: 401
              message: Not Authenticated
            - code: 403
              message: Permission Denied
            - code: 404
              message: Not Found
        """
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        Deletes a gallery
        ---

        parameters:
            - name: Authorization
              description: Bearer token to make an authenticated request.
              required: true
              paramType: header
        responseMessages:
            - code: 401
              message: Not Authenticated
            - code: 403
              message: Permission Denied
            - code: 404
              message: Not Found
        """
        return self.destroy(request, *args, **kwargs)

    def perform_destroy(self, instance):
        self.gallery = instance
        self.perform_delete()

    def get_current_user(self):
        return self.request.user

    def get_serializer_class(self):
        return GallerySerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated, DRYPermissions]
        return [permission() for permission in permission_classes]