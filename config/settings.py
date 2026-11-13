"""Настройки Django, приложений, API и базы данных проекта rental.

Параметры окружения загружаются из .env. Для базы можно выбрать
MySQL, иначе используется SQLite.
"""

import os
import environ
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / '.env')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')

# SECURITY WARNING: don't run with debug turned on in production!

ALLOWED_HOSTS = env.list(
    'ALLOWED_HOSTS',
    default=['127.0.0.1', 'localhost'],)


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'django_filters',

    'apps.base.apps.BaseConfig',
    'apps.users.apps.UsersConfig',
    'apps.static.apps.StaticConfig',
    'apps.reviews.apps.ReviewsConfig',
    'apps.bookings.apps.BookingsConfig',
    'apps.analytics.apps.AnalyticsConfig',
    'apps.rental_auth.apps.RentalAuthConfig',
    'apps.listings.apps.ListingsConfig',
    'rest_framework_simplejwt.token_blacklist',  # для возможности отзыва refresh-токенов
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

REST_FRAMEWORK = {'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',
                                              'rest_framework.filters.SearchFilter',
                                              'rest_framework.filters.OrderingFilter',),
              'DEFAULT_PAGINATION_CLASS': 'pagination.RentalPageNumberPagination',
              'DEFAULT_AUTHENTICATION_CLASSES': [
                    'rest_framework_simplejwt.authentication.JWTAuthentication',
                  # 'rest_framework.authentication.BasicAuthentication',
                  # 'rest_framework.authentication.TokenAuthentication',
              ],
              "DEFAULT_PERMISSION_CLASSES": [
                    "rest_framework.permissions.IsAuthenticated",],
             'DEFAULT_THROTTLE_CLASSES': [
                     'rest_framework.throttling.AnonRateThrottle',
                     'rest_framework.throttling.UserRateThrottle'
                 ],
            'DEFAULT_THROTTLE_RATES': {
                    'anon': '100/m',
                    'user': '100/m'
                },
              }

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=10),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=100),
    'ROTATE_REFRESH_TOKENS': True, # при refresh генерить новый refresh
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
}

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases
if env.bool('MYSQL', default=False):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': env('DB_NAME'),
            'USER': env('DB_USER'),
            'PASSWORD': env('DB_PASSWORD'),
            'HOST': env('DB_HOST', default="localhost"),
            'PORT': env('DB_PORT', default="3306"),
            'OPTIONS': {'charset': 'utf8mb4'},
        },
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        },
    }


AUTH_USER_MODEL = "users.User"


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
LANGUAGES = [
    ('ua', 'Украинский'),
    ('ru', 'Русский'),
    ('en', 'English'),
    ('de', 'Deutsch'),
]
TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Email
# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration

MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}
