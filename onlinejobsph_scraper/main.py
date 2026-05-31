import json

from apify import Actor
from crawlee.crawlers import BeautifulSoupCrawler
from crawlee.http_clients import HttpxHttpClient
from crawlee.request_loaders import ThrottlingRequestManager
from crawlee.storages import RequestQueue

from .routes import router

HOSTNAME = 'www.onlinejobs.ph'
BASE_URL = f'https://{HOSTNAME}'
CRAWL_DELAY_SECONDS = 5


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
                start_urls.append(f'{base}/{offset}?jobkeyword={job_keyword}')
            else:
                start_urls.append(f'{base}/{offset}')

        # ThrottlingRequestManager keys domains by bare hostname (used directly as
        # the dict key), while set_crawl_delay resolves its arg through URL().host —
        # so pass the hostname to `domains` and a full URL to set_crawl_delay.
        queue = await RequestQueue.open()
        request_manager = ThrottlingRequestManager(
            inner=queue,
            domains=[HOSTNAME],
            request_manager_opener=RequestQueue.open,
        )
        request_manager.set_crawl_delay(BASE_URL, CRAWL_DELAY_SECONDS)

        crawler = BeautifulSoupCrawler(
            request_handler=router,
            request_manager=request_manager,
            max_requests_per_crawl=max_pages + max_pages * 30,
            http_client=HttpxHttpClient(),
        )

        await crawler.run(start_urls)

        if not Actor.is_at_home():
            dataset = await Actor.open_dataset()
            result = await dataset.get_data()
            with open('output.json', 'w') as f:
                json.dump(result.items, f, indent=2, ensure_ascii=False)
            Actor.log.info(f'Wrote {len(result.items)} jobs to output.json')
