from django.core.management.base import BaseCommand
from gift2redeem.apps.retailers.models import RetailerCard


class Command(BaseCommand):
    help = 'Refresh card balances'

    def handle(self, *args, **options):
        cards = RetailerCard.objects.all()
        for card in cards:
            card.poll_balance()