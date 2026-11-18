"""
Fill the Home Page + Site Settings with the content of the original static website, so every
section is editable from Django admin straight away.

Usage:
    python manage.py seed_site_content            # only seeds an empty home page
    python manage.py seed_site_content --reset    # wipes banners/FAQs/... and seeds again

Images are copied from  static/img/  into  media/  when they exist, e.g.
    static/img/Banner2.png
    static/img/ABOUT US.png
Files that are missing are skipped with a warning; upload them from the admin later.
"""
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction
from django.urls import reverse

from Catalog.models import Product
from SiteContent.models import (
    SiteSetting, HomePage, HomeBanner, HomeAboutHighlight, HomeFeaturedProduct,
    HomeWhyPoint, HomeFeatureBlock, HomeFeatureBlockPoint, HomeFAQ,
)

STATIC_IMG = Path(settings.BASE_DIR) / 'static' / 'img'
FEATURED_PER_CATEGORY = 5
MAP_EMBED_URL = (
    "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d4521.070618239124!2d72.4535156!3d22.9403951!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x395e911724c19011%3A0x2a7435c0da8b4dab!2sOsteon%20Life%20Science%20Pvt.%20Ltd.!5e1!3m2!1sen!2sin!4v1791611510216!5m2!1sen!2sin"
)

ABOUT_HIGHLIGHTS = [
    "Perfect Planning", "Professional Workers", "First Working Process",
    "Efficient Execution", "Customer Focus", "Advanced Technology",
]

WHY_POINTS = [
    ("Uncompromising Quality:", "Rigorous biomechanical testing and strict adherence to global regulatory standards and international ISO certifications."),
    ("Advanced Infrastructure:", "State-of-the-art in-house CNC machining, 5-axis mill-turn centers, and sterile cleanroom packaging facilities."),
    ("Comprehensive Portfolio:", "A massive catalog of trauma, spine, and joint solutions, alongside agile OEM & ODM manufacturing services."),
]

FAQS = [
    ("What quality certifications do your products hold?", "All our products undergo strict quality control and comply with international health and safety regulations, ensuring they meet the highest medical and pharmaceutical standards."),
    ("How does Osteon Life Science ensure the efficacy of its products?", "We invest heavily in ongoing research and development, rigorous clinical testing, and sourcing premium raw materials so that every product delivers measurable, reliable results."),
    ("Do you supply to both healthcare facilities and individual consumers?", "Yes, we proudly partner with hospitals, clinics, and pharmacies for bulk supply, while also providing select product lines directly to consumers for continued care."),
    ("Are your implants supplied sterile or non-sterile?", "We offer both sterile and non-sterile product lines to meet the specific requirements of our clients. Our sterile products are processed and packaged in state-of-the-art cleanroom facilities to ensure maximum patient safety."),
    ("Do you export products internationally?", "Yes. While we are proudly \"Made in India,\" our products are \"Made for the World.\" We have a robust global distribution network and regularly export our orthopedic implants and instruments to international markets."),
    ("What is the typical lead time for custom OEM/ODM manufacturing?", "Lead times vary depending on the complexity and volume of the order. However, our lean manufacturing processes and agile team allow us to adapt quickly and offer highly competitive timelines without compromising on quality."),
    ("Are your manufacturing facilities ISO certified?", "Absolutely. Our world-class manufacturing infrastructure strictly adheres to international regulatory guidelines for medical device manufacturing, ensuring consistent quality and compliance."),
]


