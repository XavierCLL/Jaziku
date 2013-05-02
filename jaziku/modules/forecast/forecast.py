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
from numpy import matrix
from clint.textui import colored

from jaziku import env
from jaziku.core.analysis_interval import get_range_analysis_interval
from jaziku.modules.forecast.graphs import forecast_graphs
from jaziku.modules.maps.data import forecast_data_for_maps
from jaziku.utils import console, output


def pre_process():
    """Show message and prepare directory
    """

    # directory for the forecast results
    env.globals_vars.FORECAST_DIR \
        = os.path.join(env.globals_vars.OUTPUT_DIR, _('Jaziku_Forecast'))   # 'results'

    print _("\nSaving the result for forecast in:").format(env.globals_vars.FORECAST_DIR)
    if env.globals_vars.ARGS.output:
        print "   " + colored.cyan(env.globals_vars.FORECAST_DIR)
    else:
        print "   " + colored.cyan(os.path.relpath(env.globals_vars.FORECAST_DIR, os.path.abspath(os.path.dirname(env.globals_vars.ARGS.runfile))))

    # reset forecast_var_I_lag_N
    if env.config_run.settings['class_category_analysis'] == 3:
        for lag in env.globals_vars.ALL_LAGS:

            env.globals_vars.probability_forecast_values[lag] = {}
            for idx, tag in enumerate(['below', 'normal', 'above']):
                env.globals_vars.probability_forecast_values[lag][tag] \
                    = env.config_run.settings['forecast_var_I_lag_'+str(lag)][idx]

    if env.config_run.settings['class_category_analysis'] == 7:
        for lag in env.globals_vars.ALL_LAGS:

            env.globals_vars.probability_forecast_values[lag] = {}
            for idx, tag in enumerate(['below3', 'below2','below1', 'normal', 'above1', 'above2', 'above3']):
                env.globals_vars.probability_forecast_values[lag][tag] \
                    = env.config_run.settings['forecast_var_I_lag_'+str(lag)][idx]

            if env.globals_vars.forecast_contingency_table['type'] == '3x7':
                for tag in ['below3', 'below2', 'below1']:
                    if env.globals_vars.probability_forecast_values[lag][tag] != '':
                        env.globals_vars.probability_forecast_values[lag]['below'] = tag
                    else:
                        del env.globals_vars.probability_forecast_values[lag][tag]
                for tag in ['above3', 'above2', 'above1']:
                    if env.globals_vars.probability_forecast_values[lag][tag] != '':
                        env.globals_vars.probability_forecast_values[lag]['above'] = tag
                    else:
                        del env.globals_vars.probability_forecast_values[lag][tag]


