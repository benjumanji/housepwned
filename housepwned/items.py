# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PriceItem(scrapy.Item):
    """
    Item to hold the sale for a given date, location and property type
    """
    location = scrapy.Field()
    date = scrapy.Field()
    property_type = scrapy.Field()
    num_sold = scrapy.Field()
    avg_price = scrapy.Field()
    med_price = scrapy.Field()

    def __init__(self, date, location, property_type,
                 num_sold, avg_price, med_price):

        super(scrapy.Item, self).__init__()

        self['date'] = date
        self['location'] = location
        self['property_type'] = property_type
        self['num_sold'] = num_sold
        self['avg_price'] = avg_price
        self['med_price'] = med_price
