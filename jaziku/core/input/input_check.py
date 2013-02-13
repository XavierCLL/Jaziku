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

from jaziku.env import globals_vars
from jaziku.utils import  console


def count_null_values(values):
    """
    Return the number of valid null values of array

    :return:
        number of nulls (int)
    """
    null_counter = 0
    for value in values:
        if globals_vars.is_valid_null(value):
            null_counter += 1

    return null_counter


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
#       (var_type == "I" and station.var_I.frequency_data == "daily"):
#        end_date = date(station.process_period['end'], 12, 31)
#        if config_run.get['analysis_interval'] == "trimester":
#            date_plus = monthrange(station.process_period['end'] + 1, 1)[1] +\
#                        monthrange(station.process_period['end'] + 1, 2)[1]
#            date_minus = 61
#        else:
#            date_plus = date_minus = globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL * 2
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
    console.msg(_("      var D: {0} null of {1}:").format(station.var_D.null_values_in_process_period,
                                                          len(station.var_D.data_in_process_period)), newline=False)
    # check var D
    if  station.var_D.null_values_in_process_period / float(len(station.var_D.data_in_process_period)) >= 0.15:
        console.msg_error(_("the number of null values is greater than 15% of total\n"
                            "of values inside common period, therefore, for Jaziku\n"
                            "the data are not consistent for process."))

    console.msg(_("ok"), color='green')

    # var I
    console.msg(_("      var I: {0} null of {1}:").format(station.var_I.null_values_in_process_period,
        len(station.var_I.data_in_process_period)), newline=False)
    # check var I
    if  station.var_I.null_values_in_process_period / float(len(station.var_I.data_in_process_period)) >= 0.15:
        console.msg_error(_("the number of null values is greater than 15% of total\n"
                            "of values inside common period, therefore, for Jaziku\n"
                            "the data are not consistent for process."))

    console.msg(_("ok"), color='green')
