# OnlineJobs.ph Scraper

An [Apify](https://apify.com/) Actor that scrapes job postings from [OnlineJobs.ph](https://www.onlinejobs.ph) by keyword and page count. Built with [Crawlee](https://crawlee.dev/python/) using a BeautifulSoup parser and an httpx HTTP client.

## How it works

The scraper runs in two phases:

1. **Listing phase** — Crawls each search-results page and collects job detail URLs (`a[href^="/jobseekers/job/"]`).
2. **Detail phase** — Visits each collected URL and extracts the structured fields below.

Search-result pages are paginated with an offset of 30 per page (`/jobseekers/jobsearch/{offset}`). The crawl runs one request at a time and caps the rate at **12 requests/minute** to honor the site's `robots.txt` `Crawl-delay: 5`.

## Input parameters

Passed as CLI arguments locally, or as Apify input-schema fields on the platform.

| Parameter    | Type    | Required | Default | Description                                                            |
| ------------ | ------- | -------- | ------- | ---------------------------------------------------------------------- |
| `jobKeyword` | string  | No       | —       | Search keyword (e.g. `virtual assistant`, `gtm`). Blank = all jobs.    |
| `maxPages`   | integer | No       | `5`     | Maximum search-result pages to crawl (30 jobs per page).               |

Total requests per run are capped at `maxPages + maxPages × 30` (listing pages + up to 30 detail pages each).

## Output fields

Each scraped job is pushed as one dataset item with these fields (all extracted from the detail page):

| Field             | Type           | Description                                            |
| ----------------- | -------------- | ------------------------------------------------------ |
| `jobUrl`          | string (URL)   | Canonical job detail URL                               |
| `jobTitle`        | string         | Job title                                              |
| `employmentType`  | string         | `Full Time`, `Part Time`, `Gig`, or `Any`              |
| `salary`          | string \| null | Raw salary string (e.g. `$4-6 per hour`); `null` if absent |
| `dateUpdated`     | string         | Date last updated, parsed to ISO `YYYY-MM-DD` when possible |
| `fullDescription` | string         | Job description, with `<ojfilter>` tags stripped       |
| `skills`          | string[]       | Listed skills/top-skill labels                         |

> **Note:** `employerName` is not extracted — the employer section is hidden behind a login wall for unauthenticated requests.

See [docs/requirements.md](docs/requirements.md) for the full spec, including CSS selectors and error-handling rules.

## Local development

Requires [Poetry](https://python-poetry.org/) (install with `pipx install poetry`).

Install dependencies:

```sh
poetry install
```

### Run directly with Python

```sh
poetry run python -m onlinejobsph_scraper --jobKeyword "virtual assistant" --maxPages 3
```

Both flags are optional (`--jobKeyword` defaults to all jobs, `--maxPages` defaults to `5`). Items are written to `storage/datasets/default/`.

### Run via the Apify CLI

Set the input in `storage/key_value_stores/default/INPUT.json`, then:

```sh
apify run
```

Use `apify run -p` to purge storage between runs.

## Deployment

The Actor builds from the [Dockerfile](Dockerfile) (`apify/actor-python:3.13` base) and is configured by [.actor/actor.json](.actor/actor.json) and [.actor/INPUT_SCHEMA.json](.actor/INPUT_SCHEMA.json). On the Apify platform, items are pushed to the run's default dataset.

## Project layout

```
onlinejobsph_scraper/
  __main__.py   # CLI entry point (argparse → main)
  main.py       # Actor setup, URL generation, crawler config, rate limiting
  routes.py     # Listing + detail request handlers
.actor/         # Apify Actor + input schema config
docs/           # Full scraping requirements / field spec
Dockerfile      # Apify Actor image
```
