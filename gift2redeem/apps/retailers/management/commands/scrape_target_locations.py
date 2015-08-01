from django.core.management.base import BaseCommand, CommandError
from gift2redeem.apps.retailers.models import *

import mechanicalsoup, re


class Command(BaseCommand):
    help = 'Loads locations for Target'

    def handle(self, *args, **options):
        RetailerLocation.objects.filter(retailer=Retailer.objects.get(name="Target")).delete()
        url_prefix = "http://www.target.com/"
        browser = mechanicalsoup.Browser()
        state_list = browser.get(url_prefix + "store-locator/state-listing")
        state_links = state_list.soup.select(".statelink")

        for state_link in state_links:
            location_list = browser.get(url_prefix + "store-locator/" + state_link["href"])
            location_rows = location_list.soup.select("tr.data-row")

            for location_row in location_rows:
                location_links = location_row.select("td")

                # Retrieve the store attribs
                store_href = location_links[1].select("a")[0]["href"]
                store_name = str(location_links[1].select("a")[0].text)
                store_address = str(location_links[2].text).strip()
                store_city_state = str(location_links[3].text).strip()
                store_phone = str(location_links[4].text).strip()

                m = re.search("^(.*),.*([A-Z][A-Z])(\d\d\d\d\d-\d\d\d\d).*$", store_city_state)
                if m:
                    city = str(m.group(1))
                    state = str(m.group(2))
                    postal = str(m.group(3))

                # Retrieve the store lat/lng
                location_page = browser.get(url_prefix + store_href)
                location_page_source = location_page.text

                raw_lat = re.search(',"Latitude":([-0-9.]+),', location_page_source)
                raw_lng = re.search(',"Longitude":([-0-9.]+)\}', location_page_source)

                if raw_lat and raw_lng:
                    store_latitude = str(raw_lat.group(1))
                    store_longitude = str(raw_lng.group(1))
                    retailer_location = RetailerLocation()
                    retailer_location.is_active = True
                    retailer_location.retailer = Retailer.objects.get(name="Target")
                    retailer_location.lat = store_latitude
                    retailer_location.lng = store_longitude
                    retailer_location.address = store_address
                    retailer_location.address2 = ""
                    retailer_location.city = city
                    retailer_location.state = state
                    retailer_location.postal_code = postal
                    retailer_location.save()
