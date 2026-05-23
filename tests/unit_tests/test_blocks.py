"""StreamField block tests — exercise ``render()`` directly."""

from __future__ import annotations

import responses

from wagtail_unirate.blocks import (
    CurrencyConversionBlock,
    CurrencyRateBlock,
    MultiCurrencyPriceBlock,
)

BASE = "https://api.unirateapi.com"


def test_currency_rate_block_renders_html(
    mocked_responses: responses.RequestsMock,
) -> None:
    mocked_responses.get(f"{BASE}/api/rates", json={"rate": "0.92"})
    block = CurrencyRateBlock()
    rendered = block.render({"base": "USD", "quote": "EUR", "decimals": 4, "label": ""})
    assert '<span class="wagtail-unirate-rate">' in rendered
    assert "1 USD = 0.9200 EUR" in rendered


def test_currency_rate_block_label_prepended(
    mocked_responses: responses.RequestsMock,
) -> None:
    mocked_responses.get(f"{BASE}/api/rates", json={"rate": "0.92"})
    block = CurrencyRateBlock()
    rendered = block.render(
        {
            "base": "USD",
            "quote": "EUR",
            "decimals": 2,
            "label": "Today's rate",
        }
    )
    assert "Today's rate: 1 USD = 0.92 EUR" in rendered


def test_currency_rate_block_silent_on_failure(
    mocked_responses: responses.RequestsMock,
) -> None:
    mocked_responses.get(f"{BASE}/api/rates", status=500)
    block = CurrencyRateBlock()
    rendered = block.render({"base": "USD", "quote": "EUR", "decimals": 2, "label": ""})
    assert rendered == ""


def test_currency_conversion_block_renders(
    mocked_responses: responses.RequestsMock,
) -> None:
    mocked_responses.get(f"{BASE}/api/rates", json={"rate": "0.92"})
    block = CurrencyConversionBlock()
    rendered = block.render(
        {"amount": 100, "base": "USD", "quote": "EUR", "decimals": 2}
    )
    assert "100.00 USD = 92.00 EUR" in rendered


def test_currency_conversion_block_same_currency_renders_unchanged(
    mocked_responses: responses.RequestsMock,
) -> None:
    block = CurrencyConversionBlock()
    rendered = block.render(
        {"amount": 50, "base": "USD", "quote": "USD", "decimals": 2}
    )
    assert "50.00 USD = 50.00 USD" in rendered
    assert len(mocked_responses.calls) == 0


def test_currency_conversion_block_silent_on_failure(
    mocked_responses: responses.RequestsMock,
) -> None:
    mocked_responses.get(f"{BASE}/api/rates", status=500)
    block = CurrencyConversionBlock()
    rendered = block.render(
        {"amount": 100, "base": "USD", "quote": "EUR", "decimals": 2}
    )
    assert rendered == ""


def test_multi_currency_price_block_renders_list(
    mocked_responses: responses.RequestsMock,
) -> None:
    mocked_responses.get(f"{BASE}/api/rates", json={"rate": "0.92"})  # USD->EUR
    mocked_responses.get(f"{BASE}/api/rates", json={"rate": "0.79"})  # USD->GBP
    block = MultiCurrencyPriceBlock()
    rendered = block.render(
        {
            "amount": 9.99,
            "base": "USD",
            "targets": "EUR, GBP",
            "decimals": 2,
        }
    )
    assert '<ul class="wagtail-unirate-prices">' in rendered
    assert "<li>9.99 USD</li>" in rendered
    assert "<li>9.19 EUR</li>" in rendered
    assert "<li>7.89 GBP</li>" in rendered


def test_multi_currency_price_block_skips_failed_targets(
    mocked_responses: responses.RequestsMock,
) -> None:
    mocked_responses.get(f"{BASE}/api/rates", json={"rate": "0.92"})  # USD->EUR OK
    mocked_responses.get(f"{BASE}/api/rates", status=500)  # USD->GBP fails
    block = MultiCurrencyPriceBlock()
    rendered = block.render(
        {
            "amount": 9.99,
            "base": "USD",
            "targets": "EUR,GBP",
            "decimals": 2,
        }
    )
    assert "9.19 EUR" in rendered
    assert "GBP" not in rendered.split("</li>")[1]


def test_multi_currency_price_block_skips_self_target(
    mocked_responses: responses.RequestsMock,
) -> None:
    mocked_responses.get(f"{BASE}/api/rates", json={"rate": "0.92"})
    block = MultiCurrencyPriceBlock()
    rendered = block.render(
        {
            "amount": 100,
            "base": "USD",
            "targets": "USD, EUR",
            "decimals": 2,
        }
    )
    # Base appears once (the leading <li>), EUR appears once.
    assert rendered.count("USD") == 1
    assert rendered.count("EUR") == 1
