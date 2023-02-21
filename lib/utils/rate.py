# -*- coding: utf-8 -*-

import threading
import time

from queue import Queue


class RateLimiter:

    def __init__(self, rate, time_window=60):
        self.queue = Queue(maxsize=rate)
        self.time_window = time_window

    def pause(self):
        request_time = time.time()
        if self.queue.full():
            # If the queue is full, wait until the oldest request is older than 60 seconds
            oldest_request_limit = self.queue.get() + self.time_window
            if request_time < oldest_request_limit:
                time.sleep(oldest_request_limit - request_time)
        # If the queue is not full, just add the request time to the queue
        self.queue.put(request_time)

    def get_rate(self):
        return self.queue.qsize()
