# -*- coding: utf-8 -*-
# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

import scrapy
from urlparse import parse_qs, urlparse

from housepwned.items import PriceItem


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


def extract_url_info(url):
    """
    Get the date and location from the url.

    For some reason the link to the next month doubles up on all the query
    params so you have year / month appearing twice. We want the second
    occurence, if there is one (all initial links have the param once).

    Returns a tuple of date and location, date format: YYYY-MM.
    """
    qs = urlparse(url).query
    params = parse_qs(qs)

    year = params['year'][1] if len(params['year']) == 2 else params['year'][0]
    month = params['month'][1] if len(params['month']) == 2 else params['month'][0]
    return ('%s-%s' % (year, month), params['location'][0])


def extract_row(date, location, response, i):
    """
    Extract one row of data from the price table.

    This is represents price data relating to a type of property for a given
    post code and date.
    """

    property_xpath = '//div[@class="homeco_pr_content"]/div[2]/table/tr[%s]/td[1]/text()' % i
    num_xpath = '//div[@class="homeco_pr_content"]/div[2]/table/tr[%s]/td[2]/text()' % i
    avg_xpath = '//div[@class="homeco_pr_content"]/div[2]/table/tr[%s]/td[3]/text()' % i
    med_xpath = '//div[@class="homeco_pr_content"]/div[2]/table/tr[%s]/td[4]/text()' % i

    property_type = response.xpath(property_xpath)[0].extract()
    num = int_from_xpath(response, num_xpath)
    avg = int_from_xpath(response, avg_xpath)
    med = int_from_xpath(response, med_xpath)

    return PriceItem(date, location, property_type, num, avg, med)


class HomeCoSpider(scrapy.Spider):
    name = "homeco"
    allowed_domains = ["home.co.uk"]
    start_urls = [
        "http://www.home.co.uk/guides/sold_house_prices.htm?location=E14&month=01&year=2002"
    ]

    def parse(self, response):
        date, location = extract_url_info(response.url)

        for i in range(2,5):
            yield extract_row(date, location, response, i)

        link = get_next_link(response)
        if link:
            yield scrapy.Request(link)
