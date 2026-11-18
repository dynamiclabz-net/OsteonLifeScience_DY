import re

from django.utils.text import slugify


def readable_slug(value):
    """slugify() that keeps '2.7 mm' as '2-7-mm' and '&' as 'and'."""
    value = str(value or "")
    value = re.sub(r'(\d)\.(\d)', r'\1-\2', value)
    value = value.replace('&', ' and ')
    return slugify(value)


def unique_slug(instance, source_value, max_length=200):
    """Return a slug for `instance` that is unique across its model (and excludes itself)."""
    model = instance.__class__
    base = readable_slug(source_value)[:max_length] or "item"
    slug = base
    counter = 2
    while model.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
        suffix = f"-{counter}"
        slug = f"{base[:max_length - len(suffix)]}{suffix}"
        counter += 1
    return slug
