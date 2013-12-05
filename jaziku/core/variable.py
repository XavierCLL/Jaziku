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
from datetime import date
from dateutil.relativedelta import relativedelta
from numpy import median, average, var, std
from scipy.stats.stats import variation, skew, kurtosis

from jaziku import env
from jaziku.core.input import vars
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
        plus attributes return of methods:
            data_and_null_in_process_period()
            do_some_statistic_of_data()
    """

    def __init__(self, type, station):
        if type in ['D','I']:
            self.type = type
        else:
            raise

        self.station = station

    def set_file(self, file):

        if self.type == 'D':
            self.file_name = os.path.basename(file)
            # if path to file is relative convert to absolute
            if not os.path.isabs(file):
                self.file_path = os.path.abspath(os.path.join(os.path.dirname(env.globals_vars.ARGS.runfile),file))
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
                    self.file_path = os.path.abspath(os.path.join(os.path.dirname(env.globals_vars.ARGS.runfile),file))
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

                end_date_required = date(last_year, 3, 1) + relativedelta(days=-1) # last day of february

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
                if idx_data+n >= size_data:
                    n_month_list = [float('nan')]
                    continue
                n_month_list.append(self.data[idx_data+n])
            # calculate the N-month value
            value = calculate_specific_values_of_time_series(self, n_month_list)
            data_n_monthly.append(value)

        self.data = data_n_monthly

    def monthly2bimonthly(self):
        return self.monthly2n_monthly(2)

    def monthly2trimonthly(self):
        return self.monthly2n_monthly(3)

    def convert2(self, new_freq_data):

        if new_freq_data == 'monthly':
            if env.var_[self.type].is_daily():
                self.daily2monthly()

        if new_freq_data == 'bimonthly':
            if env.var_[self.type].is_daily():
                self.daily2monthly()
                self.monthly2bimonthly()
            if env.var_[self.type].is_monthly():
                self.monthly2bimonthly()

        if new_freq_data == 'trimonthly':
            if env.var_[self.type].is_daily():
                self.daily2monthly()
                self.monthly2trimonthly()
            if env.var_[self.type].is_monthly():
                self.monthly2trimonthly()

    def data_and_null_in_process_period(self):
        """Calculate the data without the null values inside
        the process period and too calculate the null values.

        :return by reference:
            VARIABLE.data_in_process_period (list)
            VARIABLE.data_filtered_in_process_period (list)
            VARIABLE.date_in_process_period (list)
            VARIABLE.nulls_in_process_period (int)
        """
        start_date_var = date(self.station.process_period['start'], 1, 1)
        if (self.type == 'D' and env.var_D.is_daily()) or (self.type == 'I' and env.var_I.is_daily()):
            end_date_var = date(self.station.process_period['end'], 12, 31)
        else:
            end_date_var = date(self.station.process_period['end'], 12, 1)

        # data inside the process period
        self.data_in_process_period = self.data[self.date.index(start_date_var):\
                                                self.date.index(end_date_var) + 1]
        # date inside the process period
        self.date_in_process_period = self.date[self.date.index(start_date_var):\
                                      self.date.index(end_date_var) + 1]
        # nulls inside the process period
        self.nulls_in_process_period, \
        self.percentage_of_nulls_in_process_period = array.check_nulls(self.data_in_process_period)

        # delete all valid nulls and clean
        self.data_filtered_in_process_period = array.clean(self.data_in_process_period)

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



