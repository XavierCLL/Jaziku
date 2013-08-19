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

import os
import csv
from calendar import monthrange
from datetime import date
from dateutil.relativedelta import relativedelta

from jaziku import env
from jaziku.core.analysis_interval import get_values_in_range_analysis_interval, get_range_analysis_interval
from jaziku.utils import  array, output


def get_specific_values(station, var, lag, month, day=None):
    """Return all values of var_D, var_I or date
    inside the period to process with a specific lag,
    trimester/month and/or day.

    :param station: station for calculate the lag
    :type station: Station
    :param var: variable to process 'var_D', 'var_I', 'date'
    :type var: str
    :param lag: lag to get values
    :type lag: int
    :param month: trimester/month to get values
    :type month: int
    :param day: day of month, or None if is trimester
    :type day: int

    :return: list of specific values
    :rtype: list
    """

    var_select = {'date': 0, 'var_D': 1, 'var_I': 2}
    lag_select = {0: station.time_series['lag_0'], 1: station.time_series['lag_1'], 2: station.time_series['lag_2']}
    temp_list = []
    for line in lag_select[lag]:
        if day:
            if month == line[0].month and day == line[0].day:
                temp_list.append(line)
        else:
            if month == line[0].month:
                temp_list.append(line)
    return [row[var_select[var]] for row in temp_list]


def calculate_specific_value_of_time_series(variable, values_in_range_analysis_interval):
    '''Calculate time series of specific values in range analysis interval
    (this values is values in specific lag, year, month and range analysis interval)
    and calculate the mean or accumulate (based on mode calculation series), but if
    the number of nulls is great than 40% in this values, the return value is NaN.
    '''

    # check percentage of nulls
    number_of_nulls, percentage_of_nulls = array.check_nulls(values_in_range_analysis_interval)

    if percentage_of_nulls > 40:
        time_series_value = float('NaN')
    elif variable.type == 'I' and variable.type_series in ['ONI1', 'ONI2', 'CAR']:
        # SPECIAL CASE 1: when var_I is ONI1, ONI2 or CAR, don't calculate trimesters because the ONI and CAR
        # series was calculated by trimesters from original source
        time_series_value = values_in_range_analysis_interval[0]
    else:
        # calculate time series based on mode calculation series
        if env.config_run.settings['mode_calculation_series_'+variable.type] == 'mean':
            time_series_value = array.mean(values_in_range_analysis_interval)
        if env.config_run.settings['mode_calculation_series_'+variable.type] == 'accumulate':
            time_series_value = sum(array.clean(values_in_range_analysis_interval))

    return time_series_value


