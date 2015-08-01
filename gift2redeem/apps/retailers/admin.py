from django.contrib import admin
from gift2redeem.apps.retailers.models import WalletCard,Retailer, CardBalance,CardProfile,OneTimePassword,RetailerOffer, RetailerLocation,RetailerCard
class WalletCardInline(admin.TabularInline):
    model = WalletCard
    extra = 1

class RetailerAdmin(admin.ModelAdmin):
	list_display  = ('name', 'is_active',)
	list_filter   = ['is_active',]	
	search_fields = ['name', 'description',]

class CardProfileAdmin(admin.ModelAdmin):
    list_display  = ('name', 'retailer', 'is_active',)
    list_filter   = ['is_active',]
    search_fields = ['name', ]

class RetailerLocationAdmin(admin.ModelAdmin):
    list_display  = ('address', 'address2', 'city', 'state', 'postal_code', 'lat', 'lng', 'retailer', 'is_active',)
    list_filter   = ['is_active', 'retailer', 'state',]
    search_fields = ['address', 'address2', 'city', 'state', 'postal_code', ]

class RetailerCardAdmin(admin.ModelAdmin):
	inlines = (WalletCardInline,)
	list_display  = ('number', 'pin', 'expiration_date', 'card_profile',)
	list_filter   = ['card_profile',]
	search_fields = ['number', 'pin']

class RetailerOfferAdmin(admin.ModelAdmin):
	list_display  = ('name', 'image_url', 'description', 'price','url',)
	list_filter   = ['name',]
	search_fields = ['name']

class CardBalanceAdmin(admin.ModelAdmin):
	list_display  = ('card', 'balance', 'is_active',)
	list_filter   = ['is_active',]
	search_fields = ['card',]

class OtpAdmin(admin.ModelAdmin):
	list_display  = ('otp', 'is_active',)
	list_filter   = ['is_active',]	
	search_fields = ['user', 'otp',]

class WalletCardAdmin(admin.ModelAdmin):
	list_display  = ('user', 'card',)
	list_filter   = ['is_active',]	
	search_fields = ['user', 'card',]

admin.site.register(WalletCard,  WalletCardAdmin)
admin.site.register(RetailerCard,  RetailerCardAdmin)
admin.site.register(CardBalance,  CardBalanceAdmin)
admin.site.register(Retailer,  RetailerAdmin)
admin.site.register(RetailerOffer,  RetailerOfferAdmin)
admin.site.register(CardProfile, CardProfileAdmin)
admin.site.register(RetailerLocation, RetailerLocationAdmin)
admin.site.register(OneTimePassword,  OtpAdmin)

