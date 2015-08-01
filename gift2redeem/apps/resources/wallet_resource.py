from django.contrib.auth.models import User
from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.utils import trailing_slash
from tastypie.authentication import SessionAuthentication
from tastypie.authorization import Authorization
from tastypie.http import HttpUnauthorized
from tastypie import fields
from tastypie.resources import ModelResource

from gift2redeem.apps.models import *


class WalletCardResource(ModelResource):
	cards = tastypie.fields.ToManyField(Card, 'cards', full=True)
	class Meta:
        resource_name = 'wallet'
        queryset = WalletCard.objects.all()
        allowed_methods = ['get','post']

