"""Wagtail StreamField blocks for inserting currency widgets into pages.

Three blocks are provided:

* :class:`CurrencyRateBlock` — renders today's rate for a chosen base/quote
  pair.
* :class:`CurrencyConversionBlock` — renders a single amount converted to a
  target currency.
* :class:`MultiCurrencyPriceBlock` — renders a single price in several
  target currencies (useful for international product pages).

Each block fetches rates through :class:`wagtail_unirate.client.UniRateAccessor`
so caching (when configured) and error-suppression work uniformly.
"""

from __future__ import annotations

import logging
from typing import Any

from django.utils.safestring import mark_safe
from wagtail import blocks

from wagtail_unirate.client import get_accessor

logger = logging.getLogger(__name__)

_CRYPTO_DEFAULT_DECIMALS = {"BTC": 8, "ETH": 6, "XBT": 8}


def _format(amount: float, code: str, decimals: int) -> str:
    code = code.upper()
    if decimals == 2 and code in _CRYPTO_DEFAULT_DECIMALS:
        decimals = _CRYPTO_DEFAULT_DECIMALS[code]
    return f"{amount:,.{decimals}f} {code}"


class _DecimalsBlockMixin:
    """Adds a shared ``decimals`` choice field to the conversion blocks."""

    @staticmethod
    def _decimals_block() -> blocks.IntegerBlock:
        return blocks.IntegerBlock(
            min_value=0,
            max_value=8,
            default=2,
            help_text="Number of decimals to display.",
        )


class CurrencyRateBlock(blocks.StructBlock):
    """Render the current exchange rate for a single pair.

    Editors enter ISO currency codes (``USD``, ``EUR``). The rendered HTML
    is a single ``<span>`` with the rate; on lookup failure the block
    renders an empty fragment so the surrounding page still loads.
    """

    base = blocks.CharBlock(max_length=8, help_text="Base currency code, e.g. USD.")
    quote = blocks.CharBlock(max_length=8, help_text="Quote currency code, e.g. EUR.")
    decimals = _DecimalsBlockMixin._decimals_block()
    label = blocks.CharBlock(
        required=False,
        max_length=64,
        help_text="Optional label rendered before the rate (e.g. 'Today's rate').",
    )

    class Meta:
        icon = "site"
        label = "Currency rate"
        template = None  # rendered inline via render()

    def render(
        self,
        value: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> str:
        base = value["base"].upper()
        quote = value["quote"].upper()
        decimals = int(value.get("decimals", 2) or 2)
        label = value.get("label") or ""
        try:
            rate = get_accessor().get_rate(base, quote)
        except Exception:
            logger.warning(
                "CurrencyRateBlock(%s/%s) lookup failed",
                base,
                quote,
                exc_info=True,
            )
            return ""
        body = f"1 {base} = {rate:,.{decimals}f} {quote}"
        if label:
            body = f"{label}: {body}"
        return mark_safe(f'<span class="wagtail-unirate-rate">{body}</span>')


class CurrencyConversionBlock(blocks.StructBlock):
    """Render ``amount`` of ``base`` converted into ``quote``.

    Useful for callouts like "Subscriptions at $9.99 USD (~€9.20 EUR)".
    """

    amount = blocks.FloatBlock(
        help_text="Amount in the base currency.",
    )
    base = blocks.CharBlock(max_length=8, help_text="Base currency code.")
    quote = blocks.CharBlock(max_length=8, help_text="Quote currency code.")
    decimals = _DecimalsBlockMixin._decimals_block()

    class Meta:
        icon = "calculator"
        label = "Currency conversion"
        template = None

    def render(
        self,
        value: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> str:
        amount = float(value["amount"])
        base = value["base"].upper()
        quote = value["quote"].upper()
        decimals = int(value.get("decimals", 2) or 2)
        try:
            converted = get_accessor().convert(base, quote, amount)
        except Exception:
            logger.warning(
                "CurrencyConversionBlock(%s %s->%s) lookup failed",
                amount,
                base,
                quote,
                exc_info=True,
            )
            return ""
        return mark_safe(
            '<span class="wagtail-unirate-conversion">'
            f"{_format(amount, base, decimals)} = "
            f"{_format(converted, quote, decimals)}"
            "</span>"
        )


class MultiCurrencyPriceBlock(blocks.StructBlock):
    """Render a single price in several target currencies.

    The editor enters ``amount`` + ``base`` + a comma-separated list of
    ``targets``. The block renders an unordered list of converted prices,
    skipping any target whose lookup fails (so a single bad pair never
    hides the rest).
    """

    amount = blocks.FloatBlock(help_text="Price in the base currency.")
    base = blocks.CharBlock(max_length=8, help_text="Base currency code.")
    targets = blocks.CharBlock(
        help_text="Comma-separated target currency codes, e.g. 'EUR,GBP,JPY'.",
    )
    decimals = _DecimalsBlockMixin._decimals_block()

    class Meta:
        icon = "table"
        label = "Multi-currency price"
        template = None

    def render(
        self,
        value: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> str:
        amount = float(value["amount"])
        base = value["base"].upper()
        targets = [t.strip().upper() for t in value["targets"].split(",") if t.strip()]
        decimals = int(value.get("decimals", 2) or 2)
        accessor = get_accessor()
        items: list[str] = []
        items.append(f"<li>{_format(amount, base, decimals)}</li>")
        for target in targets:
            if target == base:
                continue
            try:
                converted = accessor.convert(base, target, amount)
            except Exception:
                logger.warning(
                    "MultiCurrencyPriceBlock(%s->%s) lookup failed",
                    base,
                    target,
                    exc_info=True,
                )
                continue
            items.append(f"<li>{_format(converted, target, decimals)}</li>")
        body = "".join(items)
        return mark_safe(f'<ul class="wagtail-unirate-prices">{body}</ul>')


__all__ = [
    "CurrencyConversionBlock",
    "CurrencyRateBlock",
    "MultiCurrencyPriceBlock",
]
