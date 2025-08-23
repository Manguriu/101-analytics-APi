# from pathlib import Path
# import os
# import dj_database_url  # type: ignore

# BASE_DIR = Path(__file__).resolve().parent.parent

# # Load environment variables based on environment
# if os.getenv("DJANGO_ENV", "development") == "production":
#     env_file = BASE_DIR / ".env.production"
# else:
#     env_file = BASE_DIR / ".env.development"

# if os.path.exists(env_file):
#     from dotenv import load_dotenv

#     load_dotenv(env_file)
# elif os.path.exists(BASE_DIR / ".env"):  # Fallback to .env if exists
#     from dotenv import load_dotenv

#     load_dotenv(BASE_DIR / ".env")

# # Security
# SECRET_KEY = os.getenv("SECRET_KEY")
# if not SECRET_KEY:
#     # Provide a default for development but raise error in production
#     if os.getenv("DJANGO_ENV") == "production" or os.getenv("RENDER"):
#         raise ValueError("No SECRET_KEY set for Django application")
#     else:
#         SECRET_KEY = "django-insecure-development-key-only-change-in-production"

# DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

# # Parse ALLOWED_HOSTS from environment variable
# allowed_hosts = os.getenv("ALLOWED_HOSTS", "")
# if allowed_hosts:
#     ALLOWED_HOSTS = [host.strip() for host in allowed_hosts.split(",")]
# else:
#     ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# # Add Render's hostname automatically
# RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")
# if RENDER_EXTERNAL_HOSTNAME:
#     ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# # Add production domain if in production
# if os.getenv("DJANGO_ENV") == "production" or not DEBUG:
#     ALLOWED_HOSTS.extend(
#         ["one01-analytics-api.onrender.com", "farm101-analytics-p.vercel.app"]
#     )

# # Application definition
# INSTALLED_APPS = [
#     "django.contrib.admin",
#     "django.contrib.auth",
#     "django.contrib.contenttypes",
#     "django.contrib.sessions",
#     "django.contrib.messages",
#     "django.contrib.staticfiles",
#     "corsheaders",
#     "rest_framework",
#     "rest_framework.authtoken",
#     "drf_spectacular",
#     "poultry.core",
#     "poultry",
#     "poultry.user",
#     "poultry.flock",
# ]

# MIDDLEWARE = [
#     "django.middleware.security.SecurityMiddleware",
#     "whitenoise.middleware.WhiteNoiseMiddleware",
#     "corsheaders.middleware.CorsMiddleware",
#     "django.contrib.sessions.middleware.SessionMiddleware",
#     "django.middleware.common.CommonMiddleware",
#     "django.middleware.csrf.CsrfViewMiddleware",
#     "django.contrib.auth.middleware.AuthenticationMiddleware",
#     "django.contrib.messages.middleware.MessageMiddleware",
#     "django.middleware.clickjacking.XFrameOptionsMiddleware",
# ]

# ROOT_URLCONF = "poultry.urls"

# TEMPLATES = [
#     {
#         "BACKEND": "django.template.backends.django.DjangoTemplates",
#         "DIRS": [],
#         "APP_DIRS": True,
#         "OPTIONS": {
#             "context_processors": [
#                 "django.template.context_processors.debug",
#                 "django.template.context_processors.request",
#                 "django.contrib.auth.context_processors.auth",
#                 "django.contrib.messages.context_processors.messages",
#             ],
#         },
#     },
# ]

# WSGI_APPLICATION = "poultry.wsgi.application"

# # Database configuration
# if os.getenv("DATABASE_URL"):
#     # Use DATABASE_URL if available (for production)
#     DATABASES = {
#         "default": dj_database_url.config(
#             default=os.getenv("DATABASE_URL"),
#             conn_max_age=600,
#             conn_health_checks=True,
#         )
#     }
# else:
#     # Use individual DB settings for development
#     DATABASES = {
#         "default": {
#             "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.sqlite3"),
#             "NAME": os.getenv("DB_NAME", BASE_DIR / "db.sqlite3"),
#             "USER": os.getenv("DB_USER", ""),
#             "PASSWORD": os.getenv("DB_PASS", ""),
#             "HOST": os.getenv("DB_HOST", ""),
#             "PORT": os.getenv("DB_PORT", ""),
#         }
#     }

# # Password validation
# AUTH_PASSWORD_VALIDATORS = [
#     {
#         "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
#     },
#     {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
#     {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
#     {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
# ]

# # Internationalization
# LANGUAGE_CODE = "en-us"
# TIME_ZONE = "UTC"
# USE_I18N = True
# USE_TZ = True

# # Static files
# STATIC_URL = "/static/"
# STATIC_ROOT = BASE_DIR / "staticfiles"

# # WhiteNoise configuration
# if not DEBUG:
#     STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# # Media files
# MEDIA_URL = "/media/"
# MEDIA_ROOT = BASE_DIR / "media"

# # Default primary key field type
# DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# # Custom user model
# AUTH_USER_MODEL = "core.User"

# # DRF settings
# REST_FRAMEWORK = {
#     "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
#     "DEFAULT_AUTHENTICATION_CLESSES": [
#         "rest_framework.authentication.TokenAuthentication",
#     ],
#     "DEFAULT_PERMISSION_CLASSES": [
#         "rest_framework.permissions.IsAuthenticated",
#     ],
# }

