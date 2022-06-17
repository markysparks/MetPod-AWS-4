

def to_fahrenheit(value):
    """Convert the input in degrees C to Fahrenheit and return the result
    rounded to one decimal place.
    param value: The input temperature value in degrees C.
    :return: The temperature value in Fahrenheit.
    """
    if value is not None:
        value_fahrenheit = round(((float(value) * 1.8) + 32), 1)
        return value_fahrenheit
    else:
        return None


def to_ms(value):
    """Convert an in put speed in knots to metre's per second and return the
    whole integer result.
    param value: The speed in knots.
    :return: The input speed converted to metre's per second.
    """
    if value is not None:
        value_ms = int(round(float(value) * 0.5144447, 0))
        return value_ms
    else:
        return None


def to_mph(value):
    """Convert an in put speed in knots to miles per hour and return the
    whole integer result.
    param value: The speed in knots.
    :return: The input speed converted to miles per hour.
    """
    if value is not None:
        value_mph = int(round(float(value) * 1.152, 0))
        return value_mph
    else:
        return None


def to_inch_hg(value):
    """Convert the input pressure in hectopascals (hPa) to inches of mercury
    rounded to two decimal places.
    param value: The pressure value in hPa.
    :return: The pressure value in inches of Hg.
    """
    if value is not None:
        value_inch_hg = round((float(value) / 33.863886666667), 2)
        return value_inch_hg
    else:
        return None


def to_inches(value):
    """Convert a value in millimetres to one in inches rounded to two
    decimal places.
    param value: Value in millimetres.
    :return: Value in inches.
    """
    if value is not None:
        value_inches = round(float(value) * 0.039370, 2)
        return value_inches
    else:
        return None
