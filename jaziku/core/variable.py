#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2011-2014 IDEAM
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
from datetime import date
from calendar import monthrange
from dateutil.relativedelta import relativedelta
from numpy import median, average, var, std
from scipy.stats.stats import variation, skew, kurtosis
from copy import deepcopy

from jaziku import env
from jaziku.core.input import vars
from jaziku.core.analysis_interval import get_range_analysis_interval, get_values_in_range_analysis_interval
from jaziku.modules.climate.time_series import calculate_specific_values_of_time_series
from jaziku.utils import console, array


class Variable(object):
    """Class for save data raw, data dates, date filtered for dependent or
    independent variable of a station.

    :attributes:
        VARIABLE.station: station instance which belongs to this variable
        VARIABLE.type: type of variable 'D' (dependent) or 'I' (independent)
        VARIABLE.type_series: type of series (D or I), e.g. 'SOI'
        VARIABLE.file_name: the name of file of series
        VARIABLE.file_path: the absolute path where save the file of series
        VARIABLE.data: complete data of series
        VARIABLE.date: complete date of series
        VARIABLE.origin_data: original complete data of series
        VARIABLE.origin_date: original complete date of series
        VARIABLE.origin_frequency_data: original the frequency data
        VARIABLE.was_converted
        plus attributes return of methods:
            data_and_null_in_process_period()
            do_some_statistic_of_data()
    """

    def __init__(self, type, station):
        if type in ['D', 'I']:
            self.type = type
        else:
            raise
        # save the station instance which belongs to this variable
        self.station = station
        # for save the original data/date/freq
        self.origin_data = None
        self.origin_date = None
        self.origin_frequency_data = None

    def set_file(self, file):

        if self.type == 'D':
            self.file_name = os.path.basename(file)
            # if path to file is relative convert to absolute
            if not os.path.isabs(file):
                self.file_path = os.path.abspath(os.path.join(os.path.dirname(env.globals_vars.ARGS.runfile), file))
            else:
                self.file_path = os.path.abspath(file)

        if self.type == 'I':

            # read from internal variable independent files of Jaziku, check
            # and notify if Jaziku are using the independent variable inside
            # located in plugins/var_I/
            if file == "internal":
                if self.type_series in env.var_I.INTERNAL_FILES:
                    self.file_name = env.var_I.INTERNAL_FILES[self.type_series]
                    self.file_path = os.path.join(env.globals_vars.JAZIKU_DIR, 'data', 'var_I', self.file_name)
            else:
                self.file_name = os.path.basename(file)
                # if path to file is relative convert to absolute
                if not os.path.isabs(file):
                    self.file_path = os.path.abspath(os.path.join(os.path.dirname(env.globals_vars.ARGS.runfile), file))
                else:
                    self.file_path = os.path.abspath(file)

        # relative path to file
        self.file_relpath = os.path.relpath(file, os.path.abspath(os.path.dirname(env.globals_vars.ARGS.runfile)))

    def read_data_from_file(self):
        """Read var I or var D from files, validated and check consistent.

        :return by reference:
            VARIABLE.data
            VARIABLE.date
        """

        # -------------------------------------------------------------------------
        # Reading the variables from files and check based on range validation
        # and fill variable if is needed
        vars.read_variable(self)
        self.fill_variable()

        # save the original data/date/freq
        self.origin_data = deepcopy(self.data)
        self.origin_date = deepcopy(self.date)
        self.origin_frequency_data = env.var_[self.type].FREQUENCY_DATA

        self.was_converted = False

    def fill_variable(self):
        """Complete and fill variable with null values if the last and/or start year
        is not completed.

        This function check is the series (var D/I) are complete in the last year
        and start year, else Jaziku fill with null values for complete the year,
        but Jaziku required at least January and February for the last year and
        november and december for the start year, due the lags required these
        values.
        """

        if env.var_[self.type].is_daily():

            def below():
                first_year = self.date[0].year
                first_month = self.date[0].month
                first_day = self.date[0].day
                first_date = date(first_year, first_month, first_day)

                # if the variable have complete data in the first year
                if first_month == 1 and first_day == 1:
                    return

                start_date_required = date(first_year, 11, 1)

                # if the variable don't have the minimum data required for the first year,
                # this is, full data in november and december for the first year
                if first_date > start_date_required:
                    console.msg_error(_(
                        "Reading var {0} from file '{1}':\n"
                        "don't have the minimum data required (november and december)\n"
                        "for the first year ({2}) of the series.")
                                      .format(self.type, self.file_name, first_year))

                iter_date = first_date

                iter_date += relativedelta(days=-1)

                # fill variable for date and data for whole the first year
                while first_year == iter_date.year:
                    self.date.insert(0, iter_date)
                    self.data.insert(0, float('nan'))
                    iter_date += relativedelta(days=-1)

            def above():
                last_year = self.date[-1].year
                last_month = self.date[-1].month
                last_day = self.date[-1].day
                last_date = date(last_year, last_month, last_day)

                # if the variable have complete data in the last year
                if last_month == 12 and last_day == 31:
                    return

                end_date_required = date(last_year, 3, 1) + relativedelta(days=-1)  # last day of february

                # if the variable don't have the minimum data required for the last year,
                # this is, full data in january and february for the last year
                if last_date < end_date_required:
                    console.msg_error(_(
                        "Reading var {0} from file '{1}':\n"
                        "don't have the minimum data required (january and february)\n"
                        "for the last year ({2}) of the series.")
                                      .format(self.type, self.file_name, last_year))

                iter_date = last_date

                iter_date += relativedelta(days=1)

                # fill variable for date and data for whole the last year
                while last_year == iter_date.year:
                    self.date.append(iter_date)
                    self.data.append(float('nan'))
                    iter_date += relativedelta(days=1)

            # fill data below
            below()
            # fill data above
            above()

        if env.var_[self.type].is_monthly():

            def below():
                first_year = self.date[0].year
                first_month = self.date[0].month
                first_date = date(first_year, first_month, 1)

                # if the variable have complete data in the first year
                if first_month == 1:
                    return

                start_date_required = date(first_year, 11, 1)

                # if the variable don't have the minimum data required for the first year,
                # this is, full data in november and december for the first year
                if first_date > start_date_required:
                    console.msg_error(_(
                        "Reading var {0} from file '{1}':\n"
                        "don't have the minimum data required (november and december)\n"
                        "for the first year ({2}) of the series.")
                                      .format(self.type, self.file_name, first_year))

                iter_date = first_date

                iter_date += relativedelta(months=-1)

                # fill variable for date and data for whole the first year
                while first_year == iter_date.year:
                    self.date.insert(0, iter_date)
                    self.data.insert(0, float('nan'))
                    iter_date += relativedelta(months=-1)

            def above():
                last_year = self.date[-1].year
                last_month = self.date[-1].month
                last_date = date(last_year, last_month, 1)

                # if the variable have complete data in the last year
                if last_month == 12:
                    return

                end_date_required = date(last_year, 2, 1)

                # if the variable don't have the minimum data required for the last year,
                # this is, full data in january and february for the last year
                if last_date < end_date_required:
                    console.msg_error(_(
                        "Reading var {0} from file '{1}':\n"
                        "don't have the minimum data required (january and february)\n"
                        "for the last year ({2}) of the series.")
                                      .format(self.type, self.file_name, last_year))

                iter_date = last_date

                iter_date += relativedelta(months=1)

                # fill variable for date and data for whole the last year
                while last_year == iter_date.year:
                    self.date.append(iter_date)
                    self.data.append(float('nan'))
                    iter_date += relativedelta(months=1)

            # fill data below
            below()
            # fill data above
            above()

    def rollback_to_origin(self):
        """Rollback to origin data, date and frequency of this variable
        """
        self.data = deepcopy(self.origin_data)
        self.date = deepcopy(self.origin_date)
        env.var_[self.type].set_FREQUENCY_DATA(self.origin_frequency_data, check=False)

    def daily2Ndays(self, N_days=None):
        """Convert the data daily of the time series to 5 days, 10 days or
         15 days based on the mode calculation series.
        """

        range_analysis_interval = get_range_analysis_interval(N_days)

        data_Ndays = []
        date_Ndays = []
        for year in range(self.date[0].year, self.date[-1].year + 1):
            for month in range(1, 13):
                for day in range_analysis_interval:
                    values = get_values_in_range_analysis_interval(self, year, month, day, 0)
                    values = array.clean(values)
                    # calculate time series based on mode calculation series
                    if env.config_run.settings['mode_calculation_series_D'] == 'mean':
                        data_Ndays.append(array.mean(values))
                    if env.config_run.settings['mode_calculation_series_D'] == 'accumulate':
                        data_Ndays.append(sum(array.clean(values)))

                    date_Ndays.append(date(year, month, day))

        # save the original data/date
        self.ori_data = self.data
        self.ori_date = self.date

        # replace the original data/date with the data/date converted
        self.data = data_Ndays
        self.date = date_Ndays

    def daily2monthly(self):
        """Convert the data daily to monthly using the mean or accumulate
        defined in runfile in mode_calculation_series_X variable.

        :return by reference:
            VARIABLE.data (overwrite) (list)
            VARIABLE.date (overwrite) (list)
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
                # data
                value = calculate_specific_values_of_time_series(self, var_month_list)
                data_monthly.append(value)
                # date
                date_monthly.append(date(year, month, 1))

        self.data = data_monthly
        self.date = date_monthly

    def monthly2n_monthly(self, n_month):
        """Convert the data monthly to N-monthly using the mean or accumulate
        defined in runfile in mode_calculation_series_X variable.

        :return by reference:
            VARIABLE.data (overwrite) (list)
            VARIABLE.date (overwrite) (list)
        """

        data_n_monthly = []
        size_data = len(self.data)

        for idx_data, data in enumerate(self.data):
            n_month_list = []
            for n in range(n_month):
                if idx_data + n >= size_data:
                    n_month_list = [float('nan')]
                    continue
                n_month_list.append(self.data[idx_data + n])
            # calculate the N-month value
            value = calculate_specific_values_of_time_series(self, n_month_list)
            data_n_monthly.append(value)

        self.data = data_n_monthly

    def monthly2bimonthly(self):
        return self.monthly2n_monthly(2)

    def monthly2trimonthly(self):
        return self.monthly2n_monthly(3)

    def convert2(self, new_freq_data):
        """Convert the variable D or I to new frequency,
        this based too on the new_freq_data set in argument and
        the mode calculation series (mean or accumulate).

        Please set the new frequency:
        env.var_[D,I].set_FREQUENCY_DATA(new_freq_data, check=False)
        AFTER this function (not before).
        """

        if env.var_[self.type].FREQUENCY_DATA == new_freq_data:
            return

        if new_freq_data in ['5days', '10days', '15days']:
            if env.var_[self.type].is_daily():
                self.daily2Ndays(new_freq_data)
                self.was_converted = True
                return

        if new_freq_data == 'monthly':
            if env.var_[self.type].is_daily():
                self.daily2monthly()
                self.was_converted = True
                return

        if new_freq_data == 'bimonthly':
            if env.var_[self.type].is_daily():
                self.daily2monthly()
                self.monthly2bimonthly()
                self.was_converted = True
                return
            if env.var_[self.type].is_monthly():
                self.monthly2bimonthly()
                self.was_converted = True
                return

        if new_freq_data == 'trimonthly':
            if env.var_[self.type].is_daily():
                self.daily2monthly()
                self.monthly2trimonthly()
                self.was_converted = True
                return
            if env.var_[self.type].is_monthly():
                self.monthly2trimonthly()
                self.was_converted = True
                return

    def filling(self, mode='MeanMultiyear'):
        """Filling the variable of the time series using different methods from the
        original frequency (daily, N_days, N_monthly) of the series

        Methods of filling:
            MeanMultiyear: Use the mean multiyear inside the period
        """

        self.calculate_data_date_and_nulls_in_period()

        ### MeanMultiyear ###

        if mode == 'MeanMultiyear':

            if env.var_[self.type].is_n_daily():
                # calculate the mean N multi-year
                multiyear_values = {}
                for month in range(1, 13):
                    # range_analysis_interval = get_range_analysis_interval()
                    # for idx_day, day in enumerate(range_analysis_interval):
                    if env.var_[self.type].FREQUENCY_DATA in ['daily']:
                        n_days_range = range(1, monthrange(2000, month)[1] + 1)
                    if env.var_[self.type].FREQUENCY_DATA in ['5days', '10days', '15days']:
                        n_days_range = get_range_analysis_interval()

                    for n_day in n_days_range:
                        multiyear = []
                        for idx, value in enumerate(self.data_in_process_period):
                            if self.date_in_process_period[idx].month == month and self.date_in_process_period[
                                idx].day == n_day:
                                multiyear.append(value)
                        multiyear_values[(month, n_day)] = array.mean(multiyear)
                if env.var_[self.type].FREQUENCY_DATA in ['daily']:
                    # fix for leap year, put the average of the two mean-multiyear neighbors values (+-1 day) with its value if exists
                    multiyear_values[(2, 29)] = array.mean(
                        [multiyear_values[(2, 28)], multiyear_values[(2, 29)], multiyear_values[(3, 1)]])

                # filling the nan values with the respective multiyear value
                for idx, value in enumerate(self.data_in_process_period):
                    if env.globals_vars.is_valid_null(value):
                        idx_date_period = self.date_in_process_period[idx]
                        idx_date = self.date.index(idx_date_period)
                        self.data[idx_date] = multiyear_values[(idx_date_period.month, idx_date_period.day)]

            if env.var_[self.type].is_n_monthly():
                # calculate the mean N multi-year
                multiyear_values = {}
                for month in range(1, 13):
                    multiyear = []
                    for idx, value in enumerate(self.data_in_process_period):
                        if self.date_in_process_period[idx].month == month:
                            multiyear.append(value)
                    multiyear_values[month] = array.mean(multiyear)

                # filling the nan values with the respective multiyear value
                for idx, value in enumerate(self.data_in_process_period):
                    if env.globals_vars.is_valid_null(value):
                        idx_date_period = self.date_in_process_period[idx]
                        idx_date = self.date.index(idx_date_period)
                        self.data[idx_date] = multiyear_values[idx_date_period.month]

            self.calculate_data_date_and_nulls_in_period()

    def calculate_data_date_and_nulls_in_period(self, start_year=False, end_year=False):
        """Calculate the data without the null values inside
        the process period and too calculate the null values.

        :return by reference:
            VARIABLE.data_in_process_period (list)
            VARIABLE.data_filtered_in_process_period (list)
            VARIABLE.date_in_process_period (list)
            VARIABLE.nulls_in_process_period (int)
        (with specific period):
            VARIABLE.data_in_period (list)
            VARIABLE.data_filtered_in_period (list)
            VARIABLE.date_in_period (list)
            VARIABLE.nulls_in_period (int)
        """
        if start_year is False and end_year is False:
            is_process_period = True
        else:
            is_process_period = False

        if start_year is False:
            # set to start year of process period for this station
            start_year = env.globals_vars.PROCESS_PERIOD['start']
        if end_year is False:
            # set to end year of process period for this station
            end_year = env.globals_vars.PROCESS_PERIOD['end']

        start_date_var = min([d for d in self.date if d.year == start_year])
        end_date_var = max([d for d in self.date if d.year == end_year])

        data_in_period = self.data[self.date.index(start_date_var): \
            self.date.index(end_date_var) + 1]
        date_in_period = self.date[self.date.index(start_date_var): \
            self.date.index(end_date_var) + 1]
        nulls_in_period, \
        percentage_of_nulls_in_period = array.check_nulls(data_in_period)

        # delete all valid nulls and clean
        data_filtered_in_period = array.clean(data_in_period)

        if is_process_period:
            # return with data inside the process period
            self.data_in_process_period = data_in_period
            self.date_in_process_period = date_in_period
            self.nulls_in_process_period = nulls_in_period
            self.percentage_of_nulls_in_process_period = percentage_of_nulls_in_period
            self.data_filtered_in_process_period = data_filtered_in_period
        else:
            # return with data inside the specific period
            self.data_in_period = data_in_period
            self.date_in_period = date_in_period
            self.nulls_in_period = nulls_in_period
            self.percentage_of_nulls_in_period = percentage_of_nulls_in_period
            self.data_filtered_in_period = data_filtered_in_period

    def do_some_statistic_of_data(self):
        """Calculate several statistics based on data series,
        this is mainly used in data analysis module.

        :return by reference:
            [VARIABLE.] size_data, maximum, minimum,
            average, median, std_dev, skewness, variance,
            kurtosis and coef_variation.
        """

        # size valid data (without nulls)
        self.size_data = len(self.data_filtered_in_process_period)
        # maximum
        self.maximum = array.maximum(self.data_filtered_in_process_period)
        # minimum
        self.minimum = array.minimum(self.data_filtered_in_process_period)
        # average
        self.average = average(self.data_filtered_in_process_period)
        # median
        self.median = median(self.data_filtered_in_process_period)
        # std deviation
        self.std_dev = std(self.data_filtered_in_process_period, ddof=1)
        # skewness
        self.skewness = skew(self.data_filtered_in_process_period, bias=False)
        # variance
        self.variance = var(self.data_filtered_in_process_period)
        # kurtosis
        self.kurtosis = kurtosis(self.data_filtered_in_process_period, bias=False)
        # c-variation
        self.coef_variation = variation(self.data_filtered_in_process_period)
