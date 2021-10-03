from time import sleep
from typing import Optional, Callable
import persistqueue
from datetime import datetime
from time import sleep
import os

from pybloomfilter import BloomFilter
from threading import Lock

class JobQueue:

    def __init__(self, batch_size, path=".", max_empty_time=60, expected_url_amount=1e7) -> None:
        path = os.path.abspath(os.path.expanduser(path))

        self.batch_size = batch_size
        self.max_empty_time = max_empty_time

        self._filter = BloomFilter(expected_url_amount, 0.01, os.path.join(path, "url.filter"))
        self._url_queue = persistqueue.SQLiteAckQueue(path)

        self.lock = Lock()
    
    def add(self, url):
        with self.lock:
            if url not in self._filter:
                self._url_queue.put(url)
                self._filter.add(url)

    def succeeded(self, url):
        self._url_queue.ack(url)

    def failed(self, url):
        self._url_queue.nack(url)

    def __iter__(self):
        while True:
            if self._url_queue.active_size == 0:
                start_time = datetime.now()
                while self._url_queue.active_size == 0:
                    sleep(1)
                    if (datetime.now() - start_time).seconds >= self.max_empty_time:
                        raise StopIteration

            next_batch_size = min(self._url_queue.active_size, self.batch_size)

            yield [self._url_queue.get() for _ in range(next_batch_size)]

        
        