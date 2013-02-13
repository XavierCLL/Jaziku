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

from jaziku.env import globals_vars, config_run
from jaziku.modules.climate import result_table
from jaziku.modules.climate.lags import calculate_lags
from jaziku.modules.climate.contingency_table import contingency_table
from jaziku.modules.climate.graphs import climate_graphs
from jaziku.modules.maps.data import climate_data_for_maps
from jaziku.utils import console


def pre_process():

    print _("\n\n"
            "############### CLIMATE AND FORECAST PROCESS ################\n"
            "# Climate Module, here are calculated contingency tables,      #\n"
            "# correlations and parametric tests of interest.               #\n"
            "#                                                              #\n"
            "# Modulo forecasts, predictions are calculated here associated #\n"
            "# with the dependent variable as a function of contingency     #\n"
            "# tables and the probability of the independent variable.      #\n"
            "################################################################\n")

    # climate dir output result
    globals_vars.CLIMATE_DIR\
        = os.path.join(globals_vars.WORK_DIR, _('Jaziku_Climate'))   # 'results'

    print _("Saving the result for climate in:")
    print "   " + colored.cyan(os.path.relpath(globals_vars.CLIMATE_DIR, os.path.abspath(os.path.dirname(globals_vars.ARGS.runfile))))

    if os.path.isdir(globals_vars.CLIMATE_DIR):
        console.msg(
            _("\n > WARNING: the output directory for climate process\n"
              "   is already exist, Jaziku continue but the results\n"
              "   could be mixed or replaced of old output."), color='yellow')

def process(station):
    """
    In climate process, it calculate the relationship between the dependent and independent
    variable which is generally determined by the joint probability distribution, but that being
    unknown is replaced by the contingency table. To calculate the contingency table the data
    set of the dependent and independent variable is divided into three categories and are found
    the empirical probabilities from the empirical frequency division and the total number of
    pairs that are obtained. Also is calculated the linear correlation, the statistical chi square and
    Cramer's V and in order that the forecasts thrown by the program are reliable, a
    hygrometric distribution is used to describe the probability distribution among all the
    possible categories of the independent variable.
    """

    # restore threshold problem values
    globals_vars.threshold_problem = [False, False, False]

    # -------------------------------------------------------------------------
    # inform some characteristic to process

    # define if results will made by trimester or every n days
    if globals_vars.STATE_OF_DATA in [1, 3] or config_run.settings['analysis_interval'] == "trimester":
        console.msg(_("Results will be made by trimesters"), color='cyan')
    else:
        console.msg(_("Results will be made every {} days").format(globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL), color='cyan')

    # inform the period to process
    console.msg(_("Period to process: {0}-{1}").format(station.process_period['start'], station.process_period['end']), color='cyan')

    # -------------------------------------------------------------------------
    # prepare files

    # console message
    console.msg(_("Processing climate ............................ "), newline=False)

    # create directory for output files
    if not os.path.isdir(globals_vars.CLIMATE_DIR):
        os.makedirs(globals_vars.CLIMATE_DIR)

    station.climate_dir \
        = os.path.join(globals_vars.CLIMATE_DIR, _('stations'), station.code + '_' + station.name)   # 'results'
    if not os.path.isdir(station.climate_dir):
        os.makedirs(station.climate_dir)

    # -------------------------------------------------------------------------
    # process

    calculate_lags(station)

    station.size_time_series = (len(station.common_period) / 12) - 2

    contingency_table(station)

    result_table.composite_analysis(station)

    if not globals_vars.threshold_problem[0] and not globals_vars.threshold_problem[1] and\
       not globals_vars.threshold_problem[2] and config_run.settings['graphics']:
        climate_graphs(station)
    else:
        console.msg(_("\n   continue without make graphics ............. "), color='cyan', newline=False)

    climate_data_for_maps(station)

    console.msg(_("done"), color='green')

    return station
