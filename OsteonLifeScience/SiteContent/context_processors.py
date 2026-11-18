from django.db.models import Count, Prefetch, Q

from Catalog.models import Category, SubCategory
from .models import SiteSetting


def site_globals(request):
    """Adds the site settings and the product navigation to every template."""
    if request.path.startswith('/admin/'):
        return {}

    visible_sub_categories = (
        SubCategory.objects
        .filter(active=True)
        .annotate(_live_products=Count('products', filter=Q(products__active=True)))
        .filter(_live_products__gt=0)
        .order_by('order', 'name')
    )
    categories = (
        Category.objects
        .filter(active=True)
        .prefetch_related(Prefetch('sub_categories', queryset=visible_sub_categories, to_attr='nav_sub_categories'))
    )
    nav_categories = [c for c in categories if c.nav_sub_categories]

    return {
        'site': SiteSetting.get_solo(),
        'nav_categories': nav_categories,
    }
