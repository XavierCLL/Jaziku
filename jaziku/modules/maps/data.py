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

from jaziku import env
from jaziku.utils import format_out


def climate_data_for_maps(station):
    """
    Create maps data csv file for plotting for each trimester, phenomenon and lag,
    each file contain all stations processed.
    """

    # -------------------------------------------------------------------------
    # create maps plots files for climate process, only once
    if env.globals_vars.maps_files_climate[env.config_run.settings['analysis_interval']] is None:
        # create and define csv output file for maps climate

        env.globals_vars.maps_files_climate[env.config_run.settings['analysis_interval']] = {}  # [lag][month][phenomenon]

        # define maps data files and directories
        for lag in env.config_run.settings['lags']:

            maps_dir = os.path.join(env.globals_vars.CLIMATE_DIR, _('maps'))

            maps_data_lag = os.path.join(maps_dir,
                env.globals_vars.analysis_interval_i18n,
                _('lag_{0}').format(lag))

            if not os.path.isdir(maps_data_lag):
                os.makedirs(maps_data_lag)

            # all months in year 1->12
            month_list = []
            for month in range(1, 13):

                if env.globals_vars.STATE_OF_DATA in [1, 3]:
                    categories_list = []
                    for category_label in env.config_run.settings['var_I_category_labels'].values():
                        maps_data_for_category_label = os.path.join(maps_data_lag, category_label)

                        if not os.path.isdir(maps_data_for_category_label):
                            os.makedirs(maps_data_for_category_label)

                        csv_name \
                            = os.path.join(maps_data_for_category_label, _(u'Map_Data_lag_{0}_trim_{1}_{2}.csv')
                                          .format(lag, month, category_label))

                        if os.path.isfile(csv_name):
                            os.remove(csv_name)

                        # write header
                        open_file = open(csv_name, 'w')
                        csv_file = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)
                        csv_file.writerow([_('CODE'), _('LAT'), _('LON'), _('PEARSON')] + \
                                          env.var_D.get_generic_labels(upper=True) + \
                                          [_('INDEX'), _('SUM')])
                        open_file.close()
                        del csv_file

                        categories_list.append(csv_name)

                    month_list.append(categories_list)
                if env.globals_vars.STATE_OF_DATA in [2, 4]:
                    day_list = []
                    for day in station.range_analysis_interval:
                        categories_list = []

                        for category_label in env.config_run.settings['var_I_category_labels'].values():
                            maps_data_for_category_label = os.path.join(maps_data_lag, category_label)

                            if not os.path.isdir(maps_data_for_category_label):
                                os.makedirs(maps_data_for_category_label)

                            csv_name \
                                = os.path.join(maps_data_for_category_label, _(u'Map_Data_lag_{0}_{1}_{2}.csv')
                                    .format(lag,
                                            format_out.month_in_initials(month - 1) + "_" + str(day),
                                            category_label))

                            if os.path.isfile(csv_name):
                                os.remove(csv_name)

                            # write header
                            open_file = open(csv_name, 'w')
                            csv_file = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)
                            csv_file.writerow([_('CODE'), _('LAT'), _('LON'), _('PEARSON')] + \
                                              env.var_D.get_generic_labels(upper=True) + \
                                              [_('INDEX'), _('SUM')])
                            open_file.close()
                            del csv_file

                            categories_list.append(csv_name)

                        day_list.append(categories_list)

                    month_list.append(day_list)

            env.globals_vars.maps_files_climate[env.config_run.settings['analysis_interval']][lag] = month_list

    def calculate_index(category, values):

        # below-normal-above
        if category == 3:
            # select index
            if (values['N'] >= values['B'] and values['N'] >= values['A']) or values['B'] == values['A']:
                return 0
            elif values['B'] > values['A']:
                return -values['B']
            elif values['A'] > values['B']:
                return values['A']
            return float('NaN')

        if category == 7:
            B = max([values['B3'], values['B2'], values['B1']])
            A = max([values['A3'], values['A2'], values['A1']])
            new_values = {'B':B, 'N':values['N'], 'A':A}
            return calculate_index(3, new_values)

    for lag in env.config_run.settings['lags']:

        # all months in year 1->12
        for month in range(1, 13):

            if env.globals_vars.STATE_OF_DATA in [1, 3]:
                for category_var_I in range(env.config_run.settings['class_category_analysis']):
                    if env.config_run.settings['class_category_analysis'] == 3:
                        values_CT = {'B': station.contingency_tables[lag][month - 1]['in_percentage'][category_var_I][0],
                                     'N': station.contingency_tables[lag][month - 1]['in_percentage'][category_var_I][1],
                                     'A': station.contingency_tables[lag][month - 1]['in_percentage'][category_var_I][2]}
                        p_index = calculate_index(3, values_CT)

                    if env.config_run.settings['class_category_analysis'] == 7:
                        values_CT = {'B3': station.contingency_tables[lag][month - 1]['in_percentage'][category_var_I][0],
                                     'B2': station.contingency_tables[lag][month - 1]['in_percentage'][category_var_I][1],
                                     'B1': station.contingency_tables[lag][month - 1]['in_percentage'][category_var_I][2],
                                     'N':  station.contingency_tables[lag][month - 1]['in_percentage'][category_var_I][3],
                                     'A1': station.contingency_tables[lag][month - 1]['in_percentage'][category_var_I][4],
                                     'A2': station.contingency_tables[lag][month - 1]['in_percentage'][category_var_I][5],
                                     'A3': station.contingency_tables[lag][month - 1]['in_percentage'][category_var_I][6]}
                        p_index = calculate_index(7, values_CT)

                    # write new row in file
                    csv_name = env.globals_vars.maps_files_climate[env.config_run.settings['analysis_interval']][lag][month - 1][category_var_I]
                    open_file = open(csv_name, 'a')
                    csv_file = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)
                    if env.config_run.settings['class_category_analysis'] == 3:
                        csv_file.writerow([station.code, format_out.number(station.lat), format_out.number(station.lon),
                                           format_out.number(station.pearson_list[lag][month - 1]),
                                           format_out.number(values_CT['B']),
                                           format_out.number(values_CT['N']),
                                           format_out.number(values_CT['A']),
                                           format_out.number(p_index),
                                           format_out.number(sum([float(value_CT) for value_CT in values_CT.values()]))])
                    if env.config_run.settings['class_category_analysis'] == 7:
                        csv_file.writerow([station.code, format_out.number(station.lat), format_out.number(station.lon),
                                           format_out.number(station.pearson_list[lag][month - 1]),
                                           format_out.number(values_CT['B3']),
                                           format_out.number(values_CT['B2']),
                                           format_out.number(values_CT['B1']),
                                           format_out.number(values_CT['N']),
                                           format_out.number(values_CT['A1']),
                                           format_out.number(values_CT['A2']),
                                           format_out.number(values_CT['A3']),
                                           format_out.number(p_index),
                                           format_out.number(sum([float(value_CT) for value_CT in values_CT.values()]))])
                    open_file.close()
                    del csv_file

            if env.globals_vars.STATE_OF_DATA in [2, 4]:
                for day in range(len(station.range_analysis_interval)):
                    for category_var_I in range(env.config_run.settings['class_category_analysis']):
                        if env.config_run.settings['class_category_analysis'] == 3:
                            values_CT = {'B': station.contingency_tables[lag][month - 1][day]['in_percentage'][category_var_I][0],
                                         'N': station.contingency_tables[lag][month - 1][day]['in_percentage'][category_var_I][1],
                                         'A': station.contingency_tables[lag][month - 1][day]['in_percentage'][category_var_I][2]}
                            p_index = calculate_index(3, values_CT)

                        if env.config_run.settings['class_category_analysis'] == 7:
                            values_CT = {'B3': station.contingency_tables[lag][month - 1][day]['in_percentage'][category_var_I][0],
                                         'B2': station.contingency_tables[lag][month - 1][day]['in_percentage'][category_var_I][1],
                                         'B1': station.contingency_tables[lag][month - 1][day]['in_percentage'][category_var_I][2],
                                         'N':  station.contingency_tables[lag][month - 1][day]['in_percentage'][category_var_I][3],
                                         'A1': station.contingency_tables[lag][month - 1][day]['in_percentage'][category_var_I][4],
                                         'A2': station.contingency_tables[lag][month - 1][day]['in_percentage'][category_var_I][5],
                                         'A3': station.contingency_tables[lag][month - 1][day]['in_percentage'][category_var_I][6]}
                            p_index = calculate_index(7, values_CT)

                        # write new row in file
                        csv_name = env.globals_vars.maps_files_climate[env.config_run.settings['analysis_interval']][lag][month - 1][day][category_var_I]
                        open_file = open(csv_name, 'a')
                        csv_file = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)
                        if env.config_run.settings['class_category_analysis'] == 3:
                            csv_file.writerow([station.code, format_out.number(station.lat), format_out.number(station.lon),
                                               format_out.number(station.pearson_list[lag][month - 1][day]),
                                               format_out.number(values_CT['B']),
                                               format_out.number(values_CT['N']),
                                               format_out.number(values_CT['A']),
                                               format_out.number(p_index),
                                               format_out.number(sum([float(value_CT) for value_CT in values_CT.values()]))])
                        if env.config_run.settings['class_category_analysis'] == 7:
                            csv_file.writerow([station.code, format_out.number(station.lat), format_out.number(station.lon),
                                               format_out.number(station.pearson_list[lag][month - 1][day]),
                                               format_out.number(values_CT['B3']),
                                               format_out.number(values_CT['B2']),
                                               format_out.number(values_CT['B1']),
                                               format_out.number(values_CT['N']),
                                               format_out.number(values_CT['A1']),
                                               format_out.number(values_CT['A2']),
                                               format_out.number(values_CT['A3']),
                                               format_out.number(p_index),
                                               format_out.number(sum([float(value_CT) for value_CT in values_CT.values()]))])
                        open_file.close()
                        del csv_file


