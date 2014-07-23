# -*- coding: utf-8 -*-
# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

import scrapy
from urlparse import parse_qs, urlparse

from housepwned.items import PostcodePriceItem


def parse_int(text):
    """
    Parse an int from a string, stripping £ and ,

    Note this returns 0 as a defult if text cannot be coerced to an int
    """
    stripped = text.replace(u"\xa3", "").replace(u",", "").strip()
    try:
        return int(stripped)
    except ValueError:
        return 0

def extract_int(num_list):
    """Extract an int from the SelectList"""
    if not len(num_list) == 1:
        return 0

    return parse_int(num_list[0])

def int_from_xpath(response, xpath):
    """
    Extract a single int from an xpath text, given a response
    """
    sellist = response.xpath(xpath).extract()
    return extract_int(sellist)

def get_next_link(response):
    xpath = '//div[@class="homeco_pr_content"]/div[4]/form/table/tr[1]/td[4]/table/tr[1]/td[1]/a/@href'
    linklist = response.xpath(xpath).extract()

    if not linklist:
        return None

    return linklist[0]

def extract_date(url):
    """
    Get the date from the url
    
    For some reason the link to the next month doubles up on all the query
    params so you have year / month appearing twice. We want the second
    occurence, if there is one (all initial links have the param once).

    Returns the date as a string YYYY-MM
    """
    qs = urlparse(url).query
    params = parse_qs(qs)

    year = params['year'][1] if len(params['year']) == 2 else params['year'][0]
    month = params['month'][1] if len(params['month']) == 2 else params['month'][0]
    return '%s-%s' % (year, month)


class HomeCoSpider(scrapy.Spider):
    name = "homeco"
    allowed_domains = ["home.co.uk"]
    start_urls = [
        "http://www.home.co.uk/guides/sold_house_prices.htm?location=E14&month=01&year=2002"
    ]

    num_sel = '//div[@class="homeco_pr_content"]/div[2]/table/tr[2]/td[2]/text()'
    avg_sel = '//div[@class="homeco_pr_content"]/div[2]/table/tr[2]/td[3]/text()'
    med_sel = '//div[@class="homeco_pr_content"]/div[2]/table/tr[2]/td[4]/text()'

    def parse(self, response):
        num_sold = int_from_xpath(response, self.num_sel)
        avg_price = int_from_xpath(response, self.avg_sel)
        med_price = int_from_xpath(response, self.med_sel)

        date = extract_date(response.url)

        item = PostcodePriceItem()
        item['postcode'] = "E14"
        item['date'] = date
        item['num_sold'] = num_sold
        item['avg_price'] = avg_price
        item['med_price'] = med_price

        yield item

        link = get_next_link(response)

        if link:
            yield scrapy.Request(link)

