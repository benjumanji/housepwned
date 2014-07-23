# -*- coding: utf-8 -*-
# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

import scrapy
from urlparse import parse_qs, urlparse

from housepwned.items import PriceItem, SummaryItem


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

    row_xpath = '//div[@class="homeco_pr_content"]/div[2]/table/tr[%s]/td/text()' % i
    row_data  = response.xpath(row_xpath).extract()

    # for reasons unknown if they sold no proerties of a given type, the number
    # isn't listed as zero, it's just not there. In these instances the unpack
    # will fail, so we just return a row of zeros, which is what should have
    # been there in the first place
    if not len(row_data) == 4:
        return PriceItem(date, location, row_data[0], 0, 0, 0)

    property_type, num, avg, med = row_data

    return PriceItem(date, location, property_type, parse_int(num),
                     parse_int(avg), parse_int(med))


def extract_summary(date, location, response):
    """
    Extract the headline data from the page.

    This is just the average price across all the properties along with a count
    of properties sold.
    """

    summary_xpath = '//div[@class="homeco_pr_content"]/div[1]/table/tr/td[2]/text()'
    num_list = response.xpath(summary_xpath).extract()
    sold = parse_int(num_list[0])
    avg_price = parse_int(num_list[1])

    return SummaryItem(date, location, sold, avg_price)


class HomeCoSpider(scrapy.Spider):
    name = "homeco"
    allowed_domains = ["home.co.uk"]
    start_urls = [
        "http://www.home.co.uk/guides/sold_house_prices.htm?location=se6&month=01&year=2002",
        "http://www.home.co.uk/guides/sold_house_prices.htm?location=se13&month=01&year=2002",
        "http://www.home.co.uk/guides/sold_house_prices.htm?location=elephant_castle&month=01&year=2002"
    ]

    def parse(self, response):
        date, location = extract_url_info(response.url)

        yield extract_summary(date, location, response)

        for i in range(2,5):
            yield extract_row(date, location, response, i)

        link = get_next_link(response)
        if link:
            yield scrapy.Request(link)
