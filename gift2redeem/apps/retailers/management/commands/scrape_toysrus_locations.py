from django.core.management.base import BaseCommand, CommandError
from gift2redeem.apps.retailers.models import *

import mechanicalsoup, re, json

states = ("AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI",
          "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI",
          "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC",
          "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT",
          "VT", "VA", "WA", "WV", "WI", "WY", "DC")


class Command(BaseCommand):
    help = 'Loads locations for Toys R Us'

    def handle(self, *args, **options):
        RetailerLocation.objects.filter(retailer=Retailer.objects.get(name="Toys R Us")).delete()

        browser = mechanicalsoup.Browser()
        pos_pairs = []
        for state in states:
            state_page = browser.get(
                "http://www.toysrus.com/isvc/trus-sl/search?substore=tru&locale=en_US&callback=jQuery191017880051862448454_1405271976309&storeTag=TOYSRUS&storeTag=BABIESRUS&height=655&width=727&address=%s&radius=800&_=1405271976310" % (
                state)).text
            json_friendly = []
            lines = state_page.split("\n")
            for line in lines:
                if line == "    )" or line.find("jQuery191017880051862448454_1405271976309(") > 0:
                    continue
                json_friendly.append(line.replace("'", '"'))

            obj = json.loads(''.join(json_friendly))
            results = obj["RESULTS"]
            for result in results:
                store = result["store"]
                pos_pair = (store["latitude"], store["longitude"])
                if pos_pair in pos_pairs:
                    continue

                retailer_location = RetailerLocation()
                retailer_location.is_active = True
                retailer_location.retailer = Retailer.objects.get(name="Toys R Us")
                retailer_location.lat = store["latitude"]
                retailer_location.lng = store["longitude"]
                retailer_location.address = store["address1"]
                retailer_location.address2 = store["address2"]
                retailer_location.city = store["city"]
                retailer_location.state = store["stateCode"]
                retailer_location.postal_code = store["postalCode"]
                retailer_location.save()

                pos_pairs.append(pos_pair)

	