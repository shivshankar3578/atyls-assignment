from scrapy.crawler import CrawlerProcess
from .product_spider import ProductsSpider


def run_scraper(limit=1):
    settings = {
        "BOT_NAME": "scraper",
        "LOG_LEVEL": "INFO",
        "FEEDS": {
            "products.json": {"format": "json", "overwrite": True},  # Output to JSON
        },
    }

    process = CrawlerProcess(settings=settings)
    process.crawl(ProductsSpider, limit=limit)
    process.start()


if __name__ == "__main__":
    run_scraper(limit=1)