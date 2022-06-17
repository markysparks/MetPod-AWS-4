import re


def find_numeric_data(dataline):
    """Use regular expressions to find and extract all digit data groups.
    This will include values like 1, 12.3, 2345, 0.34 i.e. any number or
    decimal number.
    param dataline: The data line from digit groups are to be extracted.
    :return: A list containing the digit groups extracted.
    """
    data_search_exp = '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ' \
                      ') )(?:' \
                      '[Ee] [+-]? \d+ ) ?'

    find_data_exp = re.compile(data_search_exp, re.VERBOSE)
    data = find_data_exp.findall(dataline)
    return data
