import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapyDemo.items import ZazhiusItem
import time
import re

class ZazhiusSpider(CrawlSpider):
    name = 'zazhius'
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
          ':authority': 'www.zazhi.us',
          'referer': 'https://www.zazhi.us/magazines?cao_type=1'
        }
    }
    start_urls = ['https://www.zazhi.us/magazines?cao_type=1/']
    rules = (
        Rule(LinkExtractor(allow=r'https://www.zazhi.us/magazines/([a-z]+-*[a-z]+/)*page/\S+'), follow=True),
        Rule(LinkExtractor(allow=r'https://www.zazhi.us/\d+.html'), callback='parse_item'),
    )

    def parse_item(self, response):
        self.logger.debug(f"开始解析文章详情页：{response.url}")
        if "免费" in response.css(".price::text").getall():
            item = ZazhiusItem()
            article = response.xpath('//article[@class="article-content"]')
            item['website_url'] = 'https://www.zazhi.us'
            item['journal_url'] = response.url
            item['magazine_name'] = article.xpath('//a[@rel="tag"]/text()').get()
            if item['magazine_name']:
                item['magazine_name'] = item['magazine_name'].strip().replace('\n', '').replace('\r', '')
            item['createDate'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            item['journal_name'] = article.xpath('//h1/text()').get()
            item['category'] = article.xpath('//a[@rel="category"]/text()').get()
            image_urls = article.xpath('//div[@class="entry-wrapper"]//img/@src').getall()
            item['image_urls'] = [self.getImgUrl(url, item['website_url']) for url in image_urls]
            item['postDate'] = article.xpath('//span[@class="meta-date"]//text()').get()
            item['pan_share_pwd'] = article.xpath('//span[@id="refurl"]/text()').get()
            post_id = response.xpath("//a[contains(text(),'立即下载')]/@data-id").get()
            item['source_url'] = f"https://www.zazhi.us/go?post_id={post_id}"
            self.logger.debug(f"解析{response.url}，获得基本数据：{item.items()}")
            return scrapy.Request(item['source_url'], self.parse_pan_url, cb_kwargs=dict(item=item))

        self.logger.warning(f"{response.url}不是免费，不提取数据")
        return {}

    def parse_pan_url(self, response, item):
        self.logger.debug(f'开始解析source_url的返回：{response.text}')
        item['pan_share_url'] = re.search(r"https://pan.baidu.com/[^']+", response.text).group()
        self.logger.info(f"解析{response.url}，获得完整数据：{item.items()}")
        return item

    def getImgUrl(self, url, web_prefix):
        if url.find("//") == -1:
            return web_prefix + url
        return url