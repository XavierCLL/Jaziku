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

from numpy import matrix
from math import isnan

from jaziku import env
from jaziku.core.analysis_interval import get_range_analysis_interval
from jaziku.utils import output
from jaziku.utils import console
from jaziku.modules.climate import time_series
from jaziku.modules.climate.thresholds import get_thresholds


def get_label_of_var_I_category(value, station):
    """Calculate, for a particular 'value', the var I category label based on 'categories_labels_var_I'
    and thresholds of var I, evaluate where is the 'value' inside the thresholds and return
    the correspondent label for this position.

    For some variables, for set the category of phenomenon for the normal case the thresholds
    are exclude (< >):
    for ('ONI1', 'ONI2', 'W850w', 'SST4', 'SST12'):
        the value is normal when { threshold below* < value < threshold above* }
    else:
        the value is normal when { threshold below* <= value <= threshold above* }

    :param value: values for calculate the label
    :type value: float
    :param station: station of value
    :type station: Station

    :return: label
    :rtype: str
    """

    # get thresholds of var I in the period of outlier
    thresholds_var_I = get_thresholds(station, station.var_I)

    # categorize the value of var I and get the label_of_var_I_category based in the label phenomenon

    if env.var_I.is_normal_inclusive():
        # default case

        if env.config_run.settings['class_category_analysis'] == 3:
            if value < thresholds_var_I['below']:
                label_of_var_I_category = env.config_run.settings['categories_labels_var_I']['below']
            elif value > thresholds_var_I['above']:
                label_of_var_I_category = env.config_run.settings['categories_labels_var_I']['above']
            else:
                label_of_var_I_category = env.config_run.settings['categories_labels_var_I']['normal']

        if env.config_run.settings['class_category_analysis'] == 7:
            if value < thresholds_var_I['below3']:
                label_of_var_I_category = env.config_run.settings['categories_labels_var_I']['below3']
            elif thresholds_var_I['below3'] <= value < thresholds_var_I['below2']:
                label_of_var_I_category = env.config_run.settings['categories_labels_var_I']['below2']
            elif thresholds_var_I['below2'] <= value < thresholds_var_I['below1']:
                label_of_var_I_category = env.config_run.settings['categories_labels_var_I']['below1']
            elif thresholds_var_I['below1'] <= value <= thresholds_var_I['above1']:
                label_of_var_I_category = env.config_run.settings['categories_labels_var_I']['normal']
            elif thresholds_var_I['above1'] < value <= thresholds_var_I['above2']:
                label_of_var_I_category = env.config_run.settings['categories_labels_var_I']['above1']
            elif thresholds_var_I['above2'] < value <= thresholds_var_I['above3']:
                label_of_var_I_category = env.config_run.settings['categories_labels_var_I']['above2']
            elif value > thresholds_var_I['above3']:
                label_of_var_I_category = env.config_run.settings['categories_labels_var_I']['above3']
    else:
        # SPECIAL CASE 2: for some variables, for set the category of phenomenon for the normal case the thresholds are exclude (< >)
        # please see env/var_I file

        if env.config_run.settings['class_category_analysis'] == 3:
            if value <= thresholds_var_I['below']:
                label_of_var_I_category = env.config_run.settings['categories_labels_var_I']['below']
            elif value >= thresholds_var_I['above']:
                label_of_var_I_category = env.config_run.settings['categories_labels_var_I']['above']
            else:
                label_of_var_I_category = env.config_run.settings['categories_labels_var_I']['normal']

        if env.config_run.settings['class_category_analysis'] == 7:
            if value <= thresholds_var_I['below3']:
                label_of_var_I_category = env.config_run.settings['categories_labels_var_I']['below3']
            elif thresholds_var_I['below3'] < value <= thresholds_var_I['below2']:
                label_of_var_I_category = env.config_run.settings['categories_labels_var_I']['below2']
            elif thresholds_var_I['below2'] < value <= thresholds_var_I['below1']:
                label_of_var_I_category = env.config_run.settings['categories_labels_var_I']['below1']
            elif thresholds_var_I['below1'] < value < thresholds_var_I['above1']:
                label_of_var_I_category = env.config_run.settings['categories_labels_var_I']['normal']
            elif thresholds_var_I['above1'] <= value < thresholds_var_I['above2']:
                label_of_var_I_category = env.config_run.settings['categories_labels_var_I']['above1']
            elif thresholds_var_I['above2'] <= value < thresholds_var_I['above3']:
                label_of_var_I_category = env.config_run.settings['categories_labels_var_I']['above2']
            elif value >= thresholds_var_I['above3']:
                label_of_var_I_category = env.config_run.settings['categories_labels_var_I']['above3']

    return label_of_var_I_category


