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

import os
import csv
from calendar import monthrange
from datetime import date
from dateutil.relativedelta import relativedelta

from ...utils import globals_vars
from ...utils import format_out
from ...utils.mean import mean


def get_lag_values(station, var, lag, month, day=None):
    """
    Return all values of var_D, var_I or date
    of specific lag, month and/or day.
    """

    var_select = {'date': 0, 'var_D': 1, 'var_I': 2}
    lag_select = {0: station.Lag_0, 1: station.Lag_1, 2: station.Lag_2}
    temp_list = []
    for line in lag_select[lag]:
        if day:
            if month == line[0].month and day == line[0].day:
                temp_list.append(line)
        else:
            if month == line[0].month:
                temp_list.append(line)
    return [row[var_select[var]] for row in temp_list]


def calculate_lags(station):
    """
    Calculate and return lags 0, 1 and 2 of specific stations
    and save csv file of time series for each lag and trimester,
    the lags are calculated based in: +1 year below of start
    common period and -1 year above of end common period.

    Return:
    station with: Lag_0, Lag_1, Lag_2 and range_analysis_interval
    """

    # initialized Lag_X
    # format list: [trim, [ date, mean_var_D, mean_var_I ]], ...
    Lag_0 = []
    Lag_1 = []
    Lag_2 = []

    # directories to save lags
    dir_lag = [os.path.join(station.climate_dir, _('time_series'), _('lag_0')),
               os.path.join(station.climate_dir, _('time_series'), _('lag_1')),
               os.path.join(station.climate_dir, _('time_series'), _('lag_2'))]

    # range based on analysis interval
    range_analysis_interval = None
    if station.analysis_interval != "trimester":
        if station.analysis_interval_num_days == 5:
            range_analysis_interval = [1, 6, 11, 16, 21, 26]
        if station.analysis_interval_num_days == 10:
            range_analysis_interval = [1, 11, 21]
        if station.analysis_interval_num_days == 15:
            range_analysis_interval = [1, 16]

    def get_var_D_values():
        var_D_values = []
        if station.data_of_var_D == "daily":
            # clone range for add the last day (32) for calculate interval_day_var_D
            rai_plus = list(range_analysis_interval)
            rai_plus.append(32)
            # from day to next iterator based on analysis interval
            # e.g. [0,1,2,3,4] for first iteration for 5 days
            interval_day_var_D =\
            range(day - 1, rai_plus[rai_plus.index(day) + 1] - 1)

            for iter_day in interval_day_var_D:
                now = date(iter_year, month, 1) + relativedelta(days=iter_day)
                # check if continues with the same month
                if now.month == month:
                    index_var_D = station.date_D.index(now)
                    var_D_values.append(station.var_D[index_var_D])
        if station.data_of_var_D == "monthly":
            # get the three values for var_D in this month
            for iter_month in range(3):
                var_D_values.append(station.var_D[station.date_D.index(
                    date(iter_year, month, 1) + relativedelta(months=iter_month))])

        return var_D_values

    def get_var_I_values():
        var_I_values = []
        if station.data_of_var_I == "daily":
            # from day to next iterator based on analysis interval
            start_interval = range_analysis_interval[range_analysis_interval.index(day) - lag]
            try:
                end_interval = range_analysis_interval[range_analysis_interval.index(day) + 1 - lag]
            except:
                end_interval = range_analysis_interval[0]

            start_date = date(iter_year, month, start_interval)

            if range_analysis_interval.index(day) - lag < 0:
                start_date += relativedelta(months= -1)

            iter_date = start_date

            while iter_date.day != end_interval:
                index_var_I = station.date_I.index(iter_date)
                var_I_values.append(station.var_I[index_var_I])
                iter_date += relativedelta(days=1)

        if station.data_of_var_I == "monthly":
            if station.state_of_data in [1, 3]:
                # get the three values for var_I in this month
                for iter_month in range(3):
                    var_I_values.append(station.var_I[station.date_I.index(
                        date(iter_year, month, 1) + relativedelta(months=iter_month - lag))])
            if station.state_of_data in [2]:
                # keep constant value for month
                if station.analysis_interval == "trimester":
                    var_I_values.append(station.var_I[station.date_I.index(
                        date(iter_year, month, 1) + relativedelta(months= -lag))])
                else:
                    real_date = date(iter_year, month, day) + relativedelta(days= -station.analysis_interval_num_days * lag)
                    # e.g if lag 2 in march and calculate to 15days go to february and not january
                    if month - real_date.month > 1:
                        real_date = date(real_date.year, real_date.month + 1, 1)

                    var_I_values.append(station.var_I[station.date_I.index(
                        date(real_date.year, real_date.month, 1))])

        return var_I_values

    if station.state_of_data in [1, 3]:

        for lag in globals_vars.lags:

            if not os.path.isdir(dir_lag[lag]):
                os.makedirs(dir_lag[lag])

            # all months in year 1->12
            for month in range(1, 13):
                csv_name = os.path.join(dir_lag[lag],
                    _('Mean_lag_{0}_trim_{1}_{2}_{3}_{4}_{5}_'
                      '({6}-{7}).csv')
                    .format(lag, month, station.code,
                        station.name, station.type_D,
                        station.type_I,
                        station.process_period['start'],
                        station.process_period['end']))

                if os.path.isfile(csv_name):
                    os.remove(csv_name)

                # output write file:
                # [[ yyyy/month, Mean_Lag_X_var_D, Mean_Lag_X_var_I ],... ]
                open_file = open(csv_name, 'w')
                csv_file = csv.writer(open_file, delimiter=';')

                iter_year = station.process_period['start']

                # iteration for years from first-year +1 to end-year -1 inside
                # range common_period
                while iter_year <= station.process_period['end']:

                    # get values and calculate mean_var_D
                    mean_var_D = mean(get_var_D_values())

                    # get values and calculate mean_var_I
                    mean_var_I = mean(get_var_I_values())

                    # add line in list: Lag_X
                    vars()['Lag_' + str(lag)].append([date(iter_year, month, 1),
                                                      mean_var_D,
                                                      mean_var_I])

                    # add line output file csv_file
                    csv_file.writerow([str(iter_year) + "/" + str(month),
                                       format_out.number(mean_var_D),
                                       format_out.number(mean_var_I)])
                    # next year
                    iter_year += 1

                open_file.close()
                del csv_file

    if station.state_of_data in [2, 4]:

        for lag in globals_vars.lags:

            if not os.path.isdir(dir_lag[lag]):
                os.makedirs(dir_lag[lag])

            # all months in year 1->12
            for month in range(1, 13):
                csv_name = os.path.join(dir_lag[lag],
                    _('Mean_lag_{0}_{1}days_month_{2}_{3}_'
                      '{4}_{5}_{6}_({7}-{8}).csv')
                    .format(lag, station.analysis_interval_num_days,
                        month, station.code,
                        station.name, station.type_D,
                        station.type_I,
                        station.process_period['start'],
                        station.process_period['end']))

                if os.path.isfile(csv_name):
                    os.remove(csv_name)

                # output write file:
                # [[ yyyy/month, Mean_Lag_X_var_D, Mean_Lag_X_var_I ],... ]
                open_file = open(csv_name, 'w')
                csv_file = csv.writer(open_file, delimiter=';')

                #days_for_this_month = monthrange(iter_year, month)[1]

                for day in range_analysis_interval:

                    iter_year = station.process_period['start']

                    # iteration for years from first-year +1 to end-year -1 inside
                    # range common_period
                    while iter_year <= station.process_period['end']:

                        # test if day exist in month and year
                        if day > monthrange(iter_year, month)[1]:
                            iter_year += relativedelta(years= +1)
                            continue

                        # get values and calculate mean_var_D
                        mean_var_D = mean(get_var_D_values())

                        # get values and calculate mean_var_I
                        mean_var_I = mean(get_var_I_values())

                        # add line in list: Lag_X
                        vars()['Lag_' + str(lag)].append([date(iter_year, month, day),
                                                          mean_var_D,
                                                          mean_var_I])

                        # add line output file csv_file
                        csv_file.writerow([str(iter_year) + "/" + str(month)
                                           + "/" + str(day),
                                           format_out.number(mean_var_D),
                                           format_out.number(mean_var_I)])
                        # next year
                        iter_year += 1

                open_file.close()
                del csv_file

    station.range_analysis_interval = range_analysis_interval
    station.Lag_0, station.Lag_1, station.Lag_2 = Lag_0, Lag_1, Lag_2
