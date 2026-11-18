from rest_framework import serializers
from .models import *


class ProductImageSerializer(serializers.ModelSerializer):
    alt_text = serializers.CharField(source='alt', read_only=True)

    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'alt_text', 'order')


class ProductSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpecification
        fields = ('id', 'title', 'content', 'order')


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    specifications = ProductSpecificationSerializer(many=True, read_only=True)
    sub_category_name = serializers.CharField(source='sub_category.name', read_only=True)
    sub_category_slug = serializers.CharField(source='sub_category.slug', read_only=True)
    category_id = serializers.IntegerField(source='sub_category.category_id', read_only=True)
    category_name = serializers.CharField(source='sub_category.category.name', read_only=True)
    category_slug = serializers.CharField(source='sub_category.category.slug', read_only=True)
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'url', 'short_description', 'overview', 'catalogue_file',
            'sub_category', 'sub_category_name', 'sub_category_slug',
            'category_id', 'category_name', 'category_slug',
            'related_products', 'images', 'specifications',
            'seo_title', 'seo_h1', 'meta_description', 'primary_keyword', 'secondary_keywords',
            'order', 'active',
        )
        read_only_fields = ('slug',)


class SubCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    product_count = serializers.SerializerMethodField()
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = SubCategory
        fields = (
            'id', 'name', 'slug', 'url', 'short_description', 'description', 'image',
            'category', 'category_name', 'category_slug', 'product_count',
            'seo_title', 'seo_h1', 'meta_description', 'primary_keyword', 'secondary_keywords',
            'order', 'active',
        )
        read_only_fields = ('slug',)

    def get_product_count(self, obj):
        return obj.products.filter(active=True).count()


class CategorySerializer(serializers.ModelSerializer):
    sub_categories = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = Category
        fields = (
            'id', 'name', 'slug', 'url', 'short_description', 'description', 'image',
            'sub_categories', 'product_count',
            'seo_title', 'seo_h1', 'meta_description', 'primary_keyword', 'secondary_keywords',
            'order', 'active',
        )
        read_only_fields = ('slug',)

    def get_sub_categories(self, obj):
        subs = [s for s in obj.sub_categories.all() if s.active]
        return [{'id': s.id, 'name': s.name, 'slug': s.slug, 'url': s.get_absolute_url()} for s in subs]

    def get_product_count(self, obj):
        return Product.objects.filter(sub_category__category=obj, active=True).count()
