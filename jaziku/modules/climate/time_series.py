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

import os
import csv
from calendar import monthrange
from datetime import date

from jaziku import env
from jaziku.core.analysis_interval import get_values_in_range_analysis_interval, get_range_analysis_interval
from jaziku.utils import array, output


def get_specific_values(station, var, lag, n_month, day=None):
    """Return all values of var_D, var_I or date
    inside the period to process with a specific lag,
    n_month and/or day.

    :param station: station for calculate the lag
    :type station: Station
    :param var: variable to process 'var_D', 'var_I', 'date'
    :type var: str
    :param lag: lag to get values
    :type lag: int
    :param n_month: N-monthly or month to get values
    :type n_month: int
    :param day: day of month, or None if is n-monthly
    :type day: int

    :return: list of specific values
    :rtype: list
    """

    var_select = {'date': 0, 'var_D': 1, 'var_I': 2}
    lag_select = {0: station.time_series['lag_0'], 1: station.time_series['lag_1'], 2: station.time_series['lag_2']}
    temp_list = []
    for line in lag_select[lag]:
        if day:
            if n_month == line[0].month and day == line[0].day:
                temp_list.append(line)
        else:
            if n_month == line[0].month:
                temp_list.append(line)
    return [row[var_select[var]] for row in temp_list]


def calculate_specific_values_of_time_series(variable, specific_values):
    '''Calculate time series of specific values in range analysis interval
    (this values is values in specific lag, year, month and range analysis interval)
    and calculate the mean or accumulate (based on mode calculation series), but if
    the number of nulls is great than 40% in this values, the return value is NaN.
    '''

    # if only have one value, return this
    if isinstance(specific_values, (int, float)):
        return specific_values
    elif isinstance(specific_values, list) and len(specific_values) == 1:
        return specific_values[0]

    # check percentage of nulls
    number_of_nulls, percentage_of_nulls = array.check_nulls(specific_values)

    # check if null if over 40% (except if is 1)
    if percentage_of_nulls > 40 and number_of_nulls != 1:
        return float('NaN')
    # calculate time series based on mode calculation series
    if env.config_run.settings['mode_calculation_series_' + variable.type] == 'mean':
        return array.mean(specific_values)
    if env.config_run.settings['mode_calculation_series_' + variable.type] == 'accumulate':
        return sum(array.clean(specific_values))


