import os
import dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================
# SEGURIDAD REAL (Sin llaves bajo el limpiapiés)
# ==========================================

# Intentamos sacar la llave de Railway
SECRET_KEY = os.environ.get('SECRET_KEY')

# Si NO hay llave y NO estamos en modo debug, lanzamos un error crítico
if not SECRET_KEY and not DEBUG:
    raise ValueError("ERROR CRÍTICO: La variable SECRET_KEY no está configurada en Railway.")

# Si no hay llave pero estamos en local (DEBUG=True), usamos una de juguete
if not SECRET_KEY:
    SECRET_KEY = 'django-insecure-dev-key-solo-para-entorno-local-2026'
# DEBUG: Solo será True si tú lo pones explícitamente en Railway. 
# En producción SIEMPRE debe ser False.
DEBUG = os.environ.get('DEBUG', 'False').lower() in ['true', '1', 't']

# ALLOWED_HOSTS: Agregamos el dominio de Railway al fallback por si acaso
_hosts = os.environ.get('ALLOWED_HOSTS', 'qzmotors.cl,www.qzmotors.cl,web-production-0711f.up.railway.app,localhost')
ALLOWED_HOSTS = [h.strip() for h in _hosts.split(',') if h.strip()]

# CSRF: Lo mismo aquí
_csrf = os.environ.get('CSRF_TRUSTED_ORIGINS', 'https://qzmotors.cl,https://www.qzmotors.cl,https://web-production-0711f.up.railway.app')
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf.split(',') if o.strip()]
# Configuración de Proxy (Vital para Railway + Cloudflare)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# ==========================================
# APLICACIONES Y MIDDLEWARE
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
# BASE DE DATOS Y ESTÁTICOS
# ==========================================

DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{os.path.join(BASE_DIR, "db.sqlite3")}',
        conn_max_age=600
    )
}

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'