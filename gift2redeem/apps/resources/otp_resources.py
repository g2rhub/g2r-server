from decimal import Decimal
import simplejson
from random import randint
import dateutil.parser

from django.conf.urls import url
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from tastypie.utils import trailing_slash
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer

from gift2redeem.apps.retailers.models import *


class OneTimePasswordResource(ModelResource):
    class Meta:
        queryset = OneTimePassword.objects.all()
        resource_name = 'otp'
        fields = ['number', 'bin', 'expiration_date']

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/otp_request/$" % (self._meta.resource_name), self.wrap_view('otp_request'),\
            	name="api_otp_request"),
            url(r"^(?P<resource_name>%s)/verify_otp/$" % (self._meta.resource_name), self.wrap_view('verify_otp'),
            	name="api_verify_otp"),
        ]


    def otp_request(self, request, **kwargs):
        import pdb;pdb.set_trace()
        try:
            if request.method == 'GET':
                username = request.GET['username']
                if username:
                    user = User.objects.filter(username=username).first()
                    if user:
                        otp_verify = OneTimePassword.objects.filter(user=user, is_active=True).first()
                        if not otp_verify:
                            opt_random = randint(0,999999)
                            otp_create, otp_true = OneTimePassword.objects.get_or_create(user=user, otp=opt_random)
                            res = {"result": {"status": "True", "opt_data": otp_create.otp}}
                        else:
                            res = {"result": {"status": "True", "opt_data": otp_verify.otp}}
                        return HttpResponse(simplejson.dumps(res), content_type="application/json")
                    else:
                        res = {"result": {"status": "False", "message": "User Does not exist "}}
                        return HttpResponse(simplejson.dumps(res), content_type="application/json")
                else:
                    res = {"result": {"status": "False", "message": "Username Not entered"}}
                    return HttpResponse(simplejson.dumps(res), content_type="application/json")
            else:
                res = {"result": {"status": "False", "message": "Method Not allowed"}}
                return HttpResponse(simplejson.dumps(res), content_type="application/json")  
        except:
            res = {"result": {"status": "False", "message": "Something Went wrong"}}
            return HttpResponse(simplejson.dumps(res), content_type="application/json")

    def verify_otp(self, request, **kwargs):
        #import pdb;pdb.set_trace()
        try:
            if request.method == 'POST':
                username = request.POST['username']
                otp = request.POST["otp"]
                if username:
                    user = User.objects.filter(username=username).first()
                    if user:
                        otp_verify = OneTimePassword.objects.filter(user=user, otp=otp).first()
                        if otp_verify:
                            otp_verify.is_active=False
                            otp_verify.save()
                            res = {"result": {"status": "True", "message": "Verify otp success"}}
                            return HttpResponse(simplejson.dumps(res), content_type="application/json")
                        else:
                            res = {"result": {"status": "False", "message": "Otp verification Failed"}}
                            return HttpResponse(simplejson.dumps(res), content_type="application/json")
            else:
                res = {"result": {"status": "False", "message": "Method Not allowed"}}
                return HttpResponse(simplejson.dumps(res), content_type="application/json")
            
        except:
            res = {"result": {"status": "False", "message": "Something Went wrong"}}
            return HttpResponse(simplejson.dumps(res), content_type="application/json")


