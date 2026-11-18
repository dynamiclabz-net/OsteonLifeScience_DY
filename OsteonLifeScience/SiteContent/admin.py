from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html

from .models import *


def thumb(image_field, size=70):
    if image_field:
        return format_html(
            '<img src="{}" style="height:{}px;max-width:160px;object-fit:cover;border-radius:6px;border:1px solid #dfe5ea;" />',
            image_field.url, size,
        )
    return "-"


class SingletonAdmin(admin.ModelAdmin):
    """Admin for models that only ever have one row: the list page jumps straight to the edit form."""

    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = self.model.get_solo()
        url_name = f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change'
        return redirect(reverse(url_name, args=[obj.pk]))


# ---------------------------------------------------------------------------
# Home page inlines
# ---------------------------------------------------------------------------
class HomeBannerInline(admin.StackedInline):
    model = HomeBanner
    extra = 0
    fieldsets = (
        ('Media', {'fields': (('media_type', 'layout'), 'preview', 'background_image', 'background_video')}),
        ('Text', {'fields': ('eyebrow', ('title_line_1', 'title_accent'), 'description')}),
        ('Buttons', {'fields': (('primary_button_text', 'primary_button_url'), ('secondary_button_text', 'secondary_button_url'))}),
        ('Display', {'fields': (('order', 'active'),)}),
    )
    readonly_fields = ('preview',)

    def preview(self, obj):
        return thumb(obj.background_image, 90) if obj and obj.pk else "-"


class HomeAboutHighlightInline(admin.TabularInline):
    model = HomeAboutHighlight
    extra = 0
    fields = ('text', 'order', 'active')


class HomeFeaturedProductInline(admin.TabularInline):
    model = HomeFeaturedProduct
    extra = 0
    fields = ('product', 'order', 'active')
    autocomplete_fields = ('product',)


class HomeWhyPointInline(admin.TabularInline):
    model = HomeWhyPoint
    extra = 0
    fields = ('title', 'description', 'order', 'active')


class HomeFeatureBlockInline(admin.StackedInline):
    model = HomeFeatureBlock
    extra = 0
    show_change_link = True
    fields = ('tag', 'heading', 'paragraph_1', 'paragraph_2', 'image', 'image_alt', 'image_position', 'button_text', 'button_url', 'order', 'active')


class HomeFAQInline(admin.TabularInline):
    model = HomeFAQ
    extra = 0
    fields = ('question', 'answer', 'order', 'active')


@admin.register(HomePage)
class HomePageAdmin(SingletonAdmin):
    save_on_top = True
    inlines = [
        HomeBannerInline,
        HomeAboutHighlightInline,
        HomeFeaturedProductInline,
        HomeWhyPointInline,
        HomeFeatureBlockInline,
        HomeFAQInline,
    ]
    fieldsets = (
        ('Page SEO', {'fields': ('meta_title', 'meta_description', 'meta_keywords')}),
        ('About section', {'fields': ('show_about', 'about_tag', 'about_heading', 'about_paragraph_1', 'about_paragraph_2', 'about_image')}),
        ('Products section', {'fields': ('show_products', 'products_heading'), 'description': 'Choose the products to show in the "Featured Products" tab. Each product appears under its own category tab.'}),
        ('Why choose us section', {'fields': ('show_why_choose_us', 'why_tag', 'why_heading', 'why_subheading', 'why_description', 'why_image', 'why_button_text', 'why_button_url')}),
        ('Other sections', {'fields': ('show_feature_blocks', 'show_faqs', 'faq_tag', 'faq_heading', 'show_contact', 'active')}),
    )


class HomeFeatureBlockPointInline(admin.TabularInline):
    model = HomeFeatureBlockPoint
    extra = 0
    fields = ('icon_class', 'title', 'description', 'order', 'active')


@admin.register(HomeFeatureBlock)
class HomeFeatureBlockAdmin(admin.ModelAdmin):
    list_display = ('heading', 'tag', 'image_position', 'order', 'active')
    list_editable = ('order', 'active')
    list_filter = ('active', 'image_position')
    search_fields = ('heading', 'tag')
    inlines = [HomeFeatureBlockPointInline]
    save_on_top = True
    fieldsets = (
        ('Content', {'fields': ('home_page', 'tag', 'heading', 'paragraph_1', 'paragraph_2')}),
        ('Image', {'fields': ('image', 'image_alt', 'image_position')}),
        ('Button', {'fields': ('button_text', 'button_url')}),
        ('Display', {'fields': ('order', 'active')}),
    )


@admin.register(SiteSetting)
class SiteSettingAdmin(SingletonAdmin):
    save_on_top = True
    fieldsets = (
        ('Brand', {'fields': ('site_name', 'logo', 'favicon', 'designed_by_text', 'designed_by_url')}),
        ('Contact details', {'fields': ('company_name', 'address', 'email', 'phone', 'website', 'map_embed_url')}),
        ('Social links', {'fields': ('twitter_url', 'facebook_url', 'instagram_url', 'linkedin_url')}),
        ('Contact + footer text', {'fields': ('contact_tag', 'contact_heading', 'newsletter_heading', 'newsletter_text')}),
        ('Default SEO', {'fields': ('default_meta_description', 'default_meta_keywords')}),
    )
