#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2011-2012 IDEAM
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

from graphs import forecasting_graphs
from ..maps.data import forecasting_data_for_maps
from ...utils import globals_vars
from ...utils import console

def forecasting(station):
    """
    Main process for forecasting
    """

    # console message
    sys.stdout.write(_("Processing forecasting ({0}-{1}) ............ ")
    .format(station.process_period['start'], station.process_period['end']))
    sys.stdout.flush()

    # get and set date for calculate forecasting based on this
    if station.state_of_data in [1, 3]:
        try:
            station.forecasting_date = int(station.forecasting_date)
        except:
            console.msg_error_line_stations(station,
                _("Trimester forecasting \"{0}\" is invalid, "
                  "should be integer number").format(station.forecasting_date))
        if not (1 <= station.forecasting_date <= 12):
            console.msg_error_line_stations(station,
                _("Trimester forecasting \"{0}\" is invalid, "
                  "should be a month valid number (1-12)")
                .format(station.forecasting_date))
    if station.state_of_data in [2, 4]:
        try:
            forecasting_date_original = station.forecasting_date
            station.forecasting_date = station.forecasting_date.replace('-', '/')
            station.forecasting_date = station.forecasting_date.split('/')
            station.forecasting_date[0] = int(station.forecasting_date[0])
            station.forecasting_date[1] = int(station.forecasting_date[1])
        except:
            console.msg_error_line_stations(station,
                _("Month or day for calculate forecasting \"{0}\" is invalid, \n"
                  "should be month/day or month-day (e.g. 03/11)")
                .format(forecasting_date_original))
        if not (1 <= station.forecasting_date[0] <= 12):
            console.msg_error_line_stations(station,
                _("Month for forecasting process \"{0}\" is invalid, \n"
                  "should be a month valid number (1-12)")
                .format(station.forecasting_date[0]))
        if station.forecasting_date[1] not in station.range_analysis_interval:
            console.msg_error_line_stations(station,
                _("Start day (month/day) for forecasting process \"{0}\"\nis invalid, "
                  "should be a valid start day based on\nrange analysis "
                  "interval, the valid start days for\n{1} are: {2}")
                .format(station.forecasting_date[1], station.translate_analysis_interval,
                    station.range_analysis_interval))

    # create directory for output files
    if not os.path.isdir(globals_vars.forecasting_dir):
        os.makedirs(globals_vars.forecasting_dir)

    station.forecasting_dir = os.path.join(globals_vars.forecasting_dir, station.code + '_' + station.name)   # 'results'
    if not os.path.isdir(station.forecasting_dir):
        os.makedirs(station.forecasting_dir)

    prob_decrease_var_D = {}
    prob_normal_var_D = {}
    prob_exceed_var_D = {}

    for lag in globals_vars.lags:

        items_CT = {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'f': 0, 'g': 0, 'h': 0, 'i': 0}
        order_CT = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']

        if station.state_of_data in [1, 3]:
            _iter = 0
            for column in range(3):
                for row in range(3):
                    if not globals_vars.config_run['risk_analysis'] or\
                       station.is_sig_risk_analysis[lag][station.forecasting_date - 1][_iter] == _('yes'):
                        items_CT[order_CT[_iter]] \
                            = station.contingencies_tables_percent[lag][station.forecasting_date - 1][column][row] / 100.0
                        _iter += 1

        if station.state_of_data in [2, 4]:
            month = station.forecasting_date[0]
            day = station.range_analysis_interval.index(station.forecasting_date[1])
            _iter = 0
            for column in range(3):
                for row in range(3):
                    if not globals_vars.config_run['risk_analysis'] or\
                       station.is_sig_risk_analysis[lag][month - 1][day][_iter] == _('yes'):
                        items_CT[order_CT[_iter]]\
                            = station.contingencies_tables_percent[lag][month - 1][day][column][row] / 100.0
                        _iter += 1

        prob_decrease_var_D[lag] = (items_CT['a'] * station.f_var_I_B[lag]) +\
                                   (items_CT['d'] * station.f_var_I_N[lag]) +\
                                   (items_CT['g'] * station.f_var_I_A[lag])

        prob_normal_var_D[lag] = (items_CT['b'] * station.f_var_I_B[lag]) +\
                                 (items_CT['e'] * station.f_var_I_N[lag]) +\
                                 (items_CT['h'] * station.f_var_I_A[lag])

        prob_exceed_var_D[lag] = (items_CT['c'] * station.f_var_I_B[lag]) +\
                                 (items_CT['f'] * station.f_var_I_N[lag]) +\
                                 (items_CT['i'] * station.f_var_I_A[lag])

    station.prob_decrease_var_D = prob_decrease_var_D
    station.prob_normal_var_D = prob_normal_var_D
    station.prob_exceed_var_D = prob_exceed_var_D

    if not globals_vars.threshold_problem[0] and not globals_vars.threshold_problem[1] and\
       not globals_vars.threshold_problem[2] and globals_vars.config_run['graphics']:
        forecasting_graphs(station)
    else:
        sys.stdout.write(_("\ncontinue without make graphics for forecasting  "))
        sys.stdout.flush()

    forecasting_data_for_maps(station)

    console.msg(_("done"), color='green')
