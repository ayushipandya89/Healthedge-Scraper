import scrapy
from healthedge_scraper.items import HealthedgeItem


class HealthEdgeSpider(scrapy.Spider):
    name = 'healthedge'
    allowed_domains = ['health-edge.co.uk']
    start_urls = ['https://health-edge.co.uk']

    custom_settings = {
        'FEED_FORMAT': 'json',
        'FEED_URI': 'output.json',
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 3
    }

    def parse(self, response):
        category_links = response.xpath(
            "//div[contains(@class, 'site-footer__item')][div/p[text()='Consumables']]//div[contains(@class, "
            "'site-footer__rte')]//a/@href").getall()
        for link in category_links:
            yield scrapy.Request(response.urljoin(link), callback=self.parse_category_page)

    def parse_category_page(self, response):
        category_name = response.xpath("//h2[@class='h1 mega-title mega-title--large']/text()").get()
        subcategories_link = response.xpath("//div[@class='custom-content']//a/@href").getall()
        for link in subcategories_link:
            yield scrapy.Request(response.urljoin(link), callback=self.parse_subcategory_page,
                                 meta={'category_name': category_name}, dont_filter=True)

    def parse_subcategory_page(self, response):
        category_name = response.meta['category_name']
        subcategory_name = response.xpath("//div[@class='section-header text-center']/h1/text()[2]").get()
        subcategory_name_cleaned = subcategory_name.strip() if subcategory_name else None

        products = response.xpath("//div[@id='Collection']//li")

        for product in products:
            item = HealthedgeItem()
            item['category'] = category_name
            item['sub_category'] = subcategory_name_cleaned
            img_src = product.xpath(".//img/@src").get()
            if not img_src:
                continue
            item['product_image'] = response.urljoin(img_src) if img_src else None
            product_url = product.xpath(".//a/@href").get()
            yield scrapy.Request(response.urljoin(product_url), callback=self.parse_product_detail, meta={'item': item})
        if next_page_link := response.xpath(
                "//ul[@class='list--inline pagination']/li/a[@class='btn btn--tertiary btn--narrow' and contains(span["
                "@class='icon__fallback-text'], 'Next page')]/@href").get():
            yield scrapy.Request(url=response.urljoin(next_page_link), callback=self.parse_subcategory_page,
                                 meta={'category_name': category_name})

    def parse_product_detail(self, response):
        item = response.meta['item']
        product_name = response.xpath("//h1[@class='product-single__title']/text()").get()
        description = response.xpath('//div[@class="product-single__description rte"]//text()').getall()
        cleaned_description = ' '.join(description).strip() if description else None
        cleaned_description = ' '.join(cleaned_description.split())
        item['product_name'] = product_name
        item['product_description'] = cleaned_description
        yield item
