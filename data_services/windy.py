import requests
import logging
import os
import utilities

logging.basicConfig(level=logging.INFO)
logging.captureWarnings(True)


def transmit_windy(parameters):
    """Transmit a formatted data message to the Met Office WoW website"""
    if not all(value is None for value in parameters.values()) and os.getenv(
            'WINDY_ENABLE', 'false') == 'true':
        data = dict()
        windy_url = os.getenv('WINDY_URL',
                              'https://stations.windy.com/pws/update/')
        api_key = os.getenv('WINDY_AUTH_KEY')
        windy_url = windy_url + api_key

        data['winddir'] = parameters['winddir10m']
        data['wind'] = utilities.to_ms(parameters['windspd10m'])
        data['gust'] = utilities.to_ms(parameters['windgust10m'])
        data['temp'] = parameters['temperature']
        data['precip'] = parameters['rainrate']
        data['mbar'] = parameters['qnh']
        data['dewpoint'] = parameters['dewpoint']
        data['rh'] = parameters['humidity']

        logging.info('WINDY-MSG prepped:')
        logging.info(data)

        try:
            req = requests.get(windy_url, params=data, timeout=20)
            logging.info('WINDY-message transmitted: ' + str(req))
        except requests.exceptions.RequestException as e:
            logging.warning(e)
