# OnlineJobs.ph Scraper

OnlineJobs.ph doesn't offer a public API, but this scraper acts as an unofficial **OnlineJobs.ph API** to help you extract the job data you need, when you need it, and at scale. Just type in a search keyword, set how many pages to crawl, and get clean, structured job listings exported in the format of your choice.

Built with [Crawlee](https://crawlee.dev/python/) (BeautifulSoup parser + httpx client) and deployed as an [Apify](https://apify.com/) Actor.

## What does OnlineJobs.ph Scraper do?

OnlineJobs.ph Scraper extracts job postings from [OnlineJobs.ph](https://www.onlinejobs.ph) — the largest marketplace for hiring Filipino virtual assistants and remote workers — and exports them into JSON, CSV, Excel, or HTML. You can then use this data in your own data projects, hiring pipelines, market reports, and applications.

- 🔎 Search **any keyword** (e.g. `virtual assistant`, `gtm`, `seo`) — or leave it blank to scrape all jobs
- 📄 Scrape job listings across **multiple search-result pages** (30 jobs per page)
- 🧾 Extract full job details: title, employment type, salary, last-updated date, description, and required skills
- 📤 Export data in multiple formats: JSON, CSV, Excel, or HTML
- 🔌 Connect to any AI chatbot or workflow using the Apify API, MCP server, webhooks, and SDKs (Python & Node.js)

## What data can you get from OnlineJobs.ph?

|                      |                         |                    |
| -------------------- | ----------------------- | ------------------ |
| 🧑‍💼 Job title         | ⏱ Employment type       | 💵 Salary          |
| 📅 Date last updated | 📝 Full job description | 🏷️ Required skills |
| 🔗 Job detail URL    |                         |                    |

> **Note:** `employerName` is **not** extracted — the employer section on OnlineJobs.ph is hidden behind a login wall for unauthenticated visitors.

## Why scrape OnlineJobs.ph?

- 🕵️ Research the Filipino remote-work and VA market by role, salary, and recency
- 📈 Monitor hiring trends and in-demand skills over time
- 💸 Benchmark salaries across roles and employment types
- 🗂 Build a custom database of available positions
- 🤺 Track competitors' job postings and hiring activity
- 📩 Feed an automated job-search or lead-generation pipeline

## How to use OnlineJobs.ph Scraper

OnlineJobs.ph Scraper is built for an easy start, even if you've never scraped before:

1. Create a free [Apify account](https://console.apify.com/sign-up) using your email.
2. Open OnlineJobs.ph Scraper.
3. Enter a **Job Keyword** and the **Max Pages** you want to crawl.
4. Click **Start** and wait for the data to be extracted.
5. Download your data in JSON, CSV, Excel, HTML, or XML.

## Input

The input is a simple JSON object. OnlineJobs.ph Scraper recognizes the following parameters:

| Parameter    | Type    | Required | Default | Description                                                         |
| ------------ | ------- | -------- | ------- | ------------------------------------------------------------------- |
| `jobKeyword` | string  | No       | —       | Search keyword (e.g. `virtual assistant`, `gtm`). Blank = all jobs. |
| `maxPages`   | integer | No       | `5`     | Maximum search-result pages to crawl (30 jobs per page).            |

### Input example

```json
{
  "jobKeyword": "virtual assistant",
  "maxPages": 3
}
```

## Output

The results are wrapped into a dataset you can find in the **Storage** tab and access via the API. Each scraped job is a separate item in the dataset.

You can manage the results in any language (Python, PHP, Node.js). See the [API reference](https://docs.apify.com/api/v2) to learn more about getting results from this Actor.

### Scraped OnlineJobs.ph job listings

The structure of each item looks like this:

```json
{
  "jobUrl": "https://www.onlinejobs.ph/jobseekers/job/Virtual-Assistant-1234567",
  "jobTitle": "Executive Virtual Assistant",
  "employmentType": "Full Time",
  "salary": "$4-6 per hour",
  "dateUpdated": "2026-05-31",
  "fullDescription": "We are looking for an experienced executive virtual assistant to manage calendars, handle email, and support day-to-day operations...",
  "skills": ["Email Management", "Calendar Management", "Customer Support"]
}
```

### Output fields

| Field             | Type           | Description                                                 |
| ----------------- | -------------- | ----------------------------------------------------------- |
| `jobUrl`          | string (URL)   | Canonical job detail URL                                    |
| `jobTitle`        | string         | Job title                                                   |
| `employmentType`  | string         | `Full Time`, `Part Time`, `Gig`, or `Any`                   |
| `salary`          | string \| null | Raw salary string (e.g. `$4-6 per hour`); `null` if absent  |
| `dateUpdated`     | string         | Date last updated, parsed to ISO `YYYY-MM-DD` when possible |
| `fullDescription` | string         | Job description, with `<ojfilter>` tags stripped            |
| `skills`          | string[]       | Listed skills / top-skill labels                            |

## During the run

OnlineJobs.ph Scraper runs in two phases:

1. **Listing phase** — crawls each search-results page and collects job detail URLs.
2. **Detail phase** — visits each collected URL and extracts the structured fields above.

To respect the site's `robots.txt` (`Crawl-delay: 5`), the crawler runs **one request at a time** and caps its rate at **12 requests/minute**. Total requests per run are bounded by `maxPages` listing pages plus up to 30 detail pages each.

If a detail page can't be fetched, the job is still recorded (with empty fields) rather than silently dropped, so your dataset stays complete and predictable.

## Integrations

You can connect OnlineJobs.ph Scraper with almost any cloud service or web app. Apify offers integrations with Make, Zapier, Slack, Google Sheets, Google Drive, GitHub, and more, plus webhooks to trigger actions whenever a run finishes.

### Using the Apify API

The [Apify API](https://docs.apify.com/api/v2) gives you programmatic access to run the Actor, schedule it, and fetch results. Use the [`apify-client`](https://docs.apify.com/api/client/js/) NPM package for Node.js or the [`apify-client`](https://docs.apify.com/api/client/python/) PyPI package for Python.

### Using an MCP server

With the Apify API you can use this Actor through an MCP server and connect it to clients like Claude Desktop, or build your own. Read more about [setting up Apify Actors with MCP](https://docs.apify.com/platform/integrations/mcp).

## Is it legal to scrape OnlineJobs.ph?

This scraper only collects data that employers have chosen to publish publicly, and it honors the site's crawl-delay. It does not extract data behind the login wall (such as employer contact details).
