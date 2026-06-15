from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set. Add it to your .env file.")

DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,mealflow2026.vercel.app').split(',')

# Vercel / reverse-proxy settings
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000,https://mealflow2026.vercel.app').split(',')
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition
INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'myapp',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

UNFOLD = {
    "SITE_TITLE": "MealFlow Admin",
    "SITE_HEADER": "MealFlow Admin Dashboard",
    "SITE_SYMBOL": "speed",  
    "THEME": "emerald",      
    "SHOW_HISTORY": True,
    "SHOW_SIDEBAR_FILTER": True,
    "DASHBOARD_CALLBACK": "myapp.utils.dashboard_callback",
    "COLORS": {
        "primary": {
            "50": "#f0fdf4",
            "100": "#dcfce7",
            "200": "#bbf7d0",
            "300": "#86efac",
            "400": "#4ade80",
            "500": "#22c55e",  
            "600": "#16a34a",
            "700": "#15803d",
            "800": "#166534",
            "900": "#14532d",
            "950": "#052e16",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Navigation",
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": "/admin/",
                    },
                    {
                        "title": "Meal Schedules",
                        "icon": "restaurant_menu",
                        "link": "/admin/myapp/menuitem/",
                    },
                ],
            },
            {
                "title": "Customer Escalations",
                "items": [
                    {
                        "title": "Reported Issues",
                        "icon": "report_problem",
                        "link": "/admin/myapp/reportissue/",
                    },
                    {
                        "title": "Reviews & Ratings",
                        "icon": "star",
                        "link": "/admin/myapp/mealreview/",
                    },
                    {
                        "title": "Enquiries & Questions",
                        "icon": "mail",
                        "link": "/admin/myapp/enquiry/",
                    },
                ],
            },
            {
                "title": "Finance & Subscriptions",
                "items": [
                    {
                        "title": "Subscribers",
                        "icon": "person",
                        "link": "/admin/myapp/subscriberinfo/",
                    },
                    {
                        "title": "Payments Got",
                        "icon": "payments",
                        "link": "/admin/myapp/paymentinfo/",
                    },
                ],
            },
        ],
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'MealFlow.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'MealFlow.wsgi.application'

# Database - Supabase
DATABASES = {
    'default': dj_database_url.parse(os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3'))
}

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Stripe
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', '')
