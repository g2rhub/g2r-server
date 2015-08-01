from django.test                          import TestCase
from django.test.client                   import Client
from django.contrib.auth.models           import User
from gift2redeem                          import settings
from gift2redeem.apps.user_profile.models import *
from gift2redeem.apps.retailers.models    import *
from gift2redeem.apps.wallet.models       import *


from gift2redeem.apps.user_profile.view_models import *

import json, uuid

class HttpApiTest(TestCase):
	def setUp(self):
		self.c = Client()

		self.retailer             = Retailer()
		self.retailer.is_active   = True
		self.retailer.name        = "Target"
		self.retailer.description = "Your favorite superstore"
		self.retailer.save()

		self.retailerCardProfile                        = RetailerCardProfile()
		self.retailerCardProfile.is_active              = True
		self.retailerCardProfile.retailer               = self.retailer
		self.retailerCardProfile.name                   = "Target Gift Card"
		self.retailerCardProfile.balance_check_function = "get_target_card_balance"
		self.retailerCardProfile.ocr_function           = "ocr_target_card"
		self.retailerCardProfile.min_amount             = 1
		self.retailerCardProfile.max_amount             = 1000
		self.retailerCardProfile.is_usable_online       = True
		self.retailerCardProfile.is_usable_instore      = True
		self.retailerCardProfile.pin_required           = True
		self.retailerCardProfile.has_expiration_date    = False
		self.retailerCardProfile.has_realtime_balance   = True
		self.retailerCardProfile.details                = "Your goto gift card"
		self.retailerCardProfile.redemption_information = "Redeem at your local target or online"
		self.retailerCardProfile.terms_and_conditions   = "See website"
		self.retailerCardProfile.save()

		self.retailerLocation             = RetailerLocation()
		self.retailerLocation.is_active   = True
		self.retailerLocation.retailer    = self.retailer
		self.retailerLocation.lat         = 37.157592
		self.retailerLocation.lng         = -121.653767
		self.retailerLocation.address     = "1061 Cochrane Rd"
		self.retailerLocation.address2    = ""
		self.retailerLocation.city        = "Morgan Hill"
		self.retailerLocation.state       = "CA"
		self.retailerLocation.postal_code = "95037"
		self.retailerLocation.save()


	def test_registration(self, assert_it=True):
		self.t_username = "nickcrafford@gmail.com"
		resp = self.c.post('/api/v1/register/',{"username" : self.t_username})
		if assert_it:
			self.assertEqual(200, resp.status_code)

		resp_dict = json.loads(resp.content)
		if assert_it:
			self.assertTrue("api_key" in resp_dict["data"])
		
		self.api_key = resp_dict["data"]["api_key"]
		self.user    = User.objects.get(username=self.t_username)
		self.profile = ProfileVM.get(self.user)		
		if assert_it:
			self.assertTrue(self.profile)
	
	def test_update_profile(self):
		self.test_login(False)
		new_username = "nick.crafford@arf.com"
		new_api_key  = "abc123"
		resp = self.c.post('/api/v1/update-profile/',{"username" : new_username, "api_key" : new_api_key, "is_guest" : "0", "enable_push_notifications" : "0"})
		
		self.assertEqual(200, resp.status_code)

		resp_dict = json.loads(resp.content)
		self.assertEqual(resp_dict["data"]["profile"]["user"]["username"], new_username)
		self.assertEqual(resp_dict["data"]["profile"]["is_guest"], False)
		self.assertEqual(resp_dict["data"]["profile"]["enable_push_notifications"], False)

		resp = self.c.post('/api/v1/update-profile/',{"username" : new_username, "api_key" : new_api_key, "is_guest" : "1", "enable_push_notifications" : "1"})

		self.assertEqual(200, resp.status_code)

		resp_dict = json.loads(resp.content)
		self.assertEqual(resp_dict["data"]["profile"]["user"]["username"], new_username)
		self.assertEqual(resp_dict["data"]["profile"]["is_guest"], True)
		self.assertEqual(resp_dict["data"]["profile"]["enable_push_notifications"], True)

		resp = self.c.post('/api/v1/login/', {"username" : new_username, "api_key" : new_api_key})

		self.assertEqual(200, resp.status_code)


	def test_login(self, assert_it=True):
		self.test_registration(False)

		resp = self.c.post('/api/v1/login/', {"username" : self.t_username, "api_key" : "XXX"})
		if assert_it:
			self.assertEqual(403, resp.status_code)				

		resp = self.c.post('/api/v1/login/', {"username" : self.t_username, "api_key" : self.api_key})
		if assert_it:
			self.assertEqual(200, resp.status_code)

	def test_get_retailers(self, assert_it=True):
		self.test_login(True)

		resp = self.c.post('/api/v1/retailers/', {})
		if assert_it:
			self.assertEqual(200, resp.status_code)

		resp_dict = json.loads(resp.content)
		retailers = resp_dict["data"]["retailers"]
		retailer  = retailers[0]
		
		if assert_it:
			self.assertEqual(len(retailers), 1)
			self.assertEqual(retailer["name"], "Target")
			self.assertEqual(retailer["is_active"], True)
			self.assertEqual(len(retailer["card_profiles"]), 1)

		retailer_card_profile = retailer["card_profiles"][0]
		if assert_it:
			self.assertEqual(retailer_card_profile["has_realtime_balance"], True)

	def test_save_card(self):
		self.test_login(False)

		offer                 = RetailerOffer()
		offer.is_active       = True
		offer.retailer        = self.retailer
		offer.name            = "$5 candy bars!"
		offer.description     = "Used to be $10 now $5"
		offer.trigger_balance = 5.00
		offer.save()

		resp = self.c.post('/api/v1/save-card/', {
			"is_active"                : True,
			"number"                   : "041212918926090",
			"pin"                      : "14400173",
			"expiration_date"          : "2014-03-29",
			"retailer_card_profile_id" : self.retailerCardProfile.id
		})

		resp_dict = json.loads(resp.content)
		balance   = resp_dict["data"]["card"]["balance"]
		offers    = resp_dict["data"]["card"]["offers"]

		self.assertEqual(float(balance), float(10.00))
		self.assertEqual(len(offers), 1)

		# Retrieve cards
		resp = self.c.post('/api/v1/cards/')
		self.assertEqual(resp.status_code, 200)

		resp_dict = json.loads(resp.content)
		self.assertEqual(len(resp_dict["data"]["cards"]), 1)

	def test_check_best_buy_balance(self):
		self.test_login(False)

		bb_retailer             = Retailer()
		bb_retailer.is_active   = True
		bb_retailer.name        = "Best Buy"
		bb_retailer.description = "Electronics for all!"	
		bb_retailer.save()

		bb_retailerCardProfile                        = RetailerCardProfile()
		bb_retailerCardProfile.is_active              = True
		bb_retailerCardProfile.retailer               = bb_retailer
		bb_retailerCardProfile.name                   = "Best Buy Gift Card"
		bb_retailerCardProfile.balance_check_function = "get_best_buy_card_balance"
		bb_retailerCardProfile.ocr_function           = "ocr_best_buy_card"
		bb_retailerCardProfile.min_amount             = 1
		bb_retailerCardProfile.max_amount             = 1000
		bb_retailerCardProfile.is_usable_online       = True
		bb_retailerCardProfile.is_usable_instore      = True
		bb_retailerCardProfile.pin_required           = True
		bb_retailerCardProfile.has_expiration_date    = False
		bb_retailerCardProfile.has_realtime_balance   = True
		bb_retailerCardProfile.details                = "Your goto gift card"
		bb_retailerCardProfile.redemption_information = "Redeem at your local target or online"
		bb_retailerCardProfile.terms_and_conditions   = "See website"
		bb_retailerCardProfile.save()	

		resp = self.c.post('/api/v1/save-card/', {
			"is_active"                : True,
			"number"                   : "6088819061758966",
			"pin"                      : "1243",
			"expiration_date"          : "2014-03-29",
			"retailer_card_profile_id" : bb_retailerCardProfile.id
		})			

		self.assertEqual(resp.status_code, 200)

		resp_dict = json.loads(resp.content)
		balance   = resp_dict["data"]["card"]["balance"]

		self.assertEqual(float(balance), float(10.00))

	def test_ocr_card(self):
		settings.OCR_DEBUG = True
		self.test_login(True)
		resp = None
		with open("gift2redeem/apps/tests/assets/card_back.jpg") as fp:
			resp = self.c.post("/api/v1/get-card-number", {"retailer_card_profile_id": self.retailerCardProfile.id, "card_image" : fp})

		self.assertEqual(resp.status_code, 200)

		resp_dict = json.loads(resp.content)

		self.assertEqual(resp_dict["data"]["number"], "78910")
		self.assertEqual(resp_dict["data"]["pin"],    "123456")




