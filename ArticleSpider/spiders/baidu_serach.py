# -*- coding: utf-8 -*-
__author__ = 'luhui.liu'

import scrapy
import re
from scrapy.http import Request

# 拼接url前边的主域名地址
from urllib import parse

import datetime


#from scrapy.xlib.pydispatch import dispatcher
import time
from ArticleSpider.items import LvChaSoftItem, ArticleItemLoader

from ArticleSpider.utils.common import get_md5

from scrapy import signals


class LcsoftSpider(scrapy.Spider):
    name = "baidu_search"
    allowed_domains = ["www.baidu.com"]
    start_urls = ['http://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=0&rsv_idx=1&ch=12&tn=56060048_4_pg&wd=小米']

    # 收集绿茶软件园所有404的url以及404页面数
    handle_httpstatus_list = [404]

    def __init__(self, **kwargs):
        self.fail_urls = []
        # spider启动信号和spider_opened函数绑定
        # dispatcher.connect(self.spider_opened, signals.spider_opened)
        # spider关闭信号和spider_spider_closed函数绑定
        #dispatcher.connect(self.handle_spider_closed, signals.spider_closed)

    def handle_spider_closed(self, spider, reason):
        print("[33lc] spiders is closed!")
        # session = loadSession()
        # log = session.query(SpiderCrawlLog).filter(SpiderCrawlLog.spiderID == self.rule.id,SpiderCrawlLog.endTime == None).first()
        # log.endTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # log.status = "closed"
        # session.commit()
        self.crawler.stats.set_value("failed_urls", ",".join(self.fail_urls))

    def parse(self, response):

        """This function parses a property page.

                @url http://www.33lc.com/soft/
                @returns items 1
                @scrapes title url url_object_id front_image_url front_image_path
                @scrapes type size update_time content tag fav_nums download_urls
        """

        """
        1.获取文章列表页中的文章url并交个scrapy下载后并进行解析
        2.获取下一页的url并交给scrapy进行下载，下载完成后交个parse函数
        :param response:
        :return:
        """
        # 解析软件下载分类软件列表
        # post_nodes = response.css ("#archive .floated-thumb .post-thumb a")
        post_nodes = response.xpath("//*[@id='main1k']/div[2]/dl")
        for post_node in post_nodes:
            list_url = post_node.xpath("./dd/a[1]/@href").extract_first("")
            yield Request(url=parse.urljoin(response.url, list_url), callback=self.parse_list)
            print(list_url)

    def parse_list(self, response):
        '''
        1.获取文章列表页中的文章url并交个scrapy下载后并进行解析
        2.获取下一页的url并交个scrapy进行下载，下载完成后交给parse_list函数
        '''
        post_nodes = response.xpath("//div[@class='soft_list']/div/p/a")
        for post_node in post_nodes:
            image_url = post_node.xpath('./img/@src').extract_first("")
            post_url = post_node.xpath('./@href').extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url":parse.urljoin(response.url,image_url)},callback=self.parse_detail)

        # 提取下一页并交给scrapy进行下载
        next_url = response.xpath("//*[@class='laypage_next']/@href").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse_list)

    def parse_detail(self, response):
        article_item = LvChaSoftItem()

        # 通过item loader加载item
        front_image_url = response.meta.get("front_image_url", "")  # 文章封面图
        item_loader = ArticleItemLoader(item=LvChaSoftItem(), response=response)
        item_loader.add_xpath("title", "//div[@id='soft_title']/text()")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_value("front_image_url", [front_image_url])
        item_loader.add_xpath("type", "//*[@id='main1k']/div[3]/a[3]/text()")
        item_loader.add_xpath("size", "//em[@id='ljdx']/text()")
        item_loader.add_xpath("update_time", "//*[@id='main1k']/div[4]/div[2]/div[2]/div[1]/p[6]/em/text()")
        item_loader.add_xpath("content", "//*[@class='rjjsbox']/p/text()")
        item_loader.add_xpath("tag", "//*[@class='fllist clearfix']/p[4]/em/text()")
        item_loader.add_xpath("fav_nums", "//*[@class='fllist clearfix']/p[5]/em/@class")
        item_loader.add_xpath("download_urls", "//*[@class='clearfix count_down']/dd/a[1]/@href")

        article_item = item_loader.load_item()
        yield article_item
