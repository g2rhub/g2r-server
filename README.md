g2r-server
==========

Setup your local environment
-----
* Install Python 2.7+ (Python 3 will NOT work)
* Ensure pip is installed
* Install virtualenv http://docs.python-guide.org/en/latest/dev/virtualenvs/
* Install PostgreSQL http://www.postgresql.org/download/
* Clone server repository (git clone https://github.com/g2rhub/g2r-server.git)
* Change directory to server (cd g2r-server)
* Create a new virtualenv (virtualenv venv)
* Activate virtualenv (source venv/bin/activate/)
* Install dependencies via pip (pip install -r requirements.txt)
* Create gift2redeem database in PostgreSQL
* Set database environment variable (export DATABASE_URL='postgres://your_db_user:@localhost:5432/gift2redeem')
* Create all database tables. Make sure to create a super user. (python manage.py syncdb)
* Start up the development server (python manage.py runserver)
* Access development server (http://localhost:8000/admin/)

Setup a Retailer
------
* Log into the development serve (http://localhost:8000/admin/)
* Create a retailer using the GUI (Set the name to Target)
* Set the deals URL to (http://slickdeals.net/newsearch.php?daysprune=-1&forumchoice%5B%5D=9&forumchoice%5B%5D=4&q=target&rss=1)
* Load Target locations (python manage.py scrape_target_locations)
* Load deals (python manage.py get_deals)

Start testing out the API
------
Retrieves a username and api_key token to be used with all subsequent requests  
http://localhost:8000/api/v1/account/

Add a card (POST)
------
/api/v1/card/?username=NDN39UP2J32CJU8L&api_key=d9b1080119e762d67dc5da636c4b42156de52f10
```
{
  "is_active" : true,
  "retailer" : 1,
  "numer" : 10010101010,
  "pin" : 1234
}
```

Update a card (PUT)
------
/api/v1/card/6/?username=NDN39UP2J32CJU8L&api_key=d9b1080119e762d67dc5da636c4b42156de52f10
```
{
  "is_active" : true,
  "retailer" : 1,
  "numer" : 10010101010,
  "pin" : 1234
}
```

Delete a card (DELETE)
------
/api/v1/card/6/?username=NDN39UP2J32CJU8L&api_key=d9b1080119e762d67dc5da636c4b42156de52f10

All Retailer Totals (GET)
------
Retrieve the totals for all retailers/user's cards  
http://localhost:8000/api/v1/retailer/?api_key=d9b1080119e762d67dc5da636c4b42156de52f10&username=NDN39UP2J32CJU8L&format=json

Single Retailer Totals (GET)
------
Retrieve the totals for all retailers/user's cards  
http://localhost:8000/api/v1/retailer/1/?api_key=d9b1080119e762d67dc5da636c4b42156de52f10&username=NDN39UP2J32CJU8L&format=json


Offer Search (GET)
------
Retrieves the 20 offers from retailers close by. Offers are ranked by purchase price and available funds by retailer.  
http://localhost:8000/api/v1/offer?lat=37.2361&lng=-121.9617&api_key=d9b1080119e762d67dc5da636c4b42156de52f10&username=NDN39UP2J32CJU8L&format=json
