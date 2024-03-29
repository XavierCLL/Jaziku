#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==============================================================================
# Copyright © 2011-2017 Xavier Corredor Ll. - IDEAM
# Instituto de Hidrología, Meteorología y Estudios Ambientales
# Carrera 10 No. 20-30
# Bogotá, Colombia
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Team:
#   Developer:
#       Xavier Corredor Llano < xcorredorl(a)ideam.gov.co >
#   Roadmap, technical-theoretical support, tester and product
#   verification, doc-user and manual:
#       Ines Sánchez Rodriguez < icsanchez(a)ideam.gov.co >
# ==============================================================================

# ==============================================================================
# IMPORTS

import sys
import gc
import os.path
from matplotlib import use

# internationalization and init languages variable "_()"
import gettext
from jaziku.i18n import i18n

# jaziku imports
from jaziku import env
from jaziku.core import settings
from jaziku.core import stations
from jaziku.core.input import runfile, arg
from jaziku.core.station import Station
from jaziku.modules.climate import climate
from jaziku.modules.forecast import forecast
from jaziku.modules.data_analysis import data_analysis
from jaziku.modules.maps import maps
from jaziku.utils import console, output


# ==============================================================================
# MAIN PROCESS


def main(arg_runfile=False, arg_force=False, arg_output=False):
    """
    Main process of Jaziku
    """

    # check python version
    if sys.version_info[0] != 3:
        console.msg_error(_("You version of python is {0}, please use Jaziku with "
                            "python 3").format(sys.version_info[0:2]), False)

    # initialize matplotlib backend in raster graphics (png)
    try:
        use("AGG", force=True)
    except TypeError:
        use("AGG")  # for old version of matplotlib

    # set the root directory where jaziku was installed
    env.globals_vars.JAZIKU_DIR = os.path.dirname(os.path.realpath(__file__))

    # Parser and check arguments
    if not arg_runfile:
        env.globals_vars.ARGS = arg.arguments.parse_args()
        env.globals_vars.arg_runfile = env.globals_vars.ARGS.runfile
        env.globals_vars.arg_force = env.globals_vars.ARGS.force
        env.globals_vars.arg_output = env.globals_vars.ARGS.output
    else:
        env.globals_vars.arg_runfile = arg_runfile
        env.globals_vars.arg_force = arg_force
        env.globals_vars.arg_output = arg_output

    # -------------------------------------------------------------------------
    # Initialize all settings variables in None

    env.config_run.init()

    # -------------------------------------------------------------------------
    # READ RUNFILE
    # reading configuration run, list of grids and stations from runfile

    # test if runfile exist
    if not os.path.isfile(env.globals_vars.arg_runfile):
        console.msg_error(_("[runfile] no such file or directory: {0}".format(env.globals_vars.arg_runfile)), False)

    # read all settings and all stations from runfile
    stations_list = runfile.read_runfile()

    # -------------------------------------------------------------------------
    # Setting language

    i18n.set_language(env.config_run.settings['language'])

    # -------------------------------------------------------------------------
    # Start message

    print(_("\n"
            "############################ JAZIKU ############################\n"
            "#           Jaziku is statistical inference software           #\n"
            "#               for the teleconnections analysis.              #\n"
            "#                                                              #\n"
            "#                 Version {0} - {1}\t               #\n"
            "#           Copyright (C) 2011-2018 Xavier Corredor Ll. - IDEAM - Colombia           #\n"
            "################################################################") \
        .format(env.globals_vars.VERSION, env.globals_vars.VERSION_DATE))

    # -------------------------------------------------------------------------
    # GET/SET AND CHECK SETTINGS TO RUN

    settings.main(stations_list)

    # -------------------------------------------------------------------------
    # DEFINED OUTPUT DIRECTORY FOR SAVE RESULTS

    if env.globals_vars.arg_output:
        # absolute directory to save all results defined in arguments
        env.globals_vars.OUTPUT_DIR = os.path.abspath(env.globals_vars.arg_output)
    else:
        # absolute directory to save all results,
        # this is absolute directory where is the runfile + filename of runfile
        env.globals_vars.OUTPUT_DIR = os.path.abspath(os.path.splitext(env.globals_vars.arg_runfile)[0])

    # -------------------------------------------------------------------------
    # PREPARE ALL OUTPUT DIRECTORIES FOR SAVE RESULTS

    output.prepare_dirs()

    # -------------------------------------------------------------------------
    # DATA ANALYSIS

    if env.config_run.settings['data_analysis']:
        # PRE-PROCESS: prepare data for all stations for data analysis process
        stations.prepare_all_stations(stations_list,
                                      prepare_data_for_data_analysis=True,
                                      prepare_data_for_climate_forecast=False)

        # main process for data analysis
        data_analysis.main(stations_list)


    # -------------------------------------------------------------------------
    # CLIMATE AND FORECAST PRE-PROCESS

    # climate
    if env.config_run.settings['climate_process']:
        # PRE-PROCESS: prepare data for all stations for climate (and forecast) process
        stations.prepare_all_stations(stations_list,
                                      prepare_data_for_data_analysis=False,
                                      prepare_data_for_climate_forecast=True)

        climate.pre_process()

    # forecast
    if env.config_run.settings['forecast_process']:
        forecast.pre_process()

    # -------------------------------------------------------------------------
    # CLIMATE AND FORECAST MAIN PROCESS

    if env.config_run.settings['climate_process']:
        # process each station from stations list
        for station in stations_list:

            # console message
            print(_("\n################# STATION: {0} ({1})").format(station.name, station.code))

            ## process climate and forecast for this station
            # run climate process
            if env.config_run.settings['climate_process']:
                climate.process(station)

            # run forecast process
            if env.config_run.settings['forecast_process']:
                # TODO: run forecast without climate¿?
                forecast.process(station)

        console.msg(gettext.ngettext(
            _("\n{0} station processed."),
            _("\n{0} stations processed."),
            Station.stations_processed).format(Station.stations_processed), color='green')

    # delete instance of stations for clean memory
    del stations_list
    # force run garbage collector memory
    gc.collect()


    # -------------------------------------------------------------------------
    # MAPS PROCESS

    # process to create maps
    if env.config_run.settings['maps']:

        # first check requirements
        maps.pre_process()

        for grid in maps.Grid.all_grids:
            # process all maps for this grid
            maps.process(grid)

        for grid in maps.Grid.all_grids:
            console.msg(gettext.ngettext(
                _("\n{0} map created for {1}"),
                _("\n{0} maps created for {1}"),
                maps.Grid.maps_created_in_grid).format(maps.Grid.maps_created_in_grid, grid.grid_fullname),
                        color='green')

    console.msg(_("\nProcess completed!"), color='green')

    print(_("Good bye :)"))

    console.msg_footer()

    # clear all variables and exit
    # sys.modules[__name__].__dict__.clear()
    # sys.exit()


# Run main() when call jaziku.py
if __name__ == "__main__":
    main()
