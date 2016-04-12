import io
import json
import sys
import pprint
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator


def main():
    print "authenticating"
    with io.open('yelp_config_secret.json') as cred:
        creds = json.load(cred)
        auth = Oauth1Authenticator(**creds)
        client = Client(auth)

    location, query = sys.argv[1], sys.argv[2]

    if not location and query:
        print "Error - usage: findmesomething.py location query"
        sys.exit

    print "Looking for %s in %s on yelp!" %(query,location)




    queryYelp(client,sys.argv[1],sys.argv[2])



def queryYelp(client,location,query):
    """use the yelp api to find the desired place at a location"""

    #user should be able to pick the language
    params = {
        'term' : query,
        'lang' : 'en'
    }
    response = client.search(location,**params)
    print "Got response, printing:"

    for business in response.businesses:
        print "business: " + business.name
        print str(business.rating) + " stars with " +\
            str(business.review_count) + " reviews."
        print "phone: " + str(business.phone)
        print "address: "
        for address_line in business.location.display_address:
            print address_line


if __name__ == '__main__':
    main()
