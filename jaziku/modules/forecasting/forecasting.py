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

import os

from graphs import forecasting_graphs
from jaziku.modules.maps.data import forecasting_data_for_maps
from jaziku.utils import globals_vars
from jaziku.utils import console

def forecasting(station):
    """
    In forecasting process the aim is predict the forecast given a phenomenon phase that
    represents the independent variable, the dependent variable is affected, yielding results in
    terms of decreased, increased or normal trend in its regime.
    """

    # console message
    console.msg(_("Processing forecasting ({0}-{1}) ............ ")
        .format(station.process_period['start'], station.process_period['end']), newline=False)

    # get and set date for calculate forecasting based on this TODO: forecasting_date now is static
    if station.state_of_data in [1, 3]:
        try:
            globals_vars.forecasting_date = int(globals_vars.config_run['forecasting_date'])
        except:
            console.msg_error_line_stations(station,
                _("Trimester forecasting \"{0}\" is invalid, "
                  "must be integer number").format(globals_vars.config_run['forecasting_date']))
        if not (1 <= globals_vars.forecasting_date <= 12):
            console.msg_error_line_stations(station,
                _("Trimester forecasting \"{0}\" is invalid, "
                  "must be a month valid number (1-12)")
                .format(globals_vars.forecasting_date))
    if station.state_of_data in [2, 4]:
        try:
            globals_vars.forecasting_date = globals_vars.config_run['forecasting_date'].replace('-', '/')
            globals_vars.forecasting_date = globals_vars.forecasting_date.split('/')
            globals_vars.forecasting_date[0] = int(globals_vars.forecasting_date[0])
            globals_vars.forecasting_date[1] = int(globals_vars.forecasting_date[1])
        except:
            console.msg_error_line_stations(station,
                _("Month or day for calculate forecasting \"{0}\" is invalid, \n"
                  "must be month/day or month-day (e.g. 03/11)")
                .format(globals_vars.config_run['forecasting_date']))
        if not (1 <= globals_vars.forecasting_date[0] <= 12):
            console.msg_error_line_stations(station,
                _("Month for forecasting process \"{0}\" is invalid, \n"
                  "must be a month valid number (1-12)")
                .format(globals_vars.forecasting_date[0]))
        if globals_vars.forecasting_date[1] not in station.range_analysis_interval:
            console.msg_error_line_stations(station,
                _("Start day (month/day) for forecasting process \"{0}\"\nis invalid, "
                  "must be a valid start day based on\nrange analysis "
                  "interval, the valid start days for\n{1} are: {2}")
                .format(globals_vars.forecasting_date[1], globals_vars.translate_analysis_interval,
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
                       station.is_sig_risk_analysis[lag][globals_vars.forecasting_date - 1][_iter] == _('yes'):
                        items_CT[order_CT[_iter]] \
                            = station.contingencies_tables_percent[lag][globals_vars.forecasting_date - 1][column][row] / 100.0
                        _iter += 1

        if station.state_of_data in [2, 4]:
            month = globals_vars.forecasting_date[0]
            day = station.range_analysis_interval.index(globals_vars.forecasting_date[1])
            _iter = 0
            for column in range(3):
                for row in range(3):
                    if not globals_vars.config_run['risk_analysis'] or\
                       station.is_sig_risk_analysis[lag][month - 1][day][_iter] == _('yes'):
                        items_CT[order_CT[_iter]]\
                            = station.contingencies_tables_percent[lag][month - 1][day][column][row] / 100.0
                        _iter += 1

        prob_decrease_var_D[lag] = (items_CT['a'] * globals_vars.forecasting_phen_below[lag]) +\
                                   (items_CT['d'] * globals_vars.forecasting_phen_normal[lag]) +\
                                   (items_CT['g'] * globals_vars.forecasting_phen_above[lag])

        prob_normal_var_D[lag] = (items_CT['b'] * globals_vars.forecasting_phen_below[lag]) +\
                                 (items_CT['e'] * globals_vars.forecasting_phen_normal[lag]) +\
                                 (items_CT['h'] * globals_vars.forecasting_phen_above[lag])

        prob_exceed_var_D[lag] = (items_CT['c'] * globals_vars.forecasting_phen_below[lag]) +\
                                 (items_CT['f'] * globals_vars.forecasting_phen_normal[lag]) +\
                                 (items_CT['i'] * globals_vars.forecasting_phen_above[lag])

    station.prob_decrease_var_D = prob_decrease_var_D
    station.prob_normal_var_D = prob_normal_var_D
    station.prob_exceed_var_D = prob_exceed_var_D

    if not globals_vars.threshold_problem[0] and not globals_vars.threshold_problem[1] and\
       not globals_vars.threshold_problem[2] and globals_vars.config_run['graphics']:
        forecasting_graphs(station)
    else:
        console.msg(_("\ncontinue without make graphics for forecasting  "), newline=False)

    forecasting_data_for_maps(station)

    console.msg(_("done"), color='green')
