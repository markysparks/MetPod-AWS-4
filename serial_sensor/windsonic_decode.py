import os
import re
import warnings
import value_checks
import utilities
from datetime import datetime, timezone


class Windsonic:

    def __init__(self):
        # b'\x02Q,194,000.04,N,00,\x0315\r\n'
        self.search_exp = re.compile('\w,\d\d\d,\d\d\d.\d\d,\w,\d\d')

        # Instrument corrections
        self.anemo_offset = int(os.getenv('ANEMO_OFFSET', 0))

        self.wind_list = []

    def data_decoder(self, dataline):
        """
        Extract available weather parameters from the sensor data, check that
        data falls within sensible boundaries. If necessary, the sensor must
        be setup to output its data in the required format e.g.
       '\x02Q,194,005.04,N,00,\x0315' with units in knots and degrees
        (194 degrees and 5.04 kts in this case).
        :param dataline: Sensor data output string.
        """
        data = {}

        if self.search_exp.search(dataline):
            data_elements = utilities.find_numeric_data(dataline)
            if len(data_elements) == 5:
                winddir_raw = int(
                    round(float(data_elements[1]), 0)) + self.anemo_offset
                if winddir_raw == 0:
                    pass
                elif winddir_raw < 0:
                    winddir_raw += 360
                elif winddir_raw > 360:
                    winddir_raw -= 360
                windspeed_raw = int(round(float(data_elements[2]), 0))
                if value_checks.windspeed_check(windspeed_raw) \
                        and value_checks.winddir_check(winddir_raw):
                    winddir = winddir_raw
                    windspeed = windspeed_raw
                    data.update({'winddir': winddir, 'windspeed': windspeed})
                    # wind_data = self.collect_winds([windspeed, winddir])
                    # if wind_data is not None:
                    # data.update({'winddir': wind_data[1],
                    # 'windspeed': wind_data[0]})
                    obstime = (datetime.now(timezone.utc)).isoformat()
                    data.update({'obstime': obstime})
                else:
                    data = None
        else:
            warnings.warn('Invalid Windsonic sensor data', Warning)
        return data

    def collect_winds(self, wind):
        self.wind_list.append(wind)
        if len(self.wind_list) == 3:
            wind_vector = (max(self.wind_list, key=lambda x: x[0]))
            self.wind_list.clear()
            return wind_vector
        else:
            return None
