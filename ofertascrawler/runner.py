import os
import random
import scrapy

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from ofertascrawler.spiders.ofertas import OfertasSpider

WORKERS = os.getenv('SPIDER_WORKERS', 8)
USER_AGENTS = ['Mozilla/5.0 (X11; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0',
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
               'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
               'Mozilla/5.0 (Linux; Android 7.1.2; AFTMM Build/NS6265; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.110 Mobile Safari/537.36',
               'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Mobile/15E148 Safari/604.1',
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
               'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
               'Mozilla/5.0 (X11; Datanyze; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36']


def main():
    urls = []
    with open('./data/offers.csv') as urlfile:
        urls = urlfile.readlines()

    random.shuffle(USER_AGENTS)

    process = CrawlerProcess(get_project_settings())
    for i in range(WORKERS):
        boundaries = [i * (len(urls)//WORKERS), (i+1) * (len(urls)//WORKERS)]
        user_agent = random.choice(USER_AGENTS)
        process.crawl(OfertasSpider, urlfile=urls[boundaries[0]:boundaries[1]], user_agent=user_agent)

    process.start()


if __name__ == '__main__':
    main()
