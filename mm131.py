#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import urllib
import os
from sys import stdout as sOut

#图片保存路径.
images_path="images/"


#进度百分比.
def progress(a, b, c): 
    '''回调函数
    @a: 已经下载的数据块
    @b: 数据块的大小
    @c: 远程文件的大小
    ''' 
    per = 100.0 * a * b / c 
    if per > 100: 
        per = 100 
    sOut.write("Downloading %.2f%% \r" % (per))
    sOut.flush()

class Mm131Spider(scrapy.Spider):
    name = "mm131"
    allowed_domains = ["mm131.com"]
    start_urls = (
	'http://www.mm131.com/xinggan/',
	'http://www.mm131.com/xiaohua/',
	'http://www.mm131.com/chemo/',
	'http://www.mm131.com/qingchun/',
	'http://www.mm131.com/qipao/',
	'http://www.mm131.com/mingxing/',
	
    )

    def __init__(self):
	if not os.access(images_path, os.F_OK):
		os.mkdir(images_path)

    def parse(self, response):
    	sel = scrapy.Selector(response)

	#提取当前分页有效链接.
	link = response.xpath('//dl[@class="list-left public-box"]').xpath('//a[@target="_blank"]/@href').extract()
#	item['title'] = response.xpath('//dl[@class="list-left public-box"]').xpath('//a[@target="_blank"]/img/@alt').extract()
	for url in link:
		if ".html" in url:
			yield scrapy.Request(url, callback=self.parse)
	title = response.xpath('//div[@class="content-pic"]/a/img').xpath('@alt').extract()
	link = response.xpath('//div[@class="content-pic"]/a/img').xpath('@src').extract()

	#开始分析下载.
	try:
		title1 = title[0].split('(')
		picname = title1[0]
		picdir = images_path + picname
		if not os.path.exists(picdir):
			os.makedirs(picdir)
		savename =(picdir + "/" + title[0] + ".jpg")
	#如果有重复的就跳过不下载.
		if not os.path.exists(savename):
			self.logger.info(title[0] + " ==> Not yet download,will be start to get it.")
			urllib.urlretrieve(link[0],savename, progress)
		else:
			self.logger.info(title[0] + " ==> Already download,Skip...")
	except IndexError:
		pass
	except UnboundLocalError:
		pass
	

	#从分类页获取其他分页.	
	urls = sel.xpath('/html/body/div/dl/dd/a/@href').extract()
	xilie = response.xpath('//div/dl/dt/a[2]/@href').extract()

	#分析页面,某些分页不带主站地址的加上主站url,组合成新的链接.
	for pg_list in urls:
		if "mm131" not in pg_list:
			pg_list = xilie[0] + pg_list
		yield scrapy.Request(pg_list, callback=self.parse)

	#从单个图集列表获取其他分页.
	tujis = response.xpath('//div[@class="content-page"]/a/@href').extract()
	tuji_xilie = response.xpath('//div[@class="place"]/a[2]/@href').extract()
	for tuji_list in tujis:
		if "mm131" not in tuji_list:
			tuji_list = tuji_xilie[0] + tuji_list
		yield scrapy.Request(tuji_list, callback=self.parse)

