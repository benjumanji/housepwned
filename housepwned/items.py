# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PostcodePriceItem(scrapy.Item):
    """
    Item to hold the sale for a given postcode
    """
    postcode = scrapy.Field()
    date = scrapy.Field()
    num_sold = scrapy.Field()
    avg_price = scrapy.Field()
    med_price = scrapy.Field()
