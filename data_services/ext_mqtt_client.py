import logging
import time
import paho.mqtt.client as paho
from paho import mqtt


# with this callback you can see if your publish was successful
def on_publish(userdata, mid, properties=None):
    logging.info("Ext MQTT mid: " + str(mid))


# print which topic was subscribed to
def on_subscribe(userdata, mid, granted_qos, properties=None):
    logging.info("Ext MQTT Subscribed: " + str(mid) + " " + str(
        granted_qos))


class ExtMQTTclient:
    """Create an MQTT client for publishing messages to an external
    MQTT broker in addition to the internal broker (if required)."""
    logging.basicConfig(level=logging.INFO)
    logging.captureWarnings(True)
    connected = False

    def __init__(self, host, client_id, port, user, password):
        # global variable for the state of the connection
        self.connected = False
        # allow time for networking to be established
        time.sleep(4)
        # create new instance
        self.client = paho.Client(
            client_id=client_id, userdata=None, protocol=paho.MQTTv5)
        # attach function to callback
        self.client.on_connect = self.on_connect
        # attach function to callback
        self.client.on_message = self.on_message
        self.client.on_subscribe = on_subscribe

        # enable TLS for secure connection
        self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        # set username and password
        self.client.username_pw_set(user, password)
        # connect to broker
        self.client.connect(host, port)
        # start the loop
        self.client.loop_start()

        # Wait for connection
        while not self.connected:
            time.sleep(0.1)

    def on_connect(self, mqtt_client, userdata, flags, rc, properties=None):
        if rc == 0:
            # Connected
            self.connected = True
            logging.info("Ext MQTT CONNACK received with code %s." % rc)
        else:
            logging.info("Ext MQTT Connection failed")

    def on_message(self, mqtt_client, userdata, msg):
        logging.info(msg.topic + " " + str(msg.qos) + " " + str(
            msg.payload.decode("utf-8", "ignore")))
        # msg_in = json.loads(msg_decode)  # decode json data
        self.client.publish(msg.topic, str(msg.payload.decode(
            "utf-8", "ignore")))
