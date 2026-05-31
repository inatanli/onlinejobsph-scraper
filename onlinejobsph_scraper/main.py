from apify import Actor
from crawlee.crawlers import BeautifulSoupCrawler
from crawlee.http_clients import HttpxHttpClient
from .routes import router

async def main() -> None:
    """The crawler entry point."""
    async with Actor:
        crawler = BeautifulSoupCrawler(
            request_handler=router,
            max_requests_per_crawl=10,
            http_client=HttpxHttpClient(),
        )

        await crawler.run(
            [
                'https://www.onlinejobs.ph/jobseekers/jobsearch',
            ]
        )
