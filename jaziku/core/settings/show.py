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

from jaziku import env
from jaziku.utils import console


def configuration_run(stop_in=None):

    # load input settings saved
    settings = env.globals_vars.input_settings

    if stop_in != None:
        settings[stop_in] = '?'

    print _("\nConfiguration run:")

    console.msg("  Modules:", color='cyan')
    print "   {0} ------------- {1}".format("data analysis", settings["data_analysis"])
    if stop_in == "data_analysis": return
    print "   {0} ----------- {1}".format("climate process", settings["climate_process"])
    if stop_in == "climate_process": return
    print "   {0} ---------- {1}".format("forecast process", settings["forecast_process"])
    if stop_in == "forecast_process": return

    console.msg("  General options:", color='cyan')
    print "   {0} --------- {1}".format("analysis interval", settings["analysis_interval"])
    if stop_in == "analysis_interval": return
    print "   {0} --- {1}".format("class category analysis", settings["class_category_analysis"])
    if stop_in == "class_category_analysis": return
    print "   {0} ------------ {1}".format("process period", settings["process_period"])
    if stop_in == "process_period": return
    print "   {0} --------------- {1}".format("analog year", settings["analog_year"])
    if stop_in == "analog_year": return
    print "   {0} ---------------------- {1}".format("lags", settings["lags"])
    if stop_in == "lags": return
    print "   {0} ------------------ {1}".format("language", settings["language"])
    if stop_in == "language": return

    console.msg("  Check options:", color='cyan')
    print "   {0} ----------- {1}".format("consistent data", settings["consistent_data"])
    if stop_in == "consistent_data": return
    print "   {0} ------------- {1}".format("risk analysis", settings["risk_analysis"])
    if stop_in == "risk_analysis": return

    console.msg("  Output options:", color='cyan')
    print "   {0} ------------------ {1}".format("graphics", settings["graphics"])
    if stop_in == "graphics": return
    print "   {0} ---------------------- {1}".format("maps", settings["maps"])
    if stop_in == "maps": return
    if stop_in == "var_I_category_labels": return
    for x, label in enumerate(settings["var_I_category_labels"]):
        if x == 0:
            print "   {0} ----- {1}".format("var I category labels", label)
        else:
            print "                             {0}".format(label)
    if stop_in == "var_I_category_labels": return

    console.msg("  Var D options:", color='cyan')
    print "   {0} ---------------- {1}".format("type var D", settings["type_var_D"])
    if stop_in == "type_var_D": return
    print "   {0} - {1}".format("calculation mode series D", settings["calculation_mode_series_D"])
    if stop_in == "calculation_mode_series_D": return
    print "   {0} -------------- {1}".format("limits var D", settings["limits_var_D"])
    if stop_in == "limits_var_D": return
    print "   {0} ---------- {1}".format("thresholds var D", settings["thresholds_var_D"])
    if stop_in == "thresholds_var_D": return

    console.msg("  Var I options:", color='cyan')
    print "   {0} ---------------- {1}".format("type var I", settings["type_var_I"])
    if stop_in == "type_var_I": return
    print "   {0} - {1}".format("calculation mode series I", settings["calculation_mode_series_I"])
    if stop_in == "calculation_mode_series_I": return
    print "   {0} -------- {1}".format("path to file var I", settings["path_to_file_var_I"])
    if stop_in == "path_to_file_var_I": return
    print "   {0} -------------- {1}".format("limits var I", settings["limits_var_I"])
    if stop_in == "limits_var_I": return
    print "   {0} ---------- {1}".format("thresholds var I", settings["thresholds_var_I"])
    if stop_in == "thresholds_var_I": return

    if env.config_run.settings['forecast_process']:
        console.msg("  Forecast options:", color='cyan')
        print "   {0} ------------- {1}".format("forecast date", settings["forecast_date"])
        if stop_in == "forecast_date": return
        print "   {0} ------ {1}".format("forecast var I lag 0", settings["forecast_var_I_lag_0"])
        if stop_in == "forecast_var_I_lag_0": return
        print "   {0} ------ {1}".format("forecast var I lag 1", settings["forecast_var_I_lag_1"])
        if stop_in == "forecast_var_I_lag_1": return
        print "   {0} ------ {1}".format("forecast var I lag 2", settings["forecast_var_I_lag_2"])
        if stop_in == "forecast_var_I_lag_2": return

    console.msg("  Maps options:", color='cyan')
    if env.config_run.settings['maps']:
        print "   {0} --------------- {1}".format("overlapping", settings["overlapping"])
        if stop_in == "overlapping": return
        print "   {0} ------------ {1}".format("marks stations", settings["marks_stations"])
        if stop_in == "marks_stations": return
        print "   {0} ------------ {1}".format("shape boundary", settings["shape_boundary"])
        if stop_in == "shape_boundary": return

    # Print some warnings and notifications

    if env.config_run.settings['path_to_file_var_I'] == 'internal':
        internal_file_I_name = env.var_I.INTERNAL_FILES[env.var_I.TYPE_SERIES]
        split_internal_var_I = internal_file_I_name.split(".")[0].split("_")
        console.msg(
            _("\n > You are using internal files for independent\n"
              "   variable defined as {0} which has data from\n"
              "   {1} to {2} and the source of data was\n"
              "   obtained in {3}.\n"
              "   url: {4}")
            .format(split_internal_var_I[0], split_internal_var_I[1],
                split_internal_var_I[2], ' '.join(split_internal_var_I[3::]),
                env.var_I.INTERNAL_URLS[env.var_I.TYPE_SERIES]))

    if (not env.config_run.settings['limits_var_D']['below'] or
        not env.config_run.settings['limits_var_D']['above'] or
        not env.config_run.settings['limits_var_I']['below'] or
        not env.config_run.settings['limits_var_I']['above']):
        console.msg(_("\n > WARNING: you are using one or more limits as\n"
                      "   'none' value, this means that series values\n"
                      "   will not be checked if they are valid in\n"
                      "   its limits coherent. This option is not\n"
                      "   recommended, use it with precaution"), color='yellow')