def forecast_data_for_maps(station):
    """
    Create maps data csv file for plotting for each trimester, phenomenon and
    lag, each file contain all stations processed.
    """
    # -------------------------------------------------------------------------
    # create maps plots files for forecast process, only once

    # select text for forecast date
    if env.globals_vars.STATE_OF_DATA in [1, 3]:
        forecast_date_formatted = format_out.trimester_in_initials(env.config_run.settings['forecast_date']['month'] - 1)
    if env.globals_vars.STATE_OF_DATA in [2, 4]:
        forecast_date_formatted = format_out.month_in_initials(env.config_run.settings['forecast_date']['month'] - 1) \
                                  + "_" + str(env.config_run.settings['forecast_date']['day'])

    if forecast_date_formatted not in env.globals_vars.maps_files_forecast[env.config_run.settings['analysis_interval']]:

        if env.globals_vars.STATE_OF_DATA in [1, 3]:
            lags_list = {}
            # define maps data files and directories
            for lag in env.config_run.settings['lags']:

                maps_dir = os.path.join(env.globals_vars.FORECAST_DIR, _('maps'),
                    env.globals_vars.analysis_interval_i18n,
                    format_out.trimester_in_initials(env.config_run.settings['forecast_date']['month'] - 1))

                if not os.path.isdir(maps_dir):
                    os.makedirs(maps_dir)

                # write the headers in file
                csv_name = os.path.join(maps_dir, _(u'Map_Data_lag_{0}_{1}.csv')
                .format(lag, format_out.trimester_in_initials(env.config_run.settings['forecast_date']['month'] - 1)))

                if os.path.isfile(csv_name):
                    os.remove(csv_name)

                open_file = open(csv_name, 'w')
                csv_file = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)
                csv_file.writerow([_('code'), _('lat'), _('lon'),
                                   _('forecast_date'), _('prob_decrease_var_D'),
                                   _('prob_normal_var_D'), _('prob_exceed_var_D'),
                                   _('index'), _('sum')])
                open_file.close()
                del csv_file

                lags_list[lag] = csv_name
            env.globals_vars.maps_files_forecast[env.config_run.settings['analysis_interval']][forecast_date_formatted] = lags_list

        if env.globals_vars.STATE_OF_DATA in [2, 4]:
            lags_list = {}
            # define maps data files and directories
            for lag in env.config_run.settings['lags']:

                maps_dir = os.path.join(env.globals_vars.FORECAST_DIR, _('maps'),
                    env.globals_vars.analysis_interval_i18n,
                    forecast_date_formatted)

                if not os.path.isdir(maps_dir):
                    os.makedirs(maps_dir)

                # write the headers in file
                csv_name = os.path.join(maps_dir, _(u'Map_Data_lag_{0}_{1}.csv')
                .format(lag, forecast_date_formatted))

                if os.path.isfile(csv_name):
                    os.remove(csv_name)

                open_file = open(csv_name, 'w')
                csv_file = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)
                csv_file.writerow([_('code'), _('lat'), _('lon'),
                                   _('forecast_date'), _('prob_decrease_var_D'),
                                   _('prob_normal_var_D'), _('prob_exceed_var_D'),
                                   _('index'), _('sum')])
                open_file.close()
                del csv_file

                lags_list[lag] = csv_name
            env.globals_vars.maps_files_forecast[env.config_run.settings['analysis_interval']][forecast_date_formatted] = lags_list

    def calculate_index():
        # select index
        if station.prob_decrease_var_D[lag] > station.prob_normal_var_D[lag]:
            if station.prob_decrease_var_D[lag] > station.prob_exceed_var_D[lag]:
                p_index = -station.prob_decrease_var_D[lag]
            elif station.prob_exceed_var_D[lag] > station.prob_normal_var_D[lag]:
                p_index = station.prob_exceed_var_D[lag]
            elif station.prob_decrease_var_D[lag] == station.prob_normal_var_D[lag]:
                p_index = 0
            else:
                p_index = station.prob_decrease_var_D[lag]
        else:
            if station.prob_normal_var_D[lag] == station.prob_exceed_var_D[lag]:
                p_index = 0
            elif station.prob_normal_var_D[lag] > station.prob_exceed_var_D[lag]:
                p_index = 0
            else:
                p_index = station.prob_exceed_var_D[lag]

        return p_index

    for lag in env.config_run.settings['lags']:

        p_index = calculate_index()

        # write new row in file
        csv_name = env.globals_vars.maps_files_forecast[env.config_run.settings['analysis_interval']][forecast_date_formatted][lag]
        open_file = open(csv_name, 'a')
        csv_file = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)
        csv_file.writerow([station.code,
                           format_out.number(station.lat, 4),
                           format_out.number(station.lon, 4),
                           forecast_date_formatted,
                           format_out.number(station.prob_decrease_var_D[lag]),
                           format_out.number(station.prob_normal_var_D[lag]),
                           format_out.number(station.prob_exceed_var_D[lag]),
                           format_out.number(p_index),
                           format_out.number(sum([station.prob_decrease_var_D[lag],
                                                  station.prob_normal_var_D[lag],
                                                  station.prob_exceed_var_D[lag]]))])
        open_file.close()
        del csv_file