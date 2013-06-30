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
from math import isnan

from jaziku import env
from jaziku.core.analysis_interval import get_range_analysis_interval
from jaziku.utils import output
from jaziku.utils.text import slugify


def calculate_index(category, values):
    """Calculate the index based on values and the category, the index value
    is the maximum value predominating the values near to normal.

    The index value is calculated as follows: If the maximum value is by
    below, the index is negative of this value; if the maximum value is normal,
    the index is zero; if the maximum value is by above, the index is the
    same value. If there are two equal maximums values (i.g. below and above),
    the index is normal (zero), in 7 categories if there are two maximums by
    below or by above, selected the value near to normal.

    :param category: Category to calculate the index (3 or 7)
    :type category: int
    :param values: Values
    :type values: dict

    :return: {'value': index, 'position': position of index}
    :rtype: dict
    """

    # first check if all values are zero
    if not False in [value==0 for value in values.values()]:
        return {'value':float('NaN'),
                'position':None}

    # below-normal-above
    if category == 3:
        # select index
        if (values['normal'] >= values['below'] and values['normal'] >= values['above']) or values['below'] == values['above']:
            return {'value':0,
                    'position':'normal'}
        elif values['below'] > values['above']:
            return {'value':-values['below'],
                    'position':'below'}
        elif values['above'] > values['below']:
            return {'value':values['above'],
                    'position':'above'}

        return {'value':float('NaN'),
                'position':None}

    if category == 7:
        B = max([values['below3'], values['below2'], values['below1']])
        A = max([values['above3'], values['above2'], values['above1']])
        new_values = {'below':B, 'normal':values['normal'], 'above':A}
        # get index based on algorithm of 3 categories
        index_3cat = calculate_index(3, new_values)

        # check if is nan
        if isnan(index_3cat['value']):
            return index_3cat

        # find index position for 7 categories
        if index_3cat['position'] == 'below':
            if values['below3'] == -index_3cat['value']:
                position = 'below3'
            if values['below2'] == -index_3cat['value']:
                position = 'below2'
            if values['below1'] == -index_3cat['value']:
                position = 'below1'
        if index_3cat['position'] == 'above':
            if values['above3'] == index_3cat['value']:
                position = 'above3'
            if values['above2'] == index_3cat['value']:
                position = 'above2'
            if values['above1'] == index_3cat['value']:
                position = 'above1'
        if index_3cat['position'] == 'normal':
            position = 'normal'

        return {'value':index_3cat['value'],
                'position':position}


