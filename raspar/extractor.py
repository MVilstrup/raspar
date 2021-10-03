from typing import Any, Optional
from concurrent.futures import ThreadPoolExecutor
import re
from raspar.wrappers import FieldValidator, LinkGenerator

class Extractor:
    _workers = ThreadPoolExecutor()

    URL_PATTERN: Optional[str] = None
    ELEMENT_PATTERN: Optional[str] = None

    def __init__(self) -> None:
        if self.URL_PATTERN is None:
            raise ValueError("Extractors should define the static variable 'URL_PATTERN'")

        self._fields = {name: value for name, value in self.__dict__.items() if isinstance(value, FieldValidator)}
        self._links = {name: value for name, value in self.__dict__.items() if isinstance(value, LinkGenerator)}
        self._url_pattern = re.compile(self.URL_PATTERN)


    def matches(self, url):
        return self._url_pattern.search(url)

    def extract_items(self, page):
        def _extract(element):
            item = {}
            for key, validator in self._fields.items():
                item[key] = validator(element)
            
            return item
        
        if self.ELEMENT_PATTERN is None:
            return [_extract(page)] 
        else:
            return [_extract(element) for element in page.select(self.ELEMENT_PATTERN)]

    
    def extract_links(self, page):
        links = []
        for link_extractor in self._links.values():
            links += link_extractor(page)

        return links

    def fetch(self, url):
        from raspar.crawl import Crawl
        return Crawl(2, extractors=[self]).fetch(url)
    
    def __call__(self, page) -> Any:
        return {
            "items": self.extract_items(page),
            "links": self.extract_links(page)
        }

    



            