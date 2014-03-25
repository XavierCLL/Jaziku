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
from datetime import date

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
            station.var_D.read_data_from_file()
            station.var_I.read_data_from_file()
        console.msg(_("done"), color='green')

        # show some information of variables
        console.msg(_("   var_D ({0}):").format(env.var_D.TYPE_SERIES), newline=False)
        console.msg(_("has data {0}").format(env.var_D.FREQUENCY_DATA), color='cyan')

        console.msg(_("   var_I ({0}):").format(env.var_I.TYPE_SERIES), newline=False)
        console.msg(_("has data {0}").format(env.var_I.FREQUENCY_DATA), color='cyan')

        # show thresholds tu use
        console.msg(_("Thresholds to use (for {0} categories):").format(env.config_run.settings['class_category_analysis']))

        console.msg(_("   var_D ({0}):").format(env.var_D.TYPE_SERIES), newline=False)

        thresholds_D = env.var_D.get_global_thresholds()
        if isinstance(thresholds_D, list):
            console.msg(' | '.join([str(thr) for thr in thresholds_D]), color='cyan')

        console.msg(_("   var_I ({0}):").format(env.var_I.TYPE_SERIES), newline=False)

        thresholds_I = env.var_I.get_global_thresholds()
        if isinstance(thresholds_I, list):
            console.msg(' | '.join([str(thr) for thr in thresholds_I]), color='cyan')

        # common and process period
        console.msg(_("Calculate common and process period for each stations ... "), newline=False)
        for station in stations_list:
            station.calculate_common_and_process_period()
        console.msg(_("done"), color='green')

        # global common period
        console.msg(_("Calculate, check and set the global process period ...... "), newline=False)
        calculate_process_period(stations_list)
        console.msg(_("done"), color='green')
        # show the period calculated if is defined as maximum
        if not env.config_run.settings['process_period']:
            console.msg(_("   The maximum global common period is:"), newline=False)
            console.msg("{0}-{1}".format(env.globals_vars.PROCESS_PERIOD['start'],
                                          env.globals_vars.PROCESS_PERIOD['end']), color='cyan')

        # data, date and null
        console.msg(_("Prepare data, date and null in process period ........... "), newline=False)
        for station in stations_list:
            station.var_D.calculate_data_date_and_nulls_in_period()
            station.var_I.calculate_data_date_and_nulls_in_period()
        console.msg(_("done"), color='green')

        # check the consistent data for all stations
        if env.config_run.settings['consistent_data'] is not False:
            console.msg(_("Check if the data are consistent for var_D and var_I:"))
            for station in stations_list:
                validation.check_consistent_data(station)

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
                station.var_D.calculate_data_date_and_nulls_in_period()
                station.var_I.calculate_data_date_and_nulls_in_period()
            console.msg(_("done"), color='green')


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


def global_process_period(stations_list):
    """Calculate the maximum global common period of all stations
    based on all common process period of all series

    :arg:
        stations: list of all stations
    :return:
        'start': start year of global process period
        'end': end year of global process period
    """
    firsts = True
    for station in stations_list:
        if firsts:
            global_common_date = set(station.var_D.date) & set(station.var_I.date)
            firsts = False
        else:
            global_common_date = global_common_date & set(station.var_D.date) & set(station.var_I.date)

    global_common_date = list(global_common_date)
    global_common_date.sort()

    # if there aren't not common dates for all stations, return false
    if not global_common_date:
        return False

    start_year = global_common_date[0].year + 1
    end_year = global_common_date[-1].year - 1

    return {'start': start_year,
             'end': end_year}


def calculate_process_period(stations_list):
    """Check and set the process period, this is the
    maximum global common period or the particular period
    but this inside the maximum global common period

    :arg:
        stations: list of all stations
    :return by reference:
        env.globals_vars.PROCESS_PERIOD:
            'start': start year of process period
            'end': end year of process period
    """

    # calculate the maximum global common period
    max_global_period = global_process_period(stations_list)

    if max_global_period is False:
        console.msg_error(_(
                    "There is no a global common period for all stations,\n"
                    "this mean that two or more stations don't have any\n"
                    "data for a common date. Please check the data of\n"
                    "stations."))

    # if the period was defined in runfile
    if env.config_run.settings['process_period']:
        # check if the period defined are inside the global period
        if not (env.config_run.settings['process_period']['start'] >= max_global_period['start'] and
                env.config_run.settings['process_period']['end'] <= max_global_period['end']):
                console.msg_error(_(
                    "The period defined in argument {0}-{1} is outside in the\n"
                    "maximum global common period possible {2}-{3}.")
                .format(env.config_run.settings['process_period']['start'],
                    env.config_run.settings['process_period']['end'],
                    max_global_period['start'], max_global_period['end']))

        # set the process_period
        env.globals_vars.PROCESS_PERIOD = \
            {'start': env.config_run.settings['process_period']['start'],
             'end': env.config_run.settings['process_period']['end']}

        # check if the common period at least 3 years before calculate the process period
        if (env.globals_vars.PROCESS_PERIOD['end'] - env.globals_vars.PROCESS_PERIOD['start']) < 3:
            console.msg_error(_("The process period {0}-{1} has less than 3 years,\n"
                                "Jaziku need at least 3 years for run.")
                .format(env.globals_vars.PROCESS_PERIOD['start'], env.globals_vars.PROCESS_PERIOD['end']))

    # if the period is the maximum global period (maximum in runfile)
    else:
        # set the process_period
        env.globals_vars.PROCESS_PERIOD = \
            {'start': max_global_period['start'],
             'end': max_global_period['end']}

        # check if the common period at least 3 years before calculate the process period
        if (env.globals_vars.PROCESS_PERIOD['end'] - env.globals_vars.PROCESS_PERIOD['start']) < 3:
            console.msg_error(_("The maximum global common period possible of intersection\n"
                                "for all stations and {0} time series is {1}-{2},\n"
                                "Jaziku need at least 3 years for run, please check the\n"
                                "data of stations.")
                .format(env.var_I.TYPE_SERIES, env.globals_vars.PROCESS_PERIOD['start'], env.globals_vars.PROCESS_PERIOD['end']))
