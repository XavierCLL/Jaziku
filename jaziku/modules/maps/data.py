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

from jaziku.env import globals_vars, config_run
from jaziku.utils import format_out


def climate_data_for_maps(station):
    """
    Create maps data csv file for plotting for each trimester, phenomenon and lag,
    each file contain all stations processed.
    """

    # -------------------------------------------------------------------------
    # create maps plots files for climate process, only once
    if globals_vars.maps_files_climate[config_run.settings['analysis_interval']] is None:
        # create and define csv output file for maps climate
        phenomenon = {0: globals_vars.phenomenon_below,
                      1: globals_vars.phenomenon_normal,
                      2: globals_vars.phenomenon_above}
        globals_vars.maps_files_climate[config_run.settings['analysis_interval']] = {}  # [lag][month][phenomenon]

        # define maps data files and directories
        for lag in config_run.settings['lags']:

            maps_dir = os.path.join(globals_vars.CLIMATE_DIR, _('maps'))

            maps_data_lag = os.path.join(maps_dir,
                globals_vars.analysis_interval_i18n,
                _('lag_{0}').format(lag))

            if not os.path.isdir(maps_data_lag):
                os.makedirs(maps_data_lag)

            # all months in year 1->12
            month_list = []
            for month in range(1, 13):

                if station.state_of_data in [1, 3]:
                    categories_list = []
                    for category in phenomenon:
                        maps_data_phenom = os.path.join(maps_data_lag, phenomenon[category])

                        if not os.path.isdir(maps_data_phenom):
                            os.makedirs(maps_data_phenom)

                        csv_name \
                            = os.path.join(maps_data_phenom, _(u'Map_Data_lag_{0}_trim_{1}_{2}.csv')
                                          .format(lag, month, phenomenon[category]))

                        if os.path.isfile(csv_name):
                            os.remove(csv_name)

                        # write new row in file
                        open_file = open(csv_name, 'w')
                        csv_file = csv.writer(open_file, delimiter=globals_vars.OUTPUT_CSV_DELIMITER)
                        csv_file.writerow([_('code'), _('lat'), _('lon'), _('pearson'),
                                           _('var_below'), _('var_normal'), _('var_above'),
                                           _('p_index'), _('sum')])
                        open_file.close()
                        del csv_file

                        categories_list.append(csv_name)

                    month_list.append(categories_list)
                if station.state_of_data in [2, 4]:
                    day_list = []
                    for day in station.range_analysis_interval:
                        categories_list = []

                        for category in phenomenon:
                            maps_data_phenom = os.path.join(maps_data_lag, phenomenon[category])

                            if not os.path.isdir(maps_data_phenom):
                                os.makedirs(maps_data_phenom)

                            csv_name \
                                = os.path.join(maps_data_phenom, _(u'Map_Data_lag_{0}_{1}_{2}.csv')
                                    .format(lag,
                                            globals_vars.get_month_in_text(month - 1) + "_" + str(day),
                                            phenomenon[category]))

                            if os.path.isfile(csv_name):
                                os.remove(csv_name)

                            # write new row in file
                            open_file = open(csv_name, 'w')
                            csv_file = csv.writer(open_file, delimiter=globals_vars.OUTPUT_CSV_DELIMITER)
                            csv_file.writerow([_('code'), _('lat'), _('lon'), _('pearson'),
                                               _('var_below'), _('var_normal'), _('var_above'),
                                               _('p_index'), _('sum')])
                            open_file.close()
                            del csv_file

                            categories_list.append(csv_name)

                        day_list.append(categories_list)

                    month_list.append(day_list)

            globals_vars.maps_files_climate[config_run.settings['analysis_interval']][lag] = month_list

    def calculate_index():
        # select index
        if var_below > var_normal:
            if var_below > var_above:
                return -var_below
            elif var_above > var_normal:
                return var_above
            elif var_below == var_normal:
                return 0
            else:
                return var_below
        else:
            if var_normal == var_above:
                return 0
            elif var_normal > var_above:
                return 0
            else:
                return var_above

    for lag in config_run.settings['lags']:

        # all months in year 1->12
        for month in range(1, 13):

            if station.state_of_data in [1, 3]:
                for phenomenon in [0, 1, 2]:
                    var_below = station.contingencies_tables_percent[lag][month - 1][phenomenon][0]
                    var_normal = station.contingencies_tables_percent[lag][month - 1][phenomenon][1]
                    var_above = station.contingencies_tables_percent[lag][month - 1][phenomenon][2]

                    p_index = calculate_index()

                    # write new row in file
                    csv_name = globals_vars.maps_files_climate[config_run.settings['analysis_interval']][lag][month - 1][phenomenon]
                    open_file = open(csv_name, 'a')
                    csv_file = csv.writer(open_file, delimiter=globals_vars.OUTPUT_CSV_DELIMITER)
                    csv_file.writerow([station.code, format_out.number(station.lat), format_out.number(station.lon),
                                       format_out.number(station.pearson_list[lag][month - 1]),
                                       format_out.number(var_below), format_out.number(var_normal),
                                       format_out.number(var_above), format_out.number(p_index),
                                       format_out.number(sum([float(var_below),
                                                              float(var_normal),
                                                              float(var_above)]))])
                    open_file.close()
                    del csv_file

            if station.state_of_data in [2, 4]:
                for day in range(len(station.range_analysis_interval)):
                    for phenomenon in [0, 1, 2]:
                        var_below = station.contingencies_tables_percent[lag][month - 1][day][phenomenon][0]
                        var_normal = station.contingencies_tables_percent[lag][month - 1][day][phenomenon][1]
                        var_above = station.contingencies_tables_percent[lag][month - 1][day][phenomenon][2]

                        p_index = calculate_index()

                        # write new row in file
                        csv_name = globals_vars.maps_files_climate[config_run.settings['analysis_interval']][lag][month - 1][day][phenomenon]
                        open_file = open(csv_name, 'a')
                        csv_file = csv.writer(open_file, delimiter=globals_vars.OUTPUT_CSV_DELIMITER)
                        csv_file.writerow([station.code, format_out.number(station.lat), format_out.number(station.lon),
                                           format_out.number(station.pearson_list[lag][month - 1][day]),
                                           format_out.number(var_below), format_out.number(var_normal),
                                           format_out.number(var_above), format_out.number(p_index),
                                           format_out.number(sum([float(var_below),
                                                                  float(var_normal),
                                                                  float(var_above)]))])
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
    if station.state_of_data in [1, 3]:
        forecast_date_formatted = globals_vars.get_trimester_in_text(globals_vars.forecast_date - 1)
    if station.state_of_data in [2, 4]:
        month = globals_vars.forecast_date[0]
        day = globals_vars.forecast_date[1]
        forecast_date_formatted = globals_vars.get_month_in_text(month - 1) + "_" + str(day)

    if forecast_date_formatted not in globals_vars.maps_files_forecast[config_run.settings['analysis_interval']]:

        if station.state_of_data in [1, 3]:
            lags_list = {}
            # define maps data files and directories
            for lag in config_run.settings['lags']:

                maps_dir = os.path.join(globals_vars.FORECAST_DIR, _('maps'),
                    globals_vars.analysis_interval_i18n,
                    globals_vars.get_trimester_in_text(globals_vars.forecast_date - 1))

                if not os.path.isdir(maps_dir):
                    os.makedirs(maps_dir)

                # write the headers in file
                csv_name = os.path.join(maps_dir, _(u'Map_Data_lag_{0}_{1}.csv')
                .format(lag, globals_vars.get_trimester_in_text(globals_vars.forecast_date - 1)))

                if os.path.isfile(csv_name):
                    os.remove(csv_name)

                open_file = open(csv_name, 'w')
                csv_file = csv.writer(open_file, delimiter=globals_vars.OUTPUT_CSV_DELIMITER)
                csv_file.writerow([_('code'), _('lat'), _('lon'),
                                   _('forecast_date'), _('prob_decrease_var_D'),
                                   _('prob_normal_var_D'), _('prob_exceed_var_D'),
                                   _('index'), _('sum')])
                open_file.close()
                del csv_file

                lags_list[lag] = csv_name
            globals_vars.maps_files_forecast[config_run.settings['analysis_interval']][forecast_date_formatted] = lags_list

        if station.state_of_data in [2, 4]:
            lags_list = {}
            # define maps data files and directories
            for lag in config_run.settings['lags']:

                maps_dir = os.path.join(globals_vars.FORECAST_DIR, _('maps'),
                    globals_vars.analysis_interval_i18n,
                    forecast_date_formatted)

                if not os.path.isdir(maps_dir):
                    os.makedirs(maps_dir)

                # write the headers in file
                csv_name = os.path.join(maps_dir, _(u'Map_Data_lag_{0}_{1}.csv')
                .format(lag, forecast_date_formatted))

                if os.path.isfile(csv_name):
                    os.remove(csv_name)

                open_file = open(csv_name, 'w')
                csv_file = csv.writer(open_file, delimiter=globals_vars.OUTPUT_CSV_DELIMITER)
                csv_file.writerow([_('code'), _('lat'), _('lon'),
                                   _('forecast_date'), _('prob_decrease_var_D'),
                                   _('prob_normal_var_D'), _('prob_exceed_var_D'),
                                   _('index'), _('sum')])
                open_file.close()
                del csv_file

                lags_list[lag] = csv_name
            globals_vars.maps_files_forecast[config_run.settings['analysis_interval']][forecast_date_formatted] = lags_list

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

    for lag in config_run.settings['lags']:

        p_index = calculate_index()

        # write new row in file
        csv_name = globals_vars.maps_files_forecast[config_run.settings['analysis_interval']][forecast_date_formatted][lag]
        open_file = open(csv_name, 'a')
        csv_file = csv.writer(open_file, delimiter=globals_vars.OUTPUT_CSV_DELIMITER)
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