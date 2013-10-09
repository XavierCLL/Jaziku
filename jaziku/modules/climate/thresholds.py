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

import copy
import numpy
from datetime import date
from dateutil.relativedelta import relativedelta

from jaziku import env
from jaziku.core.input import validation
from jaziku.utils import console, input, array


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


# decorator
def thresholds_to_dict_format(func):
    """Format the thresholds to defined dictionary for
    more easy to use inside code.
    """
    def wrapper_func(*args, **kwargs):
        thresholds = func(*args, **kwargs)

        if not isinstance(thresholds, list):
            # it is when it is called twice or is false
            return thresholds
        if env.config_run.settings['class_category_analysis'] == 3:
            return {'below': thresholds[0],
                    'above': thresholds[1]}
        if env.config_run.settings['class_category_analysis'] == 7:
            return {'below3': thresholds[0],
                    'below2': thresholds[1],
                    'below1': thresholds[2],
                    'above1': thresholds[3],
                    'above2': thresholds[4],
                    'above3': thresholds[5]}
    return wrapper_func


# decorator
def validate_thresholds(variable, force=False):
    """Decorator function for validate thresholds calculated or
     assigned in its limits established

    :param variable: variable to validate
    :param force: this force the validation of thresholds, if the limits
    can't not set or are undefined show error and exit.
    """
    def decorator(func):
        def wrapper_func(*args, **kwargs):
            thresholds = func(*args, **kwargs)
            if not isinstance(thresholds, dict):
                # it is when it is called twice or is false
                return thresholds
            # check ------------------
            # error if limits of variable are none, if defined thresholds
            # as standard deviation are need defined limits
            if force:
                if env.config_run.settings['limits_var_'+variable.type]['below'] is None or \
                   env.config_run.settings['limits_var_'+variable.type]['above'] is None:

                    # if the variable is a internal variable
                    if env.var_[variable.type].TYPE_SERIES in env.var_[variable.type].INTERNAL_TYPES:
                        # get default limits for internal variable
                        env.config_run.settings['limits_var_'+variable.type]['below'] = 'default'
                        env.config_run.settings['limits_var_'+variable.type]['above'] = 'default'
                        validation.set_limits(variable)
                    else:
                        console.msg_error(_("If you use standard deviation (sd) as thresholds\n"
                                            "and if series ({0}) is a external type, you need\n"
                                            "defined the limits for this variable, because Jaziku\n"
                                            "check the (sd) thresholds calculated are within limits.")
                        .format(env.var_[variable.type].TYPE_SERIES))
            # check thresholds if are within limits of variable
            for key, threshold in thresholds.items():
                try:
                    validation.is_the_value_within_limits(threshold, variable)
                except ValueError as error:
                    console.msg_error(_("The threshold calculated or assigned to '{0}'\n"
                                        "for the series {1}, is outside its limits defined.\n\n{2}")
                    .format(env.globals_vars.categories(key), env.var_[variable.type].TYPE_SERIES, error))
            return thresholds
        return wrapper_func
    return decorator


def thresholds_to_list(thresholds):
    """Return a ordered thresholds list from
    dictionary thresholds.
    """
    if env.config_run.settings['class_category_analysis'] == 3:
        return [thresholds['below'],
                thresholds['above']]
    if env.config_run.settings['class_category_analysis'] == 7:
        return [thresholds['below3'],
                thresholds['below2'],
                thresholds['below1'],
                thresholds['above1'],
                thresholds['above2'],
                thresholds['above3']]


