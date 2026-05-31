import asyncio
import argparse

from .main import main

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='OnlineJobs.ph scraper')
    parser.add_argument('--jobKeyword', type=str, default=None)
    parser.add_argument('--maxPages', type=int, default=5)
    args = parser.parse_args()

    asyncio.run(main(job_keyword=args.jobKeyword, max_pages=args.maxPages))
