from urllib.parse import quote_plus

from apify import Actor
from crawlee import ConcurrencySettings
from crawlee.crawlers import BeautifulSoupCrawler
from crawlee.http_clients import HttpxHttpClient

BASE_URL = 'https://www.onlinejobs.ph'

# Defined after BASE_URL: routes.py imports BASE_URL from this module, so the
# name must exist before `from .routes import router` triggers that import.
from .routes import router  # noqa: E402
# robots.txt declares `Crawl-delay: 5`, i.e. one request every 5s → 12/min.
CRAWL_DELAY_SECONDS = 5
MAX_REQUESTS_PER_MINUTE = 60 // CRAWL_DELAY_SECONDS


async def main(job_keyword: str | None = None, max_pages: int = 5) -> None:
    """The crawler entry point."""
    async with Actor:
        actor_input = await Actor.get_input() or {}
        job_keyword = actor_input.get('jobKeyword', job_keyword)
        max_pages = actor_input.get('maxPages', max_pages)

        base = f'{BASE_URL}/jobseekers/jobsearch'
        start_urls = []
        for i in range(max_pages):
            offset = i * 30
            if job_keyword:
                start_urls.append(f'{base}/{offset}?jobkeyword={quote_plus(job_keyword)}')
            else:
                start_urls.append(f'{base}/{offset}')

        # Single-domain crawl: process one page at a time and cap the rate to
        # honor robots.txt's Crawl-delay. This keeps all requests in the default
        # RequestQueue, so `apify run -p` fully purges between runs.
        concurrency_settings = ConcurrencySettings(
            desired_concurrency=1,
            max_concurrency=1,
            max_tasks_per_minute=MAX_REQUESTS_PER_MINUTE,
        )

        crawler = BeautifulSoupCrawler(
            request_handler=router,
            concurrency_settings=concurrency_settings,
            max_requests_per_crawl=max_pages + max_pages * 30,
            http_client=HttpxHttpClient(timeout=30),
            max_request_retries=1,
            ignore_http_error_status_codes=[410],
        )

        await crawler.run(start_urls)
