import json
import logging
import os
import time
import paho.mqtt.client as mqtt
from services import Services
from ext_mqtt_client import ExtMQTTclient


class DataServices:
    logging.basicConfig(level=logging.INFO)
    logging.captureWarnings(True)
    connected = False

    def __init__(self):
        self.dewpoint = None
        self.pressure = None
        self.qnh = None
        self.qfe = None
        self.tendency = None
        self.trend = None
        self.temperature = None
        self.temp2 = None
        self.daymax = None
        self.daymax_calc = None
        self.nightmin = None
        self.nightmin_calc = None
        self.humidity = None
        self.winddir = None
        self.windspeed = None
        self.windgust10m = None
        self.windgust_calc10m = None
        self.winddir10m = None
        self.winddir_calc10m = None
        self.windspeed10m = None
        self.windspeed_calc10m = None
        self.rainrate = None
        self.rainaccum = None
        self.battvolts = None
        self.paneltemp = None

        self.site_id = os.getenv('SITE_ID', 'mpduk')
        self.enable_ext_mqtt = os.getenv('EXT_MQTT_ENABLE', 'false')
        self.use_calc_winds = os.getenv('USE_CALC_WINDS', 'true')
        self.use_calc_maxmin_temps = os.getenv('USE_CALC_MAXMIN_TEMPS', 'true')

        if self.enable_ext_mqtt == 'true':
            host = os.getenv('EXT_MQTT_HOST',
                             '0b1310a3a837400f837a44119cdbc2ab.s1.eu.hivemq'
                             '.cloud')
            client_id = os.getenv('EXT_MQTT_CLIENT_ID', 'metpod')
            port = int(os.getenv('EXT_MQTT_PORT', 8883))
            user = os.getenv('EXT_MQTT_USER', 'metpod')
            password = os.getenv('EXT_MQTT_PASSWORD')
            self.ext_mqtt_qos = int(os.getenv('EXT_MQTT_QOS', '1'))

            self.ext_mqtt = ExtMQTTclient(
                host, client_id, port, user, password)

        Services(self)

        if os.getenv('ENABLE', 'true') == 'true':
            # global variable for the state of the connection
            self.connected = False
            # allow time for networking to be established
            time.sleep(8)
            # create new instance
            self.client = mqtt.Client('data_services')
            # attach function to callback
            self.client.on_connect = self.on_connect
            # attach function to callback
            self.client.on_message = self.on_message
            # connect to broker
            self.client.connect(
                os.getenv('MQTT_BROKER', 'localhost'))
            # start the loop
            self.client.loop_start()

            # Wait for connection
            while not self.connected:
                time.sleep(0.1)

            # subscribe to all site topics
            self.client.subscribe([('sensors/#', 1)])

            while True:
                time.sleep(1)

    def on_connect(self, mqtt_client, userdata, flags, rc):
        if rc == 0:
            # Connected
            self.connected = True
        else:
            logging.info("MQTT Connection failed")

    def on_message(self, mqtt_client, userdata, msg):
        topic = msg.topic
        external_topic = self.site_id + '/' + topic
        msg_decode = str(msg.payload.decode("utf-8", "ignore"))
        msg_in = json.loads(msg_decode)  # decode json data
        logging.debug(topic + ' ' + str(msg_in))

        if self.enable_ext_mqtt == 'true':
            self.ext_mqtt.client.publish(
                external_topic, msg_decode, self.ext_mqtt_qos)

        if 'winddir' in msg_in:
            winddir = msg_in['winddir']
            if winddir != 'nan' and winddir != '' and winddir is not None:
                self.winddir = int(round(float(winddir), 0))
            
        if 'windspeed' in msg_in:
            windspeed = msg_in['windspeed']
            if windspeed != 'nan' and windspeed != '' \
                    and windspeed is not None:
                self.windspeed = int(round(float(windspeed), 0))
        
        if 'temperature' in msg_in:
            self.temperature = float(msg_in['temperature'])
            
        if 'humidity' in msg_in:
            self.humidity = float(msg_in['humidity'])
            
        if 'dewpoint' in msg_in:
            self.dewpoint = float(msg_in['dewpoint'])
        
        if 'pressure' in msg_in:
            self.pressure = float(msg_in['pressure'])

        if 'qnh' in msg_in:
            self.qnh = float(msg_in['qnh'])

        if 'qfe' in msg_in:
            self.qfe = float(msg_in['qfe'])

        if 'tendency' in msg_in:
            self.tendency = float(msg_in['tendency'])

        if 'trend' in msg_in:
            self.trend = float(msg_in['trend'])

        if 'batt_volts' in msg_in:
            self.battvolts = float(msg_in['battvolts'])

        if 'panel_temp' in msg_in:
            self.paneltemp = float(msg_in['paneltemp'])

        if 'rainrate' in msg_in:
            self.rainrate = float(msg_in['rainrate'])

        if 'rainaccum' in msg_in:
            self.rainaccum = float(msg_in['rainaccum'])

        if 'temp2' in msg_in:
            self.temp2 = float(msg_in['temp2'])

        if self.use_calc_maxmin_temps:
            if 'daymax_calc' in msg_in \
                    and msg_in['daymax_calc'] is not None:
                self.daymax = float(msg_in['daymax_calc'])

            if 'nightmin_calc' in msg_in \
                    and msg_in['nightmin_calc'] is not None:
                self.nightmin = float(msg_in['nightmin_calc'])
        else:
            if 'day_max' in msg_in:
                self.daymax = float(msg_in['daymax'])

            if 'nightmin' in msg_in:
                self.nightmin = float(msg_in['nightmin'])

        if self.use_calc_winds:
            if 'windgust_calc10m' in msg_in:
                windgust10m = msg_in['windgust_calc10m']
                if windgust10m != 'nan' and windgust10m != '' \
                        and windgust10m is not None:
                    self.windgust10m = int(round(float(windgust10m), 0))

            if 'winddir_calc10m' in msg_in:
                winddir10m = msg_in['winddir_calc10m']
                if winddir10m != 'nan' and winddir10m != '' \
                        and winddir10m is not None:
                    self.winddir10m = int(round(float(winddir10m), 0))

            if 'windspeed_calc10m' in msg_in:
                windspeed10m = msg_in['windspeed_calc10m']
                if windspeed10m != 'nan' and windspeed10m != '' \
                        and windspeed10m is not None:
                    self.windspeed10m = int(round(float(windspeed10m), 0))
        else:
            if 'windgust10m' in msg_in:
                windgust10m = msg_in['windgust10m']
                if windgust10m != 'nan' and windgust10m != '' \
                        and windgust10m is not None:
                    self.windgust10m = int(round(float(windgust10m), 0))

            if 'winddir10m' in msg_in:
                winddir10m = msg_in['winddir10m']
                if winddir10m != 'nan' and winddir10m != '' \
                        and winddir10m is not None:
                    self.winddir10m = int(round(float(winddir10m), 0))

            if 'windspeed10m' in msg_in:
                windspeed10m = msg_in['windspeed10m']
                if windspeed10m != 'nan' and windspeed10m != '' \
                        and windspeed10m is not None:
                    self.windspeed10m = int(round(float(windspeed10m), 0))


if __name__ == "__main__":
    DataServices()
