from rest_framework import viewsets

from django.db.models import Prefetch
from django.shortcuts import render
from django.urls import reverse

from Catalog.models import Category, SubCategory, Product, ProductImage, ProductSpecification, CatalogPageSetting
from SiteContent.models import (
    HomePage, HomeBanner, HomeAboutHighlight, HomeFeaturedProduct, HomeWhyPoint,
    HomeFeatureBlock, HomeFeatureBlockPoint, HomeFAQ,
)

from utils.decorators import handle_exceptions

PRODUCTS_PER_CATEGORY_FALLBACK = 10
RELATED_PRODUCTS_LIMIT = 3


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def live_products():
    """Active products (with their active images) that sit under an active sub category + category."""
    return (
        Product.objects
        .filter(active=True, sub_category__active=True, sub_category__category__active=True)
        .select_related('sub_category', 'sub_category__category')
        .prefetch_related(Prefetch('images', queryset=ProductImage.objects.filter(active=True)))
    )


def live_product_prefetch(to_attr='live_products'):
    return Prefetch(
        'products',
        queryset=Product.objects.filter(active=True).prefetch_related(
            Prefetch('images', queryset=ProductImage.objects.filter(active=True))
        ),
        to_attr=to_attr,
    )


def category_tree(categories):
    """Category > Sub category > products, dropping anything that has nothing to show."""
    categories = categories.filter(active=True).prefetch_related(
        Prefetch(
            'sub_categories',
            queryset=SubCategory.objects.filter(active=True).prefetch_related(live_product_prefetch()),
            to_attr='all_live_sub_categories',
        )
    )
    tree = []
    for category in categories:
        category.live_sub_categories = [s for s in category.all_live_sub_categories if s.live_products]
        if category.live_sub_categories:
            tree.append(category)
    return tree


def render_404(request):
    return render(request, '404.html', {'page_title': 'Page not found | Osteon Life Science', 'noindex': True}, status=404)


def products_breadcrumbs():
    return [('Home', reverse('home-list')), ('Products', reverse('products-list'))]


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
class HomeViewSet(viewsets.ViewSet):

    @handle_exceptions
    def list(self, request):
        home = HomePage.get_solo()

        banners = list(home.banners.filter(active=True))
        about_highlights = list(home.about_highlights.filter(active=True))
        middle = (len(about_highlights) + 1) // 2
        about_highlight_columns = [c for c in (about_highlights[:middle], about_highlights[middle:]) if c]

        feature_blocks = list(
            home.feature_blocks.filter(active=True).prefetch_related(
                Prefetch('points', queryset=HomeFeatureBlockPoint.objects.filter(active=True), to_attr='active_points')
            )
        )

        context = {
            'nav_active': 'home',
            'home': home,
            'page_title': home.meta_title,
            'meta_description': home.meta_description,
            'meta_keywords': home.meta_keywords,
            'banners': banners,
            'about_highlight_columns': about_highlight_columns,
            'product_tabs': self.build_product_tabs(home),
            'why_points': home.why_points.filter(active=True),
            'feature_blocks': feature_blocks,
            'faqs': home.faqs.filter(active=True),
        }
        return render(request, 'home.html', context)

    def build_product_tabs(self, home):
        """One tab per category. Uses the products picked in admin, or the first products of each category."""
        featured = (
            home.featured_products.filter(
                active=True, product__active=True,
                product__sub_category__active=True, product__sub_category__category__active=True,
            )
            .select_related('product__sub_category__category')
            .prefetch_related(Prefetch('product__images', queryset=ProductImage.objects.filter(active=True)))
            .order_by('order', 'id')
        )
        grouped = {}
        for item in featured:
            category = item.product.sub_category.category
            grouped.setdefault(category.id, {'category': category, 'products': []})['products'].append(item.product)

        if not grouped:
            for category in category_tree(Category.objects.all()):
                products = [p for sub in category.live_sub_categories for p in sub.live_products]
                grouped[category.id] = {'category': category, 'products': products[:PRODUCTS_PER_CATEGORY_FALLBACK]}

        return sorted(grouped.values(), key=lambda tab: (tab['category'].order, tab['category'].name))


class AboutUsViewSet(viewsets.ViewSet):

    @handle_exceptions
    def list(self, request):
        return render(request, 'about-us.html', {
            'nav_active': 'about',
            'page_title': 'About Us - Osteon Life Science',
            'meta_description': 'About Osteon Life Science - Advancing healthcare through innovation and scientific excellence.',
            'meta_keywords': 'Osteon, Life Science, Orthopedics, Healthcare, Medical Implants',
        })


