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

from jaziku import env
from jaziku.core.analysis_interval import get_range_analysis_interval
from jaziku.modules.climate.thresholds import thresholds_to_list
from jaziku.utils import output
from jaziku.modules.climate import statistic_tests
from jaziku.modules.climate.lags import get_specific_values
from jaziku.utils.matrix import column


def composite_analysis(station):
    """Calculate and print the result table for composite analysis in csv
    file, this file contain several variables of previous calculations and
    different tests.

    :param station: station for process
    :type station: Station
    """

    pearson_list = {}

    # is_sig_risk_analysis:
    #  [lag][trimester][var_I][var_D]
    #  [lag][month][day][var_I][var_D]
    is_sig_risk_analysis = {}

    def main_process():

        # test:
        # is significance risk analysis?

        is_sig_risk_analysis = []  # [var_I][var_D]

        contingency_table_matrix = matrix(specific_contingency_table['in_values'])
        sum_per_row = contingency_table_matrix.sum(axis=0).tolist()[0]
        sum_per_column = contingency_table_matrix.sum(axis=1).tolist()
        sum_contingency_table = contingency_table_matrix.sum()

        for c, column_table in enumerate(specific_contingency_table['in_values']):
            column_risk_analysis = []
            for r, Xi in enumerate(column_table):
                M = sum_per_column[c]
                n = sum_per_row[r]
                N = sum_contingency_table
                X = stats.hypergeom.cdf(Xi, N, M, n)
                Y = stats.hypergeom.sf(Xi, N, M, n, loc=1)
                if X <= 0.1 or Y <= 0.1:
                    column_risk_analysis.append(_('yes'))
                else:
                    column_risk_analysis.append(_('no'))

            is_sig_risk_analysis.append(column_risk_analysis)

        if env.globals_vars.STATE_OF_DATA in [1, 3]:
            # get values of var D and I from this lag and month
            var_D_values = get_specific_values(station, 'var_D', lag, month)

            var_I_values = get_specific_values(station, 'var_I', lag, month)

        if env.globals_vars.STATE_OF_DATA in [2, 4]:
            # get values of var D and I from this lag, month and day
            var_D_values = get_specific_values(station, 'var_D', lag, month, day)

            var_I_values = get_specific_values(station, 'var_I', lag, month, day)

        # calculate pearson correlation of var_D and var_I
        pearson = stats.pearsonr(var_D_values, var_I_values)[0]
        # significance correlation
        singr, T_test, t_crit \
            = statistic_tests.significance_correlation(rho=0, r=pearson, n=len(station.common_period) + 1, alpha=0.05, side=0)

        # contingency test
        Observed, Expected, test_stat, crit_value, df, p_value, alpha \
            = statistic_tests.contingency_test(specific_contingency_table['in_values'], None, 0.9, -1)

        # calculate the correlation of contingency table
        chi_cdf = 1 - p_value
        corr_CT = ((chi_cdf ** 2) / (station.size_time_series*(env.config_run.settings['class_category_analysis'] - 1))) ** 0.5

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
        # result table (csv file) - main contain

        if env.config_run.settings['class_category_analysis'] == 3:
            # first line for value
            csv_result_table.writerow(
                [var_D_text, var_I_text, output.number(pearson),
                 output.number(singr), is_significant_singr] + \
                [output.number(item) for item in thresholds_to_list(specific_contingency_table['thresholds_var_D'])] + \
                [output.number(item) for item in thresholds_to_list(specific_contingency_table['thresholds_var_I'])] + \
                ([''] + [
                env.config_run.settings['categories_labels_var_I']['below'],
                env.config_run.settings['categories_labels_var_I']['normal'],
                env.config_run.settings['categories_labels_var_I']['above']])*3 + \
                [output.number(test_stat), output.number(crit_value),
                 is_significant_CT, output.number(corr_CT)])
            # second/third and fourth line for value
            for index, label in enumerate(env.var_D.get_generic_labels()):
                csv_result_table.writerow(
                    ['']*9 + \
                    [label] + \
                    column(specific_contingency_table['in_values'], index) + \
                    [label] + \
                    column(specific_contingency_table['in_percentage_formatted'], index) + \
                    [label] + \
                    column(is_sig_risk_analysis, index))
            # line separator
            csv_result_table.writerow([])

        if env.config_run.settings['class_category_analysis'] == 7:
            # first line for value
            csv_result_table.writerow(
                [var_D_text, var_I_text, output.number(pearson),
                 output.number(singr), is_significant_singr] + \
                [output.number(item) for item in thresholds_to_list(specific_contingency_table['thresholds_var_D'])] + \
                [output.number(item) for item in thresholds_to_list(specific_contingency_table['thresholds_var_I'])] + \
                ([''] + [
                env.config_run.settings['categories_labels_var_I']['below3'],
                env.config_run.settings['categories_labels_var_I']['below2'],
                env.config_run.settings['categories_labels_var_I']['below1'],
                env.config_run.settings['categories_labels_var_I']['normal'],
                env.config_run.settings['categories_labels_var_I']['above1'],
                env.config_run.settings['categories_labels_var_I']['above2'],
                env.config_run.settings['categories_labels_var_I']['above3']])*3 + \
                [output.number(test_stat), output.number(crit_value),
                 is_significant_CT, output.number(corr_CT)])
            # second/third and fourth line for value
            for index, label in enumerate(env.var_D.get_generic_labels()):
                csv_result_table.writerow(
                    ['']*17 + \
                    [label] + \
                    column(specific_contingency_table['in_values'], index) + \
                    [label] + \
                    column(specific_contingency_table['in_percentage_formatted'], index) + \
                    [label] + \
                    column(is_sig_risk_analysis, index))
            # line separator
            csv_result_table.writerow([])

        return pearson, is_sig_risk_analysis

    for lag in env.config_run.settings['lags']:

        # dir and name to save the result table
        csv_name \
            = os.path.join(station.climate_dir, _('Result_Table_CA_lag_{0}_{1}_{2}_{3}_{4}_({5}-{6}).csv')
                .format(lag, station.code, station.name, station.var_D.type_series, station.var_I.type_series,
                        station.process_period['start'], station.process_period['end']))

        if os.path.isfile(csv_name):
            os.remove(csv_name)

        open_file = open(csv_name, 'w')
        csv_result_table = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)

        #===============================================================================
        # result table (csv file) - headers
        if env.config_run.settings['class_category_analysis'] == 3:
            # print first line of header
            csv_result_table.writerow(
                [_('VAR_D'), _('VAR_I'), _('PEARSON'), _('SIGN. PEARSON'),
                 _("IS SIGN 'SIGN PEARSON'?"), _('THRESHOLDS VAR D')] + \
                [''] + [_('THRESHOLDS VAR I')] + [''] + \
                [_('CONTINGENCY TABLE (CT)')] + ['']*3 + \
                [_('CONTINGENCY TABLE IN %')] + ['']*3 + \
                [_('IS SIGN RISK ANALYSIS?')] + ['']*3 + \
                [_('TEST STAT - CHI2'), _('CRIT VALUE - Chi2'), _('IS SIGN CT?'), _('CORREL CT')])
            # print second line of header
            csv_result_table.writerow(
                ['']*5 + \
                [_('below'),_('above')]*2)

        if env.config_run.settings['class_category_analysis'] == 7:
            # print first line of header
            csv_result_table.writerow(
                [_('VAR_D'), _('VAR_I'), _('PEARSON'), _('SIGN. PEARSON'),
                 _("IS SIGN 'SIGN PEARSON'?"), _('THRESHOLDS VAR D')] + \
                ['']*5 + [_('THRESHOLDS VAR I')] + ['']*5 + \
                [_('CONTINGENCY TABLE (CT)')] + ['']*7 + \
                [_('CONTINGENCY TABLE IN %')] + ['']*7 + \
                [_('IS SIGN RISK ANALYSIS?')] + ['']*7 + \
                [_('TEST STAT - CHI2'), _('CRIT VALUE - Chi2'), _('IS SIGN CT?'), _('CORREL CT')])
            # print second line of header
            csv_result_table.writerow(
                ['']*5 + \
                [_('strong below'), _('moderate below'), _('weak below'),
                 _('weak above'), _('moderate above'), _('strong above')]*2)

        pearson_list_month = []
        is_sig_risk_analysis_month = []

        # all months in year 1->12
        for month in range(1, 13):

            if env.globals_vars.STATE_OF_DATA in [1, 3]:
                # get the contingency tables and thresholds

                specific_contingency_table = station.contingency_tables[lag][month-1]

                # for print text date in result table
                var_D_text = output.trimester_in_initials(month - 1)
                var_I_text = output.trimester_in_initials(month - 1 - lag)

                pearson, is_sig_risk_analysis_list = main_process()  # <-

                pearson_list_month.append(pearson)
                is_sig_risk_analysis_month.append(is_sig_risk_analysis_list)

            if env.globals_vars.STATE_OF_DATA in [2, 4]:
                pearson_list_day = []
                is_sig_risk_analysis_list_day = []
                range_analysis_interval = get_range_analysis_interval()
                for idx_day, day in enumerate(range_analysis_interval):
                    # get the contingency tables and thresholds

                    specific_contingency_table = station.contingency_tables[lag][month-1][idx_day]

                    # this is for calculate date for print in result table
                    # this depend on range analysis interval and lags (var_I)
                    # the year no matter (tested)
                    date_now = date(2000, month, day)

                    # for print text date in result table
                    var_D_text = output.month_in_initials(date_now.month - 1) + " " + str(day)
                    var_I_text = output.month_in_initials((date_now - relativedelta(days=(range_analysis_interval[1] - 1) * lag)).month - 1)\
                                 + " " + str(range_analysis_interval[idx_day - lag])

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
