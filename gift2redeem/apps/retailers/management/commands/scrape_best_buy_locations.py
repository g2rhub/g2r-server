from django.core.management.base import BaseCommand, CommandError
from gift2redeem.apps.retailers.models import *

import json, urllib2

BEST_BUY_API_KEY = "s8zgc5dj5e3a69x583h9u5ba"


class Command(BaseCommand):
    help = 'Loads locations for Best Buy'

    def handle(self, *args, **options):
        RetailerLocation.objects.filter(retailer=Retailer.objects.get(name="Best Buy")).delete()

        for page in range(1, 15):
            response = urllib2.urlopen(
                'http://api.remix.bestbuy.com/v1/stores?format=json&apiKey=%s&pageSize=100&page=%s' % (
                BEST_BUY_API_KEY, str(page)))
            source = response.read()
            data = json.loads(source)

            for store in data["stores"]:
                lat = store["lat"]
                lng = store["lng"]
                address = store["address"]
                city = store["city"]
                state = store["region"]
                postal_code = store["postalCode"]
                retailer_location = RetailerLocation()
                retailer_location.is_active = True
                retailer_location.retailer = Retailer.objects.get(name="Best Buy")
                retailer_location.lat = lat
                retailer_location.lng = lng
                retailer_location.address = address
                retailer_location.address2 = ""
                retailer_location.city = city
                retailer_location.state = state
                retailer_location.postal_code = postal_code
                retailer_location.save()