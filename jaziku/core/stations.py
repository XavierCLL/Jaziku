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

import gettext

from jaziku import env
from jaziku.core import analysis_interval
from jaziku.core.station import Station
from jaziku.core.input import validation
from jaziku.utils import console


def prepare_all_stations(stations_list, prepare_data_for_data_analysis, prepare_data_for_climate_forecast):


    if prepare_data_for_data_analysis:
        print _("\n\n"
                "############ PREPARE ALL STATIONS FOR DATA ANALYSIS ############\n")

    if prepare_data_for_climate_forecast:
        print _("\n\n"
                "####### PREPARE ALL STATIONS FOR CLIMATE/FORECAST PROCESS ######\n")

    if prepare_data_for_data_analysis or \
      (prepare_data_for_climate_forecast and not env.config_run.settings['data_analysis']):

        # Read vars
        console.msg(_("Reading var D and var I of all stations ................. "), newline=False)
        for station in stations_list:
            station.var_D.read_data_from_file(station)
            station.var_I.read_data_from_file(station)
        console.msg(_("done"), color='green')

        # show some information of variables
        console.msg(_("   var_D ({0}):").format(env.var_D.TYPE_SERIES), newline=False)
        if env.var_D.is_daily():
            console.msg(_("has data daily").format(env.var_D.TYPE_SERIES), color='cyan')
        else:
            console.msg(_("has data monthly").format(env.var_D.TYPE_SERIES), color='cyan')

        console.msg(_("   var_I ({0}):").format(env.var_I.TYPE_SERIES), newline=False)
        if env.var_I.is_daily():
            console.msg(_("has data daily").format(env.var_I.TYPE_SERIES), color='cyan')
        else:
            console.msg(_("has data monthly").format(env.var_I.TYPE_SERIES), color='cyan')

        # show thresholds tu use
        console.msg(_("Thresholds to use (for {0} categories):").format(env.config_run.settings['class_category_analysis']))

        console.msg(_("   var_D ({0}):").format(env.var_D.TYPE_SERIES), newline=False)
        if env.config_run.settings['thresholds_var_D'] == 'default':
            thresholds_D = env.var_D.get_default_thresholds()
        else:
            thresholds_D = env.config_run.settings['thresholds_var_D']
        if isinstance(thresholds_D, list):
            console.msg(' | '.join([str(thr) for thr in thresholds_D]), color='cyan')

        console.msg(_("   var_I ({0}):").format(env.var_I.TYPE_SERIES), newline=False)
        if env.config_run.settings['thresholds_var_I'] == 'default':
            thresholds_I = env.var_I.get_default_thresholds()
        else:
            thresholds_I = env.config_run.settings['thresholds_var_I']
        if isinstance(thresholds_I, list):
            console.msg(' | '.join([str(thr) for thr in thresholds_I]), color='cyan')

        # common and process period
        console.msg(_("Calculate common and process period for each stations ... "), newline=False)
        for station in stations_list:
            station.calculate_common_and_process_period()
        console.msg(_("done"), color='green')

        # data, date and null
        console.msg(_("Prepare data, date and null in process period ........... "), newline=False)
        for station in stations_list:
            station.var_D.data_and_null_in_process_period(station)
            station.var_I.data_and_null_in_process_period(station)
        console.msg(_("done"), color='green')

        if env.config_run.settings['consistent_data'] is not False:
            console.msg(_("Check if the data are consistent for var_D and var_I:"))
            for station in stations_list:
                validation.check_consistent_data(station)

        # state of data
        console.msg(_("Set state of data ....................................... "), newline=False)
        env.globals_vars.STATE_OF_DATA = analysis_interval.get_state_of_data()
        console.msg(_("done"), color='green')

        # analysis interval
        console.msg(_("Check analysis interval ................................. "), newline=False)
        analysis_interval.check_analysis_interval()
        console.msg(_("done"), color='green')


    if prepare_data_for_climate_forecast:
        # when var D is monthly and var I is daily, only can process with data monthly,
        # then, Jaziku need convert var I of all stations to data monthly
        console.msg(_("Adjust data of all variables if is needed:"))
        is_data_adjusted = analysis_interval.adjust_data_of_variables(stations_list)
        if not is_data_adjusted:
            console.msg(_("   data not need to be adjusted"), color='cyan')

        if is_data_adjusted:
            # common and process period
            console.msg(_("Re-calculate common and process period for each stations  "), newline=False)
            for station in stations_list:
                station.calculate_common_and_process_period()
            console.msg(_("done"), color='green')

            # data, date and null
            console.msg(_("Re-prepare data, date and null in process period ........ "), newline=False)
            for station in stations_list:
                station.var_D.data_and_null_in_process_period(station)
                station.var_I.data_and_null_in_process_period(station)
            console.msg(_("done"), color='green')

    if prepare_data_for_data_analysis:

        # statistics for data analysis
        console.msg(_("Statistics of data for data analysis module ............. "), newline=False)
        for station in stations_list:
            station.var_D.do_some_statistic_of_data()
            station.var_I.do_some_statistic_of_data()
        console.msg(_("done"), color='green')

    console.msg('')
    console.msg(gettext.ngettext(
        _("{0} station prepared."),
        _("{0} stations prepared."),
        Station.stations_processed).format(Station.stations_processed), color='cyan')