class DownloadsViewSet(viewsets.ViewSet):

    @handle_exceptions
    def list(self, request):
        return render(request, 'downloads.html', {
            'nav_active': 'downloads',
            'page_title': 'Downloads - Osteon Life Science',
            'meta_description': 'Download your certificates.',
            'meta_keywords': 'Downloads, Certificates',
        })


class ProductsViewSet(viewsets.ViewSet):

    @handle_exceptions
    def list(self, request):
        page = CatalogPageSetting.get_solo()
        return render(request, 'products.html', {
            'nav_active': 'products',
            'page_title': page.seo_title,
            'meta_description': page.meta_description,
            'meta_keywords': (page.secondary_keywords or '').replace(';', ','),
            'heading': page.seo_h1,
            'intro': page.intro,
            'breadcrumbs': products_breadcrumbs(),
            'categories': category_tree(Category.objects.all()),
        })


class CategoryViewSet(viewsets.ViewSet):

    @handle_exceptions
    def retrieve(self, request, pk):
        categories = category_tree(Category.objects.filter(slug=pk))
        category = categories[0] if categories else Category.objects.filter(slug=pk, active=True).first()
        if not category:
            return render_404(request)

        sub_categories = getattr(category, 'live_sub_categories', [])
        return render(request, 'category.html', {
            'nav_active': 'products',
            'page_title': category.page_title,
            'meta_description': category.meta_description or category.short_description,
            'meta_keywords': (category.secondary_keywords or '').replace(';', ','),
            'og_image': category.image.url if category.image else None,
            'category': category,
            'sub_categories': sub_categories,
            'breadcrumbs': products_breadcrumbs() + [(category.name, category.get_absolute_url())],
        })


class SubCategoryViewSet(viewsets.ViewSet):

    @handle_exceptions
    def retrieve(self, request, pk):
        sub_category = (
            SubCategory.objects.filter(slug=pk, active=True, category__active=True)
            .select_related('category')
            .prefetch_related(live_product_prefetch())
            .first()
        )
        if not sub_category:
            return render_404(request)

        category = sub_category.category
        siblings = list(
            SubCategory.objects
            .filter(category=category, active=True, products__active=True)
            .distinct()
            .order_by('order', 'name')
        )

        return render(request, 'sub-category.html', {
            'nav_active': 'products',
            'page_title': sub_category.page_title,
            'meta_description': sub_category.meta_description or sub_category.short_description,
            'meta_keywords': (sub_category.secondary_keywords or '').replace(';', ','),
            'og_image': sub_category.image.url if sub_category.image else None,
            'category': category,
            'sub_category': sub_category,
            'products': sub_category.live_products,
            'sibling_sub_categories': siblings if len(siblings) > 1 else [],
            'breadcrumbs': products_breadcrumbs() + [
                (category.name, category.get_absolute_url()),
                (sub_category.name, sub_category.get_absolute_url()),
            ],
        })


class ProductDetailViewSet(viewsets.ViewSet):

    @handle_exceptions
    def retrieve(self, request, pk):
        product = live_products().filter(slug=pk).first()
        if not product:
            return render_404(request)

        sub_category = product.sub_category
        category = sub_category.category
        images = list(product.images.all())
        specifications = list(ProductSpecification.objects.filter(product=product, active=True))

        related = list(
            live_products().filter(related_from=product).exclude(pk=product.pk).distinct()[:RELATED_PRODUCTS_LIMIT * 2]
        )
        # Chosen in admin first, then fall back to other products of the same sub category / category.
        if len(related) < RELATED_PRODUCTS_LIMIT:
            related_ids = [p.pk for p in related] + [product.pk]
            fillers = live_products().filter(sub_category=sub_category).exclude(pk__in=related_ids)
            related += list(fillers[:RELATED_PRODUCTS_LIMIT - len(related)])
        if len(related) < RELATED_PRODUCTS_LIMIT:
            related_ids = [p.pk for p in related] + [product.pk]
            fillers = live_products().filter(sub_category__category=category).exclude(pk__in=related_ids)
            related += list(fillers[:RELATED_PRODUCTS_LIMIT - len(related)])

        return render(request, 'product-detail.html', {
            'nav_active': 'products',
            'page_title': product.page_title,
            'meta_description': product.meta_description or product.short_description,
            'meta_keywords': (product.secondary_keywords or '').replace(';', ','),
            'og_type': 'product',
            'og_image': images[0].image.url if images else None,
            'product': product,
            'category': category,
            'sub_category': sub_category,
            'images': images,
            'specifications': specifications,
            'related_products': related[:RELATED_PRODUCTS_LIMIT],
            'breadcrumbs': products_breadcrumbs() + [
                (category.name, category.get_absolute_url()),
                (sub_category.name, sub_category.get_absolute_url()),
                (product.name, product.get_absolute_url()),
            ],
        })
