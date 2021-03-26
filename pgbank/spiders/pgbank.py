import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from pgbank.items import Article


class PgbankSpider(scrapy.Spider):
    name = 'pgbank'
    allowed_domains = ['pgbank.com', 'pgbank.q4ir.com']
    start_urls = ['https://www.pgbank.com/who-we-are/news']

    def parse(self, response):
        archive = 'https://www.pgbank.com/news-archive'
        yield response.follow(archive, self.parse)

        links = response.xpath('//a[text()="Read more"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2/span/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="module_date-time"]/span/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="module_container module_container--content"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