def calculate_time_series(station, makes_files=True):
    """Calculate and add dictionary to station of time series calculated for
    lags 0, 1 and 2 of var_D and var_I based on mode calculation series and
    analysis interval defined in runfile and, of course, type of series
    (daily, monthly,...). Also makes csv file of time series for each lag and
    trimester calculated based on the analysis interval.

    :param station: station for process
    :type station: Station
    :param makes_files: make lags file time series or not
    :type makes_files: bool

    Return by reference:

    :ivar STATION.time_series['lag_0'][[date,var_D,var_I],...]: time series calculated for lag 0 of this station
    :ivar STATION.time_series['lag_1'][[date,var_D,var_I],...]: time series calculated for lag 1 of this station
    :ivar STATION.time_series['lag_2'][[date,var_D,var_I],...]: time series calculated for lag 2 of this station
    """

    # initialized Lag_X
    # format list for each lag: [trim, [ date, time_series_value_of_var_D, time_series_value_of_var_I ]], ...
    station.time_series = {'lag_0':[], 'lag_1':[], 'lag_2':[]}

    if makes_files:
        # directories to save lags
        dir_lag = [os.path.join(station.climate_dir, _('time_series'), _('lag_0')),
                   os.path.join(station.climate_dir, _('time_series'), _('lag_1')),
                   os.path.join(station.climate_dir, _('time_series'), _('lag_2'))]

    if env.globals_vars.STATE_OF_DATA in [1, 3]:

        for lag in env.config_run.settings['lags']:

            if makes_files:
                output.make_dirs(dir_lag[lag])

            # all months in year 1->12
            for month in range(1, 13):
                if makes_files:
                    csv_name = os.path.join(dir_lag[lag],
                        _('Time_Series_lag_{0}_trim_{1}_{2}_{3}_{4}_{5}_{6}_'
                          '({7}-{8}).csv')
                        .format(
                            lag, month,
                            output.trimester_in_initials(month - 1),
                            station.code,
                            station.name, station.var_D.type_series,
                            station.var_I.type_series,
                            station.process_period['start'],
                            station.process_period['end']))

                    if os.path.isfile(csv_name):
                        os.remove(csv_name)

                    # output write file:
                    # [[ yyyy/month, Mean_Lag_X_var_D, Mean_Lag_X_var_I ],... ]
                    open_file = open(csv_name, 'w')
                    csv_file = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)

                    # print headers
                    csv_file.writerow([_('DATE'), _('VAR_D')+' ({0})'.format(station.var_D.type_series),
                                       _('VAR_I')+' ({0})'.format(station.var_I.type_series)])
                    csv_file.writerow(['', env.config_run.settings['mode_calculation_series_D_i18n'],
                                       env.config_run.settings['mode_calculation_series_I_i18n']])

                iter_year = station.process_period['start']

                # iteration for years from first-year +1 to end-year -1 inside
                # range common_period
                while iter_year <= station.process_period['end']:

                    ## calculate time series, get values and calculate the mean or accumulate the values in range analysis
                    values_in_range_analysis_interval = get_values_in_range_analysis_interval(station,'D', iter_year, month)
                    time_series_value_of_var_D = calculate_specific_value_of_time_series(station.var_D, values_in_range_analysis_interval)

                    values_in_range_analysis_interval = get_values_in_range_analysis_interval(station,'I', iter_year, month, lag=lag)
                    time_series_value_of_var_I = calculate_specific_value_of_time_series(station.var_I, values_in_range_analysis_interval)

                    # add line in list: Lag_X
                    station.time_series['lag_'+str(lag)].append([date(iter_year, month, 1), time_series_value_of_var_D, time_series_value_of_var_I])

                    # add line output file csv_file
                    if makes_files:
                        csv_file.writerow([str(iter_year) + "/" + str(month),
                                           output.number(time_series_value_of_var_D),
                                           output.number(time_series_value_of_var_I)])
                    # next year
                    iter_year += 1

                if makes_files:
                    open_file.close()
                    del csv_file

    if env.globals_vars.STATE_OF_DATA in [2, 4]:

        for lag in env.config_run.settings['lags']:
            if makes_files:
                output.make_dirs(dir_lag[lag])

            # all months in year 1->12
            for month in range(1, 13):
                if makes_files:
                    csv_name = os.path.join(dir_lag[lag],
                        _('Time_Series_lag_{0}_{1}_month_{2}_{3}_'
                          '{4}_{5}_{6}_({7}-{8}).csv')
                        .format(
                            lag, env.config_run.settings['analysis_interval_i18n'],
                            month, station.code,
                            station.name, station.var_D.type_series,
                            station.var_I.type_series,
                            station.process_period['start'],
                            station.process_period['end']))

                    if os.path.isfile(csv_name):
                        os.remove(csv_name)

                    # output write file:
                    # [[ yyyy/month, Mean_Lag_X_var_D, Mean_Lag_X_var_I ],... ]
                    open_file = open(csv_name, 'w')
                    csv_file = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)

                    # print headers
                    csv_file.writerow([_('DATE'), _('VAR_D')+' ({0})'.format(station.var_D.type_series),
                                       _('VAR_I')+' ({0})'.format(station.var_I.type_series)])
                    csv_file.writerow(['', env.config_run.settings['mode_calculation_series_D_i18n'],
                                       env.config_run.settings['mode_calculation_series_I_i18n']])

                #days_for_this_month = monthrange(iter_year, month)[1]

                for day in get_range_analysis_interval():

                    iter_year = station.process_period['start']

                    # iteration for years from first-year +1 to end-year -1 inside
                    # range common_period
                    while iter_year <= station.process_period['end']:

                        # test if day exist in month and year
                        if day > monthrange(iter_year, month)[1]:
                            iter_year += relativedelta(years= +1)
                            continue

                        ## calculate time series, get values and calculate the mean or accumulate the values in range analysis of var D
                        values_in_range_analysis_interval = get_values_in_range_analysis_interval(station,'D', iter_year, month, day, lag)
                        time_series_value_of_var_D = calculate_specific_value_of_time_series(station.var_D, values_in_range_analysis_interval)

                        values_in_range_analysis_interval = get_values_in_range_analysis_interval(station,'I', iter_year, month, day, lag)
                        time_series_value_of_var_I = calculate_specific_value_of_time_series(station.var_I, values_in_range_analysis_interval)

                        # add line in list: Lag_X
                        station.time_series['lag_'+str(lag)].append([date(iter_year, month, day), time_series_value_of_var_D, time_series_value_of_var_I])

                        # add line output file csv_file
                        if makes_files:
                            csv_file.writerow([str(iter_year) + "/" + str(month)
                                               + "/" + str(day),
                                               output.number(time_series_value_of_var_D),
                                               output.number(time_series_value_of_var_I)])
                        # next year
                        iter_year += 1
                if makes_files:
                    open_file.close()
                    del csv_file