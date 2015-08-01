from django.contrib.auth.models import User
from gift2redeem.apps.retailers.models import *
from tastypie import fields
from tastypie.resources import ModelResource


class RetailerResource(ModelResource):
    class Meta:
        queryset = Retailer.objects.all()
        resource_name = 'retailer'
        fields = ['name', 'description', 'site_url']
        allowed_methods = ['get','post']
