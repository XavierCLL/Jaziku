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
from clint.textui import colored

from jaziku import env
from jaziku.modules.forecast.graphs import forecast_graphs
from jaziku.modules.maps.data import forecast_data_for_maps
from jaziku.utils import console


def pre_process():
    # directory for the forecast results
    env.globals_vars.FORECAST_DIR\
    = os.path.join(env.globals_vars.WORK_DIR, _('Jaziku_Forecast'))   # 'results'

    print _("\nSaving the result for forecast in:").format(env.globals_vars.FORECAST_DIR)
    print "   " + colored.cyan(os.path.relpath(env.globals_vars.FORECAST_DIR, os.path.abspath(os.path.dirname(env.globals_vars.ARGS.runfile))))

    if os.path.isdir(env.globals_vars.FORECAST_DIR):
        console.msg(
            _("\n > WARNING: the output directory for forecast process\n"
              "   is already exist, Jaziku continue but the results\n"
              "   could be mixed or replaced of old output."), color='yellow')

    # reset forecast_var_I_lag_N
    if env.config_run.settings['class_category_analysis'] == 3:
        for lag in ['0','1','2']:
            env.config_run.settings['forecast_var_I_lag_'+lag] \
                = {'below':env.config_run.settings['forecast_var_I_lag_'+lag][0],
                   'normal':env.config_run.settings['forecast_var_I_lag_'+lag][1],
                   'above':env.config_run.settings['forecast_var_I_lag_'+lag][2]}

    if env.config_run.settings['class_category_analysis'] == 7:
        for lag in ['0','1','2']:
            env.config_run.settings['forecast_var_I_lag_'+lag] \
                = [None if value == '' else value for value in env.config_run.settings['forecast_var_I_lag_'+lag]]
            env.config_run.settings['forecast_var_I_lag_'+lag] \
                = {'below3':env.config_run.settings['forecast_var_I_lag_'+lag][0],
                   'below2':env.config_run.settings['forecast_var_I_lag_'+lag][1],
                   'below1':env.config_run.settings['forecast_var_I_lag_'+lag][2],
                   'normal':env.config_run.settings['forecast_var_I_lag_'+lag][3],
                   'above1':env.config_run.settings['forecast_var_I_lag_'+lag][4],
                   'above2':env.config_run.settings['forecast_var_I_lag_'+lag][5],
                   'above3':env.config_run.settings['forecast_var_I_lag_'+lag][6]}

def process(station):
    """
    In forecast process the aim is predict the forecast given a phenomenon phase that
    represents the independent variable, the dependent variable is affected, yielding results in
    terms of decreased, increased or normal trend in its regime.
    """

    # console message
    console.msg(_("Processing forecast:"))

    console.msg(_("   making forecast for date: ")+env.config_run.settings['forecast_date']['text'], color="cyan", newline=False)

    # TODO: replace all instances of station.range_analysis_interval

    # create directory for output files
    if not os.path.isdir(env.globals_vars.FORECAST_DIR):
        os.makedirs(env.globals_vars.FORECAST_DIR)

    station.forecast_dir = os.path.join(env.globals_vars.FORECAST_DIR, _('stations'), station.code + '_' + station.name)   # 'results'
    if not os.path.isdir(station.forecast_dir):
        os.makedirs(station.forecast_dir)

    prob_decrease_var_D = {}
    prob_normal_var_D = {}
    prob_exceed_var_D = {}

    for lag in env.config_run.settings['lags']:

        items_CT = {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'f': 0, 'g': 0, 'h': 0, 'i': 0}
        order_CT = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']

        if env.globals_vars.STATE_OF_DATA in [1, 3]:
            _iter = 0
            for column in range(3):
                for row in range(3):
                    if not env.config_run.settings['risk_analysis'] or\
                       station.is_sig_risk_analysis[lag][env.config_run.settings['forecast_date']['month'] - 1][_iter] == _('yes'):
                        items_CT[order_CT[_iter]] \
                            = station.contingency_tables[lag][env.config_run.settings['forecast_date']['month'] - 1]['in_percentage'][column][row] / 100.0
                        _iter += 1

        if env.globals_vars.STATE_OF_DATA in [2, 4]:
            month = env.config_run.settings['forecast_date']['month']
            day = station.range_analysis_interval.index(env.config_run.settings['forecast_date']['day'])
            _iter = 0
            for column in range(3):
                for row in range(3):
                    if not env.config_run.settings['risk_analysis'] or\
                       station.is_sig_risk_analysis[lag][month - 1][day][_iter] == _('yes'):
                        items_CT[order_CT[_iter]]\
                            = station.contingency_tables[lag][month - 1][day]['in_percentage'][column][row] / 100.0
                        _iter += 1

        prob_decrease_var_D[lag] = (items_CT['a'] * env.config_run.settings['forecast_var_I_lag_'+lag]['below']) +\
                                   (items_CT['d'] * env.config_run.settings['forecast_var_I_lag_'+lag]['normal']) +\
                                   (items_CT['g'] * env.config_run.settings['forecast_var_I_lag_'+lag]['above'])

        prob_normal_var_D[lag] = (items_CT['b'] * env.config_run.settings['forecast_var_I_lag_'+lag]['below']) +\
                                 (items_CT['e'] * env.config_run.settings['forecast_var_I_lag_'+lag]['normal']) +\
                                 (items_CT['h'] * env.config_run.settings['forecast_var_I_lag_'+lag]['above'])

        prob_exceed_var_D[lag] = (items_CT['c'] * env.config_run.settings['forecast_var_I_lag_'+lag]['below']) +\
                                 (items_CT['f'] * env.config_run.settings['forecast_var_I_lag_'+lag]['normal']) +\
                                 (items_CT['i'] * env.config_run.settings['forecast_var_I_lag_'+lag]['above'])

    station.prob_decrease_var_D = prob_decrease_var_D
    station.prob_normal_var_D = prob_normal_var_D
    station.prob_exceed_var_D = prob_exceed_var_D

    if not env.globals_vars.threshold_problem[0] and not env.globals_vars.threshold_problem[1] and\
       not env.globals_vars.threshold_problem[2] and env.config_run.settings['graphics']:
        with console.redirectStdStreams():
            forecast_graphs(station)
    else:
        console.msg(_("\n   continue without make graphics ............. "), color='cyan', newline=False)

    forecast_data_for_maps(station)

    console.msg(_("done"), color='green')
