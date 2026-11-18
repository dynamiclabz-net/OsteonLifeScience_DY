import json

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


def absolute(request, path):
    if not path:
        path = '/'
    if path.startswith('http://') or path.startswith('https://'):
        return path
    if settings.SITE_BASE_URL:
        return settings.SITE_BASE_URL.rstrip('/') + path
    return request.build_absolute_uri(path)


@register.simple_tag(takes_context=True)
def canonical_url(context):
    """Absolute URL of the current page without any query string."""
    request = context['request']
    return absolute(request, request.path)


@register.simple_tag(takes_context=True)
def abs_url(context, path):
    return absolute(context['request'], path)


@register.simple_tag(takes_context=True)
def breadcrumb_ld(context, crumbs):
    """Render a BreadcrumbList JSON-LD block. `crumbs` is a list of (label, url) tuples."""
    request = context['request']
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": index,
                "name": label,
                "item": absolute(request, url or request.path),
            }
            for index, (label, url) in enumerate(crumbs, start=1)
        ],
    }
    payload = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    return mark_safe(f'<script type="application/ld+json">{payload}</script>')


@register.simple_tag(takes_context=True)
def organization_ld(context):
    request = context['request']
    site = context.get('site')
    if not site:
        return ''
    data = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": site.company_name or site.site_name,
        "url": site.website or absolute(request, '/'),
        "email": site.email,
        "address": {"@type": "PostalAddress", "streetAddress": ", ".join(site.address_lines)},
    }
    if site.logo:
        data["logo"] = absolute(request, site.logo.url)
    payload = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    return mark_safe(f'<script type="application/ld+json">{payload}</script>')


@register.filter
def split_semicolon(value):
    return [part.strip() for part in (value or '').replace(',', ';').split(';') if part.strip()]
