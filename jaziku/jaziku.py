#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#==============================================================================
# Copyright © 2011-2012 IDEAM
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
#       Xavier Corredor Llano < xcorredorl (a) ideam.gov.co >
#   Roadmap, technical/theoretical support, tester, doc-user:
#       Ines Sánchez Rodriguez < incsanchezro (a) gmail.com >
#==============================================================================

doc = '''
PROGRAM:
    Jaziku

ABOUT NAME:
    Jaziku is a word in huitoto mean jungle, forest.

DEVELOPERS:
    Ines Sánchez Rodriguez < incsanchezro (a) gmail.com >
    Xavier Corredor Llano < xcorredorl (a) ideam.gov.co >

DESCRIPTION:
    Jaziku is a software for the implementation of composite analysis
    metodology between the major indices of climate variability and major
    meteorological variables in puntual scale.

    According to IDEAM’s commitment to promote and guide scientiﬁc research
    about weather forecasting and climate, "Jazikü" is a program designed to
    evaluate teleconnections between meteorological variables with the main
    indices of climate variability affecting climate in Colombia.

    Jaziku, follows the composite methodology analysis proposed by The
    University Corporation for Atmospheric Research (UCAR)), National Oceanic
    and Atmospheric Administration (NOAA) & U.S. Department of Commerce
    (DOC)[1][1, 2][1, 2, 3][1, 2, 3] and can produce probability scenarios
    under which it is expected precipitation or any other variable for speciﬁc
    sites or areas interpolated to behave, as a function of the probability
    values predicted for each climate variability and the history of
    involvement in the quarterly average level. Such scenarios become a
    powerful tool for decision making by the national meteorological services

    [1] National Oceanic and Atmospheric Administration (NOAA) , University
    Corporation for Atmospheric Research (UCAR)). Creating a Local Climate
    Product Using Composite Analysis - Print Version of Webcast -(En Linea).
    1997-2010:COMET Website at http://meted.ucar.edu/, 1997.
    [2] A. Leetmaa Barnston, A. G. NCEP Forecasts of the El Niño of 1997 1998
    and Its U.S. Impacts. Bull. Amer. Met. Soc, 80:1829 – 1852, 1999.
    [3] M. B. Richman Montroy, D.L. Observed Nonlinearities of Monthly
    Teleconnections between Tropical Paciﬁc Sea Surface Temperature Anomalies
    and Central and Eastern North American Precipitation. Journal of Climate,
    11:1812 – 1835, 1998.

Copyright © 2011-2012 IDEAM
Instituto de Hidrología, Meteorología y Estudios Ambientales
Carrera 10 No. 20-30
Bogotá, Colombia
'''

#==============================================================================
# IMPORTS

import sys
import gc
import os.path
import csv
#from pylab import *
from clint.textui import colored

# internationalization and init languages variable "_()"
import gettext
from i18n import i18n

# local import
from utils import console
from utils import settings_run
from utils import globals_vars
from modules.station import Station
from modules.data_analysis import data_analysis
from modules.input import input_arg
from modules.input import input_runfile
from modules.maps import maps
from modules.maps.grid import Grid
from modules.maps.maps import check_basic_requirements_for_maps


#==============================================================================
# MAIN PROCESS


