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

- **CLI:** `output.json` in the working directory — array of job objects, overwritten on each run
- **Apify:** Items pushed to the default dataset (one item per job)

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

- Enforce a minimum **5-second delay** between requests as specified by `Crawl-delay: 5` in `robots.txt`
- The paths `/jobseekers/jobsearch` and `/jobseekers/job/` are not disallowed — scraping is permitted
- Implemented via Crawlee's `ThrottlingRequestManager` with `set_crawl_delay`:
  - `domains` must be a **bare hostname** (`www.onlinejobs.ph`) — the manager uses it as a dict key directly
  - `set_crawl_delay` takes a **full URL** (`https://www.onlinejobs.ph`) — it extracts the host internally
  - Passing the full URL to `domains` silently bypasses throttling (no error raised)

### Error Handling

- HTTP error on a listing page (4xx/5xx): log warning and skip that page
- HTTP error on a detail page: record the `jobUrl` with all detail fields set to `null` / `[]`
- Parse failure on any individual field: set field to `null` and continue (do not abort)

---

## Deployment Targets

### CLI

```bash
python -m onlinejobsph_scraper --jobKeyword "virtual assistant" --maxPages 5
```

### Apify

Input schema mirrors CLI args (`jobKeyword`, `maxPages`). Output is pushed to the Apify default dataset with one item per job.
