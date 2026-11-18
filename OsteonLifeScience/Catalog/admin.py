from django.contrib import admin, messages
from django.db.models import Count
from django.utils.html import format_html

from .models import *


def thumb(image_field, size=44):
    if image_field:
        return format_html(
            '<img src="{}" style="height:{}px;width:{}px;object-fit:cover;border-radius:6px;border:1px solid #dfe5ea;" />',
            image_field.url, size, size,
        )
    return format_html('<span style="color:#9aa5ad;">-</span>')


# ---------------------------------------------------------------------------
# Inlines
# ---------------------------------------------------------------------------
class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    fk_name = 'category'
    fields = ('name', 'slug', 'order', 'launch_priority', 'active')
    prepopulated_fields = {'slug': ('name',)}
    extra = 0
    show_change_link = True


class ProductInline(admin.TabularInline):
    model = Product
    fk_name = 'sub_category'
    fields = ('name', 'slug', 'order', 'launch_priority', 'content_status', 'active')
    prepopulated_fields = {'slug': ('name',)}
    extra = 0
    show_change_link = True


class ProductImageInline(admin.StackedInline):
    model = ProductImage
    fields = ('preview', 'image', 'alt_text', 'order', 'active')
    readonly_fields = ('preview',)
    extra = 1

    def preview(self, obj):
        return thumb(obj.image, 90) if obj and obj.pk else "-"


class ProductSpecificationInline(admin.StackedInline):
    model = ProductSpecification
    fields = ('title', 'content', 'order', 'active')
    extra = 1


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'name', 'sub_category_total', 'product_total', 'launch_priority', 'order', 'active')
    list_display_links = ('image_preview', 'name')
    list_editable = ('order', 'active')
    list_filter = ('active', 'launch_priority', 'content_status')
    search_fields = ('name', 'slug', 'seo_title', 'primary_keyword')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('image_preview', 'created_at', 'updated_at')
    inlines = [SubCategoryInline]
    ordering = ('order', 'name')
    save_on_top = True

    fieldsets = (
        ('Basic', {'fields': ('name', 'slug', 'order', 'active')}),
        ('Page content', {'fields': ('short_description', 'description', 'image', 'image_preview')}),
        ('SEO', {'fields': ('seo_title', 'seo_h1', 'meta_description', 'primary_keyword', 'secondary_keywords', 'proposed_url')}),
        ('Internal', {'fields': ('launch_priority', 'content_status', 'developer_notes', 'created_at', 'updated_at')}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _subs=Count('sub_categories', distinct=True),
            _products=Count('sub_categories__products', distinct=True),
        )

    @admin.display(description='Preview')
    def image_preview(self, obj):
        return thumb(obj.image)

    @admin.display(description='Sub categories', ordering='_subs')
    def sub_category_total(self, obj):
        return obj._subs

    @admin.display(description='Products', ordering='_products')
    def product_total(self, obj):
        return obj._products


# ---------------------------------------------------------------------------
# Sub Category
# ---------------------------------------------------------------------------
@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'name', 'category', 'product_total', 'launch_priority', 'content_status', 'order', 'active')
    list_display_links = ('image_preview', 'name')
    list_editable = ('order', 'active')
    list_filter = ('category', 'active', 'launch_priority', 'content_status')
    list_select_related = ('category',)
    search_fields = ('name', 'slug', 'category__name', 'seo_title', 'primary_keyword')
    autocomplete_fields = ('category',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('image_preview', 'created_at', 'updated_at')
    inlines = [ProductInline]
    ordering = ('category__order', 'order', 'name')
    save_on_top = True

    fieldsets = (
        ('Basic', {'fields': ('category', 'name', 'slug', 'order', 'active')}),
        ('Page content', {'fields': ('short_description', 'description', 'image', 'image_preview')}),
        ('SEO', {'fields': ('seo_title', 'seo_h1', 'meta_description', 'primary_keyword', 'secondary_keywords', 'proposed_url')}),
        ('Internal', {'fields': ('launch_priority', 'content_status', 'developer_notes', 'created_at', 'updated_at')}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_products=Count('products', distinct=True))

    @admin.display(description='Preview')
    def image_preview(self, obj):
        return thumb(obj.image)

    @admin.display(description='Products', ordering='_products')
    def product_total(self, obj):
        return obj._products


# ---------------------------------------------------------------------------
# Product
# ---------------------------------------------------------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'name', 'sub_category', 'category_name', 'launch_priority', 'content_status', 'image_total', 'order', 'active')
    list_display_links = ('image_preview', 'name')
    list_editable = ('order', 'active')
    list_filter = ('sub_category__category', 'sub_category', 'launch_priority', 'content_status', 'active')
    list_select_related = ('sub_category', 'sub_category__category')
    search_fields = ('name', 'slug', 'sub_category__name', 'sub_category__category__name', 'seo_title', 'primary_keyword')
    autocomplete_fields = ('sub_category', 'related_products')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProductImageInline, ProductSpecificationInline]
    actions = ['mark_active', 'mark_inactive']
    ordering = ('sub_category__category__order', 'sub_category__order', 'order', 'name')
    save_on_top = True
    list_per_page = 50

    fieldsets = (
        ('Basic', {'fields': ('sub_category', 'name', 'slug', 'order', 'active')}),
        ('Page content', {'fields': ('short_description', 'overview', 'catalogue_file', 'related_products')}),
        ('SEO', {'fields': ('seo_title', 'seo_h1', 'meta_description', 'primary_keyword', 'secondary_keywords', 'proposed_url')}),
        ('Internal', {'fields': ('launch_priority', 'content_status', 'developer_notes', 'created_at', 'updated_at')}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_images=Count('images', distinct=True)).prefetch_related('images')

    @admin.display(description='Image')
    def image_preview(self, obj):
        first = obj.primary_image
        return thumb(first.image) if first else thumb(None)

    @admin.display(description='Category', ordering='sub_category__category__name')
    def category_name(self, obj):
        return obj.sub_category.category.name

    @admin.display(description='Images', ordering='_images')
    def image_total(self, obj):
        return obj._images

    @admin.action(description='Publish selected products')
    def mark_active(self, request, queryset):
        updated = queryset.update(active=True)
        self.message_user(request, f"{updated} product(s) published.", messages.SUCCESS)

    @admin.action(description='Hide selected products')
    def mark_inactive(self, request, queryset):
        updated = queryset.update(active=False)
        self.message_user(request, f"{updated} product(s) hidden.", messages.WARNING)


# ---------------------------------------------------------------------------
# Products landing page (singleton)
# ---------------------------------------------------------------------------
@admin.register(CatalogPageSetting)
class CatalogPageSettingAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Heading', {'fields': ('seo_h1', 'intro')}),
        ('SEO', {'fields': ('seo_title', 'meta_description', 'primary_keyword', 'secondary_keywords')}),
    )

    def has_add_permission(self, request):
        return not CatalogPageSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        from django.shortcuts import redirect
        from django.urls import reverse
        obj = CatalogPageSetting.get_solo()
        return redirect(reverse('admin:Catalog_catalogpagesetting_change', args=[obj.pk]))
