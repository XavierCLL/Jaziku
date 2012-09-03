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
# Developers:
# Ines Sánchez Rodriguez < incsanchezro (a) gmail.com >
# Xavier Corredor Llano < xcorredorl (a) ideam.gov.co >
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
import locale

# import local functions in jaziku/plugins
from station import Station
from i18n import i18n
from utils import globals_vars
from utils import console
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
    global args
    args = input_arg.arguments.parse_args()

    # -------------------------------------------------------------------------
    # reading configuration run, list of grids and stations from runfile

    run_file = csv.reader(args.runfile, delimiter=';')

    stations = input_runfile.read_runfile(run_file)

    # -------------------------------------------------------------------------
    # Setting language

    settings_language = i18n.set_language(globals_vars.config_run['language'])

    # -------------------------------------------------------------------------
    # Start message

    print _("\n############################ JAZIKU ############################\n"
            "## Jaziku is a software for the implementation of composite   ##\n"
            "## analysis methodology between the major indices of climate  ##\n"
            "## variability and major meteorological variables in          ##\n"
            "## punctual scale.                                            ##\n"
            "##                                                            ##\n"
            "## Version {0} - {1}\t                              ##\n"
            "## Copyright 2011-2012 IDEAM - Colombia                       ##\n"
            "################################################################") \
            .format(globals_vars.VERSION, globals_vars.COMPILE_DATE)

    # -------------------------------------------------------------------------
    # get/set and show settings

    # set settings default
    global settings
    settings = {"climate_process": _("disabled"),
                "forecasting_process": _("disabled"),
                "process_period": _("disabled"),
                "analog_year": _("disabled"),
                "lags": None,
                "language": settings_language,
                "consistent_data": _("disabled"),
                "risk_analysis": _("disabled"),
                "graphics": _("disabled"),
                "phen_below_label": "-",
                "phen_normal_label": "-",
                "phen_above_label": "-",
                "maps": _("disabled"),
                "overlapping": None,
                "shape_boundary": _("disabled")}

    ## general options
    # climate_process
    if globals_vars.config_run['climate_process']:
        settings["climate_process"] = colored.green(_("enabled"))
    # forecasting_process
    if globals_vars.config_run['forecasting_process']:
        settings["forecasting_process"] = colored.green(_("enabled"))
    # process_period
    if globals_vars.config_run['process_period']:
        try:
            args_period_start = int(globals_vars.config_run['process_period'].split('-')[0])
            args_period_end = int(globals_vars.config_run['process_period'].split('-')[1])
            globals_vars.config_run['process_period'] = {'start': args_period_start,
                                                         'end': args_period_end}
            settings["process_period"] = colored.green("{0}-{1}".format(args_period_start, args_period_end))
        except Exception, e:
            console.msg_error(_('the period must be: year_start-year_end (ie. 1980-2008)\n\n{0}').format(e))
    # analog_year
    if globals_vars.config_run['analog_year']:
        try:
            globals_vars.config_run['analog_year'] = int(globals_vars.config_run['analog_year'])
        except:
            console.msg_error("the analog_year must be a valid year", False)
        settings["analog_year"] = colored.green(globals_vars.config_run['analog_year'])
    # lags
    if globals_vars.config_run['lags']:
        if globals_vars.config_run['lags'] == "default":
            globals_vars.lags = [0, 1, 2]
            settings["lags"] = ','.join(map(str, globals_vars.lags))
        else:
            try:
                for lag in globals_vars.config_run['lags'].split(","):
                    lag = int(lag)
                    if lag not in [0, 1, 2]:
                        raise
                    globals_vars.lags.append(lag)
            except:
                console.msg_error(_('the lags are 0, 1 and/or 2 comma separated, or default.'), False)
            settings["lags"] = colored.green(','.join(map(str, globals_vars.lags)))

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

    # print settings
    print _("\nConfiguration run:")
    console.msg(("   General options"), color='cyan')
    print "   {0} ------ {1}".format("climate process", settings["climate_process"])
    print "   {0} -- {1}".format("forecasting process", settings["forecasting_process"])
    print "   {0} ------- {1}".format("process period", settings["process_period"])
    print "   {0} ---------- {1}".format("analog year", settings["analog_year"])
    print "   {0} ----------------- {1}".format("lags", settings["lags"])
    print "   {0} ------------- {1}".format("language", settings["language"])
    console.msg(("   Check options"), color='cyan')
    print "   {0} ------ {1}".format("consistent data", settings["consistent_data"])
    print "   {0} -------- {1}".format("risk analysis", settings["risk_analysis"])
    console.msg(("   Output options"), color='cyan')
    print "   {0} ------------- {1}".format("graphics", settings["graphics"])
    print "   {0} ----- {1}".format("phen below label", settings["phen_below_label"])
    print "   {0} ---- {1}".format("phen normal label", settings["phen_normal_label"])
    print "   {0} ----- {1}".format("phen above label", settings["phen_above_label"])
    console.msg(("   Maps options"), color='cyan')
    print "   {0} ----------------- {1}".format("maps", settings["maps"])
    if globals_vars.config_run['maps']:
        print "   {0} ---------- {1}".format("overlapping", settings["overlapping"])
        print "   {0} ------- {1}".format("shape boundary", settings["shape_boundary"])

    # -------------------------------------------------------------------------
    # globals_vars.maps_files_climate

    if globals_vars.config_run['climate_process']:
        # climate dir output result
        globals_vars.climate_dir \
            = os.path.join(os.path.splitext(args.runfile.name)[0], _('Jaziku_Climate'))   # 'results'

        print _("\nSaving the result for climate in:")
        print "   " + colored.cyan(globals_vars.climate_dir)

        if os.path.isdir(globals_vars.climate_dir):
            console.msg(
                _("\n > WARNING: the output director for climate process\n"
                  "   is already exist, Jaziku continue but the results\n"
                  "   could be mixed or replaced of old output."), color='yellow')

    # -------------------------------------------------------------------------
    # globals_vars.maps_files_forecasting

    if globals_vars.config_run['forecasting_process']:
        # forecasting dir output result
        globals_vars.forecasting_dir \
            = os.path.join(os.path.splitext(args.runfile.name)[0], _('Jaziku_Forecasting'))   # 'results'

        print _("\nSaving the result for forecasting in:").format(globals_vars.forecasting_dir)
        print "   " + colored.cyan(globals_vars.forecasting_dir)

        if os.path.isdir(globals_vars.forecasting_dir):
            console.msg(
                _("\n > WARNING: the output director for forecasting process\n"
                  "   is already exist, Jaziku continue but the results\n"
                  "   could be mixed or replaced of old output."), color='yellow')


    # -------------------------------------------------------------------------
    # process each station from stations list

    for line_station, line_num in stations:

        # trim all items in line_station
        line_station = [i.strip() for i in line_station]

        # if line of station is null o empty, e.g. empty but with tabs or spaces
        if not line_station or not line_station[0].strip() or line_station[0].strip()[0] == "#":
            continue

        # new instance of station
        station = Station()

        try:
            station.code = line_station[0]
            station.name = line_station[1]
            station.lat = line_station[2].replace(',', '.')
            station.lon = line_station[3].replace(',', '.')

            # if climate_process is activated
            if globals_vars.config_run['climate_process']:
                if len(line_station) < 17:
                        raise Exception(_("Problems with the numbers of parameters inside\n"
                                          "the stations list need for run climate process.\n"))

                station.file_D = open(line_station[4], 'rb')
                station.type_D = line_station[5]
                globals_vars.type_var_D = station.type_D  # TODO:

                station.range_below_D = line_station[6]
                station.range_above_D = line_station[7]

                station.threshold_below_var_D = line_station[8].replace(',', '.')
                station.threshold_above_var_D = line_station[9].replace(',', '.')

                station.file_I = line_station[10]
                station.type_I = line_station[11]
                globals_vars.type_var_I = station.type_I  # TODO:

                station.range_below_I = line_station[12]
                station.range_above_I = line_station[13]

                station.threshold_below_var_I = line_station[14].replace(',', '.')
                station.threshold_above_var_I = line_station[15].replace(',', '.')

                station.analysis_interval = line_station[16]

                if station.analysis_interval not in globals_vars.options_analysis_interval:
                    raise Exception(_("The analysis interval {0} is invalid,\n"
                                      "should be one of these: {1}")
                                      .format(station.analysis_interval,
                                              ', '.join(globals_vars.options_analysis_interval)))

                if station.analysis_interval != "trimester":
                    # detect analysis_interval number from string
                    _count = 0
                    for digit in station.analysis_interval:
                        try:
                            int(digit)
                            _count += 1
                        except:
                            pass
                    station.analysis_interval_num_days = int(station.analysis_interval[0:_count])

                station.translate_analysis_interval \
                    = globals_vars.translate_analysis_interval[globals_vars.options_analysis_interval.index(station.analysis_interval)]

            # if forecasting_process is activated
            if globals_vars.config_run['forecasting_process']:
                if len(line_station) < 27:
                    raise Exception(_("For forecasting process you need define "
                                      "9 probability\n variables and trimester to "
                                      "process in stations file."))
                station.f_var_I_B = [float(line_station[17].replace(',', '.')),
                                     float(line_station[20].replace(',', '.')),
                                     float(line_station[23].replace(',', '.'))]
                station.f_var_I_N = [float(line_station[18].replace(',', '.')),
                                     float(line_station[21].replace(',', '.')),
                                     float(line_station[24].replace(',', '.'))]
                station.f_var_I_A = [float(line_station[19].replace(',', '.')),
                                     float(line_station[22].replace(',', '.')),
                                     float(line_station[25].replace(',', '.'))]

                station.forecasting_date = line_station[26]

        except Exception, e:
            console.msg_error(_("Reading stations from file \"{0}\" in line {1}:\n")
                        .format(args.runfile.name, line_num) +
                        ';'.join(line_station) + "\n\n" + str(e), False)

        station.line_station = line_station
        station.line_num = line_num

        # console message
        print _("\n################# STATION: {0} ({1})").format(station.name, station.code)

        # run pre_process: read, validated and check data
        station.pre_process()

        # run process:
        station.process()

        # delete instance
        del station

        # force run garbage collector memory
        gc.collect()

    console.msg(gettext.ngettext(
                "\n{0} station processed.",
                "\n{0} stations processed.",
                Station.stations_processed).format(Station.stations_processed), color='green')

    # -------------------------------------------------------------------------
    # MAPS

    # process to create maps
    if globals_vars.config_run['maps']:

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
    sys.modules[__name__].__dict__.clear()
    sys.exit()

# Run main() when call jaziku.py
if __name__ == "__main__":
    main()
