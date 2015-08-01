from django.db import models
from django.contrib.auth.models import User
from gift2redeem.apps.balance_check.card_balance import get_card_balance

OTP_CHOICES = (
    ('NEW', 'New'),
    ('FORGOT', 'Forgot'),
    ('CARD', 'Card'),
    ('OTHER', 'Other'),
)

class OneTimePassword(models.Model):
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(User)
    otp = models.CharField(max_length=50)
    otp_types = models.CharField(max_length=10, choices=OTP_CHOICES,
                                      default='NEW')
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return str(self.user.first_name)

    class Meta:
        db_table = 'one_time_password'

class UserProfile(User):
    google_id = models.CharField('google_id', max_length=200, null=True)
    google_image = models.CharField('google_image', max_length=500, null=True)
    facebook_id = models.CharField('facebook_id', max_length=200, null=True)
    dob = models.DateField(null=True)

    def __unicode__(self):
         return self.last_name + self.first_name

    def calculate_age(self):
        today = date.today()

        try: 
            birthday = self.dob.replace(year=today.year)
        # raised when birth date is February 29 and the current year is not a leap year
        except ValueError:
            birthday = self.dob.replace(year=today.year, day=born.day-1)

        if birthday > today:
            return today.year - born.year - 1
        else:
            return today.year - born.year
            
class Retailer(models.Model):
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=150, blank=True, null=True)
    description = models.TextField()
    logo = models.URLField(max_length=500)
    site_url = models.URLField(max_length=500)
    slick_deals_url = models.URLField(null=True, blank=True)
    balance_check_function = models.CharField(max_length=50, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = "g2r_retailers"


class RetailerOffer(models.Model):
    is_active = models.BooleanField(default=True)
    retailer = models.ForeignKey(Retailer)
    name = models.CharField(max_length=250)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    url = models.URLField(null=True, blank=True, max_length=500)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = "g2r_retailer_offers"


class RetailerLocation(models.Model):
    is_active = models.BooleanField(default=True)
    retailer = models.ForeignKey(Retailer)
    lat = models.DecimalField(max_digits=10, decimal_places=6)
    lng = models.DecimalField(max_digits=10, decimal_places=6)
    address = models.CharField(max_length=250)
    address2 = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=250)
    state = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=250)
    
    def __unicode__(self):
        return self.address + " " + self.address2 + " " + self.city + " " + self.state + " , " + self.postal_code

    class Meta:
        db_table = "g2r_retailer_locations"





class RetailerOfferFlat(models.Model):
    retailer_id = models.PositiveIntegerField()
    retailer_name = models.CharField(max_length=150, blank=True, null=True)
    retailer_description = models.TextField()
    retailer_logo = models.URLField(max_length=500)
    retailer_site_url = models.URLField(max_length=500)    
    retailer_total_balance = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, default=0.0)
    offer_name = models.CharField(max_length=250)
    offer_image_url = models.URLField(max_length=500, null=True, blank=True)
    offer_description = models.TextField(null=True, blank=True)
    offer_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    offer_url = models.URLField(null=True, blank=True, max_length=500)
    offer_is_purchasable = models.BooleanField(default=False)
    location_distance_km = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, default=0.0)
    location_address = models.CharField(max_length=250)
    location_address2 = models.CharField(max_length=250, null=True, blank=True)
    location_city = models.CharField(max_length=250)
    location_state = models.CharField(max_length=250)
    location_postal_code = models.CharField(max_length=250)
    location_lat = models.DecimalField(max_digits=10, decimal_places=6)
    location_lng = models.DecimalField(max_digits=10, decimal_places=6)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        managed = False

    @staticmethod
    def get_offers(lat, lng, user_id):
        query = """
            select * from (
            select 
              o.id,
              o.retailer_id,
              r.name retailer_name,
              r.description retailer_description,
              r.logo retailer_logo,
              r.site_url retailer_site_url,
              o.name offer_name,
              o.image_url offer_image_url,
              o.description offer_description,
              o.price offer_price,
              o.url offer_url,
              b.balance retailer_total_balance,
              b.balance >= o.price offer_is_purchasable,
              l.distance location_distance_km,
              l.address location_address,
              l.address2 location_address2,
              l.city location_city,
              l.state location_state,
              l.postal_code location_postal_code,
              l.lat location_lat,
              l.lng location_lng
            from
            g2r_retailer_offers o,
            g2r_retailers r,
            (
                select
                id,
                retailer_id,
                address,
                address2,
                city,
                state,
                postal_code,
                lat,
                lng,
                111.045 * DEGREES(ACOS(COS(RADIANS(%s))
                        * COS(RADIANS(lat))
                        * COS(RADIANS(%s) - RADIANS(lng))
                        + SIN(RADIANS(%s))
                        * SIN(RADIANS(lat)))) AS distance
                from
                g2r_retailer_locations
                order by distance asc
                limit 1
            ) l,
            (
              select sum(balance) balance, retailer_id
              from 
              g2r_retailer_cards c
              where c.user_id = %s
              group by retailer_id
            ) b
            where o.retailer_id = l.retailer_id
            and l.retailer_id = b.retailer_id
            and r.id = l.retailer_id
            and o.is_active = true
            ) offers
            order by offer_is_purchasable desc, offer_price desc
            limit 20
        """
        return RetailerOfferFlat.objects.raw(query, [lat, lng, lat, user_id])

class CardProfile(models.Model):
    retailer = models.ForeignKey(Retailer)
    name = models.CharField(max_length=250)
    image_url = models.CharField(max_length=500, null=True, blank=True)
    details = models.CharField(max_length=500, null=True, blank=True)
    terms_and_conditions = models.CharField(max_length=500, null=True, blank=True)
    redemption_information = models.CharField(max_length=500, null=True, blank=True)
    phone_number = models.CharField(max_length=500, null=True, blank=True)
    min_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, default=0.0)
    max_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, default=0.0)
    has_expiration_date = models.BooleanField(default=True)
    has_realtime_balance = models.BooleanField(default=True)
    is_usable_online = models.BooleanField(default=True)
    is_usable_in_store = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    has_pin = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)


    def __unicode__(self):
        return str(self.name)

    class Meta:
        db_table = 'card_profile'


class RetailerCard(models.Model):
    card_profile = models.ForeignKey(CardProfile)
    number = models.CharField(max_length=50)
    pin = models.CharField(max_length=50, blank=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)
    barcode = models.CharField(max_length=500, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return str(self.number) + u"/" + str(self.pin)

    class Meta:
        db_table = 'card'


class CardBalance(models.Model):
    is_active = models.BooleanField(default=True)
    card = models.ForeignKey(RetailerCard)
    balance = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return str(self.card.number)

    class Meta:
        db_table = 'card_balance'


class WalletCard(models.Model):
    is_active = models.BooleanField(default=True)
    card = models.ForeignKey(RetailerCard)
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return str(self.user.first_name)

    class Meta:
        db_table = 'wallet_card'

