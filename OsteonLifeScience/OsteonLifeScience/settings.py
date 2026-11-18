import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-z3%^*ppzig5p3(+apf%g0ue(jim9)+@-s-97to&v4(+rrhw+ur'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = ["https://*.v0.build"] + [
"http://127.0.0.1:8000"
]


# Application definition

INSTALLED_APPS = [
    "jazzmin",  # must be before django.contrib.admin
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "rest_framework",
    "UserDetail",
    "Catalog",
    "SiteContent",
    "FrontEnd"
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'OsteonLifeScience.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        "DIRS": [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "SiteContent.context_processors.site_globals",
            ],
        },
    },
]

WSGI_APPLICATION = 'OsteonLifeScience.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = "UserDetail.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True



STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.SessionAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
}

# Hosts that render the preview inside an iframe need cookies to be sent cross-site.
# if env_bool("DJANGO_EMBEDDED_PREVIEW", False):
#     SESSION_COOKIE_SAMESITE = "None"
#     SESSION_COOKIE_SECURE = True
#     CSRF_COOKIE_SAMESITE = "None"
#     CSRF_COOKIE_SECURE = True
#     X_FRAME_OPTIONS = "ALLOWALL"

# Used by the sitemap, canonical links and structured data. Leave empty to use the request host.
SITE_BASE_URL = os.environ.get("SITE_BASE_URL", "")

# ---------------------------------------------------------------------------
# Django admin (Jazzmin) look & feel
# ---------------------------------------------------------------------------
JAZZMIN_SETTINGS = {
    "site_title": "Osteon Admin",
    "site_header": "Osteon Life Science",
    "site_brand": "Osteon CMS",
    "site_logo": None,
    "welcome_sign": "Manage products, categories and website content",
    "copyright": "Osteon Life Science Pvt. Ltd.",
    "search_model": ["Catalog.Product"],
    "user_avatar": None,
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "View Website", "url": "/", "new_window": True},
        {"name": "Products Page", "url": "/products/", "new_window": True},
    ],
    "usermenu_links": [{"name": "View Website", "url": "/", "new_window": True}],
    "show_sidebar": True,
    "navigation_expanded": True,
    "order_with_respect_to": [
        "catalog",
        "catalog.category",
        "catalog.subcategory",
        "catalog.product",
        "catalog.catalogpagesetting",
        "sitecontent",
        "sitecontent.homepage",
        "sitecontent.homefeatureblock",
        "sitecontent.sitesetting",
        "userdetail",
        "auth",
    ],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.Group": "fas fa-users",
        "UserDetail.User": "fas fa-user-shield",
        "Catalog": "fas fa-boxes",
        "Catalog.Category": "fas fa-sitemap",
        "Catalog.SubCategory": "fas fa-folder-tree",
        "Catalog.Product": "fas fa-bone",
        "Catalog.CatalogPageSetting": "fas fa-store",
        "SiteContent": "fas fa-globe",
        "SiteContent.HomePage": "fas fa-home",
        "SiteContent.HomeFeatureBlock": "fas fa-puzzle-piece",
        "SiteContent.SiteSetting": "fas fa-cog",
    },
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": True,
    "custom_css": "admin/css/osteon_admin.css",
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "default_theme_mode": "light",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}

