#### First trial of getting urls

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import sys
from utils import generate_url

class UrlsSpider(CrawlSpider):
    name = "urls"
    allowed_domains = "https://www.booking.com"
    start_urls = [generate_url("01-01-2022", "15-10-2022", "Barcelona", "España", 3, 1, 2)]
    rules = [Rule(LinkExtractor(allow=r'.*'), callback='parse_items', follow=True)]
    
