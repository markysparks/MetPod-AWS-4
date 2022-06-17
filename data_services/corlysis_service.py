import os
import requests
import logging


def transmit_corlysis(parameters):
    """Transmit a formatted data message to the Corlysis service"""
    if not all(value is None for value in parameters.values()) and os.getenv(
            'CORLYSIS_ENABLE', 'false') == 'true':

        params = {"db": os.getenv('CORLYSIS_DB', 'metpod'), "u": os.getenv(
            'CORLYSIS_AUTH', 'token'), "p": os.getenv('CORLYSIS_TOKEN')}

        data = dict()
        data['metpodID'] = os.getenv('SITE_ID', 'mpduk1')
        data['humidity'] = parameters['humidity']
        data['tempc'] = parameters['temperature']
        data['dewptc'] = parameters['dewpoint']
        data['rainrate'] = parameters['rainrate']
        data['pressure'] = parameters['pressure']
        data['qnh'] = parameters['qnh']
        data['qfe'] = parameters['qfe']
        data['windgustkts'] = parameters['windgust10m']
        data['winddir_avg10m'] = parameters['winddir10m']
        data['windspd_avg10m'] = parameters['windspd10m']
        data['dailyrainmm'] = parameters['rainaccum']

        payload = data[
                      'metpodID'] + " temperature={},QNH={},QFE={}," \
                                    "pressure={}," \
                                    "humidity={},dewpoint={}," \
                                    "dailyrain={},rainrate={}" \
                                    "\n".format(data['tempc'],
                                                data['qnh'],
                                                data['qfe'],
                                                data['pressure'],
                                                data['humidity'],
                                                data['dewptc'],
                                                data['dailyrainmm'],
                                                data['rainrate'],
                                                )

        payload_wind = data['metpodID'] + " windgust={},winddir={}," \
                                          "windspd={}" \
                                          "\n".format(data['windgustkts'],
                                                      data['winddir_avg10m'],
                                                      data['windspd_avg10m'],
                                                      )

        logging.info('CORLYSIS MSG prepped:')
        logging.info(payload)
        logging.info(payload_wind)

        try:
            req = requests.post(os.getenv(
                'CORLYSIS_URL', 'https://corlysis.com:8086/write'),
                params=params, data=payload, timeout=20)
            logging.info('CORLYSIS PTU message transmitted' + str(req))

            if data['winddir_avg10m'] is not None:
                req = requests.post(os.getenv(
                    'CORLYSIS_URL', 'https://corlysis.com:8086/write'),
                    params=params, data=payload_wind, timeout=20)
                logging.info('CORLYSIS wind message transmitted: ' + str(req))

        except requests.exceptions.RequestException as e:
            logging.warning(e)
