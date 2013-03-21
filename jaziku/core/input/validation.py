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

from jaziku import env
from jaziku.utils import console, format_in


#==============================================================================
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
    if variable.type == 'D':
        if not env.config_run.settings['limits_var_D']['ready']:
            # set global limits for var D only once
            set_limits(variable)
        limit_below = env.config_run.settings['limits_var_D']['below']
        limit_above = env.config_run.settings['limits_var_D']['above']
    if variable.type == 'I':
        if not env.config_run.settings['limits_var_I']['ready']:
            # set global limits for var I only once
            set_limits(variable)
        limit_below = env.config_run.settings['limits_var_I']['below']
        limit_above = env.config_run.settings['limits_var_I']['above']

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
    if variable.type == 'D':
        input_limit_below = env.config_run.settings['limits_var_D']['below']
        input_limit_above = env.config_run.settings['limits_var_D']['above']
        limits_by_default = env.var_D.get_internal_limits()
    if variable.type == 'I':
        input_limit_below = env.config_run.settings['limits_var_I']['below']
        input_limit_above = env.config_run.settings['limits_var_I']['above']
        limits_by_default = env.var_I.get_internal_limits()

    if input_limit_below is not None:
        # defined limit by below
        if input_limit_below == "default":
            limit_below = limits_by_default[0]
            if limit_below is None:
                console.msg_error(_("The type '{0}' for var {1} hasn't limits by default\n"
                                    "use a internal valid type or defined the limits in the runfile")
                .format(variable.type_series, variable.type))
        else:
            limit_below = format_in.to_float(input_limit_below)
            if limit_below is None:
                console.msg_error(_("The limit '{0}' for var {1} is not valid limit")
                .format(input_limit_below, variable.type))
    else:
        limit_below = None

    if input_limit_above is not None:
        # defined limit by above
        if input_limit_above == "default":
            limit_above = limits_by_default[1]
            if limit_above is None:
                console.msg_error(_("The type '{0}' for var {1} hasn't limits by default\n"
                                    "use a internal valid type or defined the limits in the runfile")
                .format(variable.type_series, variable.type))
        else:
            limit_above = format_in.to_float(input_limit_above)
            if limit_above is None:
                console.msg_error(_("The limit '{0}' for var {1} is not valid limit")
                .format(input_limit_above, variable.type))
    else:
        limit_above = None

    if variable.type == 'D':
        env.config_run.settings['limits_var_D']['below'] = limit_below
        env.config_run.settings['limits_var_D']['above'] = limit_above
        env.config_run.settings['limits_var_D']['ready'] = True
    if variable.type == 'I':
        env.config_run.settings['limits_var_I']['below'] = limit_below
        env.config_run.settings['limits_var_I']['above'] = limit_above
        env.config_run.settings['limits_var_I']['ready'] = True


#==============================================================================
# VALIDATION OF NULL VALUES FOR DEPENDENT AND INDEPENDENT VARIABLE

def check_consistent_data(station):
    """
    Check if the data are consistent for var D and I, this is that the
    amount of null value not exceed in 15% of the total number of values
    inside process period
    """

    # -------------------------------------------------------------------------
    # check if the data are consistent for variable
    #console.msg(_("Check if var {0} are consistent").format(variable.type), newline=False)

#    # temporal var initialize start_date = start common_period + 1 year,
#    # month=1, day=1
#    start_date = date(station.process_period['start'], 1, 1)
#    # temporal var initialize end_date = end common_period - 1 year,
#    # month=12, day=31
#    if (var_type == "D" and station.var_D.frequency_data== "daily") or\
#       (var_type == "I" and env.var_I.is_daily()):
#        end_date = date(station.process_period['end'], 12, 31)
#        if env.config_run.get['analysis_interval'] == "trimester":
#            date_plus = monthrange(station.process_period['end'] + 1, 1)[1] +\
#                        monthrange(station.process_period['end'] + 1, 2)[1]
#            date_minus = 61
#        else:
#            date_plus = date_minus = env.globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL * 2
#    else:
#        end_date = date(station.process_period['end'], 12, 1)
#        date_plus = date_minus = 2
#
#    if var_type == "D":
#        values_in_common_period \
#            = station.var_D.data[station.var_D.date.index(start_date):station.var_D.date.index(end_date) + date_plus + 1]
#    if var_type == "I":
#        values_in_common_period \
#            = station.var_I.data[station.var_I.date.index(start_date) - date_minus:station.var_I.date.index(end_date) + date_plus + 1]


    # station for check
    console.msg("   {0} - {1}:".format(station.code, station.name))

    # var D
    console.msg(_("      var D: {0} ({1}%) nulls of {2}:")
                .format(station.var_D.nulls_in_process_period, station.var_D.percentage_of_nulls_in_process_period,
                        len(station.var_D.data_in_process_period)), newline=False)
    # check var D
    if  station.var_D.nulls_in_process_period / float(len(station.var_D.data_in_process_period)) > 0.15:
        console.msg_error(_("the number of null values is greater than 15% of total\n"
                            "of values inside common period, therefore, for Jaziku\n"
                            "the data are not consistent for process."))

    console.msg(_("ok"), color='green')

    # var I
    console.msg(_("      var I: {0} ({1}%) nulls of {2}:")
                .format(station.var_I.nulls_in_process_period, station.var_I.percentage_of_nulls_in_process_period,
                        len(station.var_I.data_in_process_period)), newline=False)
    # check var I
    if  station.var_I.nulls_in_process_period / float(len(station.var_I.data_in_process_period)) > 0.15:
        console.msg_error(_("the number of null values is greater than 15% of total\n"
                            "of values inside common period, therefore, for Jaziku\n"
                            "the data are not consistent for process."))

    console.msg(_("ok"), color='green')


