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

from numpy import matrix

from jaziku import env
from jaziku.core.analysis_interval import get_range_analysis_interval
from jaziku.utils import format_out
from jaziku.utils import console
from jaziku.modules.climate import lags
from jaziku.modules.climate.thresholds import get_thresholds


def get_label_of_var_I_category(value, station):
    """Calculate, for a particular 'value', the var I category label based on 'var_I_category_labels'
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
                label_of_var_I_category = env.config_run.settings['var_I_category_labels']['below']
            elif value > thresholds_var_I['above']:
                label_of_var_I_category = env.config_run.settings['var_I_category_labels']['above']
            else:
                label_of_var_I_category = env.config_run.settings['var_I_category_labels']['normal']

        if env.config_run.settings['class_category_analysis'] == 7:
            if value < thresholds_var_I['below3']:
                label_of_var_I_category = env.config_run.settings['var_I_category_labels']['below3']
            elif thresholds_var_I['below3'] <= value < thresholds_var_I['below2']:
                label_of_var_I_category = env.config_run.settings['var_I_category_labels']['below2']
            elif thresholds_var_I['below2'] <= value < thresholds_var_I['below1']:
                label_of_var_I_category = env.config_run.settings['var_I_category_labels']['below1']
            elif thresholds_var_I['below1'] <= value <= thresholds_var_I['above1']:
                label_of_var_I_category = env.config_run.settings['var_I_category_labels']['normal']
            elif thresholds_var_I['above1'] < value <= thresholds_var_I['above2']:
                label_of_var_I_category = env.config_run.settings['var_I_category_labels']['above1']
            elif thresholds_var_I['above2'] < value <= thresholds_var_I['above3']:
                label_of_var_I_category = env.config_run.settings['var_I_category_labels']['above2']
            elif value > thresholds_var_I['above3']:
                label_of_var_I_category = env.config_run.settings['var_I_category_labels']['above3']
    else:
        # SPECIAL CASE 2: for some variables, for set the category of phenomenon for the normal case the thresholds are exclude (< >)
        # please see env/var_I file

        if env.config_run.settings['class_category_analysis'] == 3:
            if value <= thresholds_var_I['below']:
                label_of_var_I_category = env.config_run.settings['var_I_category_labels']['below']
            elif value >= thresholds_var_I['above']:
                label_of_var_I_category = env.config_run.settings['var_I_category_labels']['above']
            else:
                label_of_var_I_category = env.config_run.settings['var_I_category_labels']['normal']

        if env.config_run.settings['class_category_analysis'] == 7:
            if value <= thresholds_var_I['below3']:
                label_of_var_I_category = env.config_run.settings['var_I_category_labels']['below3']
            elif thresholds_var_I['below3'] < value <= thresholds_var_I['below2']:
                label_of_var_I_category = env.config_run.settings['var_I_category_labels']['below2']
            elif thresholds_var_I['below2'] < value <= thresholds_var_I['below1']:
                label_of_var_I_category = env.config_run.settings['var_I_category_labels']['below1']
            elif thresholds_var_I['below1'] < value < thresholds_var_I['above1']:
                label_of_var_I_category = env.config_run.settings['var_I_category_labels']['normal']
            elif thresholds_var_I['above1'] <= value < thresholds_var_I['above2']:
                label_of_var_I_category = env.config_run.settings['var_I_category_labels']['above1']
            elif thresholds_var_I['above2'] <= value < thresholds_var_I['above3']:
                label_of_var_I_category = env.config_run.settings['var_I_category_labels']['above2']
            elif value >= thresholds_var_I['above3']:
                label_of_var_I_category = env.config_run.settings['var_I_category_labels']['above3']

    return label_of_var_I_category


def get_specific_contingency_table(station, lag, month, day=None):
    """Calculate and return the contingency table in absolute values,
    values in percent, values to print and thresholds by below and
    above of dependent and independent variable for specific lag,
    trimester(month) or month/day within the whole period to process.

    If the `state of data` is 1 or 3, the month is the first
    month of trimester.

    If the `state of data` is 2 or 4, the month/day is the first
    day of the fraction of `analysis interval`.

    :param station: Stations instance
    :type station: Station
    :param lag: lag for calculate the contingency table
    :type lag: int
    :param month: month for calculate the contingency table
    :type month: int
    :param day: day for calculate the contingency table when is
        data is daily
    :type day: int

    :return: specific_contingency_table dict:
        {'in_values', 'in_percentage', 'in_percentage_formatted',
        'thresholds_var_D', 'thresholds_var_I'}
    :rtype: dict
    """

    if day is None:
        # get all values of var D and var I based on this lag and month
        station.var_D.specific_values = lags.get_specific_values(station, 'var_D', lag, month)
        station.var_I.specific_values = lags.get_specific_values(station, 'var_I', lag, month)

    if day is not None:
        # get all values of var D and var I based on this lag and month
        station.var_D.specific_values = lags.get_specific_values(station, 'var_D', lag, month, day)
        station.var_I.specific_values = lags.get_specific_values(station, 'var_I', lag, month, day)

    # calculate thresholds as defined by the user in station file for var D
    thresholds_var_D = get_thresholds(station, station.var_D)

    # calculate thresholds as defined by the user in station file for var I
    thresholds_var_I = get_thresholds(station, station.var_I)

    # adjust values when two thresholds are equal and if the value to evaluate is the same value too,
    # put the value in the middle of category in contingency table
    if env.config_run.settings['class_category_analysis'] == 3:
        thresholds_idx = ['below', 'above']
    if env.config_run.settings['class_category_analysis'] == 7:
        thresholds_idx = ['below3', 'below2','below1', 'above1', 'above2', 'above3']
    epsilon = 1e-10
    for thres_idx in range(len(thresholds_idx)-1):
        if thresholds_var_D[thresholds_idx[thres_idx]] == thresholds_var_D[thresholds_idx[thres_idx+1]]:
            thresholds_var_D[thresholds_idx[thres_idx]] -= epsilon
            thresholds_var_D[thresholds_idx[thres_idx+1]] += epsilon
        if thresholds_var_I[thresholds_idx[thres_idx]] == thresholds_var_I[thresholds_idx[thres_idx+1]]:
            thresholds_var_I[thresholds_idx[thres_idx]] -= epsilon
            thresholds_var_I[thresholds_idx[thres_idx+1]] += epsilon

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
    # check if all analysis interval have valid values (not NaN values):
    # the sum of years in process period should be equal to all values in contingency table
    # or is the same as the number of values in any series time
    years_in_process_period = station.process_period['end'] - station.process_period['start'] + 1
    if sum(sum_per_column_CT) != years_in_process_period:
        if day:
            console.msg(_(" > WARNING: One of the analysis interval have all NaN values\n"
                          "   for the lag {0}, month {1} and day {2}.").format(lag,month,day), color="yellow")
        else:
            console.msg(_(" > WARNING: One of the analysis interval have all NaN values\n"
                      "   for the lag {0} and month {1} .").format(lag,month), color="yellow")
    # multiply each column (varI) of the contingency_table (CT) for its respective value of sum_per_column_CT (threshold size (TS))
    table_CTxTS = [(column*sum_per_column_CT[i]).tolist()[0] for i,column in enumerate(matrix(contingency_table))]
    # sum per column of the before table CTxTS and convert to python 2d list
    sum_per_column_table_CTxTS =  [x[0] for x in matrix(table_CTxTS).sum(axis=1).tolist()]

    if env.config_run.settings['class_category_analysis'] == 7:
        # for 7 categories the sum of var I is by categories [below*=sb+mb+wb, normal=n, above*=wa+ma+sa]
        sum_per_column_table_CTxTS = [sum(sum_per_column_table_CTxTS[0:3])]*3 + \
                                     [sum_per_column_table_CTxTS[3]] + \
                                     [sum(sum_per_column_table_CTxTS[4::])]*3

    contingency_table_in_percentage = [(column/sum_per_column_table_CTxTS[i]*100).tolist()[0] for i,column in enumerate(matrix(table_CTxTS))]

    # -------------------------------------------------------------------------
    # threshold_problem is global variable for detect problem with
    # threshold of independent variable, if a problem is detected
    # show message and print "nan" (this mean null value for
    # division by zero) in contingency tabla percent in result
    # table, jaziku continue but the graphics will not be created
    # because "nan"  character could not be calculate.

    # todo 0.6
    # if env.config_run.settings['class_category_analysis'] == 3:
    #     labels = ['below','normal','above']
    # if env.config_run.settings['class_category_analysis'] == 7:
    #     labels = ['below3','below2','below1','normal','above1','above2','above3']
    #
    # for index, label in enumerate(labels):
    #     if float(sum_per_column_table_CTxTS[index]) == 0 and not env.globals_vars.threshold_problem[index]:
    #         console.msg(
    #             _(u"\n\n > WARNING: The thresholds defined for var I\n"
    #               u"   are not suitable for compound analysis of\n"
    #               u"   variable '{0}' with relation to '{1}' inside\n"
    #               u"   category '{2}'. Therefore, the graphics\n"
    #               u"   will not be created.")
    #             .format(env.var_D.TYPE_SERIES, env.var_I.TYPE_SERIES, env.config_run.settings['var_I_category_labels'][label]), color='yellow')
    #         env.globals_vars.threshold_problem[index] = True


    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # Calculating contingency table percent with values formatted for outputs

    contingency_table_in_percentage_formatted = []
    if env.config_run.settings['class_category_analysis'] == 3:
        for row in contingency_table_in_percentage:
            contingency_table_in_percentage_formatted.append(
                [format_out.number(row[0], 1),
                format_out.number(row[1], 1),
                format_out.number(row[2], 1)])
    if env.config_run.settings['class_category_analysis'] == 7:
        for row in contingency_table_in_percentage:
            contingency_table_in_percentage_formatted.append(
                [format_out.number(row[0], 1),
                format_out.number(row[1], 1),
                format_out.number(row[2], 1),
                format_out.number(row[3], 1),
                format_out.number(row[4], 1),
                format_out.number(row[5], 1),
                format_out.number(row[6], 1)])

    # -------------------------------------------------------------------------
    # save and return

    specific_contingency_table = {'in_values':contingency_table,
                                  'in_percentage':contingency_table_in_percentage,
                                  'in_percentage_formatted':contingency_table_in_percentage_formatted,
                                  'thresholds_var_D':thresholds_var_D,
                                  'thresholds_var_I':thresholds_var_I}

    return specific_contingency_table


def get_contingency_tables(station):
    """get all contingencies tables for all trimester or
    all month/day for each lag.

    :param station: station for get all contingencies tables
    :type station: Station

    Return by reference:

    :ivar STATION.contingency_tables: get and set  to station
        all contingencies tables within a list
        [lag][month/trimester][day].
    """

    # [lag][month][phenomenon][data(0,1,2)]
    # [lag][month][day][phenomenon][data(0,1,2)]
    contingency_tables = {}
    # defined if is first iteration
    station.first_iter = True
    for lag in env.config_run.settings['lags']:

        tmp_month_list = []
        # all months in year 1->12
        for month in range(1, 13):
            if env.globals_vars.STATE_OF_DATA in [1, 3]:

                specific_contingency_table = get_specific_contingency_table(station, lag, month)

                tmp_month_list.append(specific_contingency_table)

                if station.first_iter:
                    station.first_iter = False

            if env.globals_vars.STATE_OF_DATA in [2, 4]:
                tmp_day_list = []
                for day in get_range_analysis_interval():

                    specific_contingency_table = get_specific_contingency_table(station, lag,
                        month, day)
                    tmp_day_list.append(specific_contingency_table)

                    if station.first_iter:
                        station.first_iter = False

                tmp_month_list.append(tmp_day_list)

        contingency_tables[lag] = tmp_month_list

    station.contingency_tables = contingency_tables
