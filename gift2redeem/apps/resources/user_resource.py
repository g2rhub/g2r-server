
from random import randint
import simplejson
from django.core import serializers
from django import http
from django.db import IntegrityError, transaction
from django.contrib.auth import authenticate, login, logout
from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.http import HttpResponse

from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.utils import trailing_slash
from tastypie.authentication import SessionAuthentication
from tastypie.authorization import Authorization
from tastypie.models import ApiKey
from tastypie.http import HttpUnauthorized

from utils import *
#from app.forms import *
from gift2redeem.apps.retailers.models import *

class UserResource(ModelResource):
        
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser']
        allowed_methods = ['get','post']
        filtering = { "id" : ALL }

        fields = ['username', 'first_name', 'last_name', 'last_login']

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/login%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('user_login'), name="api_login"),
            url(r"^(?P<resource_name>%s)/change_password%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('change_password'), name="api_change_password"),
            url(r"^(?P<resource_name>%s)/new%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('new_user'), name="api_new_user"),
            url(r"^user/logout/$", self.wrap_view('logout'), name='api_logout'),
        ]

    def new_user(self, request, **kwargs):
        import pdb;pdb.set_trace()
        try:
            if request.method.lower() == 'post':
                username = request.POST["identifier"]
                email = request.POST["email"]
                print(email);
                password = request.POST["password"]
                firstName = request.POST["firstName"]
                lastName = request.POST["lastName"]
                google_id = request.POST["google_id"]
                facebook_id = request.POST["facebook_id"]
                google_image = request.POST["google_image"]
                dob = request.POST["dob"]
                isactive = 'true'

                if email:
                    user = User.objects.filter(email=email)
                #         raise CustomBadRequest(
                #             code="duplicate_exception",
                #             message="That email is already used.")
                if username:
                    user = User.objects.filter(username=username)
                if user:
                    return HttpResponse("Username/Email already exist Try again")
                else:
                    user_obj, new_user = User.objects.get_or_create(username=username, email=email,is_active=isactive)
                    user_obj.set_password(password)
                    user_obj.save()
                    if user_obj:
                        user_data = User.objects.filter(username=username)
                        opt_random = randint(0,999999)
                        otp_create, otp_true = OneTimePassword.objects.get_or_create(user=user_obj, otp=opt_random)
                        user_id=user_data[0]
                        resp = ApiKey.objects.get_or_create(user_id=user_obj.id)
                        api_key = resp[0]
                        api_key.key = api_key.generate_key()
                        api_key.save()
                        up_create, upp_true = UserProfile.objects.get_or_create(user=user_obj)
                        
                        res = {"result": {"status": "True", "opt_data": otp_create.otp}}
                        return HttpResponse(simplejson.dumps(res), content_type="application/json")
            else:
                res = {"result": {"status": "False", "message": "Method Not allowed"}}
                return HttpResponse(simplejson.dumps(res), content_type="application/json")
        except:
            res = {"result": {"status": "False", "message": "Something went Wrong "}}
            return HttpResponse(simplejson.dumps(res), content_type="application/json")


    def user_login(self, request, **kwargs):
        import pdb;pdb.set_trace()
        try:
            if request.method.lower() == 'post':
                username = request.POST['username']
                password = request.POST["password"]

                if username and password:
                    user = User.objects.filter(username=username, password=password)
                    if user:
                        user_obj = user[0]
                        cards = WalletCard.objects.filter(user=user_obj)
                        user_result = {}
                        user_result['username'] = user_obj.username
                        user_result['first_name'] = user_obj.first_name
                        user_result['last_name'] = user_obj.last_name
                        card_list = []
                        if cards:
                            
                            for wcard in cards:
                                card_values = {}
                                card_values['number'] = wcard.card.number
                                card_values['pin'] = wcard.card.pin

                                card_list.append(card_values)

                        user_result['cards'] = card_list
                        res = {"result": {"status": "True", "user": user_result, "message": "Login success"}}
                        return HttpResponse(simplejson.dumps(res), content_type="application/json")
                    else:
                        res = {"result": {"status": "False", "message": "Login Fail"}}
                        return HttpResponse(simplejson.dumps(res), content_type="application/json")
            else:
                res = {"result": {"status": "False", "message": "Method Not allowed"}}
                return HttpResponse(simplejson.dumps(res), content_type="application/json")
        except:
            res = {"result": {"status": "False", "message": "Something went Wrong "}}
            return HttpResponse(simplejson.dumps(res), content_type="application/json")

    def change_password(self, request, **kwargs):
        try:
            if request.method.lower() == 'post':
                username = request.POST['username']
                old_password = request.POST["old_password"]
                new_password = request.POST["new_password"]

                if username and old_password and new_password:
                    import pdb;pdb.set_trace()
                    user_obj = authenticate(username=username, password=old_password)
                    if user_obj:
                        user_obj.set_password(new_password)
                        user_obj.save()

                        res = {"result": {"status": "True", "message": "Password Changed successfully"}}
                        return HttpResponse(simplejson.dumps(res), content_type="application/json")
                    else:
                        res = {"result": {"status": "False", "message": "User Does not exist"}}
                        return HttpResponse(simplejson.dumps(res), content_type="application/json")
            else:
                res = {"result": {"status": "False", "message": "Method Not allowed"}}
                return HttpResponse(simplejson.dumps(res), content_type="application/json")
        except:
            res = {"result": {"status": "False", "message": "Something went Wrong "}}
            return HttpResponse(simplejson.dumps(res), content_type="application/json")        

    def logout(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        if request.user and request.user.is_authenticated():
            logout(request)
            return self.create_response(request, { 'success': True })
        else:
            return self.create_response(request, { 'success': False }, HttpUnauthorized)
