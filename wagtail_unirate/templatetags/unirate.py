"""Django template tags exposed under ``{% load unirate %}``.

Every tag is forgiving by design: if the UniRate API is unreachable the
fall-back value (``""`` for string-returning tags, ``None`` for value
tags) is returned and the failure is logged. Page renders never break
because a third-party API blipped.
"""

from __future__ import annotations

import logging

from django import template
from django.conf import settings

from wagtail_unirate.client import SETTING_DEFAULT_BASE, get_accessor

register = template.Library()
logger = logging.getLogger(__name__)


_CRYPTO_DEFAULT_DECIMALS = {"BTC": 8, "ETH": 6, "XBT": 8}


def _default_base() -> str:
    return getattr(settings, SETTING_DEFAULT_BASE, "USD")


@register.simple_tag
def unirate_rate(from_currency: str, to_currency: str) -> float | None:
    """Latest rate for ``{% unirate_rate "USD" "EUR" %}``.

    Returns ``None`` and logs a warning if the lookup fails.
    """
    try:
        return get_accessor().get_rate(from_currency, to_currency)
    except Exception:
        logger.warning(
            "unirate_rate(%s, %s) lookup failed",
            from_currency,
            to_currency,
            exc_info=True,
        )
        return None


@register.simple_tag
def unirate_convert(
    amount: float,
    from_currency: str,
    to_currency: str,
) -> float | None:
    """Convert ``amount`` between currencies.

    ``{% unirate_convert 100 "USD" "EUR" %}`` → ``92.5``.
    """
    try:
        return get_accessor().convert(from_currency, to_currency, float(amount))
    except Exception:
        logger.warning(
            "unirate_convert(%s, %s, %s) failed",
            amount,
            from_currency,
            to_currency,
            exc_info=True,
        )
        return None


@register.simple_tag
def unirate_to(amount: float, target: str, base: str | None = None) -> float | None:
    """Convert ``amount`` (in the configured default base) into ``target``.

    The default base is ``settings.UNIRATE_DEFAULT_BASE_CURRENCY`` (``"USD"``
    if unset). Pass ``base`` to override per-call.
    """
    actual_base = base or _default_base()
    try:
        return get_accessor().convert(actual_base, target, float(amount))
    except Exception:
        logger.warning(
            "unirate_to(%s, %s, base=%s) failed",
            amount,
            target,
            actual_base,
            exc_info=True,
        )
        return None


@register.simple_tag
def unirate_format(amount: float, currency: str, decimals: int = 2) -> str:
    """Format ``amount`` as ``"123.45 USD"`` without pulling in Babel.

    Crypto codes (``BTC``/``ETH``/``XBT``) default to 8 decimals.
    """
    code = currency.upper()
    if decimals == 2 and code in _CRYPTO_DEFAULT_DECIMALS:
        decimals = _CRYPTO_DEFAULT_DECIMALS[code]
    return f"{float(amount):,.{decimals}f} {code}"


@register.simple_tag
def unirate_currencies() -> list[str]:
    """All supported currency codes; empty list on lookup failure."""
    try:
        return get_accessor().get_supported_currencies()
    except Exception:
        logger.warning("unirate_currencies lookup failed", exc_info=True)
        return []


@register.simple_tag
def unirate_historical_rate(
    from_currency: str, to_currency: str, date: str
) -> float | None:
    """Historical rate on ``date`` (``YYYY-MM-DD``). Pro-gated.

    Returns ``None`` if the call fails (e.g. free-tier API key on a
    Pro-gated endpoint).
    """
    try:
        return get_accessor().get_historical_rate(from_currency, to_currency, date)
    except Exception:
        logger.warning(
            "unirate_historical_rate(%s, %s, %s) failed",
            from_currency,
            to_currency,
            date,
            exc_info=True,
        )
        return None


__all__ = [
    "register",
    "unirate_convert",
    "unirate_currencies",
    "unirate_format",
    "unirate_historical_rate",
    "unirate_rate",
    "unirate_to",
]
