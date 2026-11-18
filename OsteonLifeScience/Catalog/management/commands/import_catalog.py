"""
Import Category > Sub Category > Product from the SEO developer brief (Excel).

Usage:
    python manage.py import_catalog
    python manage.py import_catalog --file data/other.xlsx
    python manage.py import_catalog --update          # overwrite rows that already exist
    python manage.py import_catalog --hide-later      # import "P3 - Later" rows as hidden

Sheet "SEO Page Map" columns:
    Main Category | Parent Category | Proposed Page / Subcategory | Page Type | Proposed URL |
    Primary Keyword Theme | Secondary Keyword Themes | Suggested SEO Title | Suggested H1 |
    Suggested Meta Description | Launch Priority | Content / Product Status | Developer / Content Notes
"""
from pathlib import Path

import openpyxl
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from Catalog.models import Category, SubCategory, Product, CatalogPageSetting

SHEET_NAME = 'SEO Page Map'
DEFAULT_FILE = Path(settings.BASE_DIR) / 'data' / 'Osteon_Website_Product_Categories_SEO_Developer_Brief.xlsx'

CATEGORY_PAGE_TYPES = {'category landing'}
SUB_CATEGORY_PAGE_TYPES = {'subcategory', 'anatomical category'}
PRODUCT_PAGE_TYPES = {'product family'}
CATALOG_ROOT_NAME = 'all products'

STATUS_MAP = {
    'create / review': 'create_review',
    'verify portfolio': 'verify_portfolio',
    'development / verify': 'development_verify',
    'review existing page': 'review_existing',
}


def clean(value):
    if value is None:
        return ''
    return str(value).strip()


def parse_priority(value):
    value = clean(value).upper()
    for code in ('P1', 'P2', 'P3'):
        if value.startswith(code):
            return code
    return 'P3'


def last_url_segment(url):
    parts = [p for p in clean(url).split('/') if p]
    return parts[-1] if parts else ''


class Command(BaseCommand):
    help = "Import categories, sub categories and products from the SEO developer brief Excel file."

    def add_arguments(self, parser):
        parser.add_argument('--file', default=str(DEFAULT_FILE), help='Path to the .xlsx file')
        parser.add_argument('--update', action='store_true', help='Overwrite records that already exist')
        parser.add_argument('--hide-later', action='store_true', help='Import "P3 - Later" rows as inactive')

    def handle(self, *args, **options):
        path = Path(options['file'])
        if not path.exists():
            raise CommandError(f"File not found: {path}")

        workbook = openpyxl.load_workbook(path, data_only=True)
        if SHEET_NAME not in workbook.sheetnames:
            raise CommandError(f'Sheet "{SHEET_NAME}" not found. Sheets: {workbook.sheetnames}')

        rows = [r for r in workbook[SHEET_NAME].iter_rows(min_row=2, values_only=True) if any(r)]
        self.update = options['update']
        self.hide_later = options['hide_later']
        self.stats = {'categories': [0, 0], 'sub_categories': [0, 0], 'products': [0, 0]}  # [created, updated]
        self.category_order = {}
        self.warnings = []

        with transaction.atomic():
            # Pass 1: categories first, then sub categories, then products,
            # so the foreign keys always exist whatever the sheet order is.
            for row in rows:
                if clean(row[0]).lower() == CATALOG_ROOT_NAME:
                    self.import_catalog_page(row)
                elif clean(row[3]).lower() in CATEGORY_PAGE_TYPES:
                    self.import_category(row)

            for row in rows:
                if clean(row[3]).lower() in SUB_CATEGORY_PAGE_TYPES:
                    self.import_sub_category(row)

            for row in rows:
                if clean(row[3]).lower() in PRODUCT_PAGE_TYPES:
                    self.import_product(row)

        for label, (created, updated) in self.stats.items():
            self.stdout.write(self.style.SUCCESS(f"{label:<15} created: {created:<4} updated: {updated}"))
        for warning in self.warnings:
            self.stdout.write(self.style.WARNING(warning))
        self.stdout.write(self.style.SUCCESS("Catalog import finished."))

    # ------------------------------------------------------------------
    def common_fields(self, row):
        priority = parse_priority(row[10])
        meta_description = clean(row[9])
        return {
            'primary_keyword': clean(row[5]) or None,
            'secondary_keywords': clean(row[6]) or None,
            'seo_title': clean(row[7]) or None,
            'seo_h1': clean(row[8]) or None,
            'meta_description': meta_description or None,
            'launch_priority': priority,
            'content_status': STATUS_MAP.get(clean(row[11]).lower(), 'create_review'),
            'developer_notes': clean(row[12]) or None,
            'proposed_url': clean(row[4]) or None,
            'active': not (self.hide_later and priority == 'P3'),
        }

    def save(self, stat_key, instance, created):
        instance.save()
        self.stats[stat_key][0 if created else 1] += 1

    def upsert(self, model, lookup, fields, stat_key, slug=None):
        instance = model.objects.filter(**lookup).first()
        if instance is None:
            instance = model(**lookup, **fields)
            if slug:
                instance.slug = slug
            self.save(stat_key, instance, True)
        elif self.update:
            for key, value in fields.items():
                setattr(instance, key, value)
            self.save(stat_key, instance, False)
        return instance

    # ------------------------------------------------------------------
    def import_catalog_page(self, row):
        page = CatalogPageSetting.get_solo()
        if self.update or not page.meta_description:
            page.seo_title = clean(row[7]) or page.seo_title
            page.seo_h1 = clean(row[8]) or page.seo_h1
            page.meta_description = clean(row[9]) or None
            page.intro = clean(row[9]) or None
            page.primary_keyword = clean(row[5]) or None
            page.secondary_keywords = clean(row[6]) or None
            page.save()

    def import_category(self, row):
        name = clean(row[0])
        order = (len(self.category_order) + 1) * 10
        self.category_order[name] = order
        fields = self.common_fields(row)
        fields.update({
            'order': order,
            'short_description': (clean(row[9]) or '')[:300] or None,
            'description': clean(row[9]) or None,
        })
        fields['active'] = True  # top level pages stay visible; products decide what is shown
        self.upsert(Category, {'name': name}, fields, 'categories', slug=last_url_segment(row[4]) or None)

    def import_sub_category(self, row):
        category = Category.objects.filter(name=clean(row[0])).first()
        if not category:
            self.warnings.append(f"Skipped sub category '{clean(row[2])}': category '{clean(row[0])}' not found.")
            return
        name = clean(row[2])
        count = SubCategory.objects.filter(category=category).count()
        fields = self.common_fields(row)
        fields.update({
            'order': (count + 1) * 10,
            'short_description': (clean(row[9]) or '')[:300] or None,
            'description': clean(row[9]) or None,
        })
        self.upsert(SubCategory, {'category': category, 'name': name}, fields, 'sub_categories')

    def import_product(self, row):
        category = Category.objects.filter(name=clean(row[0])).first()
        parent_name = clean(row[1])
        sub_category = SubCategory.objects.filter(category=category, name=parent_name).first() if category else None
        if not sub_category:
            self.warnings.append(
                f"Skipped product '{clean(row[2])}': sub category '{parent_name}' not found in '{clean(row[0])}'."
            )
            return
        name = clean(row[2])
        count = Product.objects.filter(sub_category=sub_category).count()
        fields = self.common_fields(row)
        fields.update({
            'order': (count + 1) * 10,
            'short_description': (clean(row[9]) or '')[:300] or None,
            'overview': clean(row[9]) or None,
        })
        self.upsert(Product, {'sub_category': sub_category, 'name': name}, fields, 'products')
