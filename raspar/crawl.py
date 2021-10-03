from typing import Tuple, Optional, Callable
import requests
import validators
import re
from fake_useragent import UserAgent
from raspar.job_queue import JobQueue
from raspar.utils import recursive_expansion
from concurrent.futures import ThreadPoolExecutor, as_completed
import raspar.status as status
from raspar.status import Status
from raspar.page import Page

class Crawl:
    def __init__(self, num_workers, extractors, expected_url_amount=1e7, timeout=10, max_size=1.) -> None:
        self.job_queue = JobQueue(num_workers * 10, expected_url_amount)
        self.num_workers: int = num_workers
        self.extractors = extractors
        self.timeout: int = timeout
        self.max_size: float = max_size

        self.combined_patterns = re.compile("|".join([ext.URL_PATTERN for ext in extractors]))
        self.ua = UserAgent()

    @property
    def headers(self):
        return {
            'User-Agent': str(self.ua.random),
            "Accept-Encoding": "br, gzip, deflate",
            "Accept": "test/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "http://www.google.com/",
        }

    def _parse(self, url, page):
        items = []
        links = []

        for extractor in self.extractors:
            if extractor.matches(url):
                result = extractor(page)
                items += result["items"]
                links += result["links"]

        self.add(*links)
        return status.ALL_OK, url, items

    def fetch(self, url: str, session=None):
        session = session if session is not None else requests

        """
        Check size before downloading
        """
        head = session.head(url, allow_redirects=True)
        if head.status_code < 200:
            return status.INFORMATION_RESPONSE, url, None
        elif 400 >= head.status_code < 500:
            return status.CLIENT_ERROR, url, None
        elif head.status_code >= 500:
            return status.SERVER_ERROR, url, None

        mb_size = int(head.headers.get('content-length', -1)) / float(1 << 20)
        if mb_size > self.max_size:
            return status.CONTENT_TOO_BIG_ERROR, url, None

        try:
            response = session.get(url, headers=self.headers, timeout=self.timeout)
            if response.status_code < 200:
                return status.INFORMATION_RESPONSE, url, None
            elif 400 >= response.status_code < 500:
                return status.CLIENT_ERROR, url, None
            elif response.status_code >= 500:
                return status.SERVER_ERROR, url, None
            
            page = None
            try:
                page = Page(url, response.text)
            except:
                return status.COULD_NOT_PARSE_ERROR, url, None

            return self._parse(url, page)

        except requests.exceptions.Timeout:
            # Maybe set up for a retry, or continue in a retry loop
            return status.TIMEOUT_ERROR, url, None
        except requests.exceptions.TooManyRedirects:
            # Tell the user their URL was bad and try a different one
            return status.TOO_MANY_REDIRECTS, url, None
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            return status.REQUEST_ERROR, url, None
        except:
            return status.RUNTIME_ERROR, url, None
        

    def add(self, *urls: Tuple[str]):
        """
        New urls can be added before and during the extraction process has begun
        """
        for url in recursive_expansion(urls, lambda el: isinstance(el, str) and validators.url(el)):
            if self.combined_patterns.search(url):
                self.job_queue.add(url)

    def __iter__(self):
        with ThreadPoolExecutor(self.num_workers) as pool:
            for url_batch in self.job_queue:
                with requests.Session() as session:
                    yielded_urls = set()
                    jobs = {}
                    try:
                        jobs = {pool.submit(self.fetch, url, session): url for url in url_batch}
                        for future in as_completed(jobs):
                            url = jobs[future]

                            yield future.result()
                            yielded_urls.add(url)
                            self.job_queue.succeeded(url)
                    except:
                        for url in jobs.values():
                            if url not in yielded_urls:
                                self.job_queue.failed(url)
                

            