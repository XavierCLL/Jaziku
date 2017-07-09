#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2011-2017 Xavier Corredor Ll. - IDEAM
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

from jaziku import env
from jaziku.utils import console, input


# ==============================================================================
# VALIDATION OF LIMITS FOR DEPENDENT AND INDEPENDENT VARIABLE


def is_the_value_within_limits(value, variable):
    """Check the `value` if is within limits
    defined for this type of variable by default
    or defined in runfile.

    :param value: the value for check
    :type value: float
    :param variable: the variable to which the value belongs
    :type variable: Variable

    :return: True if passed the check, or raise ValueError
    """

    # first test if the value is a valid null
    if env.globals_vars.is_valid_null(value):
        return True

    # get input values for limits define in runfile
    if not env.config_run.settings['limits_var_' + variable.type]['ready']:
        # set global limits for var D only once
        set_limits(variable)
    limit_below = env.config_run.settings['limits_var_' + variable.type]['below']
    limit_above = env.config_run.settings['limits_var_' + variable.type]['above']

    ## check
    if limit_below is not None:
        # check by below
        if value < limit_below:
            raise ValueError(_("Error validating the value '{0}' it isn't within\n"
                               "limits ({1} to {2}) defined for the var {3} ({4}).")
                             .format(round(value, 4), limit_below, limit_above, variable.type, variable.type_series))
    if limit_above is not None:
        # check by above
        if value > limit_above:
            raise ValueError(_("Error validating the value '{0}' it isn't within\n"
                               "limits ({1} to {2}) defined for the var {3} ({4}).")
                             .format(round(value, 4), limit_below, limit_above, variable.type, variable.type_series))

    return True


def set_limits(variable):
    """Set the limits by default or defined in runfile
    for the var_D or var_I

    :param variable: variable for set the limits
    :type variable: Variable

    Return by reference (one):

    :ivar limits_var_I: env.config_run.settings['limits_var_I']['below'] and ['above']
    :ivar limits_var_D: env.config_run.settings['limits_var_D']['below'] and ['above']

    .. note:: Only needs to run once for variable
    """
    # get input values for limits define in runfile
    input_limit_below = env.config_run.settings['limits_var_' + variable.type]['below']
    input_limit_above = env.config_run.settings['limits_var_' + variable.type]['above']
    limits_by_default = env.var_[variable.type].get_internal_limits()

    if input_limit_below is not None:
        # defined limit by below
        if input_limit_below == "default":
            # check if limit by default have valid value
            if limits_by_default is None:
                limit_below = None
            else:
                limit_below = limits_by_default[0]
            if limit_below is None:
                console.msg_error(_("The type '{0}' for var {1} hasn't limits by default for\n"
                                    "data {2}, use a internal valid type and/or valid data frequency\n"
                                    "or defined the particular limits in the runfile")
                                  .format(variable.type_series, variable.type, env.var_[variable.type].FREQUENCY_DATA))
        else:
            limit_below = input.to_float(input_limit_below)
            if limit_below is None:
                console.msg_error(_("The limit '{0}' for var {1} is not valid limit")
                                  .format(input_limit_below, variable.type))
    else:
        limit_below = None

    if input_limit_above is not None:
        # defined limit by above
        if input_limit_above == "default":
            # check if limit by default have valid value
            if limits_by_default is None:
                limit_above = None
            else:
                limit_above = limits_by_default[1]
            if limit_above is None:
                console.msg_error(_("The type '{0}' for var {1} hasn't limits by default for\n"
                                    "data {2}, use a internal valid type and/or valid data frequency\n"
                                    "or defined the particular limits in the runfile")
                                  .format(variable.type_series, variable.type, env.var_[variable.type].FREQUENCY_DATA))
        else:
            limit_above = input.to_float(input_limit_above)
            if limit_above is None:
                console.msg_error(_("The limit '{0}' for var {1} is not valid limit")
                                  .format(input_limit_above, variable.type))
    else:
        limit_above = None

    env.config_run.settings['limits_var_' + variable.type]['below'] = limit_below
    env.config_run.settings['limits_var_' + variable.type]['above'] = limit_above
    env.config_run.settings['limits_var_' + variable.type]['ready'] = True


# ==============================================================================
# VALIDATION OF NULL VALUES FOR DEPENDENT AND INDEPENDENT VARIABLE

def check_consistent_data(station):
    """Check if the data are consistent for var D and I, this is that the amount
    of null value not exceed in NN% (defined in runfile in consistent_data options)
    of the total number of values inside process period
    """

    # -------------------------------------------------------------------------
    # check if the data are consistent for variable

    # transform of percentage of validation to 0 -> 1
    value_of_validation = env.config_run.settings['consistent_data'] / 100.0

    # station for check
    console.msg("   {0} - {1}:".format(station.code, station.name))

    def check(var_type):
        console.msg(_("      var {0}: {1} ({2}%) nulls of {3}:")
                    .format(var_type, station.var_[var_type].nulls_in_process_period,
                            station.var_[var_type].percentage_of_nulls_in_process_period,
                            len(station.var_[var_type].data_in_process_period)), newline=False)
        # check var
        if station.var_[var_type].nulls_in_process_period / float(
                len(station.var_[var_type].data_in_process_period)) > value_of_validation:
            console.msg_error(_("The number of null values is greater than {0}% of total\n"
                                "of values inside common period, therefore, for Jaziku\n"
                                "the data are not consistent for process. You can disable\n"
                                "this check in the option 'consistent_data' of runfile.").format(
                value_of_validation * 100.0))

        console.msg(_("ok"), color='green')

    # var D
    check('D')

    # var I
    check('I')