def climate_data_for_maps(station):
    """Create maps data csv file (one by lag) for climate with all information required
    for make particular maps, this included stations names, latitude, longitude, the
    probabilities values, the index, the position the index and others. This file
    contain all stations processed but this function process one station each time
    and the data is added in the end of file.
    """

    # -------------------------------------------------------------------------
    # create maps plots files for climate process, only once
    if not env.globals_vars.maps_files_climate:
        # create and define csv output file for maps climate

        # define maps data files and directories
        for lag in env.config_run.settings['lags']:

            maps_dir = os.path.join(env.globals_vars.CLIMATE_DIR, _('maps'))

            maps_data_lag = os.path.join(maps_dir, _('lag_{0}').format(lag))

            output.make_dirs(maps_data_lag)

            # all months in year 1->12
            month_list = []
            for month in range(1, 13):

                if env.globals_vars.STATE_OF_DATA in [1, 3]:
                    categories_list = []
                    for category_label in env.config_run.get_categories_labels_var_I_list():
                        _category_label = category_label
                        category_label = category_label.strip().replace(' ','_')
                        maps_data_for_category_label = os.path.join(maps_data_lag, category_label)

                        output.make_dirs(maps_data_for_category_label)

                        csv_name \
                            = os.path.join(maps_data_for_category_label, _(u'Map_Data_lag_{0}_trim_{1}_{2}.csv')
                                          .format(lag, month, category_label))

                        if os.path.isfile(csv_name):
                            os.remove(csv_name)

                        # special label 'SUM' for below* and above for 7 categories
                        _list = env.config_run.settings['categories_labels_var_I']
                        if env.config_run.settings['class_category_analysis'] == 7 and \
                           _list.keys()[_list.values().index(_category_label)] != "normal":
                            sum_header = _('SUM (partial)')
                            del _list
                        else:
                            sum_header = _('SUM')
                            del _list

                        # write header
                        open_file = open(csv_name, 'w')
                        csv_file = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)
                        csv_file.writerow([_('CODE'), _('LAT'), _('LON'), _('PEARSON')] + \
                                          env.var_D.get_generic_labels(upper=True) + \
                                          [sum_header, _('INDEX'), _('INDEX POSITION')])
                        open_file.close()
                        del csv_file

                        categories_list.append(csv_name)

                    month_list.append(categories_list)
                if env.globals_vars.STATE_OF_DATA in [2, 4]:
                    day_list = []
                    for day in get_range_analysis_interval():
                        categories_list = []

                        for category_label in env.config_run.get_categories_labels_var_I_list():
                            _category_label = category_label
                            category_label = category_label.strip().replace(' ','_')
                            maps_data_for_category_label = os.path.join(maps_data_lag, category_label)

                            output.make_dirs(maps_data_for_category_label)

                            csv_name \
                                = os.path.join(maps_data_for_category_label, _(u'Map_Data_lag_{0}_{1}_{2}.csv')
                                    .format(lag,
                                            output.month_in_initials(month - 1) + "_" + str(day),
                                            category_label))

                            if os.path.isfile(csv_name):
                                os.remove(csv_name)

                            # special label 'SUM' for below* and above for 7 categories
                            _list = env.config_run.settings['categories_labels_var_I']
                            if env.config_run.settings['class_category_analysis'] == 7 and \
                               _list.keys()[_list.values().index(_category_label)] != "normal":
                                sum_header = _('SUM (partial)')
                                del _list
                            else:
                                sum_header = _('SUM')
                                del _list

                            # write header
                            open_file = open(csv_name, 'w')
                            csv_file = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)
                            csv_file.writerow([_('CODE'), _('LAT'), _('LON'), _('PEARSON')] + \
                                              env.var_D.get_generic_labels(upper=True) + \
                                              [sum_header, _('INDEX'), _('INDEX POSITION')])
                            open_file.close()
                            del csv_file

                            categories_list.append(csv_name)

                        day_list.append(categories_list)

                    month_list.append(day_list)

            env.globals_vars.maps_files_climate[lag] = month_list

    for lag in env.config_run.settings['lags']:

        # all months in year 1->12
        for month in range(1, 13):

            if env.globals_vars.STATE_OF_DATA in [1, 3]:
                for category_var_I in range(env.config_run.settings['class_category_analysis']):
                    if env.config_run.settings['class_category_analysis'] == 3:
                        values_CT = {'below': station.contingency_tables[lag][month - 1]['in_percentage'][category_var_I][0],
                                     'normal':station.contingency_tables[lag][month - 1]['in_percentage'][category_var_I][1],
                                     'above': station.contingency_tables[lag][month - 1]['in_percentage'][category_var_I][2]}
                        index = calculate_index(3, values_CT)
                    if env.config_run.settings['class_category_analysis'] == 7:
                        values_CT = {'below3': station.contingency_tables[lag][month - 1]['in_percentage'][category_var_I][0],
                                     'below2': station.contingency_tables[lag][month - 1]['in_percentage'][category_var_I][1],
                                     'below1': station.contingency_tables[lag][month - 1]['in_percentage'][category_var_I][2],
                                     'normal': station.contingency_tables[lag][month - 1]['in_percentage'][category_var_I][3],
                                     'above1': station.contingency_tables[lag][month - 1]['in_percentage'][category_var_I][4],
                                     'above2': station.contingency_tables[lag][month - 1]['in_percentage'][category_var_I][5],
                                     'above3': station.contingency_tables[lag][month - 1]['in_percentage'][category_var_I][6]}
                        index = calculate_index(7, values_CT)

                    # write new row in file
                    csv_name = env.globals_vars.maps_files_climate[lag][month - 1][category_var_I]
                    open_file = open(csv_name, 'a')
                    csv_file = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)
                    if env.config_run.settings['class_category_analysis'] == 3:
                        csv_file.writerow([station.code, output.number(station.lat), output.number(station.lon),
                                           output.number(station.pearson_list[lag][month - 1]),
                                           output.number(values_CT['below']),
                                           output.number(values_CT['normal']),
                                           output.number(values_CT['above']),
                                           output.number(sum([float(value_CT) for value_CT in values_CT.values()])),
                                           output.number(index['value']),
                                           env.globals_vars.categories(index['position'])])
                    if env.config_run.settings['class_category_analysis'] == 7:
                        csv_file.writerow([station.code, output.number(station.lat), output.number(station.lon),
                                           output.number(station.pearson_list[lag][month - 1]),
                                           output.number(values_CT['below3']),
                                           output.number(values_CT['below2']),
                                           output.number(values_CT['below1']),
                                           output.number(values_CT['normal']),
                                           output.number(values_CT['above1']),
                                           output.number(values_CT['above2']),
                                           output.number(values_CT['above3']),
                                           output.number(sum([float(value_CT) for value_CT in values_CT.values()])),
                                           output.number(index['value']),
                                           env.globals_vars.categories(index['position'])])
                    open_file.close()
                    del csv_file

            if env.globals_vars.STATE_OF_DATA in [2, 4]:
                for idx_day, day in enumerate(get_range_analysis_interval()):
                    for category_var_I in range(env.config_run.settings['class_category_analysis']):
                        if env.config_run.settings['class_category_analysis'] == 3:
                            values_CT = {'below': station.contingency_tables[lag][month - 1][idx_day]['in_percentage'][category_var_I][0],
                                         'normal':station.contingency_tables[lag][month - 1][idx_day]['in_percentage'][category_var_I][1],
                                         'above': station.contingency_tables[lag][month - 1][idx_day]['in_percentage'][category_var_I][2]}
                            index = calculate_index(3, values_CT)
                        if env.config_run.settings['class_category_analysis'] == 7:
                            values_CT = {'below3': station.contingency_tables[lag][month - 1][idx_day]['in_percentage'][category_var_I][0],
                                         'below2': station.contingency_tables[lag][month - 1][idx_day]['in_percentage'][category_var_I][1],
                                         'below1': station.contingency_tables[lag][month - 1][idx_day]['in_percentage'][category_var_I][2],
                                         'normal': station.contingency_tables[lag][month - 1][idx_day]['in_percentage'][category_var_I][3],
                                         'above1': station.contingency_tables[lag][month - 1][idx_day]['in_percentage'][category_var_I][4],
                                         'above2': station.contingency_tables[lag][month - 1][idx_day]['in_percentage'][category_var_I][5],
                                         'above3': station.contingency_tables[lag][month - 1][idx_day]['in_percentage'][category_var_I][6]}
                            index = calculate_index(7, values_CT)

                        # write new row in file
                        csv_name = env.globals_vars.maps_files_climate[lag][month - 1][idx_day][category_var_I]
                        open_file = open(csv_name, 'a')
                        csv_file = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)
                        if env.config_run.settings['class_category_analysis'] == 3:
                            csv_file.writerow([station.code, output.number(station.lat), output.number(station.lon),
                                               output.number(station.pearson_list[lag][month - 1][idx_day]),
                                               output.number(values_CT['below']),
                                               output.number(values_CT['normal']),
                                               output.number(values_CT['above']),
                                               output.number(sum([float(value_CT) for value_CT in values_CT.values()])),
                                               output.number(index['value']),
                                               env.globals_vars.categories(index['position'])])
                        if env.config_run.settings['class_category_analysis'] == 7:
                            csv_file.writerow([station.code, output.number(station.lat), output.number(station.lon),
                                               output.number(station.pearson_list[lag][month - 1][idx_day]),
                                               output.number(values_CT['below3']),
                                               output.number(values_CT['below2']),
                                               output.number(values_CT['below1']),
                                               output.number(values_CT['normal']),
                                               output.number(values_CT['above1']),
                                               output.number(values_CT['above2']),
                                               output.number(values_CT['above3']),
                                               output.number(sum([float(value_CT) for value_CT in values_CT.values()])),
                                               output.number(index['value']),
                                               env.globals_vars.categories(index['position'])])
                        open_file.close()
                        del csv_file