def get_specific_contingency_table(station, lag, n_month, start_day=None):
    """Calculate and return the contingency table in absolute values,
    values in percent, values to print and thresholds by below and
    above of dependent and independent variable for specific lag,
    N-month or month/day within the whole period to process.

    :param station: Stations instance
    :type station: Station
    :param lag: lag for calculate the contingency table
    :type lag: int
    :param n_month: month for calculate the contingency table
    :type n_month: int
    :param day: day for calculate the contingency table when is
        data is daily
    :type start_day: int

    :return: specific_contingency_table dict:
        {'in_values', 'in_percentage', 'in_percentage_formatted',
        'thresholds_var_D', 'thresholds_var_I'}
    :rtype: dict
    """

    if start_day is None:
        # get all values of var D and var I based on this lag and month
        station.var_D.specific_values = time_series.get_specific_values(station, 'var_D', lag, n_month)
        station.var_I.specific_values = time_series.get_specific_values(station, 'var_I', lag, n_month)

    if start_day is not None:
        # get all values of var D and var I based on this lag and month
        station.var_D.specific_values = time_series.get_specific_values(station, 'var_D', lag, n_month, start_day)
        station.var_I.specific_values = time_series.get_specific_values(station, 'var_I', lag, n_month, start_day)

    # calculate thresholds as defined by the user in station file for var D
    thresholds_var_D = get_thresholds(station, station.var_D)

    # calculate thresholds as defined by the user in station file for var I
    thresholds_var_I = get_thresholds(station, station.var_I)

    # adjust values when two thresholds are equal and if the value to evaluate is the same value too,
    # put the value in the middle of category in contingency table
    if env.config_run.settings['class_category_analysis'] == 3:
        thresholds_idx = ['below', 'above']
    if env.config_run.settings['class_category_analysis'] == 7:
        thresholds_idx = ['below3', 'below2', 'below1', 'above1', 'above2', 'above3']
    epsilon = 1e-10
    for thres_idx in range(len(thresholds_idx) - 1):
        if thresholds_var_D[thresholds_idx[thres_idx]] == thresholds_var_D[thresholds_idx[thres_idx + 1]]:
            thresholds_var_D[thresholds_idx[thres_idx]] -= epsilon
            thresholds_var_D[thresholds_idx[thres_idx + 1]] += epsilon
        if thresholds_var_I[thresholds_idx[thres_idx]] == thresholds_var_I[thresholds_idx[thres_idx + 1]]:
            thresholds_var_I[thresholds_idx[thres_idx]] -= epsilon
            thresholds_var_I[thresholds_idx[thres_idx + 1]] += epsilon

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    ## Calculating contingency table with absolute values

    if env.config_run.settings['class_category_analysis'] == 3:
        # matrix 3x3
        contingency_table = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    if env.config_run.settings['class_category_analysis'] == 7:
        # matrix 7x7
        contingency_table = [[0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0]]

    if env.config_run.settings['class_category_analysis'] == 3:
        if env.var_D.is_normal_inclusive():
            def __matrix_row_var_D(column_var_I):
                if station.var_D.specific_values[index] < thresholds_var_D['below']:
                    contingency_table[column_var_I][0] += 1
                if thresholds_var_D['below'] <= station.var_D.specific_values[index] <= thresholds_var_D['above']:
                    contingency_table[column_var_I][1] += 1
                if station.var_D.specific_values[index] > thresholds_var_D['above']:
                    contingency_table[column_var_I][2] += 1
        else:
            def __matrix_row_var_D(column_var_I):
                if station.var_D.specific_values[index] <= thresholds_var_D['below']:
                    contingency_table[column_var_I][0] += 1
                if thresholds_var_D['below'] < station.var_D.specific_values[index] < thresholds_var_D['above']:
                    contingency_table[column_var_I][1] += 1
                if station.var_D.specific_values[index] >= thresholds_var_D['above']:
                    contingency_table[column_var_I][2] += 1

    if env.config_run.settings['class_category_analysis'] == 7:
        if env.var_D.is_normal_inclusive():
            def __matrix_row_var_D(column_var_I):
                if station.var_D.specific_values[index] < thresholds_var_D['below3']:
                    contingency_table[column_var_I][0] += 1
                if thresholds_var_D['below3'] <= station.var_D.specific_values[index] < thresholds_var_D['below2']:
                    contingency_table[column_var_I][1] += 1
                if thresholds_var_D['below2'] <= station.var_D.specific_values[index] < thresholds_var_D['below1']:
                    contingency_table[column_var_I][2] += 1
                if thresholds_var_D['below1'] <= station.var_D.specific_values[index] <= thresholds_var_D['above1']:
                    contingency_table[column_var_I][3] += 1
                if thresholds_var_D['above1'] < station.var_D.specific_values[index] <= thresholds_var_D['above2']:
                    contingency_table[column_var_I][4] += 1
                if thresholds_var_D['above2'] < station.var_D.specific_values[index] <= thresholds_var_D['above3']:
                    contingency_table[column_var_I][5] += 1
                if station.var_D.specific_values[index] > thresholds_var_D['above3']:
                    contingency_table[column_var_I][6] += 1
        else:
            def __matrix_row_var_D(column_var_I):
                if station.var_D.specific_values[index] <= thresholds_var_D['below3']:
                    contingency_table[column_var_I][0] += 1
                if thresholds_var_D['below3'] < station.var_D.specific_values[index] <= thresholds_var_D['below2']:
                    contingency_table[column_var_I][1] += 1
                if thresholds_var_D['below2'] < station.var_D.specific_values[index] <= thresholds_var_D['below1']:
                    contingency_table[column_var_I][2] += 1
                if thresholds_var_D['below1'] < station.var_D.specific_values[index] < thresholds_var_D['above1']:
                    contingency_table[column_var_I][3] += 1
                if thresholds_var_D['above1'] <= station.var_D.specific_values[index] < thresholds_var_D['above2']:
                    contingency_table[column_var_I][4] += 1
                if thresholds_var_D['above2'] <= station.var_D.specific_values[index] < thresholds_var_D['above3']:
                    contingency_table[column_var_I][5] += 1
                if station.var_D.specific_values[index] >= thresholds_var_D['above3']:
                    contingency_table[column_var_I][6] += 1

    if env.var_I.is_normal_inclusive():
        # default case

        if env.config_run.settings['class_category_analysis'] == 3:
            for index, var_I in enumerate(station.var_I.specific_values):
                if var_I < thresholds_var_I['below']:
                    __matrix_row_var_D(0)
                if thresholds_var_I['below'] <= var_I <= thresholds_var_I['above']:
                    __matrix_row_var_D(1)
                if var_I > thresholds_var_I['above']:
                    __matrix_row_var_D(2)

        if env.config_run.settings['class_category_analysis'] == 7:
            for index, var_I in enumerate(station.var_I.specific_values):
                if var_I < thresholds_var_I['below3']:
                    __matrix_row_var_D(0)
                if thresholds_var_I['below3'] <= var_I < thresholds_var_I['below2']:
                    __matrix_row_var_D(1)
                if thresholds_var_I['below2'] <= var_I < thresholds_var_I['below1']:
                    __matrix_row_var_D(2)
                if thresholds_var_I['below1'] <= var_I <= thresholds_var_I['above1']:
                    __matrix_row_var_D(3)
                if thresholds_var_I['above1'] < var_I <= thresholds_var_I['above2']:
                    __matrix_row_var_D(4)
                if thresholds_var_I['above2'] < var_I <= thresholds_var_I['above3']:
                    __matrix_row_var_D(5)
                if var_I > thresholds_var_I['above3']:
                    __matrix_row_var_D(6)

    else:
        # SPECIAL CASE 2: for some variables, for set the category of phenomenon for the normal case the thresholds are exclude (< >)
        # please see env/var_I file

        if env.config_run.settings['class_category_analysis'] == 3:
            for index, var_I in enumerate(station.var_I.specific_values):
                if var_I <= thresholds_var_I['below']:
                    __matrix_row_var_D(0)
                if thresholds_var_I['below'] < var_I < thresholds_var_I['above']:
                    __matrix_row_var_D(1)
                if var_I >= thresholds_var_I['above']:
                    __matrix_row_var_D(2)

        if env.config_run.settings['class_category_analysis'] == 7:
            for index, var_I in enumerate(station.var_I.specific_values):
                if var_I <= thresholds_var_I['below3']:
                    __matrix_row_var_D(0)
                if thresholds_var_I['below3'] < var_I <= thresholds_var_I['below2']:
                    __matrix_row_var_D(1)
                if thresholds_var_I['below2'] < var_I <= thresholds_var_I['below1']:
                    __matrix_row_var_D(2)
                if thresholds_var_I['below1'] < var_I < thresholds_var_I['above1']:
                    __matrix_row_var_D(3)
                if thresholds_var_I['above1'] <= var_I < thresholds_var_I['above2']:
                    __matrix_row_var_D(4)
                if thresholds_var_I['above2'] <= var_I < thresholds_var_I['above3']:
                    __matrix_row_var_D(5)
                if var_I >= thresholds_var_I['above3']:
                    __matrix_row_var_D(6)

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    ## Calculating contingency table with values in percentage

    # contingency_table[varI][varD]
    # sum of column of all values in each category of var I
    sum_per_column_CT = matrix(contingency_table).sum(axis=1)
    # converting in list
    sum_per_column_CT = [float(x) for x in sum_per_column_CT]

    if env.config_run.settings['class_category_analysis'] == 7:
        # for 7 categories the sum of var I is by categories [below*=sb+mb+wb, normal=n, above*=wa+ma+sa]
        sum_per_column_CT = [sum(sum_per_column_CT[0:3])] * 3 + \
                            [sum_per_column_CT[3]] + \
                            [sum(sum_per_column_CT[4::])] * 3

    # calculate the percentage of contingency table evaluating each value with the sum value of its respective category
    with console.redirectStdStreams():
        contingency_table_in_percentage \
            = [(column / sum_per_column_CT[i] * 100).tolist()[0] for i, column in enumerate(matrix(contingency_table))]

    # fix table when the value is nan (replace with zero) it is due to while it calculate the contingency
    # table and there are not values with independent variable for one category (thresholds problem)
    # this cause division by zero and nan values
    contingency_table_in_percentage = [[i if not isnan(i) else 0 for i in c] for c in contingency_table_in_percentage]

    # special case when the forecast type is 3x7, clear columns of the var I with zeros of
    # the contingency table in absolute values for not selected categories defined in runfile
    # for forecast type 3x7
    if env.globals_vars.forecast_contingency_table['type'] == '3x7':
        # init list 7x7 with zeros
        contingency_table_3x7 = [[0] * 7] * 7
        tags = ['below3', 'below2', 'below1', 'normal', 'above1', 'above2', 'above3']
        for idx_var_I in range(7):
            # only set the real values for columns of var I for selected categories
            # in below, and above selected and normal
            if tags.index(env.globals_vars.probability_forecast_values[lag]['below']) == idx_var_I or \
                            idx_var_I == 3 or \
                            tags.index(env.globals_vars.probability_forecast_values[lag]['above']) == idx_var_I:
                contingency_table_3x7[idx_var_I] = contingency_table[idx_var_I]

        sum_per_column_CT_3x7 = matrix(contingency_table_3x7).sum(axis=1)
        sum_per_column_CT_3x7 = [float(x) for x in sum_per_column_CT_3x7]
        with console.redirectStdStreams():
            contingency_table_in_percentage_3x7 \
                = [(column / sum_per_column_CT_3x7[i] * 100).tolist()[0] for i, column in
                   enumerate(matrix(contingency_table_3x7))]

        # fix table when the value is nan (replace with zero) it is due to while it calculate the contingency
        # table and there are not values with independent variable for one category (thresholds problem)
        # this cause division by zero and nan values
        contingency_table_in_percentage_3x7 = [[i if not isnan(i) else 0 for i in c] for c in
                                               contingency_table_in_percentage_3x7]

    # -------------------------------------------------------------------------
    # threshold_problem is global variable for detect problem with
    # threshold of independent variable, if a problem is detected
    # show message and print "nan" (this mean null value for
    # division by zero) in contingency tabla percent in result
    # table, jaziku show warning message and continue the process.

    # convert 7 categories in 3 blocks: BELOW, NORMAL and ABOVE
    if env.config_run.settings['class_category_analysis'] == 7:
        sum_per_column_CT = [sum_per_column_CT[0], sum_per_column_CT[3], sum_per_column_CT[6]]

    # iterate and check for each 3 blocks: BELOW, NORMAL and ABOVE
    for index, label in enumerate([_('below'), _('normal'), _('above')]):
        if float(sum_per_column_CT[index]) == 0 and not station.threshold_problem[index]:
            console.msg(
                _("\n > WARNING: The thresholds defined for var I\n"
                  "   are not suitable in some time series for \n"
                  "   compound analysis of '{0}' with relation to\n"
                  "   '{1}' inside the block category '{2}'.\n"
                  "   Is recommended review the thresholds\n"
                  "   of two variables, or the series data .......")
                    .format(env.var_D.TYPE_SERIES, env.var_I.TYPE_SERIES, label.upper()), color='yellow', newline=False)
            station.threshold_problem[index] = True

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # Calculating contingency table percent with values formatted for outputs

    contingency_table_in_percentage_formatted = []
    if env.config_run.settings['class_category_analysis'] == 3:
        for row in contingency_table_in_percentage:
            contingency_table_in_percentage_formatted.append(
                [output.number(row[0], decimals=1),
                 output.number(row[1], decimals=1),
                 output.number(row[2], decimals=1)])
    if env.config_run.settings['class_category_analysis'] == 7:
        for row in contingency_table_in_percentage:
            contingency_table_in_percentage_formatted.append(
                [output.number(row[0], decimals=1),
                 output.number(row[1], decimals=1),
                 output.number(row[2], decimals=1),
                 output.number(row[3], decimals=1),
                 output.number(row[4], decimals=1),
                 output.number(row[5], decimals=1),
                 output.number(row[6], decimals=1)])

    # -------------------------------------------------------------------------
    # save and return

    specific_contingency_table = {'in_values': contingency_table,
                                  'in_percentage': contingency_table_in_percentage,
                                  'in_percentage_formatted': contingency_table_in_percentage_formatted,
                                  'thresholds_var_D': thresholds_var_D,
                                  'thresholds_var_I': thresholds_var_I}

    # added the special contingency table in percentage for 3x7
    if env.globals_vars.forecast_contingency_table['type'] == '3x7':
        specific_contingency_table['in_percentage_3x7'] = contingency_table_in_percentage_3x7

    return specific_contingency_table


