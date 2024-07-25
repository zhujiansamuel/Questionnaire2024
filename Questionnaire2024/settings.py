"""
Django settings for Questionnaire2024 project.

Generated by 'django-admin startproject' using Django 4.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path
from django.conf import settings
import environ

env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-e^&n-gzc8ukb0#@xm2qolkip)e4)$+&6$jwt$!ljpm@_2!u3nu"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# DEBUG = False
ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    "debug_toolbar",
    "simpleui",
    # 'simplepro',
    'easyaudit',
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.core",
    "django.contrib.admin",
    'django.contrib.sites',
    "dashboards",
    "bootstrapform",
    "survey",
    'django_ckeditor_5',
    'allauth',
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.facebook",
    "allauth.socialaccount.providers.twitter",
    "allauth.socialaccount.providers.github",
]

AUTHENTICATION_BACKENDS = [

    'django.contrib.auth.backends.ModelBackend',
    # 'allauth.account.auth_backends.AuthenticationBackend',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    # 'simplepro.middlewares.SimpleMiddleware',
]

SITE_ID = 1


ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_LOGOUT_ON_GET = True

# EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = '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'
DEFAULT_FROM_EMAIL = 'samuel20210214@gmail.com'
FROM_EMAIL = 'samuel20210214@gmail.com'
EMAIL_USE_TLS = True


ROOT_URLCONF = "Questionnaire2024.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS":  [
            './templates',
            # os.path.join(BASE_DIR, 'templates', 'allauth'),
            os.path.join(BASE_DIR, 'dashboards', 'static'),
            os.path.join(BASE_DIR, 'dashboards', 'templates')
                  ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },

    },
]

WSGI_APPLICATION = "Questionnaire2024.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "question.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = False

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# STATICFILES_DIRS = [os.path.join(BASE_DIR, "static"),]
#STATIC_ROOT = 'static'


MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

CKEDITOR_UPLOAD_PATH = os.path.join(BASE_DIR, MEDIA_ROOT, 'upload')
# CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'
CKEDITOR_IMAGE_BACKEND = 'pillow'

customColorPalette = [
    {
        'color': 'hsl(4, 90%, 58%)',
        'label': 'Red'
    },
    {
        'color': 'hsl(340, 82%, 52%)',
        'label': 'Pink'
    },
    {
        'color': 'hsl(291, 64%, 42%)',
        'label': 'Purple'
    },
    {
        'color': 'hsl(262, 52%, 47%)',
        'label': 'Deep Purple'
    },
    {
        'color': 'hsl(231, 48%, 48%)',
        'label': 'Indigo'
    },
    {
        'color': 'hsl(207, 90%, 54%)',
        'label': 'Blue'
    },
]

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                    'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],

    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
        'code','subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing', 'insertImage',
                    'bulletedList', 'numberedList', 'todoList', '|',  'blockQuote', 'imageUpload', '|',
                    'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                    'insertTable',],
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                        'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side',  '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]

        },
        'table': {
            'contentToolbar': [ 'tableColumn', 'tableRow', 'mergeTableCells',
            'tableProperties', 'tableCellProperties' ],
            'tableProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            },
            'tableCellProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            }
        },
        'heading' : {
            'options': [
                { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
                { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
                { 'model': 'heading2', 'view': 'h3', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
                { 'model': 'heading3', 'view': 'h5', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
            ]
        }
    },
    'list': {
        'properties': {
            'styles': 'true',
            'startIndex': 'true',
            'reversed': 'true',
        }
    }
}


# CKEDITOR_CONFIGS = {
#     'default': {
#         'toolbar': 'full',
#         'height': 300,
#         'width': '100%',
#     },
# }



# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "dashboards.ApplicationUser"


LOGIN_REDIRECT_URL = '/survey/'
LOGOUT_REDIRECT_URL = '/'

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

EXCEL_COMPATIBLE_CSV = True
CHOICES_SEPARATOR = "|"
USER_DID_NOT_ANSWER = "NAA"

from pathlib import Path
TEX_CONFIGURATION_FILE = Path("tex", "tex.conf")
SURVEY_DEFAULT_PIE_COLOR = "blue!50"

DISPLAY_SURVEY_QUESTIONNAIRE_INFORMATION = True
SESSION_SAVE_EVERY_REQUEST = True


SIMPLEUI_HOME_INFO = False
SIMPLEUI_HOME_ACTION = True
SIMPLEUI_ANALYSIS = False

SIMPLEUI_CONFIG = {
    'system_keep': False,
    'menu_display': ['調査のグローバル設定', 'ユーザー', '調査セット', '回答のセット','Request記録'],
    'dynamic': True,
    'menus':
    [
        {
            'name': '調査のグローバル設定',
            'icon': 'fa-solid fa-gear',
            'url': '/dashboards/global-setup-page/',
            'newTab': False,
        },

        {
            'name': 'ユーザー',
            'icon': 'fas fa-user-shield',
            'url': '/admin/dashboards/applicationuser/',
            'newTab': False,
        },

        {
            'name': '調査セット',
            'icon': 'fa-solid fa-square-poll-horizontal',
            'url': '/admin/survey/survey/',
            'newTab': False,
        },

        {
            'name': '回答のセット',
            'icon': 'fa-regular fa-comment-dots',
            'url': '/admin/survey/response/',
            'newTab': False,
        },
        {
            'name': 'Request記録',
            'icon': 'fa-solid fa-camera-retro',
            'url': '/admin/easyaudit/requestevent/',
        },

    ]
}


INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'my_cache_table',
    }
}

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# SESSION_COOKIE_AGE = 60 * 60 * 24


DJANGO_EASY_AUDIT_WATCH_MODEL_EVENTS = True
DJANGO_EASY_AUDIT_WATCH_AUTH_EVENTS = True
DJANGO_EASY_AUDIT_WATCH_REQUEST_EVENTS = True
DJANGO_EASY_AUDIT_UNREGISTERED_URLS_DEFAULT = [r'^/admin/',
                                               r'^/ajax/',
                                               r'^/dashboards/',
                                               r'^/static/',
                                               r'^/favicon.ico$',
                                               r'^/media/',
                                               r'^/sp/',
                                               r'^/__debug__/',
                                               r'^/ckeditor5/',
                                               r'^/api-auth/',
                                               ]
