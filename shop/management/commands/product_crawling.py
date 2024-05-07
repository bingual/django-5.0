import itertools
import os
import urllib
from typing import Iterator
from urllib.parse import urlparse
from urllib.request import urlopen

import environ
from django.core.files.base import ContentFile
from django.core.management import BaseCommand
from playwright.sync_api import sync_playwright
from tqdm import tqdm

from shop.models import Product

env = environ.Env()
url = env("CRAWLING_URL")

page_url_list = [
    f"{url}141",
    f"{url}142",
    f"{url}143",
    f"{url}144",
    f"{url}145",
    f"{url}146",
]
category_list = ["아우터", "상의", "하의", "신발", "악세사리", "그루밍"]


# TODO: 이 코드를 기반으로해서 비동기로 작성해보기
# TODO: 셀러리를 이용하여 더 효율적으로 비동기 코드 작성해보기
class Command(BaseCommand):
    help = "크롤링 테스트"

    def handle(self, *args, **options):

        if Product.objects.all().exists():
            user_input = input(
                "데이터가 이미 존재합니다. 그래도 실행하시겠습니까? (Y/N): "
            )
            if user_input.upper() != "Y":
                print("실행을 취소했습니다.")
                return

        with sync_playwright() as p:
            print("크롤링 시작")

            browser = p.chromium.launch()
            page = browser.new_page()

            for page_url, category_name in zip(page_url_list, category_list):
                page.goto(page_url)

                product_list = page.query_selector_all(
                    "#best__product-list > li > article > div"
                )

                product_infos = (
                    Product(
                        brand=brand,
                        category=category_name,
                        thumb=self.convert_file(thumb_url),
                        name=name,
                        sale_price=sale_price,
                        price=price,
                    )
                    for brand, thumb_url, name, sale_price, price in self.generate_product_details(
                        product_list, category_name
                    )
                )

                for chunks in self.get_chunks(product_infos, chunk_size=1000):
                    Product.objects.bulk_create(chunks, ignore_conflicts=True)

            browser.close()

        print("크롤링 종료")

    @classmethod
    def generate_product_details(cls, product_list, category_name):
        product_count = len(product_list)
        pbar = tqdm(product_list, total=product_count, desc="제품 세부정보 생성 중...")
        for i, product in enumerate(pbar):
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
                .replace(",", "")
                .strip("₩")
            )

            pbar.set_postfix(
                product=f"{i + 1}/{product_count}",
                brand=brand,
                category=category_name,
                name=name,
            )
            yield brand, thumb_url, name, sale_price, price

    @classmethod
    def get_chunks(cls, iterable: Iterator, chunk_size: int = 100) -> Iterator:
        iterator = iterable if hasattr(iterable, "__next__") else iter(iterable)
        for first in iterator:
            yield itertools.chain([first], itertools.islice(iterator, chunk_size - 1))

    @classmethod
    def convert_file(cls, url):
        response = urllib.request.urlopen(url)
        filename = os.path.basename(urlparse(url).path)
        image_file = ContentFile(content=response.read(), name=filename)
        return image_file
