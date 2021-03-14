from scrapy import signals
from itemadapter import is_item, ItemAdapter
from stem import Signal
from stem.control import Controller
import random


class EskiArchiveDownloaderMiddleware:
    def __init__(self):
        self.tor_request_count = 0
        self.tor_controller = Controller.from_port(port = 9051)
        self.tor_controller.authenticate(password='')
                    

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        if random.random() <= 0.5:
            self.tor_request_count += 1
            request.meta['proxy'] = "http://127.0.0.1:8181"
            if self.tor_request_count >= 100:    
                self.tor_request_count = 0
                self.tor_controller.signal(Signal.NEWNYM)
                

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
