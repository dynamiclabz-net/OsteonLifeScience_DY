from django.db import models
from django.urls import reverse
from django.utils import timezone

from utils.slugs import unique_slug


LAUNCH_PRIORITY_CHOICES = (
    ('P1', 'P1 - Launch'),
    ('P2', 'P2 - Launch'),
    ('P3', 'P3 - Later'),
)

CONTENT_STATUS_CHOICES = (
    ('create_review', 'Create / review'),
    ('verify_portfolio', 'Verify portfolio'),
    ('development_verify', 'Development / verify'),
    ('review_existing', 'Review existing page'),
)


class SeoFields(models.Model):
    """SEO block shared by every page type (Category, SubCategory, Product)."""

    seo_title = models.CharField(max_length=255, null=True, blank=True, help_text="Browser / Google title. Falls back to the name.")
    seo_h1 = models.CharField(max_length=255, null=True, blank=True, help_text="Main H1 of the page. Falls back to the name.")
    meta_description = models.TextField(null=True, blank=True, help_text="Shown in Google results. Keep it under ~160 characters.")
    primary_keyword = models.CharField(max_length=255, null=True, blank=True)
    secondary_keywords = models.TextField(null=True, blank=True, help_text="Separate with semicolons.")
    proposed_url = models.CharField(max_length=255, null=True, blank=True, help_text="URL proposed in the SEO brief (reference only, used to build redirects).")

    class Meta:
        abstract = True


class CatalogBase(SeoFields):
    """Fields shared by Category, SubCategory and Product."""

    order = models.PositiveIntegerField(default=0, help_text="Lower numbers are shown first.")
    launch_priority = models.CharField(max_length=2, choices=LAUNCH_PRIORITY_CHOICES, default='P1')
    content_status = models.CharField(max_length=30, choices=CONTENT_STATUS_CHOICES, default='create_review')
    developer_notes = models.TextField(null=True, blank=True, help_text="Internal only. Never shown on the website.")

    active = models.BooleanField(default=True, help_text="Untick to hide this from the website.")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(CatalogBase):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    short_description = models.CharField(max_length=300, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)

    class Meta:
        ordering = ('order', 'name')
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('category-detail', args=[self.slug])

    @property
    def page_title(self):
        return self.seo_title or f"{self.name} | Osteon Life Science"

    @property
    def page_h1(self):
        return self.seo_h1 or self.name

    def __str__(self):
        return self.name


class SubCategory(CatalogBase):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='sub_categories')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    short_description = models.CharField(max_length=300, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='sub_categories/', null=True, blank=True)

    class Meta:
        ordering = ('category__order', 'order', 'name')
        verbose_name = 'Sub Category'
        verbose_name_plural = 'Sub Categories'
        unique_together = (('category', 'name'),)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('sub-category-detail', args=[self.slug])

    @property
    def page_title(self):
        return self.seo_title or f"{self.name} | Osteon Life Science"

    @property
    def page_h1(self):
        return self.seo_h1 or self.name

    def __str__(self):
        return f"{self.category.name} > {self.name}"


class Product(CatalogBase):
    sub_category = models.ForeignKey(SubCategory, on_delete=models.PROTECT, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    short_description = models.CharField(max_length=300, null=True, blank=True, help_text="One-liner used on product cards.")
    overview = models.TextField(null=True, blank=True, help_text="Approved intended-use / overview paragraph shown on the product page.")
    catalogue_file = models.FileField(upload_to='product_catalogues/', null=True, blank=True, help_text="Only upload documents approved for public distribution.")
    related_products = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='related_from')

    class Meta:
        ordering = ('sub_category__category__order', 'sub_category__order', 'order', 'name')
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        unique_together = (('sub_category', 'name'),)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product-detail', args=[self.slug])

    @property
    def category(self):
        return self.sub_category.category

    @property
    def page_title(self):
        return self.seo_title or f"{self.name} | Osteon Life Science"

    @property
    def page_h1(self):
        return self.seo_h1 or self.name

    @property
    def primary_image(self):
        images = list(self.images.all())
        return images[0] if images else None

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=255, null=True, blank=True, help_text="Describe what the image shows. Falls back to the product name.")
    order = models.PositiveIntegerField(default=0, help_text="The first image is the main image.")

    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('order', 'id')

    @property
    def alt(self):
        return self.alt_text or self.product.name

    def __str__(self):
        return f"{self.product.name} - image {self.order}"


class ProductSpecification(models.Model):
    """One accordion item on the product page (features, sizes, material, compatibility ...)."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Plain text. A new line starts a new line on the website.")
    order = models.PositiveIntegerField(default=0)

    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('order', 'id')
        verbose_name = 'Product Specification'
        verbose_name_plural = 'Product Specifications'

    def __str__(self):
        return f"{self.product.name} - {self.title}"


class CatalogPageSetting(models.Model):
    """Singleton - content of the main /products/ landing page."""

    seo_title = models.CharField(max_length=255, default="Orthopaedic Implants & Instruments | Osteon Life Science")
    seo_h1 = models.CharField(max_length=255, default="Orthopaedic Implants & Surgical Instruments")
    meta_description = models.TextField(null=True, blank=True)
    intro = models.TextField(null=True, blank=True, help_text="Short paragraph shown under the heading.")
    primary_keyword = models.CharField(max_length=255, null=True, blank=True)
    secondary_keywords = models.TextField(null=True, blank=True)

    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Products Page Setting'
        verbose_name_plural = 'Products Page Setting'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Products page"
