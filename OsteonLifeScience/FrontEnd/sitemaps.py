from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from Catalog.models import Category, SubCategory, Product


class StaticPagesSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.8

    def items(self):
        return ['home-list', 'products-list', 'about-us-list', 'downloads-list']

    def location(self, item):
        return reverse(item)


class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Category.objects.filter(active=True, sub_categories__active=True, sub_categories__products__active=True).distinct()

    def lastmod(self, obj):
        return obj.updated_at


class SubCategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return SubCategory.objects.filter(active=True, category__active=True, products__active=True).distinct()

    def lastmod(self, obj):
        return obj.updated_at


class ProductSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Product.objects.filter(active=True, sub_category__active=True, sub_category__category__active=True)

    def lastmod(self, obj):
        return obj.updated_at


SITEMAPS = {
    'pages': StaticPagesSitemap,
    'categories': CategorySitemap,
    'sub-categories': SubCategorySitemap,
    'products': ProductSitemap,
}
