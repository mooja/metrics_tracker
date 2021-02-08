import environ
from pathlib import Path


env = environ.Env()


SECRET_KEY = env.str('SECRET_KEY')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default='localhost')
CACHES = {'default': env.cache('CACHE_URL')}
DATABASES = {'default': env.db_url('DATABASE_URL')}
LOGGING_LEVEL = env.str('LOGGING_LEVEL', default='WARNING')


root = environ.Path(__file__) - 2  # get root of the project
SITE_ROOT = root()

DEBUG = env.bool('DEBUG', default=False)
TEMPLATE_DEBUG = DEBUG

public_root = root.path('public/')
MEDIA_ROOT = public_root('media')
MEDIA_URL = env.str('MEDIA_URL', default='media/')

STATIC_ROOT = public_root('static')
STATIC_URL = env.str('STATIC_URL', default='static/')


INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "crispy_forms",
    "crispy_tailwind",
    "metrics_tracker.tracker",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware',
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

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

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': LOGGING_LEVEL,
    },
}

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS = [
    str(root.path('static/')),
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = "EST"

USE_I18N = True

USE_L10N = True

USE_TZ = True