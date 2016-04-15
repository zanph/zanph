import io
import zmq
import json
import sys
import pprint
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator

with io.open('../yelp_config_secret.json') as cred:
    creds = json.load(cred)
    auth = Oauth1Authenticator(**creds)
    client = Client(auth)

def Server(context):
    context = context or zmq.Context().instance()
    # Socket facing clients
    frontend = context.socket(zmq.ROUTER)
    frontend.bind("tcp://*:5559")

    # Socket facing services
    backend  = context.socket(zmq.ROUTER)
    backend.bind("tcp://*:5560")
    print "zmq server running on localhost:5559/5560"

    poll_workers = zmq.Poller()
    poll_workers.register(backend, zmq.POLLIN)

    poll_both = zmq.Poller()
    poll_both.register(backend, zmq.POLLIN)
    poll_both.register(frontend, zmq.POLLIN)

    clients = [[]]
    while True:
        if clients:
            sockets = dict(poll_both.poll())
        else:
            sockets = dict(poll_workers.poll())
        if sockets.get(frontend) == ZMQ.POLLIN:
            clientRequest = frontend.recv_multipart()
            clients.append(clientRequest[0]) #push client into queue
        if sockets.get(backend) == ZMQ.POLLIN:
            #workers want data
            msg = backend.recv_multipart()
            workerIdentity = msg[0]
            clientIdentity,request = clients.pop(0)

            workRequest = [workerIdentity, '',request]
            backend.send_multipart(workRequest)
            yelpResponse = backend.recv_multipart()[2]

            #fulfill frontend request
            frontendResponse = [clientIdentity,'',yelpResponse]
            frontend.send_multipart(frontendResponse)


def worker(client,location,query):
    """use the yelp api to find the desired place at a location"""

    #reuse context if it exists, otherwise make a new one
    context = context or zmq.Context.instance()
    service = context.socket(zmq.ROUTER)

    #identify worker
    service.setsockopt(zmq.IDENTITY,b'A')
    service.connect("tcp://localhost:5560")
    while True:
        #send our identity
        service.send('')
        message = service.recv()
        with myLock:
            print "yelp worker got:"
            print message
        if message != "":
            response = queryYelp(client, request)
            service.send(response)
        elif message == "END":
            break
        # else:
        #     with myLock:
        #         print "the server has the wrong identities!"
        #     break

def queryYelp(request):
    if request is None:
        print "error: empty yelp request!"
        return None
    """todo: decide request format"""
    #user should be able to pick the language
    params = {

    }
    response = client.search(location,**params)
    print "Got response, printing:"

    # for business in response.businesses:
    #     print "business: " + business.name
    #     print str(business.rating) + " stars with " +\
    #         str(business.review_count) + " reviews."
    #     print "phone: " + str(business.phone)
    #     print "address: "
    #     for address_line in business.location.display_address:
    #         print address_line


if __name__ == '__main__':
    main()
