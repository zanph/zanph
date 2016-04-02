#!/usr/bin/env/python
import time
import random
from threading import Thread, Lock
myLock = Lock()

import zmq

#import zhelpers

def serviceA(context=None):
    #reuse context if it exists, otherwise make a new one
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
        elif message == "END":
            break
        else:
            with myLock:
                print "the server has the wrong identities!"
            break

def serviceB(context=None):
    #reuse context if it exists, otherwise make a new one
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
        elif message == "END":
            break
        else:
            with myLock:
                print "the server has the wrong identities!"
            break

def frontendClient(context=None):
    #reuse context if it exists, otherwise make a new one
    context = context or zmq.Context.instance()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5559")
    socket.RCVTIMEO = 2000 #we will only wait 2s for a reply
    while True:
        #randomly request either service A or service B
        serviceRequest = random.choice([b'Service A',b'Service B'])
        with myLock:
            print "client wants %s" % serviceRequest
        socket.send(serviceRequest)
        try:
            reply = socket.recv()
        except Exception as e:
            print "client timed out"
            break
        if not reply:
            break
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
    print "zmq server running on localhost:5559/5560"

    #now setup our client and services
    Thread(target=serviceA).start()
    Thread(target=serviceB).start()
    #let the services fire up before the client starts requesting
    time.sleep(1)
    Thread(target=frontendClient).start()


    for _ in range(6):
        clientServiceRequest = frontend.recv_multipart()
        clientIdentity = clientServiceRequest[0]
        if clientServiceRequest[2] == 'Service A':
            backend.send_multipart([b'A',b'Service A']) #[identity,data]
            identity,reply = backend.recv_multipart()
            with myLock:
                print "Server got reply:"
                print reply
            frontend.send_multipart([clientIdentity,b'',reply])
        elif clientServiceRequest[2] == 'Service B':
            backend.send_multipart([b'B',b'Service B']) #[identity,data]
            identity,reply = backend.recv_multipart()
            with myLock:
                print "Server got reply:"
                print reply
            frontend.send_multipart([clientIdentity,b'',reply])

    backend.send_multipart([b'A',b'END'])
    backend.send_multipart([b'B',b'END'])

    #cleanup
    frontend.close()
    backend.close()
    context.term()

if __name__ == "__main__":
    main()