def forecast_data_for_maps(station):
    """Create maps data csv file (one by lag) for climate with all information required
    for make particular maps, this included stations names, latitude, longitude, the
    probabilities values, the index, the position the index and others. This file
    contain all stations processed but this function process one station each time
    and the data is added in the end of file.
    """

    # -------------------------------------------------------------------------
    # create maps plots files for forecast process, only once

    # run only the first time
    if not env.globals_vars.maps_files_forecast:

        maps_dir = os.path.join(
                    env.globals_vars.FORECAST_DIR, _('maps'),
                    env.config_run.settings['analysis_interval_i18n'],
                    slugify(env.config_run.settings['forecast_date']['text']))

        output.make_dirs(maps_dir)

        if env.globals_vars.STATE_OF_DATA in [1, 3]:
            lags_list = {}
            # define maps data files and directories
            for lag in env.config_run.settings['lags']:

                # write the headers in file
                csv_name = os.path.join(maps_dir, _(u'Map_Data_lag_{0}_{1}.csv')
                .format(lag, output.trimester_in_initials(env.config_run.settings['forecast_date']['month'] - 1)))

                if os.path.isfile(csv_name):
                    os.remove(csv_name)

                open_file = open(csv_name, 'w')
                csv_file = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)
                csv_file.writerow([_('CODE'), _('LAT'), _('LON'),_('FORECAST_DATE')] +\
                                   env.var_D.get_generic_labels(upper=True) + \
                                   [_('SUM'), _('INDEX'), _('INDEX POSITION')])
                open_file.close()
                del csv_file

                lags_list[lag] = csv_name
            env.globals_vars.maps_files_forecast[env.config_run.settings['forecast_date']['text']] = lags_list

        if env.globals_vars.STATE_OF_DATA in [2, 4]:
            lags_list = {}
            # define maps data files and directories
            for lag in env.config_run.settings['lags']:

                # write the headers in file
                csv_name = os.path.join(maps_dir, _(u'Map_Data_lag_{0}_{1}.csv')
                .format(lag, slugify(env.config_run.settings['forecast_date']['text'])))

                if os.path.isfile(csv_name):
                    os.remove(csv_name)

                open_file = open(csv_name, 'w')
                csv_file = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)
                csv_file.writerow([_('CODE'), _('LAT'), _('LON'),_('FORECAST_DATE')] +\
                                   env.var_D.get_generic_labels(upper=True) + \
                                   [_('SUM'), _('INDEX'), _('INDEX POSITION')])
                open_file.close()
                del csv_file

                lags_list[lag] = csv_name
            env.globals_vars.maps_files_forecast[env.config_run.settings['forecast_date']['text']] = lags_list

    # process station by lag
    for lag in env.config_run.settings['lags']:

        index = calculate_index(env.config_run.settings['class_category_analysis'], station.prob_var_D[lag])

        # write new row in file
        csv_name = env.globals_vars.maps_files_forecast[env.config_run.settings['forecast_date']['text']][lag]
        open_file = open(csv_name, 'a')
        csv_file = csv.writer(open_file, delimiter=env.globals_vars.OUTPUT_CSV_DELIMITER)

        if env.config_run.settings['class_category_analysis'] == 3:
            csv_file.writerow([station.code,
                               output.number(station.lat, 4),
                               output.number(station.lon, 4),
                               env.config_run.settings['forecast_date']['text'],
                               output.number(station.prob_var_D[lag]['below']),
                               output.number(station.prob_var_D[lag]['normal']),
                               output.number(station.prob_var_D[lag]['above']),
                               output.number(sum(station.prob_var_D[lag].values())),
                               output.number(index['value']),
                               env.globals_vars.categories(index['position'])])

        if env.config_run.settings['class_category_analysis'] == 7:
            csv_file.writerow([station.code,
                               output.number(station.lat, 4),
                               output.number(station.lon, 4),
                               env.config_run.settings['forecast_date']['text'],
                               output.number(station.prob_var_D[lag]['below3']),
                               output.number(station.prob_var_D[lag]['below2']),
                               output.number(station.prob_var_D[lag]['below1']),
                               output.number(station.prob_var_D[lag]['normal']),
                               output.number(station.prob_var_D[lag]['above1']),
                               output.number(station.prob_var_D[lag]['above2']),
                               output.number(station.prob_var_D[lag]['above3']),
                               output.number(sum(station.prob_var_D[lag].values())),
                               output.number(index['value']),
                               env.globals_vars.categories(index['position'])])
        open_file.close()
        del csv_file