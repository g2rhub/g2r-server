from django.core.management.base import BaseCommand
from gift2redeem.apps.retailers.models import Retailer, RetailerOffer
from urlparse import urlparse, parse_qs

import feedparser, re, mechanicalsoup


class Command(BaseCommand):
    args = '<retailer_id>'
    help = 'Retrieves deals for all retailers'

    def get_amount(self, title, regexes):
        for regex in regexes:
            ret = re.findall(regex, title)
            if len(ret) > 0:
                return ret[0]
        return None

    def handle(self, *args, **options):
        browser = mechanicalsoup.Browser()
        retailers = list(Retailer.objects.all())
        for retailer in retailers:
            if retailer.slick_deals_url:
                feed = feedparser.parse(str(retailer.slick_deals_url))

                # Add new deals
                for entry in feed.entries:
                    title = entry.title
                    link = entry.link
                    amount = self.get_amount(title, [r'\$[\d.]+', r'\$[\d.]+', r'\d\d.\d\d', r'[\d]+.[\d]+'])


                    if amount and RetailerOffer.objects.filter(url=link).count() <= 0:
                        try:
                            clean_balance = float(str(amount).replace("$", ""))
                        except:
                            clean_balance = "9.99"

                        retailerOffer = RetailerOffer()
                        retailerOffer.url = link
                        retailerOffer.is_active = True
                        retailerOffer.retailer = retailer
                        retailerOffer.name = title.encode('ascii', 'ignore')[:200]
                        retailerOffer.description = title.encode('ascii', 'ignore')[:200]
                        retailerOffer.price = clean_balance
                        retailerOffer.save()