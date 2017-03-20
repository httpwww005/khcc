# -*- coding: utf-8 -*-
import md5
import urlparse
import scrapy
import re
import os,binascii

class Product(scrapy.Item):
    address = scrapy.Field()
    location = scrapy.Field()
    count = scrapy.Field()
    url = scrapy.Field()

class VisitcountSpider(scrapy.Spider):
    name = "visitcount"
	
    allowed_domains = ["http://khvillages.khcc.gov.tw"]
    url_base = "http://khvillages.khcc.gov.tw/"

    def start_requests(self):
	urls = [
            'http://khvillages.khcc.gov.tw/home02.aspx?ID=$4001&IDK=2&AP=$4001_SK--1^$4001_SK2--1^$4001_PN-1^$4001_HISTORY-0',
	    'http://khvillages.khcc.gov.tw/home02.aspx?ID=$4001&IDK=2&AP=$4001_SK--1^$4001_SK2--1^$4001_PN-2^$4001_HISTORY-0',
            'http://khvillages.khcc.gov.tw/home02.aspx?ID=$4011&IDK=2&AP=$4011_SK-^$4011_SK2--1^$4011_PN-1^$4011_HISTORY-0',
            'http://khvillages.khcc.gov.tw/home02.aspx?ID=$4011&IDK=2&AP=$4011_SK-^$4011_SK2--1^$4011_PN-2^$4011_HISTORY-0'
	]

	for url in urls:
	    yield scrapy.Request(url=url, callback=self.parse_url, dont_filter=True)


    def parse_url(self, response):
        #filename = binascii.b2a_hex(os.urandom(8))
        #with open(filename, "w") as f:
        #    f.write(response.body)

        subject = response.xpath("//meta[@name='DC.Subject']/@content")[0].extract()
        self.logger.debug('subject: %s' % subject)

        if u"建物簡介" in subject:
            self.logger.debug("x")
            ax = response.xpath("//a")
            for a in ax:
                try:
                    href = a.xpath("./@href")[0].extract() or ""
                    text = a.xpath("./text()")[0].extract() or ""
                except:
                    pass

                if (("AP=$4011_HISTORY-0" in href) or ("AP=$4001_HISTORY-0" in href)) \
                and ((u"全民修屋" in text) or (u"建業新村" in text)):
                    url = urlparse.urljoin(self.url_base, href)
                    self.logger.debug('url: %s' % url)
                    yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)


    def parse(self, response):
        location_1 = response.xpath("//meta[@name='DC.Title']/@content")[0].extract()

        if u"左營" in location_1:
            location = u"左營"
        else:
            location = u"鳳山"

        self.logger.debug('location: %s' % location)

        address_1 = response.xpath("//meta[@name='DC.Subject']/@content")[0].extract() 
        address = re.match(ur".*村(.*)$",address_1).group(1)
        self.logger.debug('address: %s' % address)

        count_1 = response.xpath("//span[@style='color:#a4a4a4']/text()")[0].extract()
        count = re.match(ur".*已有(.*)人瀏覽.*$",count_1).group(1)
        self.logger.debug('count: %s' % count)

        yield {'location':location,
                'address':address,
                'count':count}
