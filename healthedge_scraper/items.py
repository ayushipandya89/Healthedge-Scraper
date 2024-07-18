import scrapy


class HealthedgeItem(scrapy.Item):
    category = scrapy.Field()
    sub_category = scrapy.Field()
    product_name = scrapy.Field()
    product_image = scrapy.Field()
    product_description = scrapy.Field()
