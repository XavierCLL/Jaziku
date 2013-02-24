#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2011-2013 IDEAM
#
# This file is part of Jaziku.
#
# Jaziku is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Jaziku is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Jaziku.  If not, see <http://www.gnu.org/licenses/>.

import math
import numpy
from datetime import date
from dateutil.relativedelta import relativedelta

from jaziku.core.input import input_validation
from jaziku.env import config_run, globals_vars
from jaziku.utils import console, format_in, array


def percentiles(values, percentile_values):
    """Calculate various percentiles of input values list

    :param values: values for make percentile
    :type values: list
    :param percentile_values: percentile values 2 or 6 depending
        of `class_category_analysis`
    :type percentile_values: list

    :return: values of percentile
    :rtype: list

    :raise ValueError: invalid argument
    """
    if len(percentile_values) in [2, 6]:
        return [numpy.percentile(values, percentile_value) for percentile_value in percentile_values]
    else:
        raise ValueError("the 'percentile_values' should be a list with 2 or 6 values")


def thresholds_dictionary(func):
    def wrapper_func(*args):
        thresholds_list = func(*args)
        if config_run.settings['class_category_analysis'] == 3:
            return {'below': thresholds_list[0],
                    'above': thresholds_list[1]}
        if config_run.settings['class_category_analysis'] == 7:
            return {'below3': thresholds_list[0],
                    'below2': thresholds_list[1],
                    'below1': thresholds_list[2],
                    'above1': thresholds_list[3],
                    'above2': thresholds_list[4],
                    'above3': thresholds_list[5]}
    return wrapper_func