def process(station):
    """In forecast process the aim is predict the forecast given a phenomenon phase that
    represents the independent variable, the dependent variable is affected, yielding results in
    terms of decreased, increased or normal trend in its regime.

    Return by reference:

    :ivar STATION.prob_var_D[lag][tag]: probabilities of var D
    """

    # console message
    console.msg(_("Processing forecast:"))

    console.msg(_("   making forecast for date: ")+env.config_run.settings['forecast_date']['text'], color="cyan", newline=False)

    station.forecast_dir = os.path.join(env.globals_vars.FORECAST_DIR, _('stations'), station.code + '_' + station.name)   # 'results'

    output.make_dirs(station.forecast_dir)

    prob_var_D = {}

    for lag in env.config_run.settings['lags']:

        prob_var_D[lag] = {}

        # get the contingency table for this lag and the specific forecast date set in runfile,
        # if 'risk_analysis' is enabled, check first if the value for the forecast date is significant
        # else put zero value
        if env.globals_vars.STATE_OF_DATA in [1, 3]:
            CT_for_forecast_date = station.contingency_tables[lag][env.config_run.settings['forecast_date']['month'] - 1]['in_percentage']

            # TODO 0.6 error?
            #console.msg_error(_("There aren't enough values in the categories of the contingency\n"
            #                    "table for to do forecast results.\n"))

        if env.globals_vars.STATE_OF_DATA in [2, 4]:
            month = env.config_run.settings['forecast_date']['month']
            day = get_range_analysis_interval().index(env.config_run.settings['forecast_date']['day'])
            CT_for_forecast_date = station.contingency_tables[lag][month - 1][day]['in_percentage']

        # convert from percentage to 0-1
        CT_for_forecast_date = (matrix(CT_for_forecast_date)/100.0).tolist()

        # when there are 3 categories
        if env.globals_vars.forecast_contingency_table['type'] == '3x3':
            for idx_varD, tag in enumerate(['below', 'normal', 'above']):
                prob_var_D[lag][tag] = \
                    (CT_for_forecast_date[0][idx_varD] * env.globals_vars.probability_forecast_values[lag]['below']) +\
                    (CT_for_forecast_date[1][idx_varD] * env.globals_vars.probability_forecast_values[lag]['normal']) +\
                    (CT_for_forecast_date[2][idx_varD] * env.globals_vars.probability_forecast_values[lag]['above'])

        # when there are 7 categories but only 3 values for the categories in forecast options
        if env.globals_vars.forecast_contingency_table['type'] == '3x7':
            tags = ['below3', 'below2','below1', 'normal', 'above1', 'above2', 'above3']
            forecast_position_selected_below = env.globals_vars.probability_forecast_values[lag]['below']
            forecast_var_I_selected_below = env.globals_vars.probability_forecast_values[lag][forecast_position_selected_below]

            forecast_var_I_selected_normal = env.globals_vars.probability_forecast_values[lag]['normal']

            forecast_position_selected_above = env.globals_vars.probability_forecast_values[lag]['above']
            forecast_var_I_selected_above = env.globals_vars.probability_forecast_values[lag][forecast_position_selected_above]

            for idx_varD, tag in enumerate(['below3', 'below2','below1', 'normal', 'above1', 'above2', 'above3']):
                prob_var_D[lag][tag] = \
                    (CT_for_forecast_date[tags.index(forecast_position_selected_below)][idx_varD] * forecast_var_I_selected_below) +\
                    (CT_for_forecast_date[3][idx_varD] * forecast_var_I_selected_normal) +\
                    (CT_for_forecast_date[tags.index(forecast_position_selected_above)][idx_varD] * forecast_var_I_selected_above)

        # when there are 7 categories and 7 values for the categories in forecast options
        if env.globals_vars.forecast_contingency_table['type'] == '7x7':
            for idx_varD, tag in enumerate(['below3', 'below2','below1', 'normal', 'above1', 'above2', 'above3']):
                prob_var_D[lag][tag] = \
                    (CT_for_forecast_date[0][idx_varD] * env.globals_vars.probability_forecast_values[lag]['below3']) +\
                    (CT_for_forecast_date[1][idx_varD] * env.globals_vars.probability_forecast_values[lag]['below2']) +\
                    (CT_for_forecast_date[2][idx_varD] * env.globals_vars.probability_forecast_values[lag]['below1']) +\
                    (CT_for_forecast_date[3][idx_varD] * env.globals_vars.probability_forecast_values[lag]['normal']) +\
                    (CT_for_forecast_date[4][idx_varD] * env.globals_vars.probability_forecast_values[lag]['above1']) +\
                    (CT_for_forecast_date[5][idx_varD] * env.globals_vars.probability_forecast_values[lag]['above2']) +\
                    (CT_for_forecast_date[6][idx_varD] * env.globals_vars.probability_forecast_values[lag]['above3'])

    station.prob_var_D = prob_var_D

    #station.prob_decrease_var_D = prob_below_var_D #TODO 0.6: replace
    #station.prob_normal_var_D = prob_normal_var_D
    #station.prob_exceed_var_D = prob_above_var_D

    if not env.globals_vars.threshold_problem[0] and not env.globals_vars.threshold_problem[1] and\
       not env.globals_vars.threshold_problem[2] and env.config_run.settings['graphics']:
        with console.redirectStdStreams():
            forecast_graphs(station)
    else:
        console.msg(_("\n   continue without make graphics ............. "), color='cyan', newline=False)

    forecast_data_for_maps(station)

    console.msg(_("done"), color='green')
