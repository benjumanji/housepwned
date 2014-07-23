# -*- coding: utf-8 -*-

# Scrapy settings for housepwned project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'housepwned'

SPIDER_MODULES = ['housepwned.spiders']
NEWSPIDER_MODULE = 'housepwned.spiders'
FEED_FORMAT = 'jsonlines'
FEED_URI = 'file:///tmp/houseco.json'
DOWNLOAD_DELAY = 2

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'housepwned (+http://www.yourdomain.com)'
