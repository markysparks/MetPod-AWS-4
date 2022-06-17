import re
import warnings
import utilities
from datetime import datetime, timezone


class RainGauge:

    def __init__(self):
        # {"rainrate"= 0.0, "rainfall"= 0.4, "units"= "mm/hr"}
        self.search_exp = re.compile('rainrate.*rainfall')

    def data_decoder(self, dataline):
        """
        Extract available weather parameters from the sensor data, check that
        data falls within sensible boundaries. If necessary, the sensor must
        be setup to output its data in the required format e.g.
        {"rainrate"= 0.0, "rainfall"= 0.4, "units"= "mm/hr"}
        with units mm / mm/hr.
        :param dataline: Sensor data output string.
        """
        data = {}
        if self.search_exp.search(dataline):
            data_elements = utilities.find_numeric_data(dataline)
            if len(data_elements) == 2:
                rainrate = float(data_elements[0])
                rainaccum = float(data_elements[1])
                data.update({'rainrate': rainrate})
                data.update(({'rainaccum': rainaccum}))
            obs_time = (datetime.now(timezone.utc)).isoformat()
            data.update({'obs_time': obs_time})
        else:
            warnings.warn('Invalid Raingauge sensor data', Warning)
        return data