def get_thresholds(station, variable):
    """Calculate and return thresholds of dependent or
    independent variable, the type of threshold as
    defined by the user in station file, these may be:
    "default", "pNN" (percentile NN), "sdN" (standard
    deviation N) and particular value.

    :param station: station for get thresholds
    :type station: Station
    :param variable: variable for calculate thresholds
    :type station: Variable

    :return: Return a dictionary depend of `class_category_analysis`, thus:

        if `class_category_analysis` is 2:
            - `<dict>`, 2 keys: {'below','above'}
        if `class_category_analysis` is 6:
            - `<dict>`, 6 keys: {'below3','below2','below1','above1','above2','above3'}
    :rtype: dict
    """

    # first clean specific values of null and empty elements
    variable.specific_values_cleaned = array.clean(variable.specific_values)

    @thresholds_dictionary
    def thresholds_by_default():
        """thresholds by default of var D or var I"""
        if variable.type == 'D':
            return default_thresholds_var_D(station, variable)
        if variable.type == 'I':
            return default_thresholds_var_I(station, variable)

    @thresholds_dictionary
    def thresholds_with_percentiles(percentile_values):

        percentile_values = [format_in.to_float(value) for value in percentile_values]

        if False in [(0 <= value <= 100) for value in percentile_values]:
            console.msg_error(_("the thresholds of var {0} were defined as "
                                "percentile\nbut are outside of range 0-100:\n{1}")
            .format(variable.type, thresholds_input))

        percentile_values_sort = list(percentile_values)
        percentile_values_sort.sort()
        if not percentile_values_sort == percentile_values:
            console.msg_error(_("the percentile values of var {0} must have "
                                "rising values:\n{1}")
            .format(variable.type, thresholds_input))
        return percentiles(variable.specific_values_cleaned, percentile_values)

    @thresholds_dictionary
    def thresholds_with_std_deviation(std_dev_values):

        std_dev_values = [format_in.to_float(value) for value in std_dev_values]

        # check if all values of std deviation are float
        if False in [isinstance(value, float) for value in std_dev_values]:
            console.msg_error(_("thresholds of var {0} were defined as "
                                "N standard deviation (sdN)\n but the value N is "
                                "invalid number (float or integer)\n{1}")
                .format(variable.type, std_dev_values))

        if config_run.settings['class_category_analysis'] == 3:

            p50 = numpy.percentile(variable.specific_values_cleaned, 50)
            std_deviation = numpy.std(variable.specific_values_cleaned)

            return [p50 - std_dev_values[0] * std_deviation,
                    p50 + std_dev_values[1] * std_deviation]

        if config_run.settings['class_category_analysis'] == 7:

            # check is the std deviations below values are decreasing
            std_dev_values_below_sort = list(std_dev_values[0:3])
            std_dev_values_below_sort.sort(reverse=True)
            if not std_dev_values_below_sort == std_dev_values[0:3]:
                console.msg_error(_("the sdt deviation values (sdN) by below (first 3) of var {0}\n"
                                    "must have decreasing values:\n{1}")
                .format(variable.type, std_dev_values))

            # check is the std deviations above values are rising
            std_dev_values_above_sort = list(std_dev_values[3::])
            std_dev_values_above_sort.sort()
            if not std_dev_values_above_sort == std_dev_values[3::]:
                console.msg_error(_("the sdt deviation values (sdN) by above (last 3) of var {0}\n"
                                    "must have rising values:\n{1}")
                .format(variable.type, std_dev_values))

            p50 = numpy.percentile(variable.specific_values_cleaned, 50)
            std_deviation = numpy.std(variable.specific_values_cleaned)

            return [p50 - std_dev_values[0] * std_deviation,
                    p50 - std_dev_values[1] * std_deviation,
                    p50 - std_dev_values[2] * std_deviation,
                    p50 + std_dev_values[3] * std_deviation,
                    p50 + std_dev_values[4] * std_deviation,
                    p50 + std_dev_values[5] * std_deviation]

    @thresholds_dictionary
    def thresholds_with_particular_values(thresholds_input):
        thresholds_input_sort = list(thresholds_input)
        thresholds_input_sort.sort()
        if not thresholds_input_sort == thresholds_input:
            console.msg_error(_("the thresholds values of var {0} must have "
                                "rising values:\n{1}")
            .format(variable.type, thresholds_input))
        try:
            for threshold in thresholds_input:
                # these values validation with type of var D or var I
                if variable.type == 'D':
                    input_validation.validation_var_D(variable.type_series, threshold, None, variable.frequency_data)
                if variable.type == 'I':
                    input_validation.validation_var_I(variable.type_series, threshold)
                    #TODO replace variable.type_series
            return thresholds_input
        except Exception, e:
            console.msg_error(_("Problems validating the thresholds for var {0}:"
                                "\n\n{1}").format(variable.type, e))

    ## get defined thresholds on config_run and variable
    if variable.type == 'D':
        thresholds_input = config_run.settings['thresholds_var_D']
    if variable.type == 'I':
        thresholds_input = config_run.settings['thresholds_var_I']

    ## now analysis threshold input in arguments
    # if are define as default
    if thresholds_input == "default":
        return thresholds_by_default()

    # check if analog_year is defined but thresholds aren't equal to "default"
    if config_run.settings['analog_year']:
        if station.first_iter:
            console.msg(_("\n > WARNING: You have defined the analog year,\n"
                          "   but the thresholds of var D must be\n"
                          "   'default' for use the analog year .........."), color='yellow', newline=False)

    # if are defined as percentile or standard deviation (all str instance)
    if not False in [isinstance(threshold,str) for threshold in thresholds_input]:

        # if are defined as percentile
        if not False in [threshold[0:1] in ['p','P'] for threshold in thresholds_input]:
            percentile_values = [threshold[1::] for threshold in thresholds_input]
            return thresholds_with_percentiles(percentile_values)

        # if are defined as standard deviation
        if not False in [threshold[0:2] in ['sd','SD'] for threshold in thresholds_input]:
            std_dev_values = [threshold[2::] for threshold in thresholds_input]
            return thresholds_with_std_deviation(std_dev_values)

    # if are defined as particular values
    if not False in [isinstance(threshold,(int, float)) for threshold in thresholds_input]:
        return thresholds_with_particular_values(thresholds_input)

    # unrecognizable thresholds
    console.msg_error(_("unrecognizable thresholds '{0}' for var {1}")
        .format(thresholds_input, variable.type))


def default_thresholds_var_D(station, variable):
    """thresholds by default of var D"""

    # check if analog_year is defined
    if config_run.settings['analog_year']:
        # check if analog_year is inside in process period
        if station.process_period['start'] <= config_run.settings['analog_year'] <= station.process_period['end']:

            _iter_date = date(config_run.settings['analog_year'], 1, 1)
            specific_values_with_analog_year = []
            # get all raw values of var D only in analog year, ignoring null values
            while _iter_date <= date(config_run.settings['analog_year'], 12, 31):
                if not globals_vars.is_valid_null(variable.data[variable.date.index(_iter_date)]):
                    specific_values_with_analog_year.append(variable.data[variable.date.index(_iter_date)])
                if variable.frequency_data == "daily":
                    _iter_date += relativedelta(days=1)
                if variable.frequency_data == "monthly":
                    _iter_date += relativedelta(months=1)

            if config_run.settings['class_category_analysis'] == 3:
                thresholds = {'below': numpy.percentile(specific_values_with_analog_year, 33),
                              'above': numpy.percentile(specific_values_with_analog_year, 66)}
            if config_run.settings['class_category_analysis'] == 7:
                # TODO:
                raise ValueError("TODO")

            # check if all thresholds are valid (not 'nan')
            if True in [math.isnan(threshold) for threshold in thresholds]:
                if station.first_iter:
                    console.msg(_("\n > WARNING: Thresholds calculated with analog year for var_D are wrong,\n"
                                  "   using default thresholds instead"), color='yellow'),
            else:
                # return thresholds with analog year
                if station.first_iter:
                    console.msg(_("\n   Using thresholds with analog year for var_D "), color='cyan'),

                return thresholds
        else:
            if station.first_iter:
                console.msg(_("\n > WARNING: The analog year ({0}) for this\n"
                              "   station is outside of process period {1} to\n"
                              "   {2}. The process continue but using the\n"
                              "   default thresholds .........................")
                            .format(config_run.settings['analog_year'],
                                    station.process_period['start'],
                                    station.process_period['end']), color='yellow', newline=False)

    # return thresholds without analog year
    if config_run.settings['class_category_analysis'] == 3:
        thresholds = {'below': numpy.percentile(variable.specific_values_cleaned, 33),
                      'above': numpy.percentile(variable.specific_values_cleaned, 66)}
    if config_run.settings['class_category_analysis'] == 7:
        # TODO:
        raise ValueError("TODO")

    return thresholds