def calculate_time_series(station, lags=None, makes_files=True):
    """Calculate and add dictionary to station of time series calculated for
    lags 0, 1 and 2 of var_D and var_I based on mode calculation series and
    analysis interval defined in runfile and, of course, type of series
    (daily, monthly,...). Also makes csv file of time series for each lag and
    trimonthly calculated based on the analysis interval.

    :param station: station for process
    :type station: Station
    :param makes_files: make lags file time series or not
    :type makes_files: bool

    Return by reference:

    :ivar STATION.time_series['lag_0'][[date,var_D,var_I],...]: time series calculated for lag 0 of this station
    :ivar STATION.time_series['lag_1'][[date,var_D,var_I],...]: time series calculated for lag 1 of this station
    :ivar STATION.time_series['lag_2'][[date,var_D,var_I],...]: time series calculated for lag 2 of this station
    """
    # if is None set lags defined in runfile
    lags = env.config_run.settings['lags'] if lags is None else lags

    # initialized Lag_X
    # format list for each lag: [trim, [ date, time_series_value_of_var_D, time_series_value_of_var_I ]], ...
    station.time_series = {'lag_0': [], 'lag_1': [], 'lag_2': []}

    if makes_files:
        # directories to save lags
        dir_lag = [os.path.join(station.climate_dir, _('time_series'), _('lag_0')),
                   os.path.join(station.climate_dir, _('time_series'), _('lag_1')),
                   os.path.join(station.climate_dir, _('time_series'), _('lag_2'))]

    if env.var_D.is_n_monthly():

        for lag in lags:

            if makes_files:
                output.make_dirs(dir_lag[lag])

            # all months in year 1->12
            for month in range(1, 13):
                if makes_files:
                    csv_name = os.path.join(dir_lag[lag],
                                            _('Time_Series_lag_{0}_{1}_{2}_{3}_{4}_{5}_'
                                              '({6}-{7}).csv')
                                            .format(
                                                lag, output.n_months_in_initials('D', month),
                                                station.code, station.name, station.var_D.type_series,
                                                station.var_I.type_series,
                                                env.globals_vars.PROCESS_PERIOD['start'],
                                                env.globals_vars.PROCESS_PERIOD['end']))

                    if os.path.isfile(csv_name):
                        os.remove(csv_name)

                    # output write file:
                    # [[ yyyy/month, Mean_Lag_X_var_D, Mean_Lag_X_var_I ],... ]
                    open_file = open(csv_name, 'w')
                    csv_file = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)

                    # print headers
                    csv_file.writerow([_('DATE'), _('VAR_D') + ' ({0})'.format(station.var_D.type_series),
                                       _('VAR_I') + ' ({0})'.format(station.var_I.type_series)])
                    csv_file.writerow(['', env.config_run.get_MODE_CALCULATION_SERIES_i18n("D"),
                                       env.config_run.get_MODE_CALCULATION_SERIES_i18n("I")])

                # iteration for all years inside process period
                for year in range(env.globals_vars.PROCESS_PERIOD['start'], env.globals_vars.PROCESS_PERIOD['end'] + 1):

                    ## calculate time series, get values and calculate the mean or accumulate the values in range analysis
                    values_in_range_analysis_interval = get_values_in_range_analysis_interval(station.var_D, year,
                                                                                              month)
                    time_series_value_of_var_D = calculate_specific_values_of_time_series(station.var_D,
                                                                                          values_in_range_analysis_interval)

                    values_in_range_analysis_interval = get_values_in_range_analysis_interval(station.var_I, year,
                                                                                              month, lag=lag)
                    time_series_value_of_var_I = calculate_specific_values_of_time_series(station.var_I,
                                                                                          values_in_range_analysis_interval)

                    # add line in list: Lag_X
                    station.time_series['lag_' + str(lag)].append(
                        [date(year, month, 1), time_series_value_of_var_D, time_series_value_of_var_I])

                    # add line output file csv_file
                    if makes_files:
                        csv_file.writerow([str(year) + "-" + output.n_monthly_int2char(month, type="D"),
                                           output.number(time_series_value_of_var_D),
                                           output.number(time_series_value_of_var_I)])

                if makes_files:
                    open_file.close()
                    del csv_file

    if env.var_D.is_n_daily():

        for lag in lags:
            if makes_files:
                output.make_dirs(dir_lag[lag])

            # all months in year 1->12
            for month in range(1, 13):
                if makes_files:
                    csv_name = os.path.join(dir_lag[lag],
                                            _('Time_Series_lag_{0}_{1}_{2}_{3}_'
                                              '{4}_{5}_{6}_({7}-{8}).csv')
                                            .format(
                                                lag, env.config_run.get_ANALYSIS_INTERVAL_i18n(),
                                                output.months_in_initials(month - 1), station.code,
                                                station.name, station.var_D.type_series,
                                                station.var_I.type_series,
                                                env.globals_vars.PROCESS_PERIOD['start'],
                                                env.globals_vars.PROCESS_PERIOD['end']))

                    if os.path.isfile(csv_name):
                        os.remove(csv_name)

                    # output write file:
                    # [[ yyyy/month, Mean_Lag_X_var_D, Mean_Lag_X_var_I ],... ]
                    open_file = open(csv_name, 'w')
                    csv_file = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)

                    # print headers
                    csv_file.writerow([_('DATE'), _('VAR_D') + ' ({0})'.format(station.var_D.type_series),
                                       _('VAR_I') + ' ({0})'.format(station.var_I.type_series)])
                    csv_file.writerow(['', env.config_run.get_MODE_CALCULATION_SERIES_i18n("D"),
                                       env.config_run.get_MODE_CALCULATION_SERIES_i18n("I")])

                for day in get_range_analysis_interval():

                    # iteration for all years inside process period
                    for year in range(env.globals_vars.PROCESS_PERIOD['start'],
                                      env.globals_vars.PROCESS_PERIOD['end'] + 1):

                        # test if day exist in month and year
                        if day > monthrange(year, month)[1]:
                            continue

                        ## calculate time series, get values and calculate the mean or accumulate the values in range analysis of var D
                        values_in_range_analysis_interval = get_values_in_range_analysis_interval(station.var_D, year,
                                                                                                  month, day, lag)
                        time_series_value_of_var_D = calculate_specific_values_of_time_series(station.var_D,
                                                                                              values_in_range_analysis_interval)

                        values_in_range_analysis_interval = get_values_in_range_analysis_interval(station.var_I, year,
                                                                                                  month, day, lag)
                        time_series_value_of_var_I = calculate_specific_values_of_time_series(station.var_I,
                                                                                              values_in_range_analysis_interval)

                        # add line in list: Lag_X
                        station.time_series['lag_' + str(lag)].append(
                            [date(year, month, day), time_series_value_of_var_D, time_series_value_of_var_I])

                        # add line output file csv_file
                        if makes_files:
                            csv_file.writerow([str(year) + "-" + output.fix_zeros(month)
                                               + "-" + output.fix_zeros(day),
                                               output.number(time_series_value_of_var_D),
                                               output.number(time_series_value_of_var_I)])
                if makes_files:
                    open_file.close()
                    del csv_file