class Command(BaseCommand):
    help = "Seed the home page and site settings with the original website content."

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Delete existing home page items and seed again')

    def handle(self, *args, **options):
        self.missing = []

        with transaction.atomic():
            site = SiteSetting.get_solo()
            if not site.map_embed_url:
                site.map_embed_url = MAP_EMBED_URL
                site.save()
            home = HomePage.get_solo()

            has_content = home.banners.exists() or home.faqs.exists() or home.why_points.exists()
            if has_content and not options['reset']:
                self.stdout.write(self.style.WARNING("Home page already has content. Use --reset to seed again."))
                return
            if options['reset']:
                for related in ('banners', 'about_highlights', 'featured_products', 'why_points', 'feature_blocks', 'faqs'):
                    getattr(home, related).all().delete()

            self.seed_home_fields(home)
            self.seed_banners(home)
            self.seed_about_highlights(home)
            self.seed_why_points(home)
            self.seed_feature_blocks(home)
            self.seed_faqs(home)
            self.seed_featured_products(home)

        for path in sorted(set(self.missing)):
            self.stdout.write(self.style.WARNING(f"Image not found (skipped): static/img/{path}"))
        self.stdout.write(self.style.SUCCESS("Site content seeded."))

    # ------------------------------------------------------------------
    def attach(self, field_file, relative_path):
        source = STATIC_IMG / relative_path
        if not source.exists():
            self.missing.append(relative_path)
            return
        with open(source, 'rb') as handle:
            field_file.save(source.name, File(handle), save=False)

    def seed_home_fields(self, home):
        home.meta_title = "Osteon Life Science | Orthopaedic Implants & Instruments"
        home.meta_description = (
            "Osteon Life Science is a next-generation manufacturer of orthopaedic implants and instruments, "
            "offering trauma, foot and ankle and craniomaxillofacial systems plus OEM and ODM manufacturing."
        )
        home.meta_keywords = "orthopaedic implants manufacturer India, trauma implants, foot and ankle implants, CMF implants, OEM ODM orthopaedic implants"
        home.about_paragraph_1 = (
            "Osteon Life Science Pvt. Ltd. is a next-generation manufacturer of orthopedic implants and instruments, "
            "driven by INNOVATION, PRECISION, and a PASSION for improving lives."
        )
        home.about_paragraph_2 = "Based in India, we design and produce world-class orthopedic solutions that meet global quality and regulatory standards"
        home.why_subheading = "Precision-Engineered Solutions for Better Outcomes"
        home.why_description = (
            "We combine advanced manufacturing technology with deep clinical insights to deliver world-class orthopedic "
            "implants that surgeons trust and patients rely on for a seamless recovery."
        )
        home.why_button_url = reverse('about-us-list')
        self.attach(home.about_image, 'ABOUT US.png')
        self.attach(home.why_image, 'Why choose us.png')
        home.save()

    def seed_banners(self, home):
        products_url = reverse('products-list')
        contact_url = reverse('home-list') + '#contact'
        about_url = reverse('about-us-list')
        downloads_url = reverse('downloads-list')

        slides = [
            dict(media_type='video', video='19538560-uhd_3840_2160_24fps.mp4', eyebrow="Premium Orthopedic Solutions",
                 title_line_1="Restoring Mobility,", title_accent="Rebuilding Lives",
                 description="Precision-engineered trauma, foot & ankle and craniomaxillofacial implants trusted by surgeons worldwide for superior clinical outcomes.",
                 primary=("Explore Products", products_url), secondary=("Contact Us", contact_url)),
            dict(image='Banner2.png', eyebrow="Advanced Trauma Systems",
                 title_line_1="Precision Trauma", title_accent="Implant Solutions",
                 description="Engineered locking plates, screws and trauma systems designed for exceptional stability, faster recovery and reliable surgical outcomes.",
                 primary=("Explore Products", products_url), secondary=("Contact Sales", contact_url)),
            dict(image='placa_mini_e_micro_mao-1.png', eyebrow="Mini & Micro Plating",
                 title_line_1="Designed For", title_accent="Surgical Precision",
                 description="High-performance mini and micro plating systems developed for maxillofacial, hand and small bone fixation procedures.",
                 primary=("View Portfolio", products_url), secondary=("Request Quote", contact_url)),
            dict(image='Placa_pe-1.png', eyebrow="Premium Orthopedic Technology",
                 title_line_1="Innovation That", title_accent="Supports Every Surgery",
                 description="Manufactured under stringent international quality standards to deliver dependable performance in every procedure.",
                 primary=("Learn More", about_url), secondary=("Download Catalog", downloads_url)),
            dict(image='small_fragments_inferior_features-scaled.png.webp', layout='glass', eyebrow="Trusted Across The Globe",
                 title_line_1="Quality Healthcare", title_accent="Without Compromise",
                 description="World-class orthopedic implants and OEM manufacturing solutions trusted by healthcare professionals worldwide.",
                 primary=("Become a Partner", contact_url), secondary=("Why Osteon", about_url)),
        ]
        for index, slide in enumerate(slides, start=1):
            banner = HomeBanner(
                home_page=home,
                media_type=slide.get('media_type', 'image'),
                layout=slide.get('layout', 'standard'),
                eyebrow=slide['eyebrow'],
                title_line_1=slide['title_line_1'],
                title_accent=slide['title_accent'],
                description=slide['description'],
                primary_button_text=slide['primary'][0], primary_button_url=slide['primary'][1],
                secondary_button_text=slide['secondary'][0], secondary_button_url=slide['secondary'][1],
                order=index * 10,
            )
            if slide.get('video'):
                self.attach(banner.background_video, slide['video'])
            if slide.get('image'):
                self.attach(banner.background_image, slide['image'])
            banner.save()

    def seed_about_highlights(self, home):
        for index, text in enumerate(ABOUT_HIGHLIGHTS, start=1):
            HomeAboutHighlight.objects.create(home_page=home, text=text, order=index * 10)

    def seed_why_points(self, home):
        for index, (title, description) in enumerate(WHY_POINTS, start=1):
            HomeWhyPoint.objects.create(home_page=home, title=title.rstrip(':'), description=description, order=index * 10)

    def seed_feature_blocks(self, home):
        products_url = reverse('products-list')
        contact_url = reverse('home-list') + '#contact'

        first = HomeFeatureBlock(
            home_page=home, tag="Clinical Excellence",
            heading="Pioneering Precision in Orthopedic Implants",
            paragraph_1="At Osteon Life Science, we leverage cutting-edge manufacturing technology and deep clinical expertise to develop trauma, spine, and joint implants that ensure superior biomechanical stability.",
            paragraph_2="Every product undergoes rigorous mechanical testing and quality control to guarantee optimal performance, faster patient recovery, and lasting reliability in the operating room.",
            image_alt="Precision Orthopedic Implants", image_position='left',
            button_text="Explore Our Range", button_url=products_url, order=10,
        )
        self.attach(first.image, 'why_coose_us_3.webp')
        first.save()

        second = HomeFeatureBlock(
            home_page=home, tag="OEM & ODM Services",
            heading="Your Trusted Partner in Global Manufacturing",
            paragraph_1="We provide comprehensive, end-to-end contract manufacturing solutions. Driven by state-of-the-art 5-axis CNC machining and sterile cleanroom packaging, we scale to meet your exact specifications.",
            image_alt="Global Manufacturing", image_position='right',
            button_text="Partner With Us", button_url=contact_url, order=20,
        )
        self.attach(second.image, 'why_coose_us_1.webp')
        second.save()

        points = [
            ('bi-shield-check', "ISO 13485 Certified", "Strict adherence to international medical device quality standards."),
            ('bi-gear-wide-connected', "Agile Production", "Lean, cost-effective manufacturing from prototyping to high-volume rollout."),
            ('bi-globe', "Global Export", "A robust distribution network delivering \"Made in India\" excellence worldwide."),
        ]
        for index, (icon, title, description) in enumerate(points, start=1):
            HomeFeatureBlockPoint.objects.create(feature_block=second, icon_class=icon, title=title, description=description, order=index * 10)

    def seed_faqs(self, home):
        for index, (question, answer) in enumerate(FAQS, start=1):
            HomeFAQ.objects.create(home_page=home, question=question, answer=answer, order=index * 10)

    def seed_featured_products(self, home):
        """Pick the first few P1 products of every category (falls back to any product)."""
        products = (
            Product.objects.filter(active=True)
            .select_related('sub_category__category')
            .order_by('sub_category__category__order', 'launch_priority', 'sub_category__order', 'order')
        )
        taken = {}
        order = 0
        for product in products:
            category_id = product.sub_category.category_id
            if taken.get(category_id, 0) >= FEATURED_PER_CATEGORY:
                continue
            taken[category_id] = taken.get(category_id, 0) + 1
            order += 10
            HomeFeaturedProduct.objects.create(home_page=home, product=product, order=order)
