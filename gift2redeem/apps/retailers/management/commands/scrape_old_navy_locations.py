from django.core.management.base import BaseCommand, CommandError
from gift2redeem.apps.retailers.models import *

import mechanicalsoup, re, json


class Command(BaseCommand):
    help = 'Loads locations for Old Navy'

    def handle(self, *args, **options):
        RetailerLocation.objects.filter(retailer=Retailer.objects.get(name="Old Navy")).delete()

        url_prefix = "http://www.oldnavy.com"
        browser = mechanicalsoup.Browser()
        link_list = browser.get(url_prefix + "/products/store-locations.jsp")
        links = link_list.soup.select("li a")

        for link in links:
            href = link["href"]
            if href.find("products") > 0:
                location_page = browser.get(url_prefix + href)
                script_tags = location_page.soup.select("script")
                for script_tag in script_tags:
                    if 1 == 1:
                        script = script_tag.text.strip().replace("\n", "").replace("\r", "").replace("\t", "")
                        if script.find("storeLocationList") > 0:
                            json_match = re.search("^.*storeLocationList: \[{(.*)}\].*$", script)
                            json_str = "{" + json_match.group(1) + "}"
                            json_str = re.sub(r"{\s*(\w)", r'{"\1', json_str)
                            json_str = re.sub(r",\s*(\w)", r',"\1', json_str)
                            json_str = re.sub(r"(\w):", r'\1":', json_str)
                            json_str = re.sub(r'"storeHours":.*\[.*\],.*"storeSpecialHours"', '"storeSpecialHours"',
                                              json_str)
                            json_str = re.sub(r'"storeSpecialHours":.*\[.*\],.*"storeAttributes"', '"storeAttributes"',
                                              json_str)

                            try:
                                store_obj = json.loads(json_str)
                                retailer_location = RetailerLocation()
                                retailer_location.is_active = True
                                retailer_location.retailer = Retailer.objects.get(name="Old Navy")
                                retailer_location.lat = store_obj["latitude"]
                                retailer_location.lng = store_obj["longitude"]
                                retailer_location.address = store_obj["storeAddress"]["addressLine1"]
                                retailer_location.address2 = store_obj["storeAddress"]["addressLine2"]
                                retailer_location.city = store_obj["storeAddress"]["cityName"]
                                retailer_location.state = store_obj["storeAddress"]["stateProvinceCode"]
                                retailer_location.postal_code = store_obj["storeAddress"]["postalCode"]
                                retailer_location.save()
                            except:
                                pass