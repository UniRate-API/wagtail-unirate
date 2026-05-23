"""Minimal Django settings for the wagtail-unirate test suite.

We keep this as small as possible: only the apps required for
``wagtail.blocks``, the test-tag template engine, and the in-memory cache.
A real consumer's project settings will be much richer; the tests just
need a working Django + Wagtail app registry.
"""

from __future__ import annotations

SECRET_KEY = "test-secret-key"

DEBUG = True

USE_TZ = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "wagtail.images",
    "wagtail.documents",
    "wagtail.snippets",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.admin",
    "wagtail",
    "taggit",
    "wagtail_unirate",
]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "wagtail-unirate-tests",
    },
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    },
]

WAGTAIL_SITE_NAME = "wagtail-unirate-tests"

UNIRATE_API_KEY = "test-key"
