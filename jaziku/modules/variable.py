#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2011-2012 IDEAM
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

import sys
from datetime import date
from numpy import median, average
from scipy.stats.stats import tstd, variation, skew, kurtosis

from jaziku.modules.input import input_vars
from jaziku.modules.input.input_check import count_null_values
from jaziku.utils import console, globals_vars
from jaziku.utils.mean import mean

class Variable():
    """
    Class for save data raw, data dates, date filtered for dependence or
    independence variable of a station.
    """
    def __init__(self, type):
        if type in ['D','I']:
            self.type = type
        else:
            raise

    def read_data_from_file(self, station, process=True, messages=True):
        """
        Read var I and varD from files, validated and check consistent.

        :return by reference:
            VARIABLE.data
            VARIABLE.date
        """

        # -------------------------------------------------------------------------
        # Reading the variables from files and check based on range validation
        if messages:
            console.msg(_("Read and check (range validation) for var {0} ... ").format(self.type), newline=False)

        if process:
            if self.type == 'D':
                input_vars.read_var_D(station)
            if self.type == 'I':
                input_vars.read_var_I(station)

        if messages and (not globals_vars.config_run['limit_var_D_below'] or not globals_vars.config_run['limit_var_D_above']):
            console.msg(_("\n > WARNING: you are using one or both limit as\n"
                          "   \"none\" value, this means that series values\n"
                          "   will not be checked if they are valid in\n"
                          "   its limits coherent. This option is not\n"
                          "   recommended, use it with precaution ........"), color='yellow', newline=False)

        if messages:
            console.msg(_("done"), color='green')

            if self.type == "I" and station.file_I == "internal":
                internal_file_I_name = globals_vars.internal_var_I_files[station.type_I]
                split_internal_var_I = internal_file_I_name.split(".")[0].split("_")
                console.msg(
                    _(" > You are using internal files for independent\n"
                      "   variable defined as {0} which has data from\n"
                      "   {1} to {2} and the source of data was\n"
                      "   obtained in {3}.\n"
                      "   url: {4}")
                    .format(split_internal_var_I[0], split_internal_var_I[1],
                        split_internal_var_I[2], ' '.join(split_internal_var_I[3::]),
                        globals_vars.internal_var_I_urls[station.type_I]), color='yellow')

            if self.frequency_data == "daily":
                console.msg(_("   the variable {0} has data daily").format(self.type), color='cyan')
            if self.frequency_data== "monthly":
                console.msg(_("   the variable {0} has data monthly").format(self.type), color='cyan')


    def daily2monthly(self):
        """
        Convert the data daily to monthly using the mean

        :return by reference:
            VARIABLE.data (rewrite) (list)
            VARIABLE.date (rewrite) (list)
        """

        data_monthly = []
        date_monthly = []

        _iter = 0
        for year in range(self.date[0].year, self.date[-1].year + 1):
            for month in range(1, 13):
                var_month_list = []
                while self.date[_iter].month == month:
                    var_month_list.append(self.data[_iter])
                    _iter += 1
                    if _iter > self.date.index(self.date[-1]):
                        break
                data_monthly.append(mean(var_month_list))
                date_monthly.append(date(year, month, 1))

        self.data = data_monthly
        self.date = date_monthly

    def data_and_null_in_process_period(self, station):
        """
        Calculate the data without the null values inside
        the process period and null values.

        :return by reference:
            VARIABLE.data_in_process_period (list)
            VARIABLE.data_filtered_in_process_period (list)
            VARIABLE.null_values_in_process_period (int)
        """
        start_date_var = date(station.process_period['start'], 1, 1)
        if self.frequency_data== "daily":
            end_date_var = date(station.process_period['end'], 12, 31)
        else:
            end_date_var = date(station.process_period['end'], 12, 1)

        # data inside the process period
        self.data_in_process_period = self.data[self.date.index(start_date_var):\
                                                self.date.index(end_date_var) + 1]
        # date inside the process period
        self.date_in_process_period = self.date[self.date.index(start_date_var):\
        self.date.index(end_date_var) + 1]
        # nulls inside the process period
        self.null_values_in_process_period = count_null_values(self.data_in_process_period)

        # delete all valid nulls
        self.data_filtered_in_process_period = [ value for value in self.data_in_process_period if not globals_vars.is_valid_null(value) ]



    def do_some_statistic_of_data(self, station):

        # size data
        self.size_data = len(self.data_filtered_in_process_period)
        # maximum
        self.maximum = max(self.data_filtered_in_process_period)
        # minimum
        self.minimum = min(self.data_filtered_in_process_period)
        # average
        self.average = average(self.data_filtered_in_process_period)
        # median
        self.median = median(self.data_filtered_in_process_period)
        # std deviation
        self.std_dev = tstd(self.data_filtered_in_process_period)
        # skewness
        self.skew = skew(self.data_filtered_in_process_period, bias=False)
        # kurtosis
        self.kurtosis = kurtosis(self.data_filtered_in_process_period, bias=False)
        # c-variation
        self.coef_variation = variation(self.data_filtered_in_process_period)



