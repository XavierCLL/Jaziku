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
from jaziku.modules.climate import result_table
from jaziku.modules.climate.lags import calculate_lags
from jaziku.modules.climate.contingency_table import get_contingency_tables
from jaziku.modules.climate.graphs import climate_graphs
from jaziku.modules.maps.data import climate_data_for_maps
from jaziku.utils import console, output


def pre_process():
    """Show message and prepare directory
    """

    print _("\n\n"
            "################# CLIMATE AND FORECAST PROCESS #################\n"
            "# Climate Module, here are calculated contingency tables,      #\n"
            "# correlations and parametric tests of interest.               #\n"
            "#                                                              #\n"
            "# Modulo forecasts, predictions are calculated here associated #\n"
            "# with the dependent variable as a function of contingency     #\n"
            "# tables and the probability of the independent variable.      #\n"
            "################################################################\n")

    print _("Saving the result for climate in:")
    if env.globals_vars.ARGS.output:
        print "   " + colored.cyan(env.globals_vars.CLIMATE_DIR)
    else:
        print "   " + colored.cyan(os.path.relpath(env.globals_vars.CLIMATE_DIR, os.path.abspath(os.path.dirname(env.globals_vars.ARGS.runfile))))


def process(station):
    """In climate process, it calculate the relationship between the dependent and independent
    variable which is generally determined by the joint probability distribution, but that being
    unknown is replaced by the contingency table. To calculate the contingency table the data
    set of the dependent and independent variable is divided into three categories and are found
    the empirical probabilities from the empirical frequency division and the total number of
    pairs that are obtained. Also is calculated the linear correlation, the statistical chi square and
    Cramer's V and in order that the forecasts thrown by the program are reliable, a
    hygrometric distribution is used to describe the probability distribution among all the
    possible categories of the independent variable.
    """

    # init threshold problem values
    env.globals_vars.threshold_problem = [False]*env.config_run.settings['class_category_analysis']

    # -------------------------------------------------------------------------
    # inform some characteristic to process

    # define if results will made by trimester or every n days
    if env.globals_vars.STATE_OF_DATA in [1, 3] or env.config_run.settings['analysis_interval'] == "trimester":
        console.msg(_("Results will be made by trimesters"), color='cyan')
    else:
        console.msg(_("Results will be made every {} days").format(env.globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL), color='cyan')

    # inform the period to process
    console.msg(_("Period to process: {0}-{1}").format(station.process_period['start'], station.process_period['end']), color='cyan')

    if env.config_run.settings['analog_year']:
        console.msg(_("Will use thresholds with analog year for var_D "), color='cyan')

    # -------------------------------------------------------------------------
    # prepare files

    # console message
    console.msg(_("Processing climate ............................ "), newline=False)

    station.climate_dir \
        = os.path.join(env.globals_vars.CLIMATE_DIR, _('stations'), station.code + '_' + station.name)   # 'results'

    output.make_dirs(station.climate_dir)

    # -------------------------------------------------------------------------
    # process

    calculate_lags(station)

    # size_time_series: is the number o years of the process period
    station.size_time_series = (len(station.common_period) / 12) - 2

    # get all contingency tables for this station
    get_contingency_tables(station)

    result_table.composite_analysis(station)

    if not env.globals_vars.threshold_problem[0] and not env.globals_vars.threshold_problem[1] and\
       not env.globals_vars.threshold_problem[2] and env.config_run.settings['graphics']:
        climate_graphs(station)
    else:
        console.msg(_("\n   continue without make graphics ............. "), color='cyan', newline=False)

    climate_data_for_maps(station)

    console.msg(_("done"), color='green')

    return station
