from decimal import Decimal
import dateutil.parser
import simplejson

from django.conf.urls import url
from django.contrib.auth.models import User
from django.http import Http404
from django.http import HttpResponse

from tastypie.utils import trailing_slash
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer

from gift2redeem.apps.retailers.models import *
from gift2redeem.apps.resources import UserResource

class RetailerCardResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    class Meta:
        queryset = RetailerCard.objects.all()
        resource_name = 'card'
        allowed_methods = ['get','post']
        fields = ['number', 'pin', 'expiration_date']

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/$" % (self._meta.resource_name), self.wrap_view('get_cards'), name="api_get_cards"),
            url(r"^(?P<resource_name>%s)/add_cards/$" % (self._meta.resource_name), self.wrap_view('add_cards'), name="api_add_cards"),

        ]

    def get_cards(self, request, **kwargs):
        self.method_check(request, allowed=['get'])

        try:
            queryset = Card.objects.all()
        except:
            raise Http404("Sorry, no results on that page.")

        objects = []

        for result in queryset:
            bundle = self.build_bundle(obj=result, request=request)
            bundle = self.full_dehydrate(bundle)
            objects.append(bundle)

        object_list = {
            'result': objects,
        }

        self.log_throttled_access(request)
        return self.create_response(request, object_list)

    def add_cards(self, request, **kwargs):
        import pdb;pdb.set_trace()
        try:
            if request.method.lower() == 'post':
                username = request.POST['username']
                user_obj = User.objects.filter(username=username).first()
                name = request.POST["name"]

                number = request.POST["number"]
                #user = User.objects.filter(username=request.POST["user"]).first()
                retailer = Retailer.objects.filter(name=request.POST["retailer"]).first()
                pin = request.POST["pin"]
                #expiration_date = dateutil.parser.parse(request.POST["expiration_date"])
                expiration_date = '2015-05-08'
                cp = CardProfile()
                cp.retailer = retailer 
                cp.name = name
                cp.save()
                if cp:
                    add_card_obj = Card.objects.filter(
                        card_profile=cp,
                        number=number,
                        pin=pin)
                    if not add_card_obj:
                        add_card_obj, cre_card = Card.objects.get_or_create(
                            card_profile=cp,
                            number=number,
                            pin=pin,
                            expiration_date=expiration_date)
                    if add_card_obj:
                        card_b = CardBalance()
                        card_b.card = add_card_obj
                        card_b.balance = '50'
                        card_b.save()

                    if add_card_obj and user_obj:
                        wallet_card = WalletCard.objects.filter(card=add_card_obj, user=user_obj)
                        if not wallet_card:
                            wallet_obj, wall = WalletCard.objects.get_or_create(card=add_card_obj, user=user_obj)
                            res = {"result": {"status": "True", "message": "Card Entered Success"}}
                            return HttpResponse(simplejson.dumps(res), content_type="application/json")
                        else:
                            res = {"result": {"status": "True", "message": "Card Already mapped"}}
                            return HttpResponse(simplejson.dumps(res), content_type="application/json")
            else:
                res = {"result": {"status": "False", "message": "User Not allowed"}}
                return HttpResponse(simplejson.dumps(res), content_type="application/json")
            
            
        except:
            res = {"result": {"status": "False", "message": "User Not allowed"}}
            return HttpResponse(simplejson.dumps(res), content_type="application/json")

