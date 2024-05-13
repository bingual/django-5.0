import urllib
from typing import List, Tuple, Dict
from urllib.parse import urlparse

import environ
from django.core.management import BaseCommand
from django.db import transaction
from playwright.sync_api import sync_playwright, Locator
from tqdm import tqdm

from shop.models import Product, Category, Brand
from theme.utils import convert_file

env = environ.Env()
URL = env("CRAWLING_PRODUCT_URL")

PAGE_URL_LIST = [
    f"{URL}141",
    f"{URL}142",
    f"{URL}143",
    f"{URL}144",
    f"{URL}145",
    f"{URL}146",
]
CATEGORY_LIST = ["아우터", "상의", "하의", "신발", "악세사리", "그루밍"]


class Command(BaseCommand):
    help = "크롤링 테스트"

    def handle(self, *args, **options):

        if Brand.objects.count() < 31:
            print("브랜드 크롤링을 먼저 실행해야합니다.")
            return

        if Product.objects.count() != 0:
            user_input = input(
                "데이터가 이미 존재합니다. 그래도 실행하시겠습니까? (Y/N): "
            )
            if user_input.upper() != "Y":
                print("실행을 취소했습니다.")
                return

        if Category.objects.count() <= 0:
            self.create_categories(CATEGORY_LIST)

        with sync_playwright() as p:
            print("크롤링 시작")

            browser = p.chromium.launch()
            page = browser.new_page()

            for page_url, category_name in zip(PAGE_URL_LIST, CATEGORY_LIST):
                page.goto(page_url)
                page.wait_for_timeout(
                    1000
                )  # TODO: swiper 효과때매 뒤늦게 요소가 로드. 최소 500ms 소요되기에 1000ms대기. 더 좋은 대안이 있으면 사용

                product_elem_list = page.locator(
                    "#best__product-list > li > article > div"
                ).all()

                product_instances = self.create_product_details(
                    product_elem_list, category_name
                )

                with transaction.atomic():
                    Product.objects.bulk_create(
                        product_instances, ignore_conflicts=True
                    )

            browser.close()

        print("크롤링 종료")

    @classmethod
    def create_categories(cls, category_list: List[str]) -> None:
        category_instances = [
            Category(name=name)
            for name in tqdm(category_list, desc="카테고리 세부정보 생성 중")
        ]
        Category.objects.bulk_create(category_instances, ignore_conflicts=True)

    @classmethod
    def create_cache_queries(cls) -> Tuple[Dict, Dict]:
        brand_cache = {brand.name: brand for brand in Brand.objects.all()}
        category_cache = {
            category.name: category for category in Category.objects.all()
        }
        return brand_cache, category_cache

    @classmethod
    def create_product_details(
        cls, product_elem_list: List[Locator], category_name: str
    ) -> List[Product]:
        product_count = len(product_elem_list)
        pbar = tqdm(
            product_elem_list, total=product_count, desc="제품 세부정보 생성 중"
        )

        brand_cache, category_cache = cls.create_cache_queries()

        product_instance_list = []

        for i, product_elem in enumerate(pbar):
            thumb_url = product_elem.locator(
                "div.item__thumb > a > img"
            ).first.get_attribute("src")
            thumb_url = urllib.parse.urljoin("https:", thumb_url)

            brand = product_elem.locator("p.info__brand").first.inner_text()
            name = product_elem.locator("h3.info__title").first.inner_text()
            price = (
                product_elem.locator("p.info__price > span:nth-of-type(2)")
                .first.inner_text()
                .replace(",", "")
                .strip("₩")
            )
            sale_price = (
                product_elem.locator("p.info__price > span.ec-sale-rate")
                .first.inner_text()
                .rstrip("%")
                if product_elem.locator(
                    "p.info__price > span.ec-sale-rate"
                ).first.inner_text()
                else "0"
            )

            product_instance = Product(
                brand=brand_cache[brand],
                category=category_cache[category_name],
                thumb=convert_file(thumb_url),
                name=name,
                price=price,
                sale_price=sale_price,
            )

            product_instance_list.append(product_instance)

            pbar.set_postfix(
                product=f"{i + 1}/{product_count}",
                brand=brand,
                category=category_name,
                name=name,
            )

        return product_instance_list