def main():
    """
    Main process of Jaziku
    """

    # check python version
    if sys.version_info[0] != 2 or sys.version_info[1] < 6:
        console.msg_error(_("You version of python is {0}, please use Jaziku with "
                      "python v2.6 or v2.7").format(sys.version_info[0:2]), False)

    # set encoding to utf-8
    reload(sys)
    sys.setdefaultencoding("utf-8")

    #set the root directory where jaziku was installed
    globals_vars.ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

    # Parser and check arguments
    globals_vars.args = input_arg.arguments.parse_args()

    # -------------------------------------------------------------------------
    # READ RUNFILE
    # reading configuration run, list of grids and stations from runfile

    # path to runfile
    globals_vars.runfile_path = os.path.join(globals_vars.args.runfile)

    # test if runfile exist
    if not os.path.isfile(globals_vars.runfile_path):
        console.msg_error(_("[runfile] no such file or directory: {0}".format(globals_vars.runfile_path)),False)

    runfile_open = open(globals_vars.runfile_path, 'rb')

    # delete all NULL byte inside the runfile.csv
    runfile = (x.replace('\0', '') for x in runfile_open)

    # open runfile as csv
    globals_vars.runfile = csv.reader(runfile, delimiter=';')

    # read all settings and all stations from runfile
    stations = input_runfile.read_runfile()

    # -------------------------------------------------------------------------
    # Setting language

    globals_vars.config_run['language'] = i18n.set_language(globals_vars.config_run['language'])

    # -------------------------------------------------------------------------
    # Start message

    print _("\n"
            "############################ JAZIKU ############################\n"
            "#           Jaziku is statistical inference software           #\n"
            "#               for the teleconnections analysis.              #\n"
            "#                                                              #\n"
            "#                 Version {0} - {1}\t               #\n"
            "#           Copyright (C) 2011-2012 IDEAM - Colombia           #\n"
            "################################################################")\
    .format(globals_vars.VERSION, globals_vars.COMPILE_DATE)

    # -------------------------------------------------------------------------
    # GET/SET SETTINGS

    globals_vars.settings = settings_run.get()

    # -------------------------------------------------------------------------
    # PRINT AND CHECK SETTINGS, AND CONTINUE

    settings_run.check()

    settings_run.show()

    settings_run.check_station_list(stations)

    settings_run.continue_run()


    # -------------------------------------------------------------------------
    # DATA ANALYSIS

    if globals_vars.config_run['data_analysis']:
        print _("\n\n"
                "#################### DATA ANALYSIS PROCESS #####################\n"
                "# Data analysis module, here is verified linearity, outliers   #\n"
                "# are reported and the primary statistical time series.        #\n"
                "################################################################\n")

        # data analysis dir output result
        globals_vars.data_analysis_dir\
            = os.path.join(os.path.splitext(globals_vars.runfile_path)[0], _('Jaziku_Data_Analysis'))   # 'results'

        print _("Saving the result for data analysis in:")
        print "   " + colored.cyan(globals_vars.data_analysis_dir)

        if os.path.isdir(globals_vars.data_analysis_dir):
            console.msg(
                _("\n > WARNING: the output directory for data analysis process\n"
                  "   is already exist, Jaziku continue but the results\n"
                  "   could be mixed or replaced of old output."), color='yellow')

        # main process for data analysis
        data_analysis.main(stations)


    # -------------------------------------------------------------------------
    # CLIMATE AND FORECASTING PRE-PROCESS

    if globals_vars.config_run['climate_process']:

        print _("\n\n"
                "############### CLIMATE AND FORECASTING PROCESS ################\n"
                "# Climate Module, here are calculated contingency tables,      #\n"
                "# correlations and parametric tests of interest.               #\n"
                "#                                                              #\n"
                "# Modulo forecasts, predictions are calculated here associated #\n"
                "# with the dependent variable as a function of contingency     #\n"
                "# tables and the probability of the independent variable.      #\n"
                "################################################################\n")

    # climate
    if globals_vars.config_run['climate_process']:
        # climate dir output result
        globals_vars.climate_dir \
            = os.path.join(os.path.splitext(globals_vars.runfile_path)[0], _('Jaziku_Climate'))   # 'results'

        print _("Saving the result for climate in:")
        print "   " + colored.cyan(globals_vars.climate_dir)

        if os.path.isdir(globals_vars.climate_dir):
            console.msg(
                _("\n > WARNING: the output directory for climate process\n"
                  "   is already exist, Jaziku continue but the results\n"
                  "   could be mixed or replaced of old output."), color='yellow')

    # forecasting
    if globals_vars.config_run['forecasting_process']:
        # forecasting dir output result
        globals_vars.forecasting_dir \
            = os.path.join(os.path.splitext(globals_vars.runfile_path)[0], _('Jaziku_Forecasting'))   # 'results'

        print _("\nSaving the result for forecasting in:").format(globals_vars.forecasting_dir)
        print "   " + colored.cyan(globals_vars.forecasting_dir)

        if os.path.isdir(globals_vars.forecasting_dir):
            console.msg(
                _("\n > WARNING: the output directory for forecasting process\n"
                  "   is already exist, Jaziku continue but the results\n"
                  "   could be mixed or replaced of old output."), color='yellow')

    # -------------------------------------------------------------------------
    # CLIMATE AND FORECASTING MAIN PROCESS

    if globals_vars.config_run['climate_process']:
        # process each station from stations list
        for station in stations:

            # console message
            print _("\n################# STATION: {0} ({1})").format(station.name, station.code)

            # pre_process: read, validated and check data
            station.pre_process()

            # process climate and forecasting for this station
            station.process()

        console.msg(gettext.ngettext(
                    _("\n{0} station processed."),
                    _("\n{0} stations processed."),
                    Station.stations_processed).format(Station.stations_processed), color='green')

    # delete instance of stations for clean memory
    del stations
    # force run garbage collector memory
    gc.collect()


    # -------------------------------------------------------------------------
    # MAPS PROCESS

    # process to create maps
    if globals_vars.config_run['maps']:

        print _("\n\n"
                "######################### MAPS PROCESS #########################\n"
                "# Map Process, here is made the Kriging interpolation on the   #\n"
                "# results of historical scenarios and forecasts most probable  #\n"
                "# of the dependent variable, also interpolation of linear      #\n"
                "# correlations.                                                #\n"
                "################################################################")

        # first check requirements
        check_basic_requirements_for_maps()

        for grid in Grid.all_grids:
            # process all maps for this grid
            maps.maps(grid)

        for grid in Grid.all_grids:
            console.msg(gettext.ngettext(
                        _("\n{0} map created for {1}"),
                        _("\n{0} maps created for {1}"),
                        Grid.maps_created_in_grid).format(Grid.maps_created_in_grid, grid.grid_fullname), color='green')

    console.msg(_("\nProcess completed!"), color='green')

    print _("Good bye :)")

    console.msg_footer()

    # clear all variables and exit
    #sys.modules[__name__].__dict__.clear()
    sys.exit()

# Run main() when call jaziku.py
if __name__ == "__main__":
    main()
