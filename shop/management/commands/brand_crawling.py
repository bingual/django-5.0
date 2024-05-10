import urllib
from typing import Iterator, List
from urllib.parse import urlparse

from django.core.management import BaseCommand
from environ import environ
from playwright.sync_api import sync_playwright, Page, Locator
from tqdm import tqdm

from shop.models import Brand
from theme.utils import convert_file, get_chunks

env = environ.Env()
URL = env("CRAWLING_BRAND_URL")


class Command(BaseCommand):
    help = "브랜드 크롤링"

    def handle(self, *args, **options):

        if Brand.objects.count() != 0:
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
            page.goto(URL)

            self.scroll_to_the_end(page)

            brand_elem_list = page.locator("#brand__product-list > li").all()

            brand_instances = (
                Brand(logo_thumb=convert_file(logo_url), name=name)
                for logo_url, name in self.generate_brand_details(brand_elem_list)
            )

            for chunks in get_chunks(brand_instances, chunk_size=100):
                Brand.objects.bulk_create(chunks, ignore_conflicts=True)

            browser.close()

        print("크롤링 종료")

    @classmethod
    def scroll_to_the_end(cls, page: Page) -> None:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

        while load_more_button := page.locator(
            "#component__brand > div.brand__content > div.component__product-more-button > a"
        ).first:

            if load_more_button:
                load_more_button.click(delay=100)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

                class_attribute = load_more_button.get_attribute("class")
                if class_attribute and "displaynone" in class_attribute:
                    break

    @classmethod
    def generate_brand_details(cls, brand_list: List[Locator]) -> Iterator[str]:
        brand_count = len(brand_list)
        pbar = tqdm(brand_list, total=brand_count, desc="브랜드 세부정보 생성 중")
        for i, brand_elem in enumerate(pbar):
            logo_query = brand_elem.locator(
                "article > div > div > div.item__thumb > a > img"
            ).first
            logo_url = logo_query.get_attribute("src")
            logo_url = urllib.parse.urljoin("https:", logo_url)
            name = brand_elem.locator(
                "article > div > div > div.item__info > h3 > div > a > span > span"
            ).first.inner_text()

            pbar.set_postfix(
                brand=f"{i + 1}/{brand_count}",
                name=name,
            )
            yield logo_url, name
