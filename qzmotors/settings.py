import os
import dj_database_url
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================
# 1. CONFIGURACIÓN DE ENTORNO (ORDEN CORREGIDO)
# ==========================================

# Definimos DEBUG primero para que la lógica de SECRET_KEY pueda usarlo
DEBUG = os.environ.get('DEBUG', 'False').lower() in ['true', '1', 't']

# Intentamos sacar la llave de Railway
SECRET_KEY = os.environ.get('SECRET_KEY')

# Fail-safe para SECRET_KEY
if not SECRET_KEY and not DEBUG:
    raise ValueError("ERROR CRÍTICO: La variable SECRET_KEY no está configurada en Railway.")

if not SECRET_KEY:
    SECRET_KEY = 'django-insecure-dev-key-solo-para-entorno-local-2026'

# ==========================================
# 2. SEGURIDAD Y RED (ALLOWED HOSTS & CSRF)
# ==========================================

# Hosts permitidos con fallbacks para evitar el Error 400
_hosts = os.environ.get('ALLOWED_HOSTS', 'qzmotors.cl,www.qzmotors.cl,web-production-0711f.up.railway.app,localhost,127.0.0.1')
ALLOWED_HOSTS = [h.strip() for h in _hosts.split(',') if h.strip()]

# Orígenes confiables para CSRF (Necesario para formularios tras Cloudflare)
_csrf = os.environ.get('CSRF_TRUSTED_ORIGINS', 'https://qzmotors.cl,https://www.qzmotors.cl,https://web-production-0711f.up.railway.app')
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf.split(',') if o.strip()]

# Configuración de Proxy (Vital para Railway + Cloudflare)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# ==========================================
# 3. DEFINICIÓN DE APLICACIONES Y MIDDLEWARE
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
    'whitenoise.middleware.WhiteNoiseMiddleware', # Debe estar aquí para los estáticos
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
# 4. BASE DE DATOS Y ARCHIVOS ESTÁTICOS
# ==========================================

DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{os.path.join(BASE_DIR, "db.sqlite3")}',
        conn_max_age=600
    )
}

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configuración de WhiteNoise optimizada para producción
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# ==========================================
# 5. INTERNACIONALIZACIÓN Y OTROS
# ==========================================

LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==========================================
# 6. CONFIGURACIÓN DE CORREO (SMTP)
# ==========================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'zuninoweb.qz@gmail.com'
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD') # Configurado en Railway
DEFAULT_FROM_EMAIL = 'QZ Motors <contacto@qzmotors.cl>'