def default_thresholds_var_I(station, variable):
    """thresholds by default of var I"""

    # thresholds for Oceanic Nino Index
    def if_var_I_is_ONI1():
        return -0.5, 0.5

    # thresholds for Oceanic Nino Index
    def if_var_I_is_ONI2():
        return -0.5, 0.5

    # thresholds for Index of the Southern Oscillation NOAA
    def if_var_I_is_SOI():
        return -0.9, 0.9

    # thresholds for Index of the Southern Oscillation calculated between Tahití and Darwin
    def if_var_I_is_SOI_TROUP():
        return -8, 8

    # thresholds for Multivariate ENSO index
    def if_var_I_is_MEI():
        return percentiles(station.var_I_values, [33, 66])

    # thresholds for Radiation wavelength Long tropical
    def if_var_I_is_OLR():
        return -0.1, 0.2

    # thresholds for Index of wind anomaly to 200 hpa
    def if_var_I_is_W200():
        return percentiles(station.var_I_values, [33, 66])

    # thresholds for Index of wind anomaly to 850 hpa west
    def if_var_I_is_W850w():
        return percentiles(station.var_I_values, [33, 66])

    # thresholds for Index of wind anomaly to 850 hpa center
    def if_var_I_is_W850c():
        return percentiles(station.var_I_values, [33, 66])

    # thresholds for Index of wind anomaly to 850 hpa east
    def if_var_I_is_W850e():
        return percentiles(station.var_I_values, [33, 66])

    # thresholds for Sea surface temperature
    def if_var_I_is_SST():
        return percentiles(station.var_I_values, [33, 66])

    # thresholds for Anomaly Sea surface temperature
    def if_var_I_is_ASST():
        return percentiles(station.var_I_values, [33, 66])

    # thresholds for % Amazon relative humidity
    def if_var_I_is_ARH():
        return percentiles(station.var_I_values, [33, 66])

    # thresholds for quasibienal oscillation index
    def if_var_I_is_QBO():
        return -4, 4

    # thresholds for North atlantic oscillation index
    def if_var_I_is_NAO():
        return -1, 1

    # thresholds for Caribbean (CAR) Index
    def if_var_I_is_CAR():
        return percentiles(station.var_I_values, [33, 66])

    # thresholds for Monthly anomaly of the ocean surface area Ocean region
    def if_var_I_is_AREA_WHWP():
        return percentiles(station.var_I_values, [33, 66])

    # switch validation
    select_threshold_var_I = {
        "ONI1": if_var_I_is_ONI1,
        "ONI2": if_var_I_is_ONI2,
        "SOI": if_var_I_is_SOI,
        "SOI_TROUP": if_var_I_is_SOI_TROUP,
        #"MEI": if_var_I_is_MEI,
        "OLR": if_var_I_is_OLR,
        "W200": if_var_I_is_W200,
        "W850w": if_var_I_is_W850w,
        "W850c": if_var_I_is_W850c,
        "W850e": if_var_I_is_W850e,
        "SST12": if_var_I_is_SST,
        "SST3": if_var_I_is_SST,
        "SST4": if_var_I_is_SST,
        "SST34": if_var_I_is_SST,
        "ASST12": if_var_I_is_ASST,
        "ASST3": if_var_I_is_ASST,
        "ASST4": if_var_I_is_ASST,
        "ASST34": if_var_I_is_ASST,
        "ARH": if_var_I_is_ARH,
        "QBO": if_var_I_is_QBO,
        "NAO": if_var_I_is_NAO,
        "CAR": if_var_I_is_CAR,
        "AREA_WHWP": if_var_I_is_AREA_WHWP
    }

    threshold_below_var_I, threshold_above_var_I = select_threshold_var_I[station.var_I.type_series]()
    return threshold_below_var_I, threshold_above_var_I
