from rest_framework import viewsets

from .models import HomePage, SiteSetting
from .serializers import HomePageSerializer, SiteSettingSerializer

from utils.decorators import handle_exceptions
from utils.responses import success_response


class HomePageViewSet(viewsets.ViewSet):

    @handle_exceptions
    def list(self, request):
        """GET - everything shown on the home page (editable from Django admin > Home Page)"""
        home_page = (
            HomePage.objects
            .prefetch_related(
                'banners', 'about_highlights', 'why_points', 'faqs',
                'feature_blocks__points',
                'featured_products__product__sub_category__category',
                'featured_products__product__images',
            )
            .get(pk=HomePage.get_solo().pk)
        )
        data = HomePageSerializer(home_page, context={'request': request}).data
        return success_response({'home_page': data})


class SiteSettingViewSet(viewsets.ViewSet):

    @handle_exceptions
    def list(self, request):
        """GET - global site details (address, email, social links ...)"""
        data = SiteSettingSerializer(SiteSetting.get_solo(), context={'request': request}).data
        return success_response({'site_setting': data})
