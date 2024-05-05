import itertools
from typing import Iterator

from django.core.management import BaseCommand
from playwright.sync_api import sync_playwright

from product.models import Product


class Command(BaseCommand):
    help = "crawling test"

    def handle(self, *args, **options):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto("https://kkst.kr/product/best_list_detail.html?cate_no=141")

            product_list = page.query_selector_all(
                "#best__product-list > li > article > div"
            )

            from django.utils import timezone

            product_infos = (
                Product(
                    thumb=thumb_content,
                    brand=brand,
                    name=name,
                    sale_price=sale_price,
                    price=price,
                    created_at=timezone.now(),
                )
                for thumb_content, brand, name, sale_price, price in self.generate_product_details(
                    product_list
                )
            )

            for chunks in self.get_chunks(product_infos, chunk_size=1000):
                print(next(chunks))
            browser.close()

    @classmethod
    def generate_product_details(cls, product_list):
        for product in product_list:
            thumb_url = product.query_selector(
                "div.item__thumb > a > img"
            ).get_attribute("src")

            if not thumb_url.startswith("https"):
                thumb_url = "https:" + thumb_url

            brand = product.query_selector("p.info__brand").inner_text()
            name = product.query_selector("h3.info__title").inner_text()
            sale_price = (
                product.query_selector("p.info__price > span.ec-sale-rate")
                .inner_text()
                .rstrip("%")
                if product.query_selector(
                    "p.info__price > span.ec-sale-rate"
                ).inner_text()
                else "0"
            )
            price = (
                product.query_selector("p.info__price > span:nth-of-type(2)")
                .inner_text()
                .strip("₩")
            )

            yield thumb_url, brand, name, sale_price, price

    @classmethod
    def get_chunks(cls, iterable: Iterator, chunk_size: int = 100) -> Iterator:
        iterator = iterable if hasattr(iterable, "__next__") else iter(iterable)
        for first in iterator:
            yield itertools.chain([first], itertools.islice(iterator, chunk_size - 1))
