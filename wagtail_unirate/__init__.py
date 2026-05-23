"""Wagtail integration for the UniRate currency-exchange API.

The package exposes:

* :class:`wagtail_unirate.client.UniRateAccessor` — a cached wrapper around
  the official ``unirate-api`` Python client, wired through Django settings.
* StreamField blocks (:mod:`wagtail_unirate.blocks`) for inserting live
  currency rates, conversions, and multi-currency price tables into
  Wagtail page bodies.
* Django template tags (``{% load unirate %}``) that work in any Wagtail
  or plain-Django template.
"""

from __future__ import annotations

from wagtail_unirate.client import UniRateAccessor, get_accessor

default_app_config = "wagtail_unirate.apps.WagtailUniRateConfig"

__all__ = [
    "UniRateAccessor",
    "get_accessor",
]
