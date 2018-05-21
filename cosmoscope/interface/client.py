import logging

import gevent
import msgpack
import json
from zerorpc import Client, Puller, Pusher, Subscriber
from zmq.error import ZMQError

from ..utils.singleton import Singleton


class SubscriberAPI(Subscriber, metaclass=Singleton):
    def __init__(self, client=None, *args, **kwargs):
        super(SubscriberAPI, self).__init__(*args, **kwargs)
        # Setup pusher service
        self.client = client


def launch(subscriber_address=None, client_address=None):
    logging.info("Starting services...")

    subscriber_address = subscriber_address or "tcp://127.0.0.1:4243"
    client_address = client_address or "tcp://127.0.0.1:4242"

    # Setup the client service
    client = Client()
    client.connect(client_address)

    # Setup the subscriber service
    subscriber = SubscriberAPI(client)
    subscriber.bind(subscriber_address)

    gevent.spawn(subscriber.run)

    logging.info(
        "Client is now sending on %s and listening on %s.",
        client_address, subscriber_address)

    # test
    trigger = gevent.event.Event()
    trigger.wait(1)
    subscriber.client.load_data(
        "/Users/nearl/projects/specutils/specutils/tests/data/L5g_0355+11_Cruz09.fits",
        "wcs1d-fits")
    trigger.wait(1)
