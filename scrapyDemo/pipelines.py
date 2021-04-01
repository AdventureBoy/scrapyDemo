# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import pymongo
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
import logging

logger = logging.getLogger(__name__)

class MongoPipeline:

    collection_name = 'magazine'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'scrapy_data')
        )

    def open_spider(self, spider):
        logger.debug(f"建立mangodb连接，url:{self.mongo_uri},db:{self.mongo_db}")
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        logger.debug("关闭mangodb连接");
        self.client.close()

    def process_item(self, item, spider):
        logger.debug(f"将item写入mongodb,collection_name:{self.collection_name},item:{ItemAdapter(item).asdict()}")
        self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
        return item


class MyImagesPipeline(ImagesPipeline):

    def file_path(self, request, response=None, info=None, *, item=None):
        logger.debug(f"确定图片保存路径:full/{item['journal_name']}.jpg")
        return f'full/{item["journal_name"]}.jpg'

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            logger.error(f"{item['journal_url']}没有图片:处理的urls:{ItemAdapter(item).get(self.images_urls_field, [])}")
            return item
        adapter = ItemAdapter(item)
        adapter['images_os_path'] = image_paths
        logger.debug(f"设置好item的images_os_path属性：{ItemAdapter(item).asdict()}")
        return item

