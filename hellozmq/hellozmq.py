import time
import random
from threading import Thread, Lock
myLock = Lock()

import zmq

import zhelpers

def serviceA(context=None):
    context = context or zmq.Context.instance()
    service = context.socket(zmq.DEALER)

    #identify worker
    service.setsockopt(zmq.IDENTITY,b'A')
    service.connect("tcp://localhost:5560")
    while True:
        message = service.recv()
        with myLock:
            print "Service A got:"
            print message
        if message == "Service A":
            #do some work
            time.sleep(random.uniform(0,0.5))
            service.send(b"Service A did your laundry")
        else:
            with myLock:
                print "the server has the wrong identities!"
            break

def serviceB(context=None):
    context = context or zmq.Context.instance()
    service = context.socket(zmq.DEALER)

    #identify worker
    service.setsockopt(zmq.IDENTITY,b'B')
    service.connect("tcp://localhost:5560")
    while True:
        message = service.recv()
        with myLock:
            print "Service B got:"
            print message
        if message == "Service B":
            #do some work
            time.sleep(random.uniform(0,0.5))
            service.send(b"Service B cleaned your room")
        else:
            with myLock:
                print "the server has the wrong identities!"
            break

def frontendClient(context=None):
    #randomly request either service A or service B
    context = context or zmq.Context.instance()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5559")

    while True:
        serviceRequest = random.choice([b'Service A',b'Service B'])
        with myLock:
            print "client wants %s" % serviceRequest
        socket.send(serviceRequest)
        reply = socket.recv()
        with myLock:
            print "Client got reply: "
            print reply
            print
        #take a nap
        time.sleep(1)

def main():
    """ main method """
    print "hello!"
    context = zmq.Context()

    # Socket facing clients
    frontend = context.socket(zmq.ROUTER)
    frontend.bind("tcp://*:5559")

    # Socket facing services
    backend  = context.socket(zmq.ROUTER)
    backend.bind("tcp://*:5560")

    #equivalent to request reply broker from zguide.zeromq.org
    #zmq.proxy(frontend, backend)

    """ i.e., zmq.proxy is equivalent to: """
    # # Initialize poll set
    # poller = zmq.Poller()
    # poller.register(frontend, zmq.POLLIN)
    # poller.register(backend, zmq.POLLIN)
    #
    # # Switch messages between sockets
    # while True:
    #     socks = dict(poller.poll())
    #
    #     if socks.get(frontend) == zmq.POLLIN:
    #         message = frontend.recv_multipart()
    #         backend.send_multipart(message)
    #
    #     if socks.get(backend) == zmq.POLLIN:
    #         message = backend.recv_multipart()
    #         frontend.send_multipart(message)

    print "zmq proxy running"

    #now setup our client and services
    Thread(target=serviceA).start()
    Thread(target=serviceB).start()
    #let the services fire up before the client starts requesting
    time.sleep(1)
    Thread(target=frontendClient).start()
    #print "started threads"


    while True:
        clientServiceRequest = frontend.recv_multipart()
        clientIdentity = clientServiceRequest[0]
        if clientServiceRequest[2] == 'Service A':
            backend.send_multipart([b'A',b'Service A']) #[identity,data]
            identity,reply = backend.recv_multipart()
            with myLock:
                print "Server got reply:"
                print reply
            frontend.send_multipart([clientIdentity,b'',reply])
            print
        elif clientServiceRequest[2] == 'Service B':
            backend.send_multipart([b'B',b'Service B']) #[identity,data]
            identity,reply = backend.recv_multipart()
            with myLock:
                print "Server got reply:"
                print reply
            frontend.send_multipart([clientIdentity,b'',reply])
            print

    # We never get here...
    frontend.close()
    backend.close()
    context.term()

if __name__ == "__main__":
    main()
