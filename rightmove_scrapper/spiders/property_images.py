from rightmove_scrapper.items import PropertyImageItem
import scrapy
import pandas as pd


class PropertyImagesSpider(scrapy.Spider):
    name = "property_images"

    custom_settings = {
        'FEED_EXPORT_FIELDS': ['property_id', 'image_urls'],
        'FEEDS': {
            'property_images.csv': {
                'format': 'csv',
                'overwrite': True
            }
        },
    }

    def start_requests(self):
        df = pd.read_csv('property_details.csv')
        prop_ids = df['property_id']
        for prop_id in prop_ids:
            yield scrapy.Request(
                url=f"https://www.rightmove.co.uk/properties/{prop_id}#/media?channel=RES_BUY",
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "property_id": prop_id,
                }

            )


    async def parse(self, response):
        page = response.meta["playwright_page"]
        property_id = response.meta["property_id"]

        try:
            await page.wait_for_selector("button#onetrust-reject-all-handler", timeout=4000)
            cookies_button = await page.query_selector("button#onetrust-reject-all-handler")
            if cookies_button:
                await cookies_button.click()
        except:
            pass

        urls_selector = await page.query_selector_all("div._25ZIhQnejkH18WEcfF8FCP img")
        img_urls = []

        for url in urls_selector:
            src = await url.get_attribute('src')
            if src:
                img_urls.append(src)

        image_item = PropertyImageItem()
        image_item['property_id'] = property_id
        image_item['image_urls'] = img_urls

        yield image_item

        await page.close()


