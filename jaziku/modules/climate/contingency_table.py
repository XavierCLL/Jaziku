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

import sys
import os
from numpy import matrix

from jaziku.env import globals_vars, config_run
from jaziku.utils import format_out
from jaziku.utils import console
from jaziku.modules.climate import lags
from jaziku.modules.climate.thresholds import get_thresholds_var_D, get_thresholds_var_I


def get_category_of_phenomenon(value, station):
    """
    Calculate the category of phenomenon for independent variable based on label phenomenon,
    evaluate where is the 'value' in the thresholds (by default or defined by user), this is
    below, normal or above and return the label for this position.

    For some variables for set the category of phenomenon the thresholds are inclusive,
    for ('ONI1', 'ONI2', 'W850w', 'SST4', 'SST12', 'ASST3', 'ASST34', 'ASST4', 'ASST12'):
        the value is not normal when { threshold below >= value >= threshold above }
    else:
        the value is not normal when { threshold below > value > threshold above }
    """

    # get thresholds of var I in the period of outlier
    threshold_below_var_I, threshold_above_var_I = get_thresholds_var_I(station)

    # categorize the value of var I and get the category_of_phenomenon based in the label phenomenon

    # SPECIAL CASE 2: for some variables for set the category of phenomenon the thresholds are inclusive
    if station.var_I.type_series in ['ONI1', 'ONI2', 'SST12', 'SST3', 'SST4', 'SST34', 'ASST12', 'ASST3', 'ASST4', 'ASST34']:
        if value <= threshold_below_var_I:
            category_of_phenomenon = globals_vars.phenomenon_below
        elif value >= threshold_above_var_I:
            category_of_phenomenon = globals_vars.phenomenon_above
        else:
            category_of_phenomenon = globals_vars.phenomenon_normal
    else:
        if value < threshold_below_var_I:
            category_of_phenomenon = globals_vars.phenomenon_below
        elif value > threshold_above_var_I:
            category_of_phenomenon = globals_vars.phenomenon_above
        else:
            category_of_phenomenon = globals_vars.phenomenon_normal

    return category_of_phenomenon


