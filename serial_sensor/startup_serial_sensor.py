import json
import serial
import logging
import warnings
import os
import time
import paho.mqtt.client as mqtt
from threading import Timer
from ptb220_decode import PTB220ascii
from ptu300_decode import PTU300ascii
from windsonic_decode import Windsonic
from raingauge_decode import RainGauge


class SerialSensor:
    def __init__(self):
        port = os.getenv('PORT', '/dev/tty.usbserial-AI02FCVO')
        baud = int(os.getenv('BAUD', '9600'))
        self.sensor = os.getenv('SENSOR', 'PTB220')
        self.qos = int(os.getenv('MQTT_QOS', 1))

        if self.sensor == 'PTB220':
            self.decoder = PTB220ascii()
        elif self.sensor == 'PTU300':
            self.decoder = PTU300ascii()
        elif self.sensor == 'WINDSONIC':
            self.decoder = Windsonic()
        elif self.sensor == 'RAINGAUGE':
            self.decoder = RainGauge()

        logging.info('Setting up sensor: ' + self.sensor)
        self.serial_port = serial.Serial(port, baud, timeout=1.0)
        logging.info('Serial port: ' + str(self.serial_port))

        logging.info('Connecting to local MQTT broker....')
        # variable for the state of the connection
        self.connected = False
        # allow time for networking to be established
        time.sleep(5)
        # create new instance
        self.client = mqtt.Client(self.sensor + '_serialclient')
        # attach function to callback
        self.client.on_connect = self.on_connect
        # connect to broker
        self.client.connect(
            os.getenv('MQTT_BROKER', 'localhost'))
        # start the loop
        self.client.loop_start()

        # Wait for connection
        while not self.connected:
            time.sleep(0.1)

        self.serialport_scan()

        while True:
            time.sleep(1)

    def on_connect(self, mqtt_client, userdata, flags, rc):
        if rc == 0:
            # Connected
            logging.info('Connected to local MQTT broker')
            self.connected = True
        else:
            logging.info("MQTT Connection failed")

    def serialport_scan(self):
        # Read a line of incoming data from the assigned serial port, then
        # pass the data onto a processor for extraction of the data values
        try:
            data_bytes = self.serial_port.readline()
            dataline = str(data_bytes)
            if (len(dataline)) > 5:
                message = self.decoder.data_decoder(dataline)
                if message is not None:
                    logging.info(message)
                    self.publish_mqtt(json.dumps(message))
        except serial.SerialException as error:
            warnings.warn("Serial port error: " + str(error), Warning)
        # Asynchronously schedule this function to run again in 1 seconds.
        Timer(1, self.serialport_scan).start()

    def publish_mqtt(self, data):
        self.client.publish('sensors/' + self.sensor, data, self.qos)


if __name__ == "__main__" and os.getenv('ENABLE', 'true') == 'true':
    logging.basicConfig(level=logging.INFO)
    logging.captureWarnings(True)
    logging.info('Starting serial port data collector....')
    SerialSensor()
