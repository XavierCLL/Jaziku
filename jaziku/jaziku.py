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

SYNOPSIS RUN:
    jaziku [-h] [-doc] -runfile runfile.scv

    for more information of structure of runfile.csv please see the manual.

EXAMPLE:
    jaziku -runfile run_file.csv

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

# internationalization:
import gettext

# import local functions in jaziku/plugins
from modules.station import Station
from i18n import i18n
from utils import globals_vars
from utils import console
from modules.data_analysis import data_analysis
from modules.input import input_arg
from modules.input import input_runfile
from modules.maps import maps
from modules.maps.grid import Grid

# internationalization:
TRANSLATION_DOMAIN = "jaziku"
LOCALE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "i18n")
gettext.bindtextdomain(TRANSLATION_DOMAIN, LOCALE_DIR)
gettext.textdomain(TRANSLATION_DOMAIN)
gettext.install(TRANSLATION_DOMAIN, LOCALE_DIR)


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

    # delete all NULL byte inside the runfile.csv
    runfile = (x.replace('\0', '') for x in globals_vars.args.runfile)

    # open runfile as csv
    globals_vars.run_file = csv.reader(runfile, delimiter=';')

    # read all settings and all stations from runfile
    stations = input_runfile.read_runfile()

    # -------------------------------------------------------------------------
    # Setting language

    settings_language = i18n.set_language(globals_vars.config_run['language'])

    # -------------------------------------------------------------------------
    # Start message

    print _("\n"
            "############################ JAZIKU ############################\n"
            "# Jaziku is a software for the implementation of composite     #\n"
            "# analysis methodology between the major indices of climate    #\n"
            "# variability and major meteorological variables in            #\n"
            "# punctual scale.                                              #\n"
            "#                                                              #\n"
            "# Version {0} - {1}\t                               #\n"
            "# Copyright 2011-2012 IDEAM - Colombia                         #\n"
            "################################################################") \
            .format(globals_vars.VERSION, globals_vars.COMPILE_DATE)

    # -------------------------------------------------------------------------
    # GET/SET SETTINGS

    # set settings default
    settings = {"data_analysis": colored.red(_("disabled")),
                "climate_process": colored.red(_("disabled")),
                "forecasting_process": colored.red(_("disabled")),
                "process_period": colored.red(_("disabled")),
                "analog_year": colored.red(_("disabled")),
                "lags": None,
                "language": settings_language,
                "consistent_data": colored.red(_("disabled")),
                "risk_analysis": colored.red(_("disabled")),
                "graphics": colored.red(_("disabled")),
                "phen_below_label": "-",
                "phen_normal_label": "-",
                "phen_above_label": "-",
                "maps": colored.red(_("disabled")),
                "overlapping": None,
                "shape_boundary": colored.red(_("disabled"))}

    ## general options
    # data_analysis
    if globals_vars.config_run['data_analysis'] == True:
        settings["data_analysis"] = colored.green(_("enabled"))
    elif not globals_vars.config_run['data_analysis'] == False:
        console.msg_error(_("'data_analysis' variable in runfile is wrong,\n"
                            "this should be 'enable' or 'disable'"), False)
    # climate_process
    if globals_vars.config_run['climate_process'] == True:
        settings["climate_process"] = colored.green(_("enabled"))
    elif not globals_vars.config_run['climate_process'] == False:
        console.msg_error(_("'climate_process' variable in runfile is wrong,\n"
                            "this should be 'enable' or 'disable'"), False)
    # forecasting_process
    if globals_vars.config_run['forecasting_process'] == True:
        settings["forecasting_process"] = colored.green(_("enabled"))
    elif not globals_vars.config_run['forecasting_process'] == False:
        console.msg_error(_("'forecasting_process' variable in runfile is wrong,\n"
                            "this should be 'enable' or 'disable'"), False)
    # process_period
    if globals_vars.config_run['process_period'] == "maximum":
        settings["process_period"] = "maximum"
        globals_vars.config_run['process_period'] = False
    else:
        try:
            args_period_start = int(globals_vars.config_run['process_period'].split('-')[0])
            args_period_end = int(globals_vars.config_run['process_period'].split('-')[1])
            globals_vars.config_run['process_period'] = {'start': args_period_start,
                                                         'end': args_period_end}
            settings["process_period"] = colored.green("{0}-{1}".format(args_period_start, args_period_end))
        except Exception, e:
            console.msg_error(_('the period must be: year_start-year_end (ie. 1980-2008)\n'
                                'or \"maximum\" for take the process period maximum possible.\n\n{0}').format(e))
    # analog_year
    if globals_vars.config_run['analog_year']:
        try:
            globals_vars.config_run['analog_year'] = int(globals_vars.config_run['analog_year'])
        except:
            console.msg_error("the analog_year must be a valid year", False)
        settings["analog_year"] = colored.green(globals_vars.config_run['analog_year'])
    # lags
    if globals_vars.config_run['lags'] in ['default', 'all']:
        globals_vars.lags = [0, 1, 2]
        settings["lags"] = ','.join(map(str, globals_vars.lags))
    else:
        try:
            for lag in str(globals_vars.config_run['lags']).split(","):
                lag = int(float(lag))
                if lag not in [0, 1, 2]:
                    raise
                globals_vars.lags.append(lag)
        except:
            console.msg_error(_('the lags are 0, 1 and/or 2 (comma separated), all or default.'), False)
        settings["lags"] = colored.green(','.join(map(str, globals_vars.lags)))

    ## input options
    # type var D
    if globals_vars.config_run['type_var_D']:
        settings["type_var_D"] = colored.green(globals_vars.config_run['type_var_D'])
    # limit var D below
    if globals_vars.config_run['limit_var_D_below'] == 'none':
        settings["limit_var_D_below"] = colored.red('none')
    elif globals_vars.config_run['limit_var_D_below'] == 'default':
        settings["limit_var_D_below"] = _('default')
    else:
        settings["limit_var_D_below"] = colored.green(globals_vars.config_run['limit_var_D_below'])
    # limit var D above
    if globals_vars.config_run['limit_var_D_above'] == 'none':
        settings["limit_var_D_above"] = colored.red('none')
    elif globals_vars.config_run['limit_var_D_above'] == 'default':
        settings["limit_var_D_above"] = _('default')
    else:
        settings["limit_var_D_above"] = colored.green(globals_vars.config_run['limit_var_D_above'])
    # threshold var D
    if globals_vars.config_run['threshold_below_var_D'] == 'default':
        settings["threshold_below_var_D"] = _('default')
    else:
        settings["threshold_below_var_D"] = colored.green(globals_vars.config_run['threshold_below_var_D'])
    if globals_vars.config_run['threshold_above_var_D'] == 'default':
        settings["threshold_above_var_D"] = _('default')
    else:
        settings["threshold_above_var_D"] = colored.green(globals_vars.config_run['threshold_above_var_D'])
    # type var I
    if globals_vars.config_run['type_var_I']:
        settings["type_var_I"] = colored.green(globals_vars.config_run['type_var_I'])
    # limit var I below
    if globals_vars.config_run['limit_var_I_below'] == 'none':
        settings["limit_var_I_below"] = colored.red('none')
    elif globals_vars.config_run['limit_var_I_below'] == 'default':
        settings["limit_var_I_below"] = _('default')
    else:
        settings["limit_var_I_below"] = colored.green(globals_vars.config_run['limit_var_I_below'])
    # limit var I above
    if globals_vars.config_run['limit_var_I_above'] == 'none':
        settings["limit_var_I_above"] = colored.red('none')
    elif globals_vars.config_run['limit_var_I_above'] == 'default':
        settings["limit_var_I_above"] = _('default')
    else:
        settings["limit_var_I_above"] = colored.green(globals_vars.config_run['limit_var_I_above'])
    # threshold var I
    if globals_vars.config_run['threshold_below_var_I'] == 'default':
        settings["threshold_below_var_I"] = _('default')
    else:
        settings["threshold_below_var_I"] = colored.green(globals_vars.config_run['threshold_below_var_I'])
    if globals_vars.config_run['threshold_above_var_I'] == 'default':
        settings["threshold_above_var_I"] = _('default')
    else:
        settings["threshold_above_var_I"] = colored.green(globals_vars.config_run['threshold_above_var_I'])
    ## check options
    # consistent_data
    if globals_vars.config_run['consistent_data']:
        settings["consistent_data"] = colored.green(_("enabled"))
    # risk_analysis
    if globals_vars.config_run['risk_analysis']:
        settings["risk_analysis"] = colored.green(_("enabled"))

    ## graphics settings
    if globals_vars.config_run['graphics']:
        settings["graphics"] = colored.green(_("enabled"))
    # if phenomenon below is defined inside arguments, else default value
    if globals_vars.config_run['phen_below_label'] and globals_vars.config_run['phen_below_label'] != "default":
        globals_vars.phenomenon_below = globals_vars.config_run['phen_below_label']
        settings["phen_below_label"] = colored.green(globals_vars.config_run['phen_below_label'])
    else:
        globals_vars.phenomenon_below = _('var_I_below')
        settings["phen_below_label"] = globals_vars.phenomenon_below
    # if phenomenon normal is defined inside arguments, else default value
    if globals_vars.config_run['phen_normal_label'] and globals_vars.config_run['phen_normal_label'] != "default":
        globals_vars.phenomenon_normal = unicode(globals_vars.config_run['phen_normal_label'], 'utf-8')
        settings["phen_normal_label"] = colored.green(globals_vars.config_run['phen_normal_label'])
    else:
        globals_vars.phenomenon_normal = _('var_I_normal')
        settings["phen_normal_label"] = globals_vars.phenomenon_normal
    # if phenomenon above is defined inside arguments, else default value
    if globals_vars.config_run['phen_above_label'] and globals_vars.config_run['phen_above_label'] != "default":
        globals_vars.phenomenon_above = unicode(globals_vars.config_run['phen_above_label'], 'utf-8')
        settings["phen_above_label"] = colored.green(globals_vars.config_run['phen_above_label'])
    else:
        globals_vars.phenomenon_above = _('var_I_above')
        settings["phen_above_label"] = globals_vars.phenomenon_above

    ## maps settings
    if globals_vars.config_run['maps']:
        if globals_vars.config_run['maps'] == "all":
            globals_vars.maps = {'climate': True, 'forecasting': True, 'correlation': True}
            settings["maps"] = ','.join(map(str, [m for m in globals_vars.maps if globals_vars.maps[m]]))
        else:
            try:
                for map_to_run in globals_vars.config_run['maps'].split(","):
                    map_to_run = map_to_run.strip()
                    if map_to_run not in ['climate', 'forecasting', 'correlation']:
                        raise
                    globals_vars.maps[map_to_run] = True
            except:
                    console.msg_error(_(
                        "the maps options are \'climate\', \'forecasting\', "
                        "\'correlation\' comma separated, or \'all\'."), False)
            settings["maps"] = colored.green(','.join(map(str, [m for m in globals_vars.maps if globals_vars.maps[m]])))
    # set the overlapping solution
    if globals_vars.config_run['overlapping'] == "default" or not globals_vars.config_run['overlapping']:
        globals_vars.config_run['overlapping'] = "average"
        settings['overlapping'] = globals_vars.config_run['overlapping']
    elif globals_vars.config_run['overlapping'] in ["average", "maximum", "minimum", "neither"]:
        settings['overlapping'] = colored.green(globals_vars.config_run['overlapping'])
    else:
        console.msg_error(_("The overlapping solution is wrong, the options are:\n"
                            "default, average, maximum, minimum or neither"), False)
    # shape_boundary method
    # TODO: add more method for cut map interpolation around shape
    if globals_vars.config_run['shape_boundary'] in ["enable", True]:
        settings["shape_boundary"] = colored.green(_("enabled"))
    elif globals_vars.config_run['shape_boundary'] in ["default", False]:
        globals_vars.config_run['shape_boundary'] = False
    else:
        console.msg_error(_("The shape_boundary is wrong, the options are:\n"
                            "disable, enable or default."), False)

    # when climate is disable:
    if not globals_vars.config_run['climate_process']:
        console.msg(_("\nClimate process is disable, then forecasting and maps\n"
                      "process will be disabled."), color="yellow")
        settings["forecasting_process"] = colored.red(_("disabled"))
        settings["maps"] = colored.red(_("disabled"))

    # -------------------------------------------------------------------------
    # PRINT SETTINGS

    print _("\nConfiguration run:")
    console.msg("   General options", color='cyan')
    print "   {0} --------- {1}".format("data analysis", settings["data_analysis"])
    print "   {0} ------- {1}".format("climate process", settings["climate_process"])
    print "   {0} --- {1}".format("forecasting process", settings["forecasting_process"])
    print "   {0} -------- {1}".format("process period", settings["process_period"])
    print "   {0} ----------- {1}".format("analog year", settings["analog_year"])
    print "   {0} ------------------ {1}".format("lags", settings["lags"])
    print "   {0} -------------- {1}".format("language", settings["language"])
    console.msg("   Var D options", color='cyan')
    print "   {0} ------------ {1}".format("type var D", settings["type_var_D"])
    print "   {0} ----- {1}".format("limit var D below", settings["limit_var_D_below"])
    print "   {0} ----- {1}".format("limit var D above", settings["limit_var_D_above"])
    print "   {0} - {1}".format("threshold below var D", settings["threshold_below_var_D"])
    print "   {0} - {1}".format("threshold above var D", settings["threshold_above_var_D"])
    console.msg("   Var I options", color='cyan')
    print "   {0} ------------ {1}".format("type var I", settings["type_var_I"])
    print "   {0} ----- {1}".format("limit var I below", settings["limit_var_I_below"])
    print "   {0} ----- {1}".format("limit var I above", settings["limit_var_I_above"])
    print "   {0} - {1}".format("threshold below var I", settings["threshold_below_var_I"])
    print "   {0} - {1}".format("threshold above var I", settings["threshold_above_var_I"])
    console.msg("   Check options", color='cyan')
    print "   {0} ------- {1}".format("consistent data", settings["consistent_data"])
    print "   {0} --------- {1}".format("risk analysis", settings["risk_analysis"])
    console.msg("   Output options", color='cyan')
    print "   {0} -------------- {1}".format("graphics", settings["graphics"])
    print "   {0} ------ {1}".format("phen below label", settings["phen_below_label"])
    print "   {0} ----- {1}".format("phen normal label", settings["phen_normal_label"])
    print "   {0} ------ {1}".format("phen above label", settings["phen_above_label"])
    console.msg("   Maps options", color='cyan')
    print "   {0} ------------------ {1}".format("maps", settings["maps"])
    if globals_vars.config_run['maps']:
        print "   {0} ----------- {1}".format("overlapping", settings["overlapping"])
        print "   {0} -------- {1}".format("shape boundary", settings["shape_boundary"])


    # -------------------------------------------------------------------------
    # DATA ANALYSIS

    # data analysis dir output result
    if globals_vars.config_run['data_analysis']:

        print _("\n\n"
                "#################### DATA ANALYSIS PROCESS #####################\n"
                "# Data analysis is ........                                    #\n"
                "# Data analysis is ........                                    #\n"
                "################################################################\n")

        # climate dir output result
        globals_vars.data_analysis_dir\
            = os.path.join(os.path.splitext(globals_vars.args.runfile.name)[0], _('Jaziku_Data_Analysis'))   # 'results'

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
                "# Data analysis is ........                                    #\n"
                "# Data analysis is ........                                    #\n"
                "################################################################\n")

    # -------------------------------------------------------------------------
    # PREPARE FILES FOR DATA OF MAPS

    # globals_vars.maps_files_climate

    if globals_vars.config_run['climate_process']:
        # climate dir output result
        globals_vars.climate_dir \
            = os.path.join(os.path.splitext(globals_vars.args.runfile.name)[0], _('Jaziku_Climate'))   # 'results'

        print _("Saving the result for climate in:")
        print "   " + colored.cyan(globals_vars.climate_dir)

        if os.path.isdir(globals_vars.climate_dir):
            console.msg(
                _("\n > WARNING: the output directory for climate process\n"
                  "   is already exist, Jaziku continue but the results\n"
                  "   could be mixed or replaced of old output."), color='yellow')

    # globals_vars.maps_files_forecasting

    if globals_vars.config_run['forecasting_process']:
        # forecasting dir output result
        globals_vars.forecasting_dir \
            = os.path.join(os.path.splitext(globals_vars.args.runfile.name)[0], _('Jaziku_Forecasting'))   # 'results'

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

            # pre_process: read, validated and check datadata
            station.pre_process()

            # process climate and forecasting for this station
            station.process()

        console.msg(gettext.ngettext(
                    "\n{0} station processed.",
                    "\n{0} stations processed.",
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
                "# Data analysis is ........                                    #\n"
                "# Data analysis is ........                                    #\n"
                "################################################################")

        for grid in Grid.all_grids:
            maps.maps(grid)
            del grid

        console.msg(gettext.ngettext(
                    "\n{0} map processed.",
                    "\n{0} maps processed.",
                    Grid.grids_processed).format(Grid.grids_processed), color='green')

    console.msg(_("\nProcess completed!"), color='green')

    print _("Good bye :)\n")

    # clear all variables and exit
    #sys.modules[__name__].__dict__.clear()
    sys.exit()

# Run main() when call jaziku.py
if __name__ == "__main__":
    main()
