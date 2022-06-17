import os
import math
import logging

logging.basicConfig(level=logging.INFO)
logging.captureWarnings(True)


class PRESSURECALCS:
    """Methods for calculating QNH, QFE pressures from observed pressure.
       Barometer height above ground level and station height above mean sea
       level used in these calculations are obtained from the application's
       environment variables.
       See the following for a description of the calculations:
        https://www.metpod.co.uk/calculators/pressure/"""

    def __init__(self):
        self.temperature = None

    def calc_qnh(self, pressure):
        """Alternative method for calculating QNH base on Ross Provans
        (Met Office) spreadsheet.
        param pressure: Observed pressure (hPa - read from sensor).
        """
        if pressure and self.temperature is not None:
            pressure = float(pressure)
            temperature = float(self.temperature)
            afht = float(os.getenv('SITE_ALTITUDE', 0))
            barht = float(os.getenv('BARO_HT', 0))

            const = (1 + (9.6 * ((math.pow(10, -5)) * afht) + (6 * (
                math.pow(10, -9)) * (math.pow(afht, 2)))))

            qnh = pressure + ((0.022857 * afht) + ((const - 1) * pressure) + (
                    const * (pressure * (math.pow(10, (barht / (18429.1 + 67.53
                                                                * temperature +
                                                                (0.003 * barht)
                                                                )))) - pressure
                             )))
            return round(qnh, 1)
        else:
            return None

    def calc_qfe(self, pressure):
        """Calculate pressure at site ground level given observed pressure,
        temperature and height above ground of the sensor.

        Applies the 'hypsometric equation':
        QFE = p x (1+ (hQFE x g) / (R x T))
        p = sensor pressure, hQFE = barometer height above station elevation,
        R = gas const.
        T = temperature in deg C.

        param pressure: Pressure reading from sensor in hPa.
        """
        if pressure and self.temperature is not None:
            self.temperature = float(self.temperature)
            pressure = float(pressure)
            sensor_height = float(os.getenv('BARO_HT', 0))

            qfe = pressure * (1 + ((sensor_height * 9.80665) / (287.04 * (
                    self.temperature + 273.15))))
            return round(qfe, 1)
        else:
            return None
