from pathlib import Path
import os
 
BASE_DIR = Path(__file__).resolve().parent.parent
 
SECRET_KEY = "django-insecure-change-this-in-production-xyz123"
 
# Must be True for media files to be served locally
DEBUG = True
 
ALLOWED_HOSTS = ['*']
 
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'detection',
]
 
# Removed whitenoise — not needed for local development
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
 
ROOT_URLCONF = 'violence_detection.urls'
 
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
 
WSGI_APPLICATION = 'violence_detection.wsgi.application'
 
# Simple SQLite — no dj_database_url needed
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
 
# Static files
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
 
# Media files — screenshots and uploads
MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
 
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
 
# ==========================
# ML Model Configuration
# ==========================
 
# IMPORTANT: Update this to your actual model path
MODEL_PATH = r'D:\visionguard_v2\violence_detection\api\modelnew.h5'
 
IMG_SIZE  = 128
THRESHOLD = 0.3
 
# Authentication
LOGIN_URL          = '/login/'
LOGIN_REDIRECT_URL = '/'
 
# Upload limits (500MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 524288000
FILE_UPLOAD_MAX_MEMORY_SIZE = 524288000