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
import sys

import result_table
from lags import calculate_lags
from contingency_table import contingency_table
from graphs import climate_graphs
from ..maps.data import climate_data_for_maps
from ...utils import globals_vars
from ...utils import console

def climate(station):
    """
    Main process for climate
    """

    # console message
    sys.stdout.write(_("Processing climate ({0}-{1}) ................ ")
        .format(station.process_period['start'], station.process_period['end']))
    sys.stdout.flush()

    # create directory for output files
    if not os.path.isdir(globals_vars.climate_dir):
        os.makedirs(globals_vars.climate_dir)

    station.climate_dir \
        = os.path.join(globals_vars.climate_dir, station.code + '_' + station.name)   # 'results'
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
        sys.stdout.write(_("\ncontinue without make graphics for climate .... "))
        sys.stdout.flush()

    climate_data_for_maps(station)

    console.msg(_("done"), color='green')

    return station
