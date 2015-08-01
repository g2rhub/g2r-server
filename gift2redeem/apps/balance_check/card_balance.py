from BeautifulSoup import *
from soupselect import *

import mechanicalsoup, re, urllib


def get_card_balance(card):
    if card.retailer.balance_check_function:
        try:
            return eval(card.retailer.balance_check_function + "(card)")
        except:
            pass
    return None


def get_best_buy_card_balance(card):
    data = urllib.urlencode({
    "GCNumber1": card.number,
    "GCSecurityNumber1": card.pin,
    "numgcshowing": 1,
    "numbuttonpushed": 1
    })

    try:
        u = urllib.urlopen("https://www.bestbuybusiness.com/bbfb/en/US/adirect/bestbuy?cmd=BBFBGiftCardBalance", data)
        html = u.read()
        soup = BeautifulSoup(html)
        raw_element = soup.findAll(name="input", recursive=True, attrs={"name": "GCBalance1"})[0]
        return float(raw_element["value"])

    except:
        return 0.00


def get_target_card_balance(card):
    print "XXX"
    data = urllib.urlencode({
    "storeId": 10151,
    "catalogId": 10051,
    "langId": -1,
    "guestUserpage": True,
    "gcCardNumber": card.number,
    "gcAccessNumber": card.pin,
    "cancelUrl": "http://www.target.com/c/target-giftcards-gift-cards/-/N-5xsxt",
    "fromManageWallet": "N"
    })

    try:
        u = urllib.urlopen("https://www-secure.target.com/GuestGCCheckGiftCardBalCmd", data)
        soup = BeautifulSoup(u.read())
        raw_balance = str(select(soup, 'td.gcBalance')[0].contents[0])
        parsed_balance = re.findall(r'[\d]+\.[\d]+', raw_balance)[0]
    except:
        parsed_balance = 0.00

    return parsed_balance


def get_oldnavy_card_balance(card):
    try:

        browser = mechanicalsoup.Browser()
        html = browser.get("https://secure-oldnavy.gap.com/buy/checkout_giftCardBalance.do?giftCardNumber=%s&pin=%s" % (
        card.number, card.pin)).text
        m = re.search("<em>\&#36;(.*)</em>", html)
        balance = str(m.group(1))
    except:
        balance = 0.00

    return balance


def get_toys_r_us_card_balance(card):
    try:
        browser = mechanicalsoup.Browser()
        page = browser.get("https://www.toysrus.com/checkout/checkAccountBalance.jsp")
        form = page.soup.form
        form.find("input", {"name": "accountNumber"})["value"] = card.number
        form.find("input", {"name": "pin"})["value"] = card.pin
        form.find("input", {"name": "step"})["value"] = "giftcardBalance"
        response = browser.submit(form, "https://www.toysrus.com/coreg/index.jsp").text
        m = re.search("(\d+\.\d\d)", response)
        balance = str(m.group(1))
    except:
        balance = 0.0
    return balance