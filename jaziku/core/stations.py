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

from jaziku.env import config_run
from jaziku.core import analysis_interval
from jaziku.core.station import Station
from jaziku.core.input import input_check
from jaziku.utils import console


def prepare_all_stations(stations_list):

    print _("\n\n"
            "################# PREPARE DATA OF ALL STATIONS #################\n")

    # Read vars
    console.msg(_("\nReading var D and var I of all stations .............. "), newline=False)
    for station in stations_list:
        station.var_D.read_data_from_file(station, process=True, messages=False)
        station.var_I.read_data_from_file(station, process=True, messages=False)
    console.msg(_("done"), color='green')

    # common and process period
    console.msg(_("\nCalculate common and process period for each stations ... "), newline=False)
    for station in stations_list:
        station.calculate_common_and_process_period()
    console.msg(_("done"), color='green')

    # data, date and null
    console.msg(_("\Prepare data, date and null in process period ......... "), newline=False)
    for station in stations_list:
        station.var_D.data_and_null_in_process_period(station)
        station.var_I.data_and_null_in_process_period(station)
    console.msg(_("done"), color='green')

    if config_run.settings['consistent_data']:
        console.msg(_("Check if the data are consistent for var D and I"))
        for station in stations_list:
            input_check.check_consistent_data(station)

    # statistics for data analysis
    if config_run.settings['data_analysis']:
        console.msg(_("\nStatistics of data for data analysis module ............... "), newline=False)
        for station in stations_list:
            station.var_D.do_some_statistic_of_data()
            station.var_I.do_some_statistic_of_data()
        console.msg(_("done"), color='green')

    # state of data
    console.msg(_("\nSet global state of data ............................. "), newline=False)
    analysis_interval.set_global_state_of_data(stations_list)
    console.msg(_("done"), color='green')

    # analysis interval
    console.msg(_("\nCheck analysis interval ............................. "), newline=False)
    analysis_interval.check_analysis_interval()
    console.msg(_("done"), color='green')


    console.msg(_("done"), color='green')
    console.msg(gettext.ngettext(
        _("   {0} station prepared."),
        _("   {0} stations prepared."),
        Station.stations_processed).format(Station.stations_processed), color='cyan')
    console.msg('')
