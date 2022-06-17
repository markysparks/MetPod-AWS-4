import os
import logging
import metoffice_wow
import windy
import corlysis_service
import wx_underground
from threading import Timer
from aws_mqtt_client import MQTTclient


class Services:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
        self.aws_mqtt_client = MQTTclient()
        self.aws_iot_setup()
        self.metoffice_wow_setup()
        self.corlysis_setup()
        self.windy_setup()
        self.wx_underground_setup()

    def aws_iot_setup(self):
        self.aws_mqtt_client.publish(
            'mpduk1', {'pressure': self.mqtt_client.pressure,
                       'qnh': self.mqtt_client.qnh,
                       'qfe': self.mqtt_client.qfe,
                       'temperature': self.mqtt_client.temperature,
                       'dewpoint': self.mqtt_client.dewpoint,
                       'humidity': self.mqtt_client.humidity,
                       'winddir10m': self.mqtt_client.winddir10m,
                       'windspd10m': self.mqtt_client.windspeed10m,
                       'windgust10m': self.mqtt_client.windgust10m,
                       'rainrate': self.mqtt_client.rainrate,
                       'rainaccum': self.mqtt_client.rainaccum,
                       'maxtemp': self.mqtt_client.daymax,
                       'mintemp': self.mqtt_client.nightmin,
                       'trend': self.mqtt_client.trend,
                       'tendency': self.mqtt_client.tendency
                       })

        Timer(int(os.getenv('AWS_TX_INTERVAL', '180')),
              self.aws_iot_setup).start()
        logging.info('AWS IoT service sleeping')

    def metoffice_wow_setup(self):
        metoffice_wow.transmit_wow(
            {'pressure': self.mqtt_client.pressure,
             'qnh': self.mqtt_client.qnh,
             'qfe': self.mqtt_client.qfe,
             'temperature': self.mqtt_client.temperature,
             'dewpoint': self.mqtt_client.dewpoint,
             'humidity': self.mqtt_client.humidity,
             'winddir10m': self.mqtt_client.winddir10m,
             'windspd10m': self.mqtt_client.windspeed10m,
             'windgust10m': self.mqtt_client.windgust10m,
             'rainrate': self.mqtt_client.rainrate,
             'rainaccum': self.mqtt_client.rainaccum
             })

        Timer(int(os.getenv('WOW_TX_INTERVAL', '600')),
              self.metoffice_wow_setup).start()
        logging.info('MetOffice WoW service sleeping')

    def windy_setup(self):
        windy.transmit_windy(
            {'pressure': self.mqtt_client.pressure,
             'qnh': self.mqtt_client.qnh,
             'qfe': self.mqtt_client.qfe,
             'temperature': self.mqtt_client.temperature,
             'dewpoint': self.mqtt_client.dewpoint,
             'humidity': self.mqtt_client.humidity,
             'winddir10m': self.mqtt_client.winddir10m,
             'windspd10m': self.mqtt_client.windspeed10m,
             'windgust10m': self.mqtt_client.windgust10m,
             'rainrate': self.mqtt_client.rainrate
             })

        Timer(int(os.getenv('WINDY_TX_INTERVAL', '300')),
              self.windy_setup).start()
        logging.info('Windy service sleeping')

    def corlysis_setup(self):
        corlysis_service.transmit_corlysis(
            {'pressure': self.mqtt_client.pressure,
             'qnh': self.mqtt_client.qnh,
             'qfe': self.mqtt_client.qfe,
             'temperature': self.mqtt_client.temperature,
             'dewpoint': self.mqtt_client.dewpoint,
             'humidity': self.mqtt_client.humidity,
             'winddir10m': self.mqtt_client.winddir10m,
             'windspd10m': self.mqtt_client.windspeed10m,
             'windgust10m': self.mqtt_client.windgust10m,
             'rainrate': self.mqtt_client.rainrate,
             'rainaccum': self.mqtt_client.rainaccum
             })

        Timer(int(os.getenv('CORLYSIS_TX_INTERVAL', '240')),
              self.corlysis_setup).start()
        logging.info('CORLYSIS service sleeping')

    def wx_underground_setup(self):
        wx_underground.transmit_wx_underground(
            {'pressure': self.mqtt_client.pressure,
             'qnh': self.mqtt_client.qnh,
             'qfe': self.mqtt_client.qfe,
             'temperature': self.mqtt_client.temperature,
             'dewpoint': self.mqtt_client.dewpoint,
             'humidity': self.mqtt_client.humidity,
             'winddir10m': self.mqtt_client.winddir10m,
             'windspd10m': self.mqtt_client.windspeed10m,
             'windgust10m': self.mqtt_client.windgust10m,
             'rainrate': self.mqtt_client.rainrate,
             'rainaccum': self.mqtt_client.rainaccum
             })

        Timer(int(os.getenv('WX_UNDERGROUND_TX_INTERVAL', '180')),
              self.wx_underground_setup).start()
        logging.info('WX Underground service sleeping')
