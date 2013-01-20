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
from numpy import matrix
from scipy import stats
from datetime import date
from dateutil.relativedelta import relativedelta

from jaziku.env import globals_vars, config_run
from jaziku.utils import format_out
from jaziku.modules.climate import statistic_tests
from jaziku.modules.climate.contingency_table import get_contingency_table
from jaziku.modules.climate.lags import get_lag_values


def composite_analysis(station):
    """
    Calculate and print the result table for composite analysis in csv
    file, this file contain several variables of previous calculations and
    different tests.
    """

    pearson_list = {}
    is_sig_risk_analysis = {}

    def main_process():
        # test:
        # is significance risk analysis?

        is_sig_risk_analysis_list = []

        contingency_table_matrix = matrix(contingency_table)
        sum_per_row = contingency_table_matrix.sum(axis=0).tolist()[0]
        sum_per_column = contingency_table_matrix.sum(axis=1).tolist()
        sum_contingency_table = contingency_table_matrix.sum()

        for c, column_table in enumerate(contingency_table):
            for r, Xi in enumerate(column_table):
                M = sum_per_column[c]
                n = sum_per_row[r]
                N = sum_contingency_table
                X = stats.hypergeom.cdf(Xi, N, M, n)
                Y = stats.hypergeom.sf(Xi, N, M, n, loc=1)
                if X <= 0.1 or Y <= 0.1:
                    is_sig_risk_analysis_list.append(_('yes'))
                else:
                    is_sig_risk_analysis_list.append(_('no'))

        if globals_vars.STATE_OF_DATA in [1, 3]:
            # get values of var D and I from this lag and month
            var_D_values = get_lag_values(station, 'var_D', lag, month)

            var_I_values = get_lag_values(station, 'var_I', lag, month)

        if globals_vars.STATE_OF_DATA in [2, 4]:
            # get values of var D and I from this lag, month and day
            var_D_values = get_lag_values(station, 'var_D', lag, month, day)

            var_I_values = get_lag_values(station, 'var_I', lag, month, day)

        # calculate pearson correlation of var_D and var_I
        pearson = stats.pearsonr(var_D_values, var_I_values)[0]
        # significance correlation
        singr, T_test, t_crit \
            = statistic_tests.significance_correlation(rho=0, r=pearson, n=len(station.common_period) + 1, alpha=0.05, side=0)

        # contingency test
        Observed, Expected, test_stat, crit_value, df, p_value, alpha \
            = statistic_tests.contingency_test(contingency_table, None, 0.9, -1)

        # calculate the correlation of contingency table
        chi_cdf = 1 - p_value
        corr_CT = ((chi_cdf ** 2) / (station.size_time_series * 2.0)) ** 0.5

        # test:
        # Is significant the contingency table?
        if test_stat > crit_value:
            is_significant_CT = _('yes')
        else:
            is_significant_CT = _('no')

        # test:
        # Is significant the singr variable?
        if (1 - singr) >= 0.05:
            is_significant_singr = _('yes')
        else:
            is_significant_singr = _('no')

        #===============================================================================
        # result table (csv file), add one line of this trimester and lag

        # add new line in csv_file_write
        csv_result_table.writerow([
            var_D_text, var_I_text,
            format_out.number(pearson), format_out.number(singr), is_significant_singr,
            thresholds_var_D_var_I[0], thresholds_var_D_var_I[1],
            thresholds_var_D_var_I[2], thresholds_var_D_var_I[3],
            contingency_table[0][0], contingency_table[0][1],
            contingency_table[0][2], contingency_table[1][0],
            contingency_table[1][1], contingency_table[1][2],
            contingency_table[2][0], contingency_table[2][1],
            contingency_table[2][2],
            contingency_table_percent_print[0][0],
            contingency_table_percent_print[0][1],
            contingency_table_percent_print[0][2],
            contingency_table_percent_print[1][0],
            contingency_table_percent_print[1][1],
            contingency_table_percent_print[1][2],
            contingency_table_percent_print[2][0],
            contingency_table_percent_print[2][1],
            contingency_table_percent_print[2][2],
            is_sig_risk_analysis_list[0], is_sig_risk_analysis_list[1],
            is_sig_risk_analysis_list[2], is_sig_risk_analysis_list[3],
            is_sig_risk_analysis_list[4], is_sig_risk_analysis_list[5],
            is_sig_risk_analysis_list[6], is_sig_risk_analysis_list[7],
            is_sig_risk_analysis_list[8],
            format_out.number(test_stat), format_out.number(crit_value),
            is_significant_CT, format_out.number(corr_CT, 4)])

        return pearson, is_sig_risk_analysis_list

    for lag in config_run.settings['lags']:

        # dir and name to save the result table
        csv_name \
            = os.path.join(station.climate_dir, _('Result_Table_CA_lag_{0}_{1}_{2}_{3}_{4}_({5}-{6}).csv')
                .format(lag, station.name, station.code, station.var_D.type_series, station.var_I.type_series,
                        station.process_period['start'], station.process_period['end']))

        if os.path.isfile(csv_name):
            os.remove(csv_name)

        open_file = open(csv_name, 'w')
        csv_result_table = csv.writer(open_file, delimiter=globals_vars.OUTPUT_CSV_DELIMITER)

        # print headers in result table
        csv_result_table.writerow([
            _('var_D'), _('var_I'), _('Pearson'), _('Sign Pearson'),
            _('Is sign \'Sign Pearson\'?'), _('threshold below (var D)'),
            _('threshold above (var D)'), _('threshold below (var I)'),
            _('threshold above (var I)'), _('Contingency Table (CT)'),
            '', '', '', '', '', '', '', '', _('Contingency Table in %'),
            '', '', '', '', '', '', '', '', _('is sig risk analysis?'),
            '', '', '', '', '', '', '', '', _('Test Stat - Chi2'),
            _('Crit Value - Chi2'), _('Is sig CT?'), _('Correl CT')])

        # print division line between lags
        csv_result_table.writerow([
            '', '', '', '', '', '', '', '', '',
            config_run.settings['phen_below_label'], '', '',
            config_run.settings['phen_normal_label'], '', '',
            config_run.settings['phen_above_label'], '', '',
            config_run.settings['phen_below_label'], '', '',
            config_run.settings['phen_normal_label'], '', '',
            config_run.settings['phen_above_label']])

        csv_result_table.writerow([
            '', '', '', '', '', '', '', '', '',
            _('var D below'), _('var D normal'), _('var D above'),
            _('var D below'), _('var D normal'), _('var D above'),
            _('var D below'), _('var D normal'), _('var D above'),
            _('var D below'), _('var D normal'), _('var D above'),
            _('var D below'), _('var D normal'), _('var D above'),
            _('var D below'), _('var D normal'), _('var D above')])

        pearson_list_month = []
        is_sig_risk_analysis_month = []

        # all months in year 1->12
        for month in range(1, 13):

            if globals_vars.STATE_OF_DATA in [1, 3]:
                # get the contingency tables and thresholds
                contingency_table,\
                contingency_table_percent,\
                contingency_table_percent_print,\
                thresholds_var_D_var_I = get_contingency_table(station, lag, month)

                # for print text date in result table
                var_D_text = globals_vars.get_trimester_in_text(month - 1)
                var_I_text = globals_vars.get_trimester_in_text(month - 1 - lag)

                pearson, is_sig_risk_analysis_list = main_process()  # <-

                pearson_list_month.append(pearson)
                is_sig_risk_analysis_month.append(is_sig_risk_analysis_list)

            if globals_vars.STATE_OF_DATA in [2, 4]:
                pearson_list_day = []
                is_sig_risk_analysis_list_day = []
                for day in station.range_analysis_interval:
                    # get the contingency tables and thresholds
                    contingency_table,\
                    contingency_table_percent,\
                    contingency_table_percent_print,\
                    thresholds_var_D_var_I = get_contingency_table(station, lag, month, day)

                    # this is for calculate date for print in result table
                    # this depend on range analysis interval and lags (var_I)
                    # the year no matter (tested)
                    date_now = date(2000, month, day)

                    # for print text date in result table
                    var_D_text = globals_vars.get_month_in_text(date_now.month - 1) + " " + str(day)
                    var_I_text = globals_vars.get_month_in_text((date_now - relativedelta(days=(station.range_analysis_interval[1] - 1) * lag)).month - 1) +\
                                 " " + str(station.range_analysis_interval[station.range_analysis_interval.index(day) - lag])

                    pearson, is_sig_risk_analysis_list = main_process()  # <-

                    pearson_list_day.append(pearson)
                    is_sig_risk_analysis_list_day.append(is_sig_risk_analysis_list)

                pearson_list_month.append(pearson_list_day)
                is_sig_risk_analysis_month.append(is_sig_risk_analysis_list_day)

        open_file.close()
        #del csv_result_table

        pearson_list[lag] = pearson_list_month
        is_sig_risk_analysis[lag] = is_sig_risk_analysis_month

    station.pearson_list = pearson_list
    station.is_sig_risk_analysis = is_sig_risk_analysis
