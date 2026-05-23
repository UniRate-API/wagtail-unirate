"""Tests for the :class:`UniRateAccessor` wrapper."""

from __future__ import annotations

import pytest
import responses

from wagtail_unirate.client import UniRateAccessor, get_accessor

BASE = "https://api.unirateapi.com"


def test_get_rate_round_trip(mocked_responses: responses.RequestsMock) -> None:
    mocked_responses.get(f"{BASE}/api/rates", json={"rate": "0.92"})
    assert get_accessor().get_rate("USD", "EUR") == pytest.approx(0.92)


def test_get_rate_same_currency_skips_http(
    mocked_responses: responses.RequestsMock,
) -> None:
    assert get_accessor().get_rate("USD", "usd") == 1.0
    assert len(mocked_responses.calls) == 0


def test_convert_round_trip(mocked_responses: responses.RequestsMock) -> None:
    mocked_responses.get(f"{BASE}/api/rates", json={"rate": "0.92"})
    assert get_accessor().convert("USD", "EUR", 100) == pytest.approx(92.0)


def test_convert_same_currency_returns_amount(
    mocked_responses: responses.RequestsMock,
) -> None:
    assert get_accessor().convert("GBP", "GBP", 50) == 50.0
    assert len(mocked_responses.calls) == 0


def test_get_supported_currencies(
    mocked_responses: responses.RequestsMock,
) -> None:
    mocked_responses.get(
        f"{BASE}/api/currencies", json={"currencies": ["USD", "EUR", "GBP"]}
    )
    assert get_accessor().get_supported_currencies() == ["USD", "EUR", "GBP"]


def test_missing_api_key_raises(settings) -> None:  # type: ignore[no-untyped-def]
    settings.UNIRATE_API_KEY = ""
    accessor = UniRateAccessor()
    with pytest.raises(RuntimeError, match="UniRate API key not configured"):
        _ = accessor.client


def test_cache_respected_when_timeout_set(
    mocked_responses: responses.RequestsMock,
    override_settings_factory,  # type: ignore[no-untyped-def]
) -> None:
    override_settings_factory(UNIRATE_CACHE_TIMEOUT=60)
    mocked_responses.get(f"{BASE}/api/rates", json={"rate": "0.92"})
    a = UniRateAccessor()
    assert a.get_rate("USD", "EUR") == pytest.approx(0.92)
    # Second call hits the cache; only one HTTP call should have been made.
    assert a.get_rate("USD", "EUR") == pytest.approx(0.92)
    assert len(mocked_responses.calls) == 1


def test_cache_skipped_when_timeout_unset(
    mocked_responses: responses.RequestsMock,
) -> None:
    mocked_responses.get(f"{BASE}/api/rates", json={"rate": "0.92"})
    mocked_responses.get(f"{BASE}/api/rates", json={"rate": "0.93"})
    a = UniRateAccessor()
    assert a.get_rate("USD", "EUR") == pytest.approx(0.92)
    assert a.get_rate("USD", "EUR") == pytest.approx(0.93)
    assert len(mocked_responses.calls) == 2


def test_cache_alias_setting_routes_to_named_cache(
    mocked_responses: responses.RequestsMock,
    override_settings_factory,  # type: ignore[no-untyped-def]
) -> None:
    override_settings_factory(
        UNIRATE_CACHE_TIMEOUT=60,
        UNIRATE_CACHE_ALIAS="default",
    )
    mocked_responses.get(f"{BASE}/api/rates", json={"rate": "1.10"})
    assert get_accessor().get_rate("EUR", "USD") == pytest.approx(1.10)
    assert get_accessor().get_rate("EUR", "USD") == pytest.approx(1.10)
    assert len(mocked_responses.calls) == 1


def test_get_accessor_is_singleton() -> None:
    assert get_accessor() is get_accessor()


def test_base_url_override_takes_effect(
    mocked_responses: responses.RequestsMock,
    override_settings_factory,  # type: ignore[no-untyped-def]
) -> None:
    override_settings_factory(UNIRATE_BASE_URL="https://api.example.test")
    mocked_responses.get("https://api.example.test/api/rates", json={"rate": "0.81"})
    assert get_accessor().get_rate("USD", "EUR") == pytest.approx(0.81)
