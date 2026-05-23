"""Template-tag tests — render through the Django template engine."""

from __future__ import annotations

import responses
from django.template import Context, Template

BASE = "https://api.unirateapi.com"


def _render(source: str, **ctx: object) -> str:
    return Template("{% load unirate %}" + source).render(Context(ctx))


def test_unirate_rate_renders_float(
    mocked_responses: responses.RequestsMock,
) -> None:
    mocked_responses.get(f"{BASE}/api/rates", json={"rate": "0.92"})
    rendered = _render('{% unirate_rate "USD" "EUR" %}')
    assert rendered == "0.92"


def test_unirate_rate_handles_failure_silently(
    mocked_responses: responses.RequestsMock,
) -> None:
    mocked_responses.get(f"{BASE}/api/rates", status=500)
    rendered = _render('{% unirate_rate "USD" "EUR" %}')
    assert rendered == "None"


def test_unirate_convert_renders_float(
    mocked_responses: responses.RequestsMock,
) -> None:
    mocked_responses.get(f"{BASE}/api/rates", json={"rate": "0.92"})
    rendered = _render('{% unirate_convert 100 "USD" "EUR" %}')
    assert float(rendered) == 92.0


def test_unirate_to_uses_default_base(
    mocked_responses: responses.RequestsMock,
) -> None:
    mocked_responses.get(f"{BASE}/api/rates", json={"rate": "0.78"})
    rendered = _render('{% unirate_to 50 "GBP" %}')
    assert float(rendered) == 39.0


def test_unirate_to_explicit_base_overrides_default(
    mocked_responses: responses.RequestsMock,
) -> None:
    mocked_responses.get(f"{BASE}/api/rates", json={"rate": "1.30"})
    rendered = _render('{% unirate_to 50 "USD" "GBP" %}')
    assert float(rendered) == 65.0


def test_unirate_to_respects_default_base_setting(
    mocked_responses: responses.RequestsMock,
    override_settings_factory,  # type: ignore[no-untyped-def]
) -> None:
    override_settings_factory(UNIRATE_DEFAULT_BASE_CURRENCY="EUR")
    mocked_responses.get(f"{BASE}/api/rates", json={"rate": "0.85"})
    rendered = _render('{% unirate_to 100 "GBP" %}')
    assert float(rendered) == 85.0
    sent_url = mocked_responses.calls[0].request.url or ""
    assert "from=EUR" in sent_url


def test_unirate_format_basic() -> None:
    rendered = _render('{% unirate_format 1234.5 "EUR" %}')
    assert rendered == "1,234.50 EUR"


def test_unirate_format_crypto_default_decimals() -> None:
    rendered = _render('{% unirate_format 0.0123456789 "BTC" %}')
    assert rendered == "0.01234568 BTC"


def test_unirate_format_explicit_decimals() -> None:
    rendered = _render('{% unirate_format 1 "USD" 4 %}')
    assert rendered == "1.0000 USD"


def test_unirate_currencies_renders_list(
    mocked_responses: responses.RequestsMock,
) -> None:
    mocked_responses.get(
        f"{BASE}/api/currencies", json={"currencies": ["USD", "EUR", "GBP"]}
    )
    rendered = _render("{% unirate_currencies as codes %}{{ codes|length }}")
    assert rendered == "3"


def test_unirate_currencies_returns_empty_on_failure(
    mocked_responses: responses.RequestsMock,
) -> None:
    mocked_responses.get(f"{BASE}/api/currencies", status=500)
    rendered = _render("{% unirate_currencies as codes %}{{ codes|length }}")
    assert rendered == "0"


def test_unirate_historical_rate_renders(
    mocked_responses: responses.RequestsMock,
) -> None:
    mocked_responses.get(f"{BASE}/api/historical/rates", json={"rate": "0.81"})
    rendered = _render('{% unirate_historical_rate "USD" "EUR" "2025-01-15" %}')
    assert rendered == "0.81"


def test_unirate_historical_rate_403_returns_none(
    mocked_responses: responses.RequestsMock,
) -> None:
    mocked_responses.get(
        f"{BASE}/api/historical/rates",
        status=403,
        json={"error": "Pro plan required"},
    )
    rendered = _render('{% unirate_historical_rate "USD" "EUR" "2025-01-15" %}')
    assert rendered == "None"


def test_assignment_form(
    mocked_responses: responses.RequestsMock,
) -> None:
    mocked_responses.get(f"{BASE}/api/rates", json={"rate": "0.92"})
    rendered = _render('{% unirate_rate "USD" "EUR" as r %}{{ r|floatformat:2 }}')
    assert rendered == "0.92"