# # DRF Spectacular settings
# SPECTACULAR_SETTINGS = {
#     "TITLE": "Poultry Analytics API",
#     "DESCRIPTION": "API for poultry farm analytics and management",
#     "VERSION": "1.0.0",
#     "SERVE_INCLUDE_SCHEMA": False,
#     "SWAGGER_UI_SETTINGS": {
#         "deepLinking": True,
#         "persistAuthorization": True,
#     },
#     "COMPONENT_SPLIT_REQUEST": True,
# }

# # CORS & CSRF
# CORS_ALLOW_ALL_ORIGINS = DEBUG
# CORS_ALLOW_CREDENTIALS = True

# if DEBUG:
#     CSRF_TRUSTED_ORIGINS = [
#         "http://localhost:3000",
#         "http://127.0.0.1:3000",
#     ]
# else:
#     CORS_ALLOWED_ORIGINS = [
#         "https://farm101-analytics-p.vercel.app",
#     ]
#     CSRF_TRUSTED_ORIGINS = [
#         "https://farm101-analytics-p.vercel.app",
#         "http://localhost:3000",
#         "http://127.0.0.1:3000",
#         f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME', '')}",
#     ]

# # CSRF cookie settings
# CSRF_COOKIE_HTTPONLY = False
# CSRF_COOKIE_SAMESITE = "Lax"

# # Security settings - use environment variables or defaults
# SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", str(not DEBUG)).lower() == "true"
# SESSION_COOKIE_SECURE = (
#     os.getenv("SESSION_COOKIE_SECURE", str(not DEBUG)).lower() == "true"
# )
# CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", str(not DEBUG)).lower() == "true"

# # Production security settings
# if not DEBUG:
#     SECURE_HSTS_SECONDS = 3600
#     SECURE_HSTS_INCLUDE_SUBDOMAINS = True
#     SECURE_HSTS_PRELOAD = True
#     SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


from pathlib import Path
import os
import dj_database_url  # type: ignore

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables based on environment
if os.getenv("DJANGO_ENV", "development") == "production":
    env_file = BASE_DIR / ".env.production"
else:
    env_file = BASE_DIR / ".env.development"

if os.path.exists(env_file):
    from dotenv import load_dotenv

    load_dotenv(env_file)
elif os.path.exists(BASE_DIR / ".env"):
    from dotenv import load_dotenv

    load_dotenv(BASE_DIR / ".env")

# Security
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    # Provide a default for development but raise error in production
    if os.getenv("DJANGO_ENV") == "production" or os.getenv("RENDER"):
        raise ValueError("No SECRET_KEY set for Django application")
    else:
        SECRET_KEY = "django-insecure-development-key-only-change-in-production"

DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

# Parse ALLOWED_HOSTS from environment variable
allowed_hosts = os.getenv("ALLOWED_HOSTS", "")
if allowed_hosts:
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts.split(",")]
else:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Add Render's hostname automatically
RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Add production domain if in production
if os.getenv("DJANGO_ENV") == "production" or not DEBUG:
    ALLOWED_HOSTS.extend(
        ["one01-analytics-api.onrender.com", "farm101-analytics-p.vercel.app"]
    )

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "drf_spectacular",
    "poultry.core",
    "poultry",
    "poultry.user",
    "poultry.flock",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "poultry.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "poultry.wsgi.application"

# Database configuration
if os.getenv("DATABASE_URL"):
    # Use DATABASE_URL if available (for production)
    DATABASES = {
        "default": dj_database_url.config(
            default=os.getenv("DATABASE_URL"),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Use individual DB settings for development
    DATABASES = {
        "default": {
            "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.sqlite3"),
            "NAME": os.getenv("DB_NAME", BASE_DIR / "db.sqlite3"),
            "USER": os.getenv("DB_USER", ""),
            "PASSWORD": os.getenv("DB_PASS", ""),
            "HOST": os.getenv("DB_HOST", ""),
            "PORT": os.getenv("DB_PORT", ""),
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise configuration
if not DEBUG:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom user model
AUTH_USER_MODEL = "core.User"

# DRF settings
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# DRF Spectacular settings
SPECTACULAR_SETTINGS = {
    "TITLE": "Poultry Analytics API",
    "DESCRIPTION": "API for poultry farm analytics and management",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
    },
    "COMPONENT_SPLIT_REQUEST": True,
}

# CORS & CSRF Configuration
CORS_ALLOW_CREDENTIALS = True

# Get CORS origins from environment variable or use defaults
cors_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
if cors_origins:
    CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins.split(",")]
else:
    # Default origins for both development and production
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://farm101-analytics-p.vercel.app",
    ]

# For development, allow all origins for easier testing
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False

# CSRF trusted origins should match CORS origins
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS.copy()

# Add Render hostname to CSRF if not already included
if (
    RENDER_EXTERNAL_HOSTNAME
    and f"https://{RENDER_EXTERNAL_HOSTNAME}" not in CSRF_TRUSTED_ORIGINS
):
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")

# Additional CORS settings for better compatibility
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# CSRF cookie settings
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = "Lax"

# Security settings - use environment variables or defaults
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", str(not DEBUG)).lower() == "true"
SESSION_COOKIE_SECURE = (
    os.getenv("SESSION_COOKIE_SECURE", str(not DEBUG)).lower() == "true"
)
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", str(not DEBUG)).lower() == "true"

# Production security settings
if not DEBUG:
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
