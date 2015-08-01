from django.conf.urls    import patterns, include, url
from django.contrib.auth import views as auth_views
from django.contrib      import admin
from tastypie.api 	import Api
from tastypie.models import ApiKey

from gift2redeem.apps.resources.card_retailer_resource import *
from gift2redeem.apps.resources.user_resource import *
from gift2redeem.apps.resources.retailer_resource import *
from gift2redeem.apps.resources.otp_resources import *
from gift2redeem.apps.retailers.api import *


import json, random, string

admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(UserResource())
v1_api.register(RetailerResource())
v1_api.register(RetailerCardResource())
v1_api.register(OneTimePasswordResource())

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    (r'^api/v1/account', create_new_account),
    (r'^api/v1/login', user_login),
    (r'^api/v1/userdata', get_user_data),
    (r'^api/v1/offer', get_offers),
    (r'^api/v1/retailer-locations', get_offers),
    (r'^api/v1/otpmail', otp_email),
    (r'^api/', include(v1_api.urls)),
)
