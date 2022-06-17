import json
import logging
import os
import time
import paho.mqtt.client as mqtt
from datetime import datetime, timezone
from wind_processor import WindProcessor
from maxmintemp import MAXMINTEMP
from pressure_calcs import PRESSURECALCS


class DataProcessor:
    """Provides methods that take 'as read' instantaneous data values,
    undertake data processing functions to determine averages, max/min's etc.
    for subsequent MQTT publishing"""
    logging.basicConfig(level=logging.INFO)
    logging.captureWarnings(True)
    connected = False

    def __init__(self):
        self.qos = 1
        self.wind_dir = None
        self.wind_speed = None
        self.temperature = None
        self.maxmintemp = MAXMINTEMP()
        self.windprocessor = WindProcessor()
        self.pressure_calcs = PRESSURECALCS()

        if os.getenv('ENABLE', 'true') == 'true':
            # variable for the state of the connection
            self.connected = False
            # allow time for networking to be established
            time.sleep(8)
            # create new instance
            self.client = mqtt.Client('data_processor')
            # attach function to callback
            self.client.on_connect = self.on_connect
            # attach function to callback
            self.client.on_message = self.on_message
            # connect to broker
            self.client.connect(os.getenv('MQTT_BROKER', 'localhost'))
            # start the loop
            self.client.loop_start()
            # wait for connection
            while not self.connected:
                time.sleep(0.1)

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
        msg_decode = str(msg.payload.decode("utf-8", "ignore"))
        # decode json data
        msg_in = json.loads(msg_decode)

        if 'winddir' and 'windspeed' in msg_in:
            winddir = msg_in['winddir']
            windspeed = msg_in['windspeed']
            self.wind_handler(winddir, windspeed)

        if 'temperature' in msg_in:
            temperature = msg_in['temperature']
            self.maxmin_temp_handler(temperature)
            # set the temperature for use in pressure QNH/QFE calculation
            self.pressure_calcs.temperature = float(temperature)

        if 'pressure' in msg_in:
            pressure = msg_in['pressure']
            self.pressure_calcs_handler(pressure)

    def wind_handler(self, wind_dir, wind_speed):
        """Pass the current instantaneous wind speed and direction to
        a wind processor to enable calculation of mean values which can then
        be published."""
        if wind_dir != 'nan' or None and wind_speed != 'nan' or None:
            windcalcs = {}
            wind_10m = self.windprocessor.process_wind_10min(
                int(float(wind_dir)), int(float(wind_speed)))
            windcalcs.update({'winddir_calc10m': wind_10m[0]})
            windcalcs.update({'windspeed_calc10m': wind_10m[1]})
            windcalcs.update({'windgust_calc10m': wind_10m[2]})
            obstime = (datetime.now(timezone.utc)).isoformat()
            windcalcs.update({'obstime': obstime})
            topic = 'sensors/windcalcs'
            self.client.publish(topic, json.dumps(windcalcs), self.qos)

    def maxmin_temp_handler(self, data):
        """Pass the current air temperature to a max/min processor to enable
        determination of day max/night min temperature which can then
        be published."""
        if data is not None or 'nan':
            maxmintemp = {}
            self.maxmintemp.add_temp(float(data))
            maxmintemp.update({'nightmin_calc': self.maxmintemp.night_min})
            maxmintemp.update({'daymax_calc': self.maxmintemp.day_max})
            obstime = (datetime.now(timezone.utc)).isoformat()
            maxmintemp.update({'obstime': obstime})
            topic = 'sensors/tempcalcs'
            self.client.publish(topic, json.dumps(maxmintemp), self.qos)

    def pressure_calcs_handler(self, pressure):
        """Obtain and publish derived pressures (QNH/QFE) from the latest
         observed/sensor pressure"""
        if pressure is not None or 'nan':
            qnh = self.pressure_calcs.calc_qnh(pressure)
            qfe = self.pressure_calcs.calc_qfe(pressure)
            qnh_qfe = {'qnh': qnh, 'qfe': qfe}
            obstime = (datetime.now(timezone.utc)).isoformat()
            qnh_qfe.update({'obstime': obstime})
            topic = 'sensors/qnh_qfe'
            self.client.publish(topic, json.dumps(qnh_qfe), self.qos)


if __name__ == "__main__":
    DataProcessor()
