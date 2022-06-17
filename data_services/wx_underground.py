import requests
import logging
import os
import utilities

logging.basicConfig(level=logging.INFO)
logging.captureWarnings(True)


def transmit_wx_underground(parameters):
    """Transmit a formatted data message to the Weather Underground website"""
    if not all(value is None for value in parameters.values()) and os.getenv(
            'WX_UNDERGROUND_ENABLE', 'false') == 'true':
        wx_underground_tx_interval = int(os.getenv(
            'WX_UNDERGROUND_TX_INTERVAL', '180'))
        wx_underground_id = os.getenv('WX_UNDERGROUND_ID')
        wx_underground_password = os.getenv('WX_UNDERGROUND_PASSWORD')
        wx_underground_url = os.getenv('WX_UNDERGROUND_URL')
        softwaretype = os.getenv('SOFTWARETYPE', 'metpod')
       
        data = dict()
        data['softwaretype'] = softwaretype
        data['ID'] = wx_underground_id
        data['PASSWORD'] = wx_underground_password
        data['action'] = 'updateraw'
        data['realtime'] = 1
        data['rtfreq'] = wx_underground_tx_interval
        data['dateutc'] = 'now'
        data['winddir'] = parameters['winddir10m']
        data['windspeedmph'] = utilities.to_mph(parameters['windspd10m'])
        data['windgustmph'] = utilities.to_mph(parameters['windgust10m'])
        data['tempf'] = utilities.to_fahrenheit(parameters['temperature'])
        data['rainin'] = utilities.to_inches(parameters['rainrate'])
        data['dailyrainin'] = utilities.to_inches(parameters['rainaccum'])
        data['baromin'] = utilities.to_inch_hg(parameters['qnh'])
        data['dewptf'] = utilities.to_fahrenheit(parameters['dewpoint'])
        data['humidity'] = parameters['humidity']

        logging.info('WX-UNDERGROUND-MSG prepped:')
        logging.info(data)

        try:
            req = requests.get(wx_underground_url, params=data, timeout=20)
            logging.info('WX-UNDERGROUND-message transmitted: ' + str(req))
        except requests.exceptions.RequestException as e:
            logging.warning(e)
