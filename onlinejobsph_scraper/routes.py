from datetime import datetime

from crawlee import Request
from crawlee.crawlers import BeautifulSoupCrawlingContext
from crawlee.router import Router

from .main import BASE_URL

router = Router[BeautifulSoupCrawlingContext]()


@router.default_handler
async def listing_handler(context: BeautifulSoupCrawlingContext) -> None:
    """Phase 1: collect job URLs from search results page."""
    context.log.info(f'Listing page: {context.request.url}')

    links = context.soup.select('a[href^="/jobseekers/job/"]:not([target])')
    requests = [
        Request.from_url(BASE_URL + a['href'], label='DETAIL')
        for a in links
        if a.get('href')
    ]
    if requests:
        await context.add_requests(requests)
    context.log.info(f'Enqueued {len(requests)} job URLs')


@router.handler('DETAIL')
async def detail_handler(context: BeautifulSoupCrawlingContext) -> None:
    """Phase 2: extract all fields from job detail page."""
    soup = context.soup
    context.log.info(f'Detail page: {context.request.url}')

    if soup.select_one('section.section-404'):
        context.log.info(f'Skipping unavailable job: {context.request.url}')
        return

    title_el = soup.select_one('h1.job__title')
    job_title = title_el.get_text(strip=True) if title_el else None

    emp_el = soup.select_one('.card.job-post .col-lg-3:nth-child(1) p.fs-18')
    employment_type = emp_el.get_text(strip=True) if emp_el else None

    sal_el = soup.select_one('.card.job-post .col-lg-3:nth-child(2) p.fs-18')
    salary_raw = sal_el.get_text(strip=True) if sal_el else None
    salary = salary_raw if salary_raw else None

    date_el = soup.select_one('.card.job-post .col-lg-3:nth-child(4) p.fs-18')
    date_updated = None
    if date_el:
        try:
            date_updated = datetime.strptime(
                date_el.get_text(strip=True), '%B %d, %Y'
            ).strftime('%Y-%m-%d')
        except ValueError:
            date_updated = date_el.get_text(strip=True)

    desc_el = soup.select_one('p#job-description')
    if desc_el:
        for tag in desc_el.find_all('ojfilter'):
            tag.decompose()
        full_description = desc_el.get_text(separator='\n', strip=True)
    else:
        full_description = None

    skill_els = soup.select('a.card-worker-topskill')
    skills = [el.get_text(strip=True) for el in skill_els]

    await context.push_data({
        'jobUrl': context.request.url,
        'jobTitle': job_title,
        'employmentType': employment_type,
        'salary': salary,
        'dateUpdated': date_updated,
        'fullDescription': full_description,
        'skills': skills,
    })