def get_contingency_tables(station):
    """get all contingencies tables for all N-monthly or
    all month/day for each lag.

    :param station: station for get all contingencies tables
    :type station: Station

    Return by reference:

    :ivar STATION.contingency_tables: get and set  to station
        all contingencies tables within a list
        [lag][n_month][day].
    """
    # init threshold problem for this station
    # for 3 and 7 categories there are 3 blocks: BELOW, NORMAL and ABOVE
    station.threshold_problem = [False] * 3

    # [lag][month][phenomenon][data(0,1,2)]
    # [lag][month][day][phenomenon][data(0,1,2)]
    contingency_tables = {}
    # defined if is first iteration
    station.first_iter = True
    for lag in env.config_run.settings['lags']:

        tmp_month_list = []
        # all months in year 1->12
        for n_month in range(1, 13):
            if env.var_D.is_n_monthly():

                specific_contingency_table = get_specific_contingency_table(station, lag, n_month)

                tmp_month_list.append(specific_contingency_table)

                if station.first_iter:
                    station.first_iter = False

            if env.var_D.is_n_daily():
                tmp_day_list = []
                for day in get_range_analysis_interval():

                    specific_contingency_table = get_specific_contingency_table(station, lag,
                                                                                n_month, day)
                    tmp_day_list.append(specific_contingency_table)

                    if station.first_iter:
                        station.first_iter = False

                tmp_month_list.append(tmp_day_list)

        contingency_tables[lag] = tmp_month_list

    station.contingency_tables = contingency_tables
