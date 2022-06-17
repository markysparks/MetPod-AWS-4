import os
import re
import warnings
import value_checks
import utilities
from datetime import datetime, timezone


class PTB220ascii:

    def __init__(self):
        # .P.1  1005.75 ***.* * 1005.8 1005.7 1005.7 000.F9
        self.search_exp = re.compile('.P.+')

    def data_decoder(self, dataline):
        """
        Extract available weather parameters from the sensor data, check that
        data falls within sensible boundaries. If necessary, the sensor must
        be setup to output its data in the required format e.g.
        P.1  1000.90 ***.* * 1000.9 1000.9 1000.9 000.E7
        tend=7
        with units of hPa, degrees C and % humidity.
        :param dataline: Sensor data output string.
        """
        data = {}

        if self.search_exp.search(dataline):
            # Instrument corrections
            pressure_corr = float(os.getenv('PRESS_CORR', 0.0))
            data_elements = utilities.find_numeric_data(dataline)

            if len(data_elements) == 9:
                if value_checks.pressure_check(float(data_elements[2])):
                    pressure = float(data_elements[2]) + pressure_corr
                    data.update({'pressure': pressure})
            elif len(data_elements) == 11:
                if value_checks.pressure_check(float(data_elements[2])):
                    pressure = float(data_elements[2]) + pressure_corr
                    trend = float(data_elements[3])
                    tendency = int(data_elements[4])
                    data.update({'pressure': pressure,
                                 'trend': trend,
                                 'tendency': tendency})
            obstime = (datetime.now(timezone.utc)).isoformat()
            data.update({'obstime': obstime})
        else:
            warnings.warn('Invalid PTB220 sensor data', Warning)
        return data

