import scrapy
from eksiarchive.items import *
from bs4 import BeautifulSoup
from datetime import datetime

import sys
if (sys.version_info>=(3, 0, 0,)):
    from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
else:
    from urlparse import urlparse, parse_qs, urlunparse
    from urllib import urlencode

class EksiSpider(scrapy.Spider):
    name = 'eksi'

    allowed_domains = ['eksisozluk.com']
    start_urls = ['https://eksisozluk.com/']

    def parse(self, response):
        if 'https://seyler.eksisozluk.com' in response.url:
            return
        
        print(f'Processing url ({len(self.crawler.engine.slot.scheduler)}): {response.url}')
        
        bs = BeautifulSoup(response.text, features='html5lib')

        title_tag = [ x for x in bs.find_all() if 'data-title' in x.attrs ]
        links = bs.find_all('a')

        if len(title_tag) == 1: 
            
            title = Title()
            title['id'] = int(title_tag[0].attrs['data-id'])
            title['name'] = title_tag[0].attrs['data-title']

            yield title

            entries = [ x for x in bs.find_all() if 'data-author' in x.attrs]
            entries = [ self.create_entry(x) for x in entries ]
        
            self.process_entries(entries, title)

            for entry in entries:
                yield entry

        pager = bs.find_all('div', {'class': 'pager'})

        if len(pager) > 0:
            uu = list(urlparse(response.url))
            qs = parse_qs(uu[4], keep_blank_values=True)

            pager = pager[0]
            current_page = int(pager.attrs['data-currentpage'])
            page_count = int(pager.attrs['data-pagecount'])
            if 'p' not in qs:    
                while page_count > current_page: #Queue all pages in topic
                    qs['p'] = current_page + 1  #Change q parameter
                    uu[4] = urlencode(qs, doseq=True)
                    new_url = self.process_link(urlunparse(uu))

                    yield response.follow(self.process_link(new_url), self.parse, priority=20) #Higher priority for next pages
                    current_page += 1
            
        if len(self.crawler.engine.slot.scheduler) < 10000:
            if '/entry/' in response.url:
                url = [ x for x in bs.find_all() if 'itemprop' in x.attrs ]

                if len(url) > 0:
                    url = 'https://eksisozluk.com' + url[0].attrs['href']
                    yield response.follow(self.process_link(url), self.parse)
                
            for link in links:
                if 'href' in link.attrs:
                    url = link.attrs['href']
                    yield response.follow(self.process_link(url), self.parse)

    def process_link(self, link):
        uu = list(urlparse(link))
        qs = parse_qs(uu[4], keep_blank_values=True)

        FORBIDDEN_QS = [
            'entryId', 'focusto', 'a', 'nr', 'rf', 'nick', 'slug', 'id', 'day'
        ]
        for item in FORBIDDEN_QS:
            if item in qs:
                del qs[item]
        
        uu[4] = urlencode(qs, doseq=True)
        new_url = urlunparse(uu)

        return new_url
    
    def process_entries(self, entries, title):
        for entry in entries:
            entry['content'] = entry['content'].strip()
            entry['title_id'] = title['id']
            
    def create_entry(self, item):
        entry = Entry()
        entry['id'] = item.attrs['data-id']
        entry['likes'] = item.attrs['data-favorite-count']
        entry['author'] = item.attrs['data-author']
        entry['author_id'] = item.attrs['data-author-id']
        entry['content'] = self.process_entry(item.find(class_='content')).get_text().strip()
        
        entry['date'] = item.find('footer').find(class_='info').find(class_='entry-date').text.split('~')[0].strip()

        try:
            entry['date'] = datetime.strptime(entry['date'], '%d.%m.%Y %H:%M').isoformat() #Parse datetime
        except:
            entry['date'] = datetime.strptime(entry['date'], '%d.%m.%Y').isoformat() #Parse datetime, with no hours (for really old entries)
        
        return entry

    def process_entry(self, item):
        for x in item.find_all('a'):
            if x['href'].startswith('/?q='):
                continue

            x.replace_with(x['href'])
        
        for x in item.find_all('br'):
            x.replace_with('\n')

        return item 
