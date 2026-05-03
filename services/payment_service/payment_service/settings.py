from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',

    'rest_framework',
    'rest_framework_simplejwt',

    'payment',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'payment_service.urls'

WSGI_APPLICATION = 'payment_service.wsgi.application'

DATABASES = {
    'default': env.db('DATABASE_URL')
}

TIME_ZONE = 'UTC'
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

_KEYS_DIR = BASE_DIR.parent.parent / 'keys'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'payment.authentication.ServiceJWTAuthentication',
    ],
}

SIMPLE_JWT = {
    'ALGORITHM': 'RS256',
    'SIGNING_KEY': None,
    'VERIFYING_KEY': open(_KEYS_DIR / 'public.pem').read(),
}

RABBITMQ_URL = env(
    'RABBITMQ_URL', default='amqp://guest:guest@localhost:5672/')
