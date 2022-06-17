import os
import re
import warnings
import value_checks
import utilities
from datetime import datetime, timezone


class PTU300ascii:

    def __init__(self):
        # b"P=  1003.8 hPa   T= 17.7 'C RH= 40.9 %RH TD=  4.3 'C  trend=*****
        # tend=*\r\n"
        self.search_exp = re.compile('P=.+hPa.+T=.+RH=.+TD=.+trend=.+tend=.')

    def data_decoder(self, dataline):
        """
        Extract available weather parameters from the sensor data, check that
        data falls within sensible boundaries. If necessary, the sensor must
        be setup to output its data in the required format e.g.
        # b"P=  1003.8 hPa   T= 17.7 'C RH= 40.9 %RH TD=  4.3 'C  trend=*****
        # tend=*\r\n"
        with units of hPa, degrees C and % humidity.
        :param dataline: Sensor data output string.
        """
        data = {}
        if self.search_exp.search(dataline):
            # Instrument corrections
            pressure_corr = float(os.getenv('PRESS_CORR', 0.0))
            temperature_corr = float(os.getenv('TEMP_CORR', 0.0))
            humidity_corr = float(os.getenv('HUMI_CORR', 0.0))

            pressure = None
            temperature = None
            humidity = None
            dewpoint = None

            data_elements = utilities.find_numeric_data(dataline)

            if len(data_elements) > 3:
                if value_checks.pressure_check(float(data_elements[0])):
                    pressure = float(data_elements[0]) + pressure_corr
                if value_checks.temperature_check(float(data_elements[1])):
                    temperature = float(data_elements[1]) + temperature_corr
                if value_checks.humidity_check(
                        int(round(float(data_elements[2])))):
                    humidity = round(float(
                        data_elements[2]) + humidity_corr, 1)
                    if humidity > 100:
                        humidity = 100
                if value_checks.temperature_check(float(data_elements[3])):
                    dewpoint = float(data_elements[3])

                data.update({'pressure': pressure,
                             'temperature': temperature,
                             'humidity': humidity,
                             'dewpoint': dewpoint})

                if len(data_elements) == 6:
                    tendency = float(data_elements[4])
                    trend = int(data_elements[5])

                    data.update({'trend': trend, 'tendency': tendency})

                obstime = (datetime.now(timezone.utc)).isoformat()
                data.update({'obstime': obstime})

        else:
            warnings.warn('Invalid PTU300 sensor data', Warning)
        return data

