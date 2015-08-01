from tastypie.resources import ModelResource, Resource
from tastypie import fields
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization
from tastypie.models import ApiKey
from gift2redeem.apps.retailers.models import *
from django.forms.models import model_to_dict
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.core import serializers
from django.http import Http404
from django.http import HttpResponse

import simplejson

#######################################################################################################
#######################################################################################################
## Basic Flow
## Create Account -> Add Card(s) -> View Offers and Retailer Balances
#######################################################################################################
#######################################################################################################

#######################################################################################################
# Create a new gift2redeem account by provisioning a username and API key
# POST -> /api/v1/account/
#######################################################################################################

def create_new_account(req):
	if req.method == "POST":
		# Create a new user
		user_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
		resp = User.objects.get_or_create(username=user_name)
		user = resp[0]

		# Create an api_key
		resp = ApiKey.objects.get_or_create(user_id=user.id)
		api_key = resp[0]
		api_key.key = api_key.generate_key()
		api_key.save()

		# Return the username and api_lkey
		data = {"username" : user_name, "api_key" : api_key.key}
		return HttpResponse(simplejson.dumps(data), content_type="application/json")
	else:
		return HttpResponse(status=404)

def user_login(req):
	#import pdb;pdb.set_trace()
	if req.method=="POST":
		firstName=req.POST["first_name"]
		lastName=req.POST["last_name"]
		username = req.POST["username"]
		logmethod=req.POST["login_method"]
		password = req.POST["password"]
		if username=='':
			return HttpResponse("Enter Username", content_type="application/json")
		if password=='':
			return HttpResponse("Enter Password", content_type="application/json")
		user = User.objects.filter(username=username)
		if not user:
                    return HttpResponse("Not registered", content_type="application/json")

		if logmethod =='':
			user = authenticate(username=username, password=password)
		else:
			emailId=username
			retailers = serializers.serialize("json", Retailer.objects.all())
			cards = serializers.serialize("json", RetailerCard.objects.all())
			cardbalance = serializers.serialize("json", CardBalance.objects.all())
			data = {'data': {'profile': {'username' : username, 'firstName' : firstName, 'lastName' : lastName, 'email' : emailId}, 'retailers': retailers, 'cards': cards, 'cardbalance':cardbalance,'session_id' : 'fkjsfh34' }}
			return HttpResponse(simplejson.dumps(data), content_type="application/json")

		if user is not None:
			if user.is_active:
				login(req, user)
				user = User.objects.get(username=username)
				username = user.username
				firstName = user.first_name
				lastName = user.last_name
				emailId = user.email
				retailers = serializers.serialize("json", Retailer.objects.all())
				cards = serializers.serialize("json", RetailerCard.objects.all())
				data = {'data': {'profile': {'username' : username, 'firstName' : firstName, 'lastName' : lastName, 'email' : emailId}, 'retailers': retailers, 'cards': cards, 'session_id' : 'fkjsfh34' }}
				print (data)
				return HttpResponse(simplejson.dumps(data), content_type="application/json")
			else:
				return HttpResponse("User is currently not active! Please contact support.")
		else:
			return HttpResponse("Username/password combination is invalid! Try again")
	else:
		return HttpResponse("Http Method Not Supported")

def get_user_data(req):
	if req.method == "POST":
		userId = req.POST["userId"]
		retailers = serializers.serialize("json", Retailer.objects.all())
		cards = serializers.serialize("json", RetailerCard.objects.all())
		data = {'data': {'profile': {}, 'retailers': retailers, 'cards': cards, 'session_id' : 'fkjsfh34' }}
		print (data)
		return HttpResponse(simplejson.dumps(data), content_type="application/json")
	else:
		return HttpResponse("Username/password combination is invalid! Try again")

def otp_email(req):
        gmail_user = "michaleraj2008@gmail.com"
        gmail_pwd = "poogaymic!@#2014"
        TO = 'michaleraj2008@gmail.com'
        SUBJECT = "G2R OTP Verification"
        TEXT = "Hi Michale Raj,\n\nYour one time password for g2r is :854678\n\nRegards,\nG2R Team."
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        BODY = '\r\n'.join(['To: %s' % TO,
                'From: %s' % gmail_user,
                'Subject: %s' % SUBJECT,
                '', TEXT])

        server.sendmail(gmail_user, [TO], BODY)
        return HttpResponse("Email Sent")
#######################################################################################################
# Create a card, update a card, or delete a card
# POST      -> /api/v1/card/?username=<user_name>&api_key=<api_key>
# PUT/DELETE-> /api/v1/card/<card_id>/?username=<user_name>&api_key=<api_key>
#######################################################################################################

class RetailerCardResource(ModelResource):
	""" CRUD for retailer cards """
	class Meta:
		queryset = RetailerCard.objects.all()
		allowed_methods = ["post", "put", "delete"]
		resource_name = "card"
		authentication = ApiKeyAuthentication()
		authorization = Authorization()		

	def obj_create(self, bundle, **kwargs):
		return super(RetailerCardResource, self).obj_create(bundle, user=bundle.request.user)

	def apply_authorization_limits(self, request, object_list):
		return object_list.filter(user=request.user)				


#######################################################################################################
# Retrieve a retailer and all the associated cards
# GET -> /api/v1/retailer/?username=<user_name>&api_key=<api_key>
# GET -> /api/v1/retailer/<retailer_id>/?username=<user_name>&api_key=<api_key>
#######################################################################################################

class RetailerResource(ModelResource):
	""" Retrieve a retailer and all the associated cards. """
	class Meta:
		queryset = Retailer.objects.all()
		resource_name = "retailer"
		allowed_methods = ["get"]
		authentication = ApiKeyAuthentication()
		authorization = Authorization()			

	def dehydrate(self, bundle):
		retailer_id = bundle.data["id"]
		t_cards = []
		total = 0.0
		cards = list(RetailerCard.objects.filter(retailer=retailer_id))
		for card in cards:
			t_cards.append(model_to_dict(card))
			if card.balance:
				total += float(card.balance)
		bundle.data["cards"] = t_cards
		bundle.data["total"] = total
		return bundle

	def obj_create(self, bundle, **kwargs):
		return super(RetailerResource, self).obj_create(bundle, user=bundle.request.user)

	def apply_authorization_limits(self, request, object_list):
		return object_list.filter(user=request.user)				


#######################################################################################################
# Retrieve a list of offers by location and retailer balance
# GET -> /api/v1/offer/?lat=<lat>&lng=<lng>&username=<user_name>&api_key=<api_key>
#
# Note: This API call will only retrieve a max of 20 records!
#######################################################################################################

def get_offers(req):
	if req.method == "GET":
		try:
			user_name = req.GET["username"]
			api_key = req.GET["api_key"]
			user = User.objects.get(username=user_name)
			api_key = ApiKey.objects.get(user_id=user, key=api_key)
		except:
			return HttpResponse(status=401)

		if "lat" not in req.GET or "lng" not in req.GET:
			return HttpResponse(status=400)

		lat = req.GET["lat"]
		lng = req.GET["lng"]
		qs = RetailerOfferFlat.get_offers(lat, lng, user.id)  
		rows = [model_to_dict(row) for row in qs]

		data = {
			"meta" : {
				"limit" : len(rows),
				"next" : None,
				"offset" : 0,
				"previous" : None,
				"total_count" : len(rows)
			},
			"objects" : rows
		}

		return HttpResponse(simplejson.dumps(data), content_type="application/json")
	else:
		return HttpResponse(status=404)