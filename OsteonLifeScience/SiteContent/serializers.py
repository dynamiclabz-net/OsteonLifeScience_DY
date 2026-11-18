from rest_framework import serializers
from Catalog.serializers import ProductSerializer
from .models import *


class SiteSettingSerializer(serializers.ModelSerializer):
    address_lines = serializers.ListField(child=serializers.CharField(), read_only=True)

    class Meta:
        model = SiteSetting
        exclude = ('created_at', 'active')


class HomeBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeBanner
        exclude = ('home_page', 'created_at', 'active')


class HomeAboutHighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeAboutHighlight
        fields = ('id', 'text', 'order')


class HomeWhyPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeWhyPoint
        fields = ('id', 'title', 'description', 'order')


class HomeFeatureBlockPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeFeatureBlockPoint
        fields = ('id', 'icon_class', 'title', 'description', 'order')


class HomeFeatureBlockSerializer(serializers.ModelSerializer):
    points = serializers.SerializerMethodField()

    class Meta:
        model = HomeFeatureBlock
        exclude = ('home_page', 'created_at', 'active')

    def get_points(self, obj):
        return HomeFeatureBlockPointSerializer([p for p in obj.points.all() if p.active], many=True).data


class HomeFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeFAQ
        fields = ('id', 'question', 'answer', 'order')


class HomePageSerializer(serializers.ModelSerializer):
    banners = serializers.SerializerMethodField()
    about_highlights = serializers.SerializerMethodField()
    why_points = serializers.SerializerMethodField()
    feature_blocks = serializers.SerializerMethodField()
    faqs = serializers.SerializerMethodField()
    featured_products = serializers.SerializerMethodField()

    class Meta:
        model = HomePage
        exclude = ('created_at', 'active')

    def _active(self, related):
        return [item for item in related.all() if item.active]

    def get_banners(self, obj):
        return HomeBannerSerializer(self._active(obj.banners), many=True, context=self.context).data

    def get_about_highlights(self, obj):
        return HomeAboutHighlightSerializer(self._active(obj.about_highlights), many=True).data

    def get_why_points(self, obj):
        return HomeWhyPointSerializer(self._active(obj.why_points), many=True).data

    def get_feature_blocks(self, obj):
        return HomeFeatureBlockSerializer(self._active(obj.feature_blocks), many=True, context=self.context).data

    def get_faqs(self, obj):
        return HomeFAQSerializer(self._active(obj.faqs), many=True).data

    def get_featured_products(self, obj):
        products = [f.product for f in self._active(obj.featured_products) if f.product.active]
        return ProductSerializer(products, many=True, context=self.context).data
