# -*- coding: utf-8 -*-
__author__ = 'luhui.liu'

from scrapy.cmdline import execute
import sys
import os



#获取相对路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy","crawl","lcsoft"])