def get_thresholds(station, variable, thresholds_input=None, process_analog_year=False):
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

    # -------------------------------------------------------------------------
    # definition of different method for calculation thresholds


    def thresholds_by_default():
        """thresholds by default of var D or var I, with or without analog year"""

        if variable.type == 'D':
            default_thresholds = env.var_D.get_default_thresholds()
            if default_thresholds is None:
                console.msg_error(_("the thresholds of var {0} ({1}) were defined as 'default'\n"
                                    "but this variable ({1}) haven't internal thresholds defined.")
                .format(variable.type, env.var_D.TYPE_SERIES))
            return get_thresholds(station, variable, default_thresholds)

        if variable.type == 'I':
            default_thresholds = env.var_I.get_default_thresholds()
            if default_thresholds is None:
                console.msg_error(_("the thresholds of var {0} ({1}) were defined as "
                                    "'default'\nbut this variable ({1}) haven't internal thresholds defined")
                .format(variable.type, env.var_I.TYPE_SERIES))
            return get_thresholds(station, variable, default_thresholds)


    def thresholds_with_analog_year_for_var_D():
        # check if analog_year is inside in process period
        if station.process_period['start'] <= env.config_run.settings['analog_year'] <= station.process_period['end']:
            _iter_date = date(env.config_run.settings['analog_year'], 1, 1)
            specific_values_with_analog_year = []
            # get all raw values of var D only in analog year
            while _iter_date <= date(env.config_run.settings['analog_year'], 12, 31):
                specific_values_with_analog_year.append(variable.data[variable.date.index(_iter_date)])
                if env.var_[variable.type].is_daily():
                    _iter_date += relativedelta(days=1)
                if env.var_[variable.type].is_monthly():
                    _iter_date += relativedelta(months=1)

            # check nulls
            number_of_nulls, percentage_of_nulls = array.check_nulls(specific_values_with_analog_year)
            if percentage_of_nulls > 25:
                console.msg_error(_("Error calculating thresholds for var {0} ({1}) using analog year,\n"
                                    "the series for analog year {2} have {3}% of nulls, more than\n"
                                    "25% of permissive nulls for analog year.")
                .format(variable.type, env.var_[variable.type].TYPE_SERIES,
                        env.config_run.settings['analog_year'], percentage_of_nulls))

            # clean list of nulls
            variable_analog_year = copy.deepcopy(variable)
            variable_analog_year.specific_values = specific_values_with_analog_year

            return get_thresholds(station, variable_analog_year, process_analog_year=True)

        else:
            console.msg_error(_("The analog year ({0}) for this station\n"
                                "is outside of process period {1} to {2}.")
                                .format(env.config_run.settings['analog_year'],
                                        station.process_period['start'],
                                        station.process_period['end']))


    @validate_thresholds(variable)
    @thresholds_to_dict_format
    def thresholds_with_percentiles(percentile_values):

        percentile_values = [input.to_float(value) for value in percentile_values]

        if False in [(0 <= value <= 100) for value in percentile_values]:
            console.msg_error(_("the thresholds of var {0} ({1}) were defined as "
                                "percentile\nbut are outside of range 0-100:\n\n{2}")
            .format(variable.type, env.var_[variable.type].TYPE_SERIES, thresholds_input))

        percentile_values_sort = list(percentile_values)
        percentile_values_sort.sort()
        if not percentile_values_sort == percentile_values:
            console.msg_error(_("the percentile values of var {0} ({1}) must have "
                                "rising values:\n\n{2}")
            .format(variable.type, env.var_[variable.type].TYPE_SERIES, thresholds_input))
        return percentiles(variable.specific_values_cleaned, percentile_values)


    @validate_thresholds(variable, force=True)
    @thresholds_to_dict_format
    def thresholds_with_std_deviation(std_dev_values):

        std_dev_values = [input.to_float(value) for value in std_dev_values]

        # check if all values of std deviation are float
        if False in [isinstance(value, float) for value in std_dev_values]:
            console.msg_error(_("thresholds of var {0} ({1}) were defined as "
                                "N standard deviation (sdN)\nbut the value N is "
                                "invalid number (float or integer)\n\n{2}")
                .format(variable.type, env.var_[variable.type].TYPE_SERIES, std_dev_values))

        # check is the std deviations values are rising
        mean_values_sort = list(std_dev_values)
        mean_values_sort.sort()
        if not mean_values_sort == std_dev_values:
            console.msg_error(_("the sdt deviation values (sdN) for the thresholds\n"
                                "of var {0} ({1}), must have rising values:\n\n{2}")
            .format(variable.type, env.var_[variable.type].TYPE_SERIES, std_dev_values))

        p50 = numpy.percentile(variable.specific_values_cleaned, 50)
        std_deviation = numpy.std(variable.specific_values_cleaned, ddof=1)

        if env.config_run.settings['class_category_analysis'] == 3:
            return [p50 + std_dev_values[0] * std_deviation,
                    p50 + std_dev_values[1] * std_deviation]

        if env.config_run.settings['class_category_analysis'] == 7:
            return [p50 + std_dev_values[0] * std_deviation,
                    p50 + std_dev_values[1] * std_deviation,
                    p50 + std_dev_values[2] * std_deviation,
                    p50 + std_dev_values[3] * std_deviation,
                    p50 + std_dev_values[4] * std_deviation,
                    p50 + std_dev_values[5] * std_deviation]


    @validate_thresholds(variable, force=True)
    @thresholds_to_dict_format
    def thresholds_with_p50(p50_values):

        p50_values = [input.to_float(value) for value in p50_values]

        # check if all values of p50+ are float
        if False in [isinstance(value, float) for value in p50_values]:
            console.msg_error(_("thresholds of var {0} ({1}) were defined as "
                                "p50 +/- N (p50+N)\nbut the value N is "
                                "invalid number (float or integer)\n\n{2}")
                .format(variable.type, env.var_[variable.type].TYPE_SERIES, p50_values))

        # check is the p50 values are rising
        p50_values_sort = list(p50_values)
        p50_values_sort.sort()
        if not p50_values_sort == p50_values:
            console.msg_error(_("the p50 values (p50+N) for the thresholds\n"
                                "of var {0} ({1}), must have rising values:\n\n{2}")
            .format(variable.type, env.var_[variable.type].TYPE_SERIES, p50_values))

        p50 = numpy.percentile(variable.specific_values_cleaned, 50)

        if env.config_run.settings['class_category_analysis'] == 3:
            return [p50 + p50_values[0],
                    p50 + p50_values[1]]

        if env.config_run.settings['class_category_analysis'] == 7:
            return [p50 + p50_values[0],
                    p50 + p50_values[1],
                    p50 + p50_values[2],
                    p50 + p50_values[3],
                    p50 + p50_values[4],
                    p50 + p50_values[5]]


    @validate_thresholds(variable)
    @thresholds_to_dict_format
    def thresholds_with_percentage(percentage_values):

        percentage_values = [input.to_float(value) for value in percentage_values]

        # check if all values of percentage are float
        if False in [isinstance(value, float) for value in percentage_values]:
            console.msg_error(_("thresholds of var {0} ({1}) were defined as "
                                "N percentage (N%)\nbut the value N is "
                                "invalid number (float or integer)\n\n{2}")
            .format(variable.type, env.var_[variable.type].TYPE_SERIES, percentage_values))

        # check is the percentage values are rising
        percentage_values_sort = list(percentage_values)
        percentage_values_sort.sort()
        if not percentage_values_sort == percentage_values:
            console.msg_error(_("the percentage values (N%) for the thresholds\n"
                                "of var {0} ({1}), must have rising values:\n\n{2}")
            .format(variable.type, env.var_[variable.type].TYPE_SERIES, percentage_values))

        _100percent = array.mean(variable.specific_values_cleaned)

        if env.config_run.settings['class_category_analysis'] == 3:

            return [_100percent*percentage_values[0]/100.0,
                    _100percent*percentage_values[1]/100.0]

        if env.config_run.settings['class_category_analysis'] == 7:

            return [_100percent*percentage_values[0]/100.0,
                    _100percent*percentage_values[1]/100.0,
                    _100percent*percentage_values[2]/100.0,
                    _100percent*percentage_values[3]/100.0,
                    _100percent*percentage_values[4]/100.0,
                    _100percent*percentage_values[5]/100.0]


    @validate_thresholds(variable)
    @thresholds_to_dict_format
    def thresholds_with_particular_values(thresholds_input):
        thresholds_input_sort = list(thresholds_input)
        thresholds_input_sort.sort()
        if not thresholds_input_sort == thresholds_input:
            console.msg_error(_("the thresholds values of var {0} ({1}) must have "
                                "rising values:\n\n{2}")
            .format(variable.type, env.var_[variable.type].TYPE_SERIES, thresholds_input))
        try:
            for threshold in thresholds_input:
                validation.is_the_value_within_limits(threshold, variable)

            # specific behavior for temperatures
            if env.var_[variable.type].TYPE_SERIES in ['TMIN', 'TMAX', 'TEMP']:
                p50 = numpy.percentile(variable.specific_values_cleaned, 50)

                if env.config_run.settings['class_category_analysis'] == 3:
                    return [p50 + thresholds_input[0],
                            p50 + thresholds_input[1]]
                if env.config_run.settings['class_category_analysis'] == 7:
                    return [p50 + thresholds_input[0],
                            p50 + thresholds_input[1],
                            p50 + thresholds_input[2],
                            p50 + thresholds_input[3],
                            p50 + thresholds_input[4],
                            p50 + thresholds_input[5]]

            return thresholds_input
        except Exception as error:
            console.msg_error(_("Problems with the thresholds for var {0} ({1}):"
                                "\n\n{2}").format(variable.type, env.var_[variable.type].TYPE_SERIES, error))


    # -------------------------------------------------------------------------
    # detect and calculate thresholds

    # check
    number_of_nulls, percentage_of_nulls = array.check_nulls(variable.specific_values)
    if percentage_of_nulls > 20 and station.first_iter:
        console.msg(_("\n > WARNING: calculating thresholds for var {0} ({1}),\n"
                      "   one of the time series have {2}% of nulls, more than\n"
                      "   20% of permissive nulls. Jaziku continue but the series\n"
                      "   could not be consistent, recommended enable 'consistent_data'\n"
                      "   inside runfile.")
                    .format(variable.type, env.var_[variable.type].TYPE_SERIES, percentage_of_nulls), color='yellow')

    # first clean specific values of null and empty elements
    variable.specific_values_cleaned = array.clean(variable.specific_values)

    ## get defined thresholds on env.config_run and variable
    if thresholds_input is None:
        if variable.type == 'D':
            thresholds_input = env.config_run.settings['thresholds_var_D']
        if variable.type == 'I':
            thresholds_input = env.config_run.settings['thresholds_var_I']

    # check if analog_year is defined but thresholds aren't equal to "default"
    if not process_analog_year:
        if env.config_run.settings['analog_year'] and variable.type == 'D':
            thresholds_with_analog_year_for_var_D()

    ## now analysis threshold input in arguments
    # if are define as default
    if thresholds_input == "default":
        return thresholds_by_default()


    # if are defined as percentile or standard deviation (all str instance)
    if not False in [isinstance(threshold,str) for threshold in thresholds_input]:

        # if are defined as p50+ - p50+NN
        if not False in [threshold.startswith(('p50+','P50+','p50-','P50-')) for threshold in thresholds_input]:
            p50_values = [threshold[3::] for threshold in thresholds_input]
            return thresholds_with_p50(p50_values)

        # if are defined as percentile - pNN
        if not False in [threshold.startswith(('p','P')) for threshold in thresholds_input]:
            percentile_values = [threshold[1::] for threshold in thresholds_input]
            return thresholds_with_percentiles(percentile_values)

        # if are defined as standard deviation - sdNN
        if not False in [threshold.startswith(('sd','SD')) for threshold in thresholds_input]:
            std_dev_values = [threshold[2::] for threshold in thresholds_input]
            return thresholds_with_std_deviation(std_dev_values)

        # if are defined as percentage - NN%
        if not False in [threshold.endswith("%") for threshold in thresholds_input]:
            percentage_values = [threshold[0:-1] for threshold in thresholds_input]
            return thresholds_with_percentage(percentage_values)

    # if are defined as particular values
    if not False in [isinstance(threshold,(int, float)) for threshold in thresholds_input]:
        return thresholds_with_particular_values(thresholds_input)

    # unrecognizable thresholds
    console.msg_error(_("unrecognizable thresholds '{0}' for var {1} ({2})")
        .format(thresholds_input, variable.type, env.var_[variable.type].TYPE_SERIES))
