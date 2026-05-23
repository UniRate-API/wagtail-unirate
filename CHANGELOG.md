# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-05-23

### Added

- `UniRateAccessor` — Django-settings-driven wrapper around the official
  `unirate-api` client, with optional Django-cache integration.
- Three StreamField blocks:
  - `CurrencyRateBlock` — renders the current rate for a single pair.
  - `CurrencyConversionBlock` — renders a single amount converted to a
    target currency.
  - `MultiCurrencyPriceBlock` — renders a single price in several target
    currencies.
- Django template tags under `{% load unirate %}`:
  `unirate_rate`, `unirate_convert`, `unirate_to`, `unirate_format`,
  `unirate_currencies`, `unirate_historical_rate`.
- Wagtail 5.x and 6.x support; Django 4.2, 5.0, 5.1, and 5.2.
- Python 3.10–3.13.
