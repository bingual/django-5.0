import asyncio
import urllib
import environ
import nest_asyncio

from typing import Union, List, Tuple
from urllib.parse import urlparse

from asgiref.sync import sync_to_async
from colorama import Fore
from django.core.management import BaseCommand
from django.db import transaction
from playwright.async_api import async_playwright, Page, Locator
from tqdm import tqdm

from shop.models import Brand, BrandThumbnail
from theme.errors import ThumbnailFetchError
from theme.utils import convert_file, delete_media_directory

nest_asyncio.apply()
env = environ.Env()
URL = env("CRAWLING_BRAND_URL")


class Command(BaseCommand):
    help = "브랜드 크롤링"

    def handle(self, *args, **options):

        brand_count = Brand.objects.count()
        if brand_count != 0:
            user_input = input(
                "데이터가 이미 존재합니다. 초기화 하고 실행하시겠습니까? (Y/N): "
            )
            if user_input.upper() != "Y":
                print("실행을 취소했습니다.")
                return

        if brand_count != 0:
            models_to_delete = [Brand(), BrandThumbnail()]
            for model_instance in tqdm(
                models_to_delete, desc="브랜드 미디어 파일 초기화중"
            ):
                delete_media_directory(model_instance)

            for brand in tqdm(Brand.objects.all(), desc="브랜드 인스턴스 초기화중"):
                brand.delete()

        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        asyncio.run(self.main())

    @classmethod
    async def main(cls):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(URL)

            await cls.click_on_load_more_button(page)
            await cls.scroll_to_the_top(page)

            try:
                brand_instances, brand_thumb_instances = await cls.create_brand_details(
                    page
                )
                await sync_to_async(cls.save_to_db)(
                    brand_instances, brand_thumb_instances
                )

            except ThumbnailFetchError as e:
                print(f"{Fore.RED}ERROR: {e.message}\nFAILED: {e.image_url}")

            await browser.close()

    @classmethod
    async def click_on_load_more_button(cls, page: Page) -> None:
        while load_more_button := page.locator(
            "#component__brand > div.brand__content > div.component__product-more-button > a"
        ).first:
            if load_more_button:
                await load_more_button.click(delay=500)

                if not await load_more_button.is_visible():
                    break

    @classmethod
    async def scroll_to_the_top(cls, page: Page) -> None:
        body_locator = page.locator("body").first
        scroll_top = await body_locator.evaluate(
            "() => document.documentElement.scrollTop"
        )

        if scroll_top > 0:
            await body_locator.evaluate("() => window.scrollTo(0, 0)")

        await page.wait_for_function("() => document.documentElement.scrollTop === 0")

    @classmethod
    async def create_brand_details(
        cls, page: Page
    ) -> Tuple[List[Brand], List[BrandThumbnail]]:
        brand_elem_list = await page.locator("#brand__product-list > li").all()
        brand_count = len(brand_elem_list)
        pbar = tqdm(brand_elem_list, total=brand_count, desc="브랜드 세부정보 생성 중")

        brand_instance_list = []
        brand_thumb_instance_list = []

        for i, brand_elem in enumerate(pbar):
            logo_url = await brand_elem.locator(
                "article > div > div > div.item__thumb > a > img"
            ).first.get_attribute("src")

            if logo_url == "/_hashcorp/theme/assets/images/preload.png":
                raise ThumbnailFetchError(
                    message="썸네일을 가져오지 못했습니다.", image_url=logo_url
                )

            logo_url = urllib.parse.urljoin("https:", logo_url)

            name = await brand_elem.locator(
                "article > div > div > div.item__info > h3 > div > a > span > span"
            ).first.inner_text()

            brand_instance = Brand(logo_thumb=convert_file(logo_url), name=name)
            brand_instance_list.append(brand_instance)

            brand_thumb_instance_list.extend(
                await cls.create_brand_thumb_details(page, brand_elem, brand_instance)
            )

            pbar.set_postfix(
                brand=f"{i + 1}/{brand_count}",
                name=name,
            )

        return brand_instance_list, brand_thumb_instance_list

    @classmethod
    async def create_brand_thumb_details(
        cls, page: Page, brand_elem: Locator, brand_instance: Brand
    ) -> Union[List[BrandThumbnail], List]:
        brand_thumb_instance_list = []

        swiper_elem = brand_elem.locator("div.brand-list__swiper").first

        if await swiper_elem.count() == 0:
            return []

        swiper_box = await swiper_elem.bounding_box()
        swiper_pos_x = swiper_box["x"] + swiper_box["width"] / 2
        swiper_pos_y = swiper_box["y"] + swiper_box["height"] / 2

        for _ in range(20):
            await page.mouse.move(swiper_pos_x, swiper_pos_y)
            await page.mouse.down()
            await page.mouse.move(swiper_pos_x + 100, swiper_pos_y)
            await page.mouse.move(swiper_pos_x, swiper_pos_y)
            await page.mouse.up()

        thumb_elem_list = await swiper_elem.locator("ul > li").all()

        for thumb_elem in thumb_elem_list:
            thumb_url = await thumb_elem.locator(
                "article > div > div.item-wrap > div.item__thumb > a > img"
            ).first.get_attribute("src")

            if thumb_url == "/_hashcorp/theme/assets/images/preload.png":
                raise ThumbnailFetchError(
                    message="썸네일을 가져오지 못했습니다.",
                    image_url=thumb_url,
                )

            thumb_url = urllib.parse.urljoin("https:", thumb_url)
            brand_thumb_instance_list.append(
                BrandThumbnail(brand=brand_instance, thumb=convert_file(thumb_url))
            )

        await page.mouse.wheel(0, 300)

        return brand_thumb_instance_list

    @classmethod
    def save_to_db(
        cls, brand_instances: List[Brand], brand_thumb_instances: List[BrandThumbnail]
    ):
        with transaction.atomic():
            Brand.objects.bulk_create(
                brand_instances,
            )
            BrandThumbnail.objects.bulk_create(
                brand_thumb_instances,
            )
