# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import datetime

#import redis
import re
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join  # TakeFirst只取第一个

import pymysql

from w3lib.html import remove_tags

from ArticleSpider.models.es_types import ArticleType

from elasticsearch_dsl.connections import connections
es = connections.create_connection(ArticleType._doc_type.using)

#redis_cli = redis.StrictRedis()


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


# 日期转换
def date_convert(value):
    try:
        result_date = datetime.datetime.strptime(value,'%Y-%m-%d').date()
    except Exception as e:
        result_date = datetime.datetime.now().date()
    return result_date


#  获取数字
def get_nums(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums


def return_value(value):
    return value


# def get_value(value):
#     # if value.strip()=='':
#     #     return "ISNULL"
#     # else:
#     #     return value
#     if value:
#         return value
#     else:
#         return "无值"

def gen_suggestions(index,info_tuple):
    # 根据字符串生成搜索建议
    used_words = set()
    suggestions = []
    for text,weigth in info_tuple:
        if text:
            #调用es的analyze借口分析字符串
            words = es.indices.analyze(index=index,analyzer="ik_max_word",params={'filter':["lowercase"]},body=text)
            analyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"])>1])
            new_words = analyzed_words - used_words
        else:
            new_words =set()

        if new_words:
            suggestions.append({"input":list(new_words),"weight":weigth})

    return suggestions

class LvChaSoftItem(scrapy.Item):
    # 标题
    title = scrapy.Field()
    # 软件url
    url = scrapy.Field()
    # 唯一id
    url_object_id = scrapy.Field()
    # 图片地址
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    # 图片对应目录
    front_image_path = scrapy.Field()
    # type 主要类别
    type = scrapy.Field()
    # 软件大小
    size = scrapy.Field()
    # 软件更新时间
    update_time = scrapy.Field(
        input_processor=MapCompose(date_convert),
    )
    # 软件介绍
    content = scrapy.Field()
    # 标签
    tag = scrapy.Field()
    # 评分
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    # 下载地址
    download_urls = scrapy.Field()


    def get_insert_sql(self):
        insert_sql = """
            INSERT INTO lcsoft_article(title, url, url_object_id, front_image_url,front_image_path,type,size,update_time,content,tag,fav_nums,download_urls)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # 空值处理
        front_image_path_result = ""
        download_urls_result = ""
        if "front_image_path" in self:
            front_image_path_result = self["front_image_path"]

        if "download_urls" in self:
            download_urls_result = self["download_urls"]

        params = (
            self["title"], self["url"], self["url_object_id"], self["front_image_url"], front_image_path_result,
            self["type"], self["size"], self["update_time"], self["content"], self["tag"], self["fav_nums"],
            download_urls_result)

        return insert_sql, params

    def save_to_es(self):
        article = ArticleType()
        article.title = self["title"]
        article.url = self["url"]
        article.front_image_url = self["front_image_url"]
        if "front_image_path" in self:
            article.front_image_path = self["front_image_path"]
        article.type = self["type"]
        article.size = self["size"]
        article.update_time = self["update_time"]
        article.content = remove_tags(self["content"])
        article.tag = self["tag"]
        article.fav_nums = self["fav_nums"]
        if "download_urls" in self:
            article.download_urls = self["download_urls"]
        article.meta.id = self["url_object_id"]

        article.suggest = gen_suggestions(ArticleType._doc_type.index,((article.title,10),(article.tag,7)))

        article.save()

        #redis_cli.incr("lcsoft_count")
        return





class ArticleItemLoader(ItemLoader):
    # 自定义itemloader
    default_output_processor = TakeFirst()
