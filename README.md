# wagtail-unirate

Wagtail + Django integration for the [UniRate](https://unirateapi.com)
currency-exchange API. Drop currency rates, conversions, and multi-currency
price tables straight into Wagtail page bodies; use template tags anywhere
in Django templates.

* StreamField blocks: `CurrencyRateBlock`, `CurrencyConversionBlock`,
  `MultiCurrencyPriceBlock`.
* Template tags under `{% load unirate %}`: `unirate_rate`,
  `unirate_convert`, `unirate_to`, `unirate_format`, `unirate_currencies`,
  `unirate_historical_rate`.
* Cached lookups via Django's standard cache framework (opt-in via
  `UNIRATE_CACHE_TIMEOUT`).
* Wagtail 5.x / 6.x · Django 4.2 / 5.0 / 5.1 / 5.2 · Python 3.10–3.13.
* No new HTTP code: every network call goes through the official
  [`unirate-api`](https://pypi.org/project/unirate-api/) Python client.

## Install

```bash
pip install wagtail-unirate
```

Add to `INSTALLED_APPS` (after the `wagtail.*` apps):

```python
INSTALLED_APPS = [
    # …
    "wagtail",
    "wagtail_unirate",
]
```

Set your API key in `settings.py` or as an environment variable:

```python
UNIRATE_API_KEY = os.environ["UNIRATE_API_KEY"]
```

Get a free key at <https://unirateapi.com>.

## Settings

| Setting | Default | Description |
|---|---|---|
| `UNIRATE_API_KEY` | — | API key. Falls back to the `UNIRATE_API_KEY` env var. |
| `UNIRATE_BASE_URL` | `https://api.unirateapi.com` | Override the API base (rare; testing or a self-hosted proxy). |
| `UNIRATE_TIMEOUT` | `30` | Per-request timeout in seconds. |
| `UNIRATE_CACHE_TIMEOUT` | `0` (off) | If positive, latest-rate / convert / supported-currency lookups are cached for this many seconds via Django's cache framework. |
| `UNIRATE_CACHE_ALIAS` | `default` | The `CACHES` alias used when caching is enabled. |
| `UNIRATE_DEFAULT_BASE_CURRENCY` | `USD` | Default base for the `unirate_to` template tag. |

## Template tags

```django
{% load unirate %}

Today's USD/EUR rate: {% unirate_rate "USD" "EUR" %}

100 USD ≈ {% unirate_convert 100 "USD" "EUR" %} EUR

A price of 9.99 in the configured base ≈
{% unirate_to 9.99 "JPY" %} JPY

{% unirate_format 1234.56 "EUR" %}   {# → "1,234.56 EUR" #}

{% unirate_currencies as codes %}
Supported codes: {{ codes|join:", " }}

Historical (Pro plan):
{% unirate_historical_rate "USD" "EUR" "2025-01-15" %}
```

Every value-returning tag falls back silently to `None` (or `[]` for
`unirate_currencies`) on API errors so a third-party blip cannot break a
page render.

## StreamField blocks

```python
from wagtail import blocks
from wagtail.fields import StreamField
from wagtail_unirate.blocks import (
    CurrencyConversionBlock,
    CurrencyRateBlock,
    MultiCurrencyPriceBlock,
)


class HomePage(Page):
    body = StreamField(
        [
            ("paragraph", blocks.RichTextBlock()),
            ("currency_rate", CurrencyRateBlock()),
            ("currency_conversion", CurrencyConversionBlock()),
            ("multi_currency_price", MultiCurrencyPriceBlock()),
        ],
        use_json_field=True,
    )
```

Editors then get three new blocks in the Wagtail page editor. Each block
renders inline HTML and silently swallows API failures (it falls back to
an empty fragment) so a transient blip never breaks the page.

## Caching tip

Currency rates change slowly. A 5- to 15-minute cache window is usually
plenty and removes virtually all per-request UniRate calls on a busy site:

```python
UNIRATE_CACHE_TIMEOUT = 600  # 10 minutes
```

<!-- unirate-ecosystem-footer:start -->
## UniRate ecosystem

UniRate ships official integrations for 40+ ecosystems, all maintained under the
[UniRate-API](https://github.com/UniRate-API) org.

**Core clients (9 languages)**
[Python](https://github.com/UniRate-API/unirate-api-python) ·
[Node.js / TypeScript](https://github.com/UniRate-API/unirate-api-nodejs) ·
[Go](https://github.com/UniRate-API/unirate-api-go) ·
[Rust](https://github.com/UniRate-API/unirate-api-rust) ·
[Java](https://github.com/UniRate-API/unirate-api-java) ·
[Ruby](https://github.com/UniRate-API/unirate-api-ruby) ·
[PHP](https://github.com/UniRate-API/unirate-api-php) ·
[.NET](https://github.com/UniRate-API/unirate-api-dotnet) ·
[Swift](https://github.com/UniRate-API/unirate-api-swift)

**JavaScript / TypeScript**
[React](https://github.com/UniRate-API/react-unirate) ·
[Next.js](https://github.com/UniRate-API/next-unirate) ·
[Remix](https://github.com/UniRate-API/remix-unirate) ·
[SvelteKit](https://github.com/UniRate-API/sveltekit-unirate) ·
[Vue](https://github.com/UniRate-API/vue-unirate) ·
[Angular](https://github.com/UniRate-API/angular-unirate) ·
[Nuxt](https://github.com/UniRate-API/nuxt-unirate) ·
[NestJS](https://github.com/UniRate-API/nestjs-unirate) ·
[tRPC](https://github.com/UniRate-API/trpc-unirate)

**Static-site generators**
[Astro](https://github.com/UniRate-API/astro-unirate) ·
[Eleventy](https://github.com/UniRate-API/eleventy-unirate) ·
[Hugo](https://github.com/UniRate-API/hugo-unirate) ·
[Jekyll](https://github.com/UniRate-API/jekyll-unirate)

**CMS & e-commerce**
[Wagtail](https://github.com/UniRate-API/wagtail-unirate) ·
[WordPress](https://github.com/UniRate-API/unirate-currency-converter) ·
[WooCommerce](https://github.com/UniRate-API/unirate-woocs) ·
[Drupal](https://github.com/UniRate-API/drupal-unirate) ·
[Strapi](https://github.com/UniRate-API/strapi-plugin-unirate) ·
[Medusa](https://github.com/UniRate-API/medusa-plugin-unirate) ·
[Symfony](https://github.com/UniRate-API/unirate-bundle) ·
[Laravel](https://github.com/UniRate-API/laravel-money-unirate) ·
[Directus](https://github.com/UniRate-API/directus-extension-unirate)

**Data, AI & backend**
[LangChain (Python)](https://github.com/UniRate-API/langchain-unirate) ·
[LangChain.js](https://github.com/UniRate-API/langchain-js-unirate) ·
[FastAPI](https://github.com/UniRate-API/fastapi-unirate) ·
[Flask](https://github.com/UniRate-API/flask-unirate) ·
[Django REST Framework](https://github.com/UniRate-API/djangorestframework-unirate) ·
[Apache Airflow](https://github.com/UniRate-API/airflow-provider-unirate) ·
[dbt](https://github.com/UniRate-API/dbt-unirate)

**Platform & tools**
[MCP server](https://github.com/UniRate-API/unirate-mcp) ·
[CLI](https://github.com/UniRate-API/unirate-cli) ·
[Cloudflare Workers](https://github.com/UniRate-API/cloudflare-workers-unirate) ·
[Home Assistant](https://github.com/UniRate-API/unirate-home-assistant) ·
[n8n](https://github.com/UniRate-API/n8n-nodes-unirate) ·
[Google Sheets](https://github.com/UniRate-API/unirate-sheets) ·
[VS Code](https://github.com/UniRate-API/vscode-unirate) ·
[Obsidian](https://github.com/UniRate-API/obsidian-currency)

**Money library bridges**
[money gem (Ruby)](https://github.com/UniRate-API/money-unirate-api) ·
[NodaMoney (.NET)](https://github.com/UniRate-API/UniRateApi.NodaMoney)

Get a free API key at [unirateapi.com](https://unirateapi.com).
<!-- unirate-ecosystem-footer:end -->

## License

MIT.