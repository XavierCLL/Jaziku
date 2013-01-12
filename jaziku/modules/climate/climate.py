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
import sys

import result_table
from lags import calculate_lags
from contingency_table import contingency_table
from graphs import climate_graphs
from jaziku.modules.maps.data import climate_data_for_maps
from jaziku.utils import globals_vars
from jaziku.utils import console

def climate(station):
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

    # console message
    console.msg(_("Processing climate ............................ "), newline=False)

    # create directory for output files
    if not os.path.isdir(globals_vars.climate_dir):
        os.makedirs(globals_vars.climate_dir)

    station.climate_dir \
        = os.path.join(globals_vars.climate_dir, _('stations'), station.code + '_' + station.name)   # 'results'
    if not os.path.isdir(station.climate_dir):
        os.makedirs(station.climate_dir)

    calculate_lags(station)

    station.size_time_series = (len(station.common_period) / 12) - 2

    contingency_table(station)

    result_table.composite_analysis(station)

    if not globals_vars.threshold_problem[0] and not globals_vars.threshold_problem[1] and\
       not globals_vars.threshold_problem[2] and globals_vars.config_run['graphics']:
        climate_graphs(station)
    else:
        console.msg(_("\n   continue without make graphics ............. "), color='cyan', newline=False)

    climate_data_for_maps(station)

    console.msg(_("done"), color='green')

    return station
