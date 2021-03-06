"""
Django settings for app project.

Generated by 'django-admin startproject' using Django 2.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCTION = os.environ.get('DATABASE_URL') != None

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 's8evah-x#4&6f$wm51-(7w^su#7okn$uyq55l#ywv91(l5^*93'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'hangouts',
    'vsts'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'app.urls'

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

WSGI_APPLICATION = 'app.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
# If Using Heroku Environemnt, then Use Database Setting on Heroku
if PRODUCTION:
    DATABASES['default'] = dj_database_url.config()

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
STATIC_URL = '/static/'

# ------------------------------------------ App specific variables --------------------------------------------------

# 1. Hangouts API Token. GDN bot will include this token at every sent request
HANGOUTS_CHAT_API_TOKEN = 'SuCgaoGMzcA-U5xymm8khOEEezAapfV9fj5r2U3Tcjw='

# 2. Chatbot webhook Base URL
WEBHOOK_URL = "https://chatbot.gramedia.io"

# 3. VSTS Oauth App ID
VSTS_OAUTH_ID = "0EF27AD4-2D82-4B85-BBFA-53218FB4FABB"

# 4. VSTS Oauth App channel secret key.
VSTS_OAUTH_SECRET = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6Im9PdmN6NU1fN3AtSGpJS2xGWHo5M3VfVjBabyJ9.eyJjaWQiOiIwZWYyN2FkNC0yZDgyLTRiODUtYmJmYS01MzIxOGZiNGZhYmIiLCJjc2kiOiJhYzc2YzcxMS1iNmM4LTQ4YTYtOGJhNS0wNzliMWY5MmZlYzgiLCJuYW1laWQiOiJlMDE2NTI5My1lOWI3LTY0OWEtOGY3MS00NzBkYmMxNzQxZTQiLCJpc3MiOiJhcHAudnNzcHMudmlzdWFsc3R1ZGlvLmNvbSIsImF1ZCI6ImFwcC52c3Nwcy52aXN1YWxzdHVkaW8uY29tIiwibmJmIjoxNTM1NDQ2OTU5LCJleHAiOjE2OTMyMTMzNTl9.wfEOWAJJiuzUaVpZB79vBnnsrAPhsxI3W-j1Wp8Blfxhja2Ce02hf_IhPF1WhQLMo0TUDrSlNNg0R8eS54fQfxb5OtmXFLLvhcVAKyc3rtCEWsH0rGn8Zq-ukabUX2kb4nnPx-UGsu2218budDm_ecE0B46XRVPqYLMA3wrMsWt8YTFK8WRSYY8QnnZD6w27BJis2qtvIIXbC-fhtWqICSAOwvv4u_3bF2OxWwD3PuQbzez6Od01SNSrMpx-aw3EA0r2XFqCJ1nJMI-kyA8skVdvU6NBHTyk_3XeNF8oDnZH13XYb6sf-VxJsGvIbXBTGXVwo16fkJ0YRhQfJBTNEA"

# 5. VSTS Oauth Token will expire in 3600 seconds
VSTS_EXPIRY_TIME = 3599
