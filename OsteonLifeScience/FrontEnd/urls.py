from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

from .sitemaps import SITEMAPS
from .views import *

router = DefaultRouter()
router.register(r'about-us', AboutUsViewSet, basename='about-us')
router.register(r'downloads', DownloadsViewSet, basename='downloads')
router.register(r'products', ProductsViewSet, basename='products')
router.register(r'category', CategoryViewSet, basename='category')
router.register(r'sub-category', SubCategoryViewSet, basename='sub-category')
router.register(r'product', ProductDetailViewSet, basename='product')


class RobotsView(TemplateView):
    template_name = 'robots.txt'
    content_type = 'text/plain'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sitemap_url'] = self.request.build_absolute_uri('/sitemap.xml')
        return context


urlpatterns = [
    # The router cannot register an empty prefix (it clashes with its own api-root), so home is mapped directly.
    path('', HomeViewSet.as_view({'get': 'list'}), name='home-list'),
    path('sitemap.xml', sitemap, {'sitemaps': SITEMAPS}, name='sitemap'),
    path('robots.txt', RobotsView.as_view(), name='robots'),
    path('', include(router.urls)),
]
