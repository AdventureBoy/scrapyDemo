# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ZazhiusItem(scrapy.Item):
    # define the fields for your item here like:
    journal_name = scrapy.Field()
    category = scrapy.Field()
    magazine_name = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    images_os_path = scrapy.Field()
    remark = scrapy.Field()
    website_url = scrapy.Field()
    journal_url = scrapy.Field()
    source_url = scrapy.Field()
    pan_share_url = scrapy.Field()
    pan_share_pwd = scrapy.Field()
    postDate = scrapy.Field()
    createDate = scrapy.Field()
