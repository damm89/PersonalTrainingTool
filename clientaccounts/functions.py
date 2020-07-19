import json

from .static_variables import *
from .models import *

from ws.static_variables import WEIGHT_MULTIPLIERS


def do_metric_calc(quantity_str, unit, multiplier):
    """
    Finds number in string according to <NUMS> regular expression.
    """
    if unit != 'piece':
        result = multiplier
        quantity = NUMS.search(quantity_str).group(0)
        if len(quantity) == 0:
            return result

        try:
            quantity = float(quantity)
            if quantity > 0:
                result *= quantity
        except ValueError:
            print("Error, returning {}".format(result))
        return result

    else:
        return 1


def string_to_100g(quantity_str):
    """
    Takes a string and tries to find out which units were used and transforms quantity back to 100 grams.
    Options can be found in WEIGHT_MULTIPLIERS
    Calls do_metric_calc to do the actual searching for the number in the string.
    """
    quantity_str = quantity_str.replace(' ','').replace(',','.')

    if quantity_str == '100g':
        return 1
    try:
        return float(quantity_str)/100.0

    except ValueError:
        for unit,multiplier in WEIGHT_MULTIPLIERS:
            if unit in quantity_str:
                return do_metric_calc(quantity_str, unit, multiplier)
        return 1