# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class RightmoveScrapperItem(scrapy.Item):
    # define the fields for your item here like:
    address = scrapy.Field()
    price = scrapy.Field()
    property_type = scrapy.Field()
    property_link =  scrapy.Field()
    no_of_rooms = scrapy.Field()
    no_of_bathrooms =  scrapy.Field()
    agent_firm = scrapy.Field()
    firm_contact = scrapy.Field()
    property_id = scrapy.Field()

class PropertyImageItem(scrapy.Item):
    property_id = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()

