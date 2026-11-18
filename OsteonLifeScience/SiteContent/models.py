from django.db import models
from django.utils import timezone

from Catalog.models import Product


class SingletonModel(models.Model):
    """Only one row ever exists (pk=1). Fetch it with Model.get_solo()."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class SiteSetting(SingletonModel):
    """Global details used in the header, footer and contact section of every page."""

    site_name = models.CharField(max_length=150, default="Osteon Life Science")
    logo = models.ImageField(upload_to='site/', null=True, blank=True, help_text="Header + footer logo. Leave empty to use static/img/OSTEON LOGO/logo.png")
    favicon = models.ImageField(upload_to='site/', null=True, blank=True, help_text="Also used in the page loader. Leave empty to use static/img/loaderlogo.png")

    company_name = models.CharField(max_length=200, default="OSTEON LIFE SCIENCE PRIVATE LIMITED")
    address = models.TextField(default="181-182, PUSHAKAR INDUSTRIAL & LOGISTICS PARK,\nSARKHEJ BAVLA HIGHWAY, CHANGODAR,\nAHMEDABAD-382213", help_text="One line per row.")
    email = models.EmailField(default="info@osteonlife.com")
    phone = models.CharField(max_length=50, null=True, blank=True)
    website = models.URLField(default="https://www.osteonlife.com")
    map_embed_url = models.TextField(null=True, blank=True, help_text="The src URL of the Google Maps embed iframe.")

    twitter_url = models.URLField(null=True, blank=True)
    facebook_url = models.URLField(null=True, blank=True)
    instagram_url = models.URLField(null=True, blank=True)
    linkedin_url = models.URLField(null=True, blank=True)

    contact_tag = models.CharField(max_length=100, default="GET IN TOUCH WITH US !")
    contact_heading = models.CharField(max_length=150, default="Contact Us")
    newsletter_heading = models.CharField(max_length=100, default="Our Newsletter")
    newsletter_text = models.TextField(default="Subscribe to our newsletter and receive the latest news about our products and services!")
    designed_by_text = models.CharField(max_length=100, default="Dynamic Labz")
    designed_by_url = models.URLField(default="https://www.dynamiclabz.net/")

    default_meta_description = models.TextField(null=True, blank=True)
    default_meta_keywords = models.CharField(max_length=500, null=True, blank=True)

    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'

    @property
    def address_lines(self):
        return [line.strip() for line in (self.address or '').splitlines() if line.strip()]

    @property
    def website_label(self):
        return (self.website or '').replace('https://', '').replace('http://', '').rstrip('/')

    def __str__(self):
        return self.site_name


class HomePage(SingletonModel):
    """Everything on the home page that is not a repeating item."""

    meta_title = models.CharField(max_length=255, default="Osteon Life Science")
    meta_description = models.TextField(null=True, blank=True)
    meta_keywords = models.CharField(max_length=500, null=True, blank=True)

    # About
    show_about = models.BooleanField(default=True)
    about_tag = models.CharField(max_length=100, default="Who We Are")
    about_heading = models.CharField(max_length=150, default="About Us")
    about_paragraph_1 = models.TextField(null=True, blank=True)
    about_paragraph_2 = models.TextField(null=True, blank=True)
    about_image = models.ImageField(upload_to='home/', null=True, blank=True)

    # Products
    show_products = models.BooleanField(default=True)
    products_heading = models.CharField(max_length=150, default="Our Products")

    # Why choose us
    show_why_choose_us = models.BooleanField(default=True)
    why_tag = models.CharField(max_length=100, default="Why Choose Us")
    why_heading = models.CharField(max_length=150, default="The Osteon Advantage")
    why_subheading = models.CharField(max_length=255, null=True, blank=True)
    why_description = models.TextField(null=True, blank=True)
    why_image = models.ImageField(upload_to='home/', null=True, blank=True)
    why_button_text = models.CharField(max_length=100, null=True, blank=True, default="Discover Our Journey")
    why_button_url = models.CharField(max_length=255, null=True, blank=True, default="/about-us/")

    # Feature blocks / FAQ / contact
    show_feature_blocks = models.BooleanField(default=True)
    show_faqs = models.BooleanField(default=True)
    faq_tag = models.CharField(max_length=100, default="Got Questions?")
    faq_heading = models.CharField(max_length=150, default="Frequently Asked Questions")
    show_contact = models.BooleanField(default=True)

    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Home Page'
        verbose_name_plural = 'Home Page'

    def __str__(self):
        return "Home page"


class HomeBanner(models.Model):
    MEDIA_CHOICES = (('image', 'Image'), ('video', 'Video'))
    LAYOUT_CHOICES = (
        ('standard', 'Standard - text on the left, dark overlay'),
        ('glass', 'Glass panel - text in a panel on the right, no overlay'),
    )

    home_page = models.ForeignKey(HomePage, on_delete=models.CASCADE, related_name='banners')
    media_type = models.CharField(max_length=10, choices=MEDIA_CHOICES, default='image')
    background_image = models.ImageField(upload_to='banners/', null=True, blank=True, help_text="Required for image banners. Also used as the video poster.")
    background_video = models.FileField(upload_to='banners/', null=True, blank=True, help_text="MP4 file. Only used when media type is Video.")
    layout = models.CharField(max_length=10, choices=LAYOUT_CHOICES, default='standard', help_text="Only used for image banners.")

    eyebrow = models.CharField(max_length=150, null=True, blank=True, help_text="Small text above the title.")
    title_line_1 = models.CharField(max_length=150, help_text="First line of the title.")
    title_accent = models.CharField(max_length=150, null=True, blank=True, help_text="Second line, shown in the accent colour.")
    description = models.TextField(null=True, blank=True)

    primary_button_text = models.CharField(max_length=60, null=True, blank=True)
    primary_button_url = models.CharField(max_length=255, null=True, blank=True, help_text="e.g. /products/ or /category/trauma/ or https://...")
    secondary_button_text = models.CharField(max_length=60, null=True, blank=True)
    secondary_button_url = models.CharField(max_length=255, null=True, blank=True)

    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('order', 'id')
        verbose_name = 'Banner Slide'
        verbose_name_plural = 'Banner Slides'

    def __str__(self):
        return f"{self.title_line_1} {self.title_accent or ''}".strip()


class HomeAboutHighlight(models.Model):
    home_page = models.ForeignKey(HomePage, on_delete=models.CASCADE, related_name='about_highlights')
    text = models.CharField(max_length=150)
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('order', 'id')
        verbose_name = 'About Highlight'
        verbose_name_plural = 'About Highlights'

    def __str__(self):
        return self.text


class HomeFeaturedProduct(models.Model):
    """Products picked for the 'Our Products' tabs. The tab is the product's category."""

    home_page = models.ForeignKey(HomePage, on_delete=models.CASCADE, related_name='featured_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='featured_on_home')
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('order', 'id')
        unique_together = (('home_page', 'product'),)
        verbose_name = 'Featured Product'
        verbose_name_plural = 'Featured Products'

    def __str__(self):
        return self.product.name


class HomeWhyPoint(models.Model):
    home_page = models.ForeignKey(HomePage, on_delete=models.CASCADE, related_name='why_points')
    title = models.CharField(max_length=150)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('order', 'id')
        verbose_name = 'Why Choose Us Point'
        verbose_name_plural = 'Why Choose Us Points'

    def __str__(self):
        return self.title


class HomeFeatureBlock(models.Model):
    POSITION_CHOICES = (('left', 'Image on the left'), ('right', 'Image on the right'))

    home_page = models.ForeignKey(HomePage, on_delete=models.CASCADE, related_name='feature_blocks')
    tag = models.CharField(max_length=100, null=True, blank=True)
    heading = models.CharField(max_length=200)
    paragraph_1 = models.TextField(null=True, blank=True)
    paragraph_2 = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='home/', null=True, blank=True)
    image_alt = models.CharField(max_length=255, null=True, blank=True)
    image_position = models.CharField(max_length=5, choices=POSITION_CHOICES, default='left')
    button_text = models.CharField(max_length=100, null=True, blank=True)
    button_url = models.CharField(max_length=255, null=True, blank=True)

    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('order', 'id')
        verbose_name = 'Feature Block'
        verbose_name_plural = 'Feature Blocks'

    def __str__(self):
        return self.heading


class HomeFeatureBlockPoint(models.Model):
    feature_block = models.ForeignKey(HomeFeatureBlock, on_delete=models.CASCADE, related_name='points')
    icon_class = models.CharField(max_length=60, default='bi-shield-check', help_text="Any Bootstrap Icons class, e.g. bi-shield-check, bi-globe, bi-gear-wide-connected")
    title = models.CharField(max_length=150)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('order', 'id')
        verbose_name = 'Feature Point'
        verbose_name_plural = 'Feature Points'

    def __str__(self):
        return self.title


class HomeFAQ(models.Model):
    home_page = models.ForeignKey(HomePage, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=300)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('order', 'id')
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question
