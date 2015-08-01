import json
 
from tastypie.exceptions import TastypieError
from tastypie.http import HttpBadRequest
import re
from gift2redeem.apps.balance_check.card_balance import *

MINIMUM_PASSWORD_LENGTH = 6
REGEX_VALID_PASSWORD = (
    ## Don't allow any spaces, e.g. '\t', '\n' or whitespace etc.
    r'^(?!.*[\s])'
    ## Check for a digit
    '((?=.*[\d])'
    ## Check for an uppercase letter
    '(?=.*[A-Z])'
    ## check for special characters. Something which is not word, digit or
    ## space will be treated as special character
    '(?=.*[^\w\d\s])).'
    ## Minimum 8 characters
    '{' + str(MINIMUM_PASSWORD_LENGTH) + ',}$')
 
 
def validate_password(password):
    #if re.match(REGEX_VALID_PASSWORD, password):
    if len(password) > 4:
        return True
    return False
 
class CustomBadRequest(TastypieError):
    """
    This exception is used to interrupt the flow of processing to immediately
    return a custom HttpResponse.
    """
 
    def __init__(self, code="", message=""):
        self._response = {
            "error": {"code": code or "not_provided",
                      "message": message or "No error message was provided."}}
 
    @property
    def response(self):
        return HttpBadRequest(
            json.dumps(self._response),
            content_type='application/json')


def card_balance(card_type, number, pin):
    res = 0.00
    if card_type != '' and number != '' and pin != '':
        card={}
        card['number']=number
        card['pin']=pin
        if card_type =='Target':
            res=get_target_card_balance(card)
        elif card_type =='BestBuy':
            res=get_best_buy_card_balance(card)
        elif card_type =='OldNavy':
            res=get_oldnavy_card_balance(card)
        elif card_type =='Toysrus': 
            res=get_toys_r_us_card_balance(card)
        return res
    else:
        return res
