"""
Django settings for costuras_paqui project.
"""
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = config('SECRET_KEY', default='dev-secret-key-change-me')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*'] if DEBUG else []


# IMPORTANT: 'unfold' MUST come BEFORE 'django.contrib.admin'
# This is the most common Unfold setup mistake.
INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.inlines',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'shop',
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

ROOT_URLCONF = 'costuras_paqui.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'costuras_paqui.wsgi.application'


# DATABASE
# To use PostgreSQL, fill in .env and use the 'postgresql' engine.
# To use SQLite for quick local testing, set USE_SQLITE=True in .env.
USE_SQLITE = config('USE_SQLITE', default=False, cast=bool)

if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='costuras_paqui'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default='postgres'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# DJANGO UNFOLD CONFIGURATION
# Sidebar grouping makes the 10 entities easy to navigate.
# Each member's models go in their assigned group.
UNFOLD = {
    "SITE_TITLE": "Costuras de Paqui",
    "SITE_HEADER": "Costuras de Paqui",
    "SITE_SUBHEADER": "Sewing shop management",
    "SITE_URL": "/",
    "SITE_SYMBOL": "checkroom",  # material icon shown next to the site title
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    "LOGIN": {
        "image": None,
    },
    "BORDER_RADIUS": "8px",
    "COLORS": {
        # Softer dusty rose - feels more like a tailor shop, less like a candy store
        "base": {
            "50": "250 250 250",
            "100": "244 244 245",
            "200": "228 228 231",
            "300": "212 212 216",
            "400": "161 161 170",
            "500": "113 113 122",
            "600": "82 82 91",
            "700": "63 63 70",
            "800": "39 39 42",
            "900": "24 24 27",
            "950": "9 9 11",
        },
        "primary": {
            "50": "253 244 247",
            "100": "252 231 238",
            "200": "250 207 224",
            "300": "246 169 199",
            "400": "240 121 168",
            "500": "228 78 138",
            "600": "210 52 113",
            "700": "180 38 92",
            "800": "150 33 76",
            "900": "126 30 66",
            "950": "76 12 36",
        },
        "font": {
            "subtle-light": "var(--color-base-500)",
            "subtle-dark": "var(--color-base-400)",
            "default-light": "var(--color-base-600)",
            "default-dark": "var(--color-base-300)",
            "important-light": "var(--color-base-900)",
            "important-dark": "var(--color-base-100)",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Customers",
                "separator": True,
                "items": [
                    {
                        "title": "Customers",
                        "icon": "person",
                        "link": "/admin/shop/customer/",
                    },
                ],
            },
            {
                "title": "Orders",
                "separator": True,
                "items": [
                    {
                        "title": "Orders",
                        "icon": "receipt_long",
                        "link": "/admin/shop/order/",
                    },
                    {
                        "title": "Order Items",
                        "icon": "list_alt",
                        "link": "/admin/shop/orderitem/",
                    },
                ],
            },
            {
                "title": "Garments & Materials",
                "separator": True,
                "items": [
                    {
                        "title": "Garments",
                        "icon": "checkroom",
                        "link": "/admin/shop/garment/",
                    },
                    {
                        "title": "Materials",
                        "icon": "inventory_2",
                        "link": "/admin/shop/material/",
                    },
                ],
            },
            {
                "title": "Production",
                "separator": True,
                "items": [
                    {
                        "title": "Employees",
                        "icon": "badge",
                        "link": "/admin/shop/employee/",
                    },
                    {
                        "title": "Work Tickets",
                        "icon": "assignment",
                        "link": "/admin/shop/workticket/",
                    },
                    {
                        "title": "Production Logs",
                        "icon": "history",
                        "link": "/admin/shop/productionlog/",
                    },
                ],
            },
            {
                "title": "Delivery",
                "separator": True,
                "items": [
                    {
                        "title": "Deliveries",
                        "icon": "local_shipping",
                        "link": "/admin/shop/delivery/",
                    },
                ],
            },
            {
                "title": "Tools",
                "separator": True,
                "items": [
                    {
                        "title": "Production Calendar",
                        "icon": "calendar_month",
                        "link": "/admin/calendar/",
                    },
                ],
            },
        ],
    }
}