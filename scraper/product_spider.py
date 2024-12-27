import scrapy
import hashlib
import json
from .publisher import RedisPublisher

class ProductsSpider(scrapy.Spider):
    name = "products"

    def __init__(self, limit=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.limit = int(limit)
        self.redis_publisher = RedisPublisher()

    def start_requests(self):
        base_url = "https://dentalstall.com/shop/page/"
        for page in range(1, self.limit + 1):
            yield scrapy.Request(f"{base_url}{page}", callback=self.parse)

    def parse(self, response):
        script_data = response.xpath('//script[@id="woocommerce-notification-js-extra"]/text()').get()
        if script_data:
            try:
                # Clean up the data: remove the JavaScript comment wrapping and semicolon
                json_data = script_data.strip().rstrip("/* ]]> */").strip()

                # Remove the 'var _woocommerce_notification_params = ' part
                json_data = json_data.split("=", 1)[-1].strip()
                json_data = json_data.rstrip(';').strip()

                # Parse JSON
                data = json.loads(json_data)
                for product in data.get("products", []):
                    title = product["title"]
                    product_hash = hashlib.sha256(title.encode()).hexdigest()
                    product_data = {
                        "title": title,
                        "url": product["url"],
                        "thumb": product["thumb"],
                        "hash": product_hash,
                    }
                    self.redis_publisher.publish_event("product_updates", product_data)
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse JSON: {e}")