def get_contingency_table(station, lag, month, day=None):
    """
    Calculate and return the contingency table in absolute values,
    values in percent, values to print and thresholds by below and
    above of dependent and independent variable.
    """

    if day is None:
        # get all values of var D and var I based on this lag and month
        station.var_D_values = lags.get_lag_values(station, 'var_D', lag, month)
        station.var_I_values = lags.get_lag_values(station, 'var_I', lag, month)

    if day is not None:
        # get all values of var D and var I based on this lag and month
        station.var_D_values = lags.get_lag_values(station, 'var_D', lag, month, day)
        station.var_I_values = lags.get_lag_values(station, 'var_I', lag, month, day)

    # calculate thresholds as defined by the user in station file for var D
    threshold_below_var_D, threshold_above_var_D = get_thresholds_var_D(station)

    # calculate thresholds as defined by the user in station file for var I
    threshold_below_var_I, threshold_above_var_I = get_thresholds_var_I(station)

    # this is to print later in contingency table
    thresholds_var_D_var_I = [format_out.number(threshold_below_var_D), format_out.number(threshold_above_var_D),
                              format_out.number(threshold_below_var_I), format_out.number(threshold_above_var_I)]

    # -------------------------------------------------------------------------
    ## Calculating contingency table with absolute values

    contingency_table = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

    # SPECIAL CASE 2: for some variables for set the category of phenomenon the thresholds are inclusive (<=, >=)
    if station.var_I.type_series in ['ONI1', 'ONI2', 'SST12', 'SST3', 'SST4', 'SST34', 'ASST12', 'ASST3', 'ASST4', 'ASST34']:
        for index, var_I in enumerate(station.var_I_values):
            if var_I <= threshold_below_var_I:
                if station.var_D_values[index] <= threshold_below_var_D:
                    contingency_table[0][0] += 1
                if threshold_below_var_D < station.var_D_values[index] < threshold_above_var_D:
                    contingency_table[0][1] += 1
                if station.var_D_values[index] >= threshold_above_var_D:
                    contingency_table[0][2] += 1
            if threshold_below_var_I < var_I < threshold_above_var_I:
                if station.var_D_values[index] <= threshold_below_var_D:
                    contingency_table[1][0] += 1
                if threshold_below_var_D < station.var_D_values[index] < threshold_above_var_D:
                    contingency_table[1][1] += 1
                if station.var_D_values[index] >= threshold_above_var_D:
                    contingency_table[1][2] += 1
            if var_I >= threshold_above_var_I:
                if station.var_D_values[index] <= threshold_below_var_D:
                    contingency_table[2][0] += 1
                if threshold_below_var_D < station.var_D_values[index] < threshold_above_var_D:
                    contingency_table[2][1] += 1
                if station.var_D_values[index] >= threshold_above_var_D:
                    contingency_table[2][2] += 1
    else:
        # normal case
        for index, var_I in enumerate(station.var_I_values):
            if var_I < threshold_below_var_I:
                if station.var_D_values[index] <= threshold_below_var_D:
                    contingency_table[0][0] += 1
                if threshold_below_var_D < station.var_D_values[index] < threshold_above_var_D:
                    contingency_table[0][1] += 1
                if station.var_D_values[index] >= threshold_above_var_D:
                    contingency_table[0][2] += 1
            if threshold_below_var_I <= var_I <= threshold_above_var_I:
                if station.var_D_values[index] <= threshold_below_var_D:
                    contingency_table[1][0] += 1
                if threshold_below_var_D < station.var_D_values[index] < threshold_above_var_D:
                    contingency_table[1][1] += 1
                if station.var_D_values[index] >= threshold_above_var_D:
                    contingency_table[1][2] += 1
            if var_I > threshold_above_var_I:
                if station.var_D_values[index] <= threshold_below_var_D:
                    contingency_table[2][0] += 1
                if threshold_below_var_D < station.var_D_values[index] < threshold_above_var_D:
                    contingency_table[2][1] += 1
                if station.var_D_values[index] >= threshold_above_var_D:
                    contingency_table[2][2] += 1

    # -------------------------------------------------------------------------
    ## Calculating contingency table with values in percent
    tertile_size = station.size_time_series / 3.0
    contingency_table_percent = matrix(contingency_table) * tertile_size

    sum_per_column_percent = contingency_table_percent.sum(axis=1)

    # -------------------------------------------------------------------------
    # threshold_problem is global variable for detect problem with
    # threshold of independent variable, if a problem is detected
    # show message and print "nan" (this mean null value for
    # division by zero) in contingency tabla percent in result
    # table, jaziku continue but the graphics will not be created
    # because "nan"  character could not be calculate.

    # if threshold by below of independent variable is wrong
    if float(sum_per_column_percent[0]) == 0 and not globals_vars.threshold_problem[0]:
        console.msg(
            _(u"\n\n > WARNING: The thresholds selected '{0}' and '{1}'\n"
              u"   are not suitable for compound analysis of\n"
              u"   variable '{2}' with relation to '{3}' inside\n"
              u"   category '{4}'. Therefore, the graphics\n"
              u"   will not be created.")
            .format(config_run.settings['threshold_below_var_I'], config_run.settings['threshold_above_var_I'],
                station.var_D.type_series, station.var_I.type_series, config_run.settings['phen_below_label']), color='yellow')
        globals_vars.threshold_problem[0] = True

    # if threshold by below or above calculating normal phenomenon of independent variable is wrong
    if float(sum_per_column_percent[1]) == 0 and not globals_vars.threshold_problem[1]:
        console.msg(
            _(u"\n\n > WARNING: The thresholds selected '{0}' and '{1}'\n"
              u"   are not suitable for compound analysis of\n"
              u"   variable '{2}' with relation to '{3}' inside\n"
              u"   category '{4}'. Therefore, the graphics\n"
              u"   will not be created.")
            .format(config_run.settings['threshold_below_var_I'], config_run.settings['threshold_above_var_I'],
                station.var_D.type_series, station.var_I.type_series, config_run.settings['phen_normal_label']), color='yellow')
        globals_vars.threshold_problem[1] = True

    # if threshold by above of independent variable is wrong
    if float(sum_per_column_percent[2]) == 0 and not globals_vars.threshold_problem[2]:
        console.msg(
            _(u"\n\n > WARNING: The thresholds selected '{0}' and '{1}'\n"
              u"   are not suitable for compound analysis of\n"
              u"   variable '{2}' with relation to '{3}' inside\n"
              u"   category '{4}'. Therefore, the graphics\n"
              u"   will not be created.")
            .format(config_run.settings['threshold_below_var_I'], config_run.settings['threshold_above_var_I'],
                station.var_D.type_series, station.var_I.type_series, config_run.settings['phen_above_label']), color='yellow')
        globals_vars.threshold_problem[2] = True

    try:
        # not shows error if there are any problem with threshold
        sys.stderr = open(os.devnull, 'w')
        # Calculating contingency table percent
        contingency_table_percent \
            = [(contingency_table_percent[0] * 100 / float(sum_per_column_percent[0])).tolist()[0],
               (contingency_table_percent[1] * 100 / float(sum_per_column_percent[1])).tolist()[0],
               (contingency_table_percent[2] * 100 / float(sum_per_column_percent[2])).tolist()[0]]
    except:
        pass

    # Contingency table percent to print in result table and graphics (reduce the number of decimals)
    contingency_table_percent_print = []
    for row in contingency_table_percent:
        contingency_table_percent_print.append([format_out.number(row[0], 1),
                                                format_out.number(row[1], 1),
                                                format_out.number(row[2], 1)])

    return contingency_table, contingency_table_percent,\
           contingency_table_percent_print, thresholds_var_D_var_I


def contingency_table(station):
    """
    Print the contingency table for each trimester and each lag
    """

    # [lag][month][phenomenon][data(0,1,2)]
    # [lag][month][day][phenomenon][data(0,1,2)]
    contingencies_tables_percent = {}
    # defined if is first iteration
    station.first_iter = True
    for lag in config_run.settings['lags']:

        tmp_month_list = []
        # all months in year 1->12
        for month in range(1, 13):
            if globals_vars.STATE_OF_DATA in [1, 3]:

                contingency_table,\
                contingency_table_percent,\
                contingency_table_percent_print,\
                thresholds_var_D_var_I = get_contingency_table(station, lag, month)

                tmp_month_list.append(contingency_table_percent)

                if station.first_iter:
                    station.first_iter = False

            if globals_vars.STATE_OF_DATA in [2, 4]:
                tmp_day_list = []
                for day in station.range_analysis_interval:

                    contingency_table,\
                    contingency_table_percent,\
                    contingency_table_percent_print,\
                    thresholds_var_D_var_I = get_contingency_table(station, lag,
                        month, day)
                    tmp_day_list.append(contingency_table_percent)

                    if station.first_iter:
                        station.first_iter = False

                tmp_month_list.append(tmp_day_list)

        contingencies_tables_percent[lag] = tmp_month_list

    station.contingencies_tables_percent = contingencies_tables_percent
