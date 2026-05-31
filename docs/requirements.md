# OnlineJobs.ph Scraper Requirements

## Target Website

- https://www.onlinejobs.ph/jobseekers/jobsearch

---

## Input Parameters

Passed as CLI arguments or Apify input schema fields.

| Parameter    | Type    | Required | Default | Description                                                                    |
| ------------ | ------- | -------- | ------- | ------------------------------------------------------------------------------ |
| `jobKeyword` | string  | No       | —       | Search keyword (e.g. `virtual+assistant`, `gtm`); if omitted, returns all jobs |
| `maxPages`   | integer | No       | `5`     | Maximum number of search result pages to crawl                                 |

---

## Output Format

- **Local (`apify run`):** Items written to `storage/datasets/default/` (one JSON file per item)
- **Apify cloud:** Items pushed to the Apify default dataset, accessible from the console

Total requests per crawl is capped at `maxPages + maxPages × 30` (listing pages + up to 30 detail pages each).

---

## Data Fields

All fields are extracted from the job detail page. The listing page is only used to collect job URLs.

### Listing Page

| Field    | Data Type    | CSS Selector                                                   | Notes                                                                                                            |
| -------- | ------------ | -------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `jobUrl` | string (URL) | `a[href^="/jobseekers/job/"]:not([target])` → `href` attribute | Relative path; prefix with `https://www.onlinejobs.ph`; `:not([target])` excludes the duplicate "See More" links |

### Detail Page Fields

| Field             | Data Type      | CSS Selector                                    | Notes                                                              |
| ----------------- | -------------- | ----------------------------------------------- | ------------------------------------------------------------------ |
| `jobTitle`        | string         | `h1.job__title`                                 | Inner text                                                         |
| `employmentType`  | string         | `.card.job-post .col-lg-3:nth-child(1) p.fs-18` | Values: `Full Time`, `Part Time`, `Gig`, `Any`; trim whitespace    |
| `salary`          | string \| null | `.card.job-post .col-lg-3:nth-child(2) p.fs-18` | Raw string (e.g. `$4-6 per hour`); `null` if empty                 |
| `dateUpdated`     | string         | `.card.job-post .col-lg-3:nth-child(4) p.fs-18` | Human-readable (e.g. `May 31, 2026`); parse to ISO date at runtime |
| `fullDescription` | string         | `p#job-description`                             | Strip `<ojfilter>` tags and inner HTML; trim whitespace            |
| `skills`          | string[]       | `a.card-worker-topskill`                        | Collect all matching elements as an array of label strings         |

> **Note on `employerName`:** This field is not rendered for unauthenticated (guest) requests — the employer section is hidden behind a login wall. Remove from scope unless authenticated scraping is added later.

---

## URL Format

```
https://www.onlinejobs.ph/jobseekers/jobsearch/{offset}?jobkeyword={jobKeyword}
```

- Pagination offset increments by **30** per page
  - Page 1 → offset `0`
  - Page 2 → offset `30`
  - Page N → offset `(N - 1) * 30`
- Example: keyword `gtm`, page 2 → `/jobseekers/jobsearch/30?jobkeyword=gtm`

---

## Crawling Strategy

### Entry Point

For each keyword, crawling starts at:

```
https://www.onlinejobs.ph/jobseekers/jobsearch/0?jobkeyword={jobKeyword}
```

### Pagination

- Pages crawled: `0, 30, 60, ..., (maxPages - 1) * 30`
- Stops after `maxPages` pages (default: `5`) regardless of total results reported on the page
- Crawler does not dynamically compute page count from the "Displaying X out of Y" counter

### Crawl Depth

- **Level 1:** Collect job URLs from each search results page — no other data extracted
- **Level 2:** Visit each job's detail URL to extract all fields

### Re-run Behavior

- Output is **overwritten** on each run — no deduplication or append logic

### Rate Limiting

- Honor `Crawl-delay: 5` from `robots.txt`: at most one request every 5 seconds → **12 requests/minute**
- The paths `/jobseekers/jobsearch` and `/jobseekers/job/` are not disallowed — scraping is permitted
- Implemented via Crawlee's `ConcurrencySettings` on the `BeautifulSoupCrawler`:
  - `max_concurrency=1` (with `desired_concurrency=1`) processes one page at a time — the crawler rejects `desired_concurrency > max_concurrency`, so both must be set
  - `max_tasks_per_minute=12` (`60 // CRAWL_DELAY_SECONDS`) caps the rate to the crawl-delay
- Since onlinejobs.ph is the only domain crawled, a plain default `RequestQueue` is used — all requests live in one queue, so `apify run -p` purges cleanly between local runs
- Avoid `ThrottlingRequestManager` here: for a single throttled domain it routes every request into a separate aliased queue (`throttled-<host>`) that `apify run -p` does **not** purge, causing requests to accumulate across local runs

### Error Handling

- HTTP error on a listing page (4xx/5xx): log warning and skip that page
- HTTP error on a detail page: record the `jobUrl` with all detail fields set to `null` / `[]`
- Parse failure on any individual field: set field to `null` and continue (do not abort)

---

## Deployment Targets

### Local (via Apify CLI)

Set input in `storage/key_value_stores/default/INPUT.json`, then:

```bash
apify run
```

### Apify

Input schema mirrors CLI args (`jobKeyword`, `maxPages`). Output is pushed to the Apify default dataset with one item per job.
