import io
import json
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator

with io.open('yelp_config_secret.json') as cred:
    creds = json.load(cred)
    auth = Oauth1Authenticator(**creds)
    client = Client(auth)

params = {
    'term': 'food',
    'lang': 'fr'
}

response = client.search('Chicago',**params)
print response
