import os
import dj_database_url
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================
# SEGURIDAD Y CONFIGURACIÓN HARDCODEADA
# ==========================================

# Tu clave secreta fija (Cuidado con subirla a repos públicos en el futuro)
SECRET_KEY = 'django-insecure-qzmotors-produccion-2026-clave-fija'

# DEBUG en True para ver la pantalla amarilla si algo falla
DEBUG = True 

# Lista de hosts permitidos (Hardcodeados para evitar el error 400)
ALLOWED_HOSTS = [
    'qzmotors.cl',
    'www.qzmotors.cl',
    'web-production-0711f.up.railway.app',
    'localhost',
    '127.0.0.1',
    '*', # El comodín final para asegurar que nada rebote
]

# Orígenes confiables para formularios (Crucial para el Admin)
CSRF_TRUSTED_ORIGINS = [
    'https://qzmotors.cl',
    'https://www.qzmotors.cl',
    'https://web-production-0711f.up.railway.app',
]

# Configuración necesaria para Cloudflare y Railway
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# ==========================================
# DEFINICIÓN DE APLICACIONES
# ==========================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'landing',
]

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

ROOT_URLCONF = 'qzmotors.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'qzmotors.wsgi.application'

# ==========================================
# BASE DE DATOS
# ==========================================

DATABASES = {
    'default': dj_database_url.config(
        # Si tienes DATABASE_URL en Railway la usará, sino usará sqlite local.
        default=f'sqlite:///{os.path.join(BASE_DIR, "db.sqlite3")}',
        conn_max_age=600
    )
}

# ==========================================
# ARCHIVOS ESTÁTICOS
# ==========================================

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ==========================================
# OTROS AJUSTES
# ==========================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'