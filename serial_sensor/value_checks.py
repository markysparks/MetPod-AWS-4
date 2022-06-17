import warnings


def pressure_check(value):
    """Check the pressure value falls within reasonable limits.
    param value: The pressure value in hectopascals (hPa).
    :return: True if the value falls with limits."""
    if 800 < value < 1200:
        return True
    else:
        warnings.warn('Pressure value fails check: ' + str(value), Warning)


def temperature_check(value):
    """Check the temperature value falls within reasonable limits.
    param value: The temperature value in degrees C.
    :return: True if the value falls with limits."""
    if -100 < value < 100 or value is None:
        return True
    else:
        warnings.warn('Temperature value fails check: ' + str(value), Warning)


def humidity_check(value):
    """Check the humidity value falls within reasonable limits.
    param value: The humidity value in per-cent (%).
    :return: True if the value falls with limits."""
    if 0 <= value <= 150:
        return True
    else:
        warnings.warn('Humidity value fails check: ' + str(value), Warning)


def windspeed_check(value):
    """Check the windspeed value falls within reasonable limits.
        param value: The windspeed value in knots.
        :return: True if the value falls with limits."""
    if 0 <= value < 500:
        return True
    else:
        warnings.warn('Wind speed value fails check: ' + str(value), Warning)


def winddir_check(value):
    """Check the wind direction value falls within reasonable limits.
        param value: The wind direction value in degrees.
        :return: True if the value falls with limits."""
    if 0 <= value <= 360:
        return True
    else:
        warnings.warn('Wind dir value fails check: ' + str(value), Warning)
