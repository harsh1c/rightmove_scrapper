import re

import scrapy
from rightmove_scrapper.items import RightmoveScrapperItem


class PropertyspiderSpider(scrapy.Spider):
    name = "propertyspider"

    custom_settings = {
        'FEED_EXPORT_FIELDS': [
            'property_id',
            'address',
            'price',
            'property_link',
            'property_type',
            'no_of_rooms',
            'no_of_bathrooms',
            'agent_firm',
            'firm_contact',
        ],
        'FEEDS': {
            'property_details.csv': {
                'format': 'csv',
                'overwrite': True
            }
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seen_links = set()

    def start_requests(self):

        yield scrapy.Request(
            url="https://www.rightmove.co.uk/property-for-sale/find.html?sortType=2&viewType=LIST&channel=BUY&index=0&radius=0.0&locationIdentifier=USERDEFINEDAREA%5E%7B%22polylines%22%3A%22kobnI%7EgmQz%7BX%7EzKatGqqnBs%7Ch%40pknAxtW%7EhR%22%7D&transactionType=BUY&displayLocationIdentifier=undefined",
            meta={
                "playwright": True,
                "playwright_include_page": True,
            }
        )

    async def safe_inner_text(self, el):
        return (await el.inner_text()).strip() if el else None

    async def safe_get_attribute(self, el, attr):
        return (await el.get_attribute(attr)).strip() if el else None

    async def parse(self, response):
        page = response.meta["playwright_page"]
        no_of_pages_selector = (await page.query_selector("div.dsrm_dropdown.Pagination_pageSelect__dUffQ + span"))
        no_of_pages = str(await no_of_pages_selector.inner_text()).replace("of", "")

        try:
            await page.wait_for_selector("button#onetrust-reject-all-handler", timeout=4000)
            cookies_button = await page.query_selector("button#onetrust-reject-all-handler")
            if cookies_button:
                await cookies_button.click()
        except:
            pass
        page_count = 1

        for _ in range(int(no_of_pages)):
            try:
                await page.wait_for_selector("button#onetrust-reject-all-handler", timeout=2000)
                cookies_button = await page.query_selector("button#onetrust-reject-all-handler")
                if cookies_button:
                    await cookies_button.click()
            except:
                pass
            await page.wait_for_selector('div.PropertyCard_propertyCardContainerWrapper__mcK1Z')

            properties = await page.query_selector_all('div.PropertyCard_propertyCardContainerWrapper__mcK1Z')

            for each_property in properties:
                address = await each_property.query_selector("address.PropertyAddress_address__LYRPq")
                price = await each_property.query_selector("div.PropertyPrice_price__VL65t")
                property_type = await each_property.query_selector("span.PropertyInformation_propertyType__u8e76")
                property_link = response.urljoin(await self.safe_get_attribute(await each_property.query_selector("a.PropertyPrice_priceLink__b24b5"), "href"))
                no_of_rooms = await each_property.query_selector("span.PropertyInformation_bedroomsCount___2b5R")
                no_of_bathrooms = await each_property.query_selector("div.PropertyInformation_bathContainer__ut8VY span")
                agent_firm = await each_property.query_selector("div.PropertyCard_propertyCardEstateAgent__DWq0a img")
                firm_contact = await each_property.query_selector("a.CallAgent_phoneLinkDesktop__gFFNQ span:nth-child(1)")


                if property_link in self.seen_links:
                    continue
                self.seen_links.add(property_link)

                detail_item = RightmoveScrapperItem()

                detail_item["address"] = await self.safe_inner_text(address)
                detail_item['price'] = await self.safe_inner_text(price)
                detail_item['property_link'] = property_link
                detail_item['property_type'] = await self.safe_inner_text(property_type)
                detail_item['no_of_rooms'] = await self.safe_inner_text(no_of_rooms)
                detail_item['no_of_bathrooms'] = await self.safe_inner_text(no_of_bathrooms)
                detail_item['agent_firm'] = str(await self.safe_get_attribute(agent_firm, 'alt')).replace("Logo", "")
                detail_item['firm_contact'] = await self.safe_inner_text(firm_contact)
                detail_item['property_id'] =  re.search("\/(\d*)#\/", property_link).group(1)

                yield detail_item
            next_button = (await page.query_selector_all("button.dsrm_button.dsrm_medium.dsrm_tertiary.dsrm_core.Pagination_button__5gDab"))[1]
            if page_count < int(no_of_pages):
                await next_button.click()
            page_count += 1

        await page.close()


