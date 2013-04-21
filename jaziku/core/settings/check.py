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
from jaziku.core import analysis_interval
from jaziku.utils import console, format_out, format_in, array


def configuration_run():

    # ------------------------
    # class_category_analysis

    env.config_run.settings['class_category_analysis'] = format_in.to_int(env.config_run.settings['class_category_analysis'])

    if env.config_run.settings['class_category_analysis'] not in [3,7]:
        console.msg_error_configuration('class_category_analysis',
            _("The 'class_category_analysis' {0} not is valid,\n"
              "this should be '3' or '7'.").format(env.config_run.settings['class_category_analysis']))

    # ------------------------
    # var_I_category_labels

    def var_I_category_labels_dictionary(func):
        def wrapper_func(*args):
            labels_list = func(*args)
            if isinstance(labels_list, dict):
            # it is when it is called twice
                return labels_list
            if env.config_run.settings['class_category_analysis'] == 3:
                return {'below': labels_list[0],
                        'normal': labels_list[1],
                        'above': labels_list[2]}
            if env.config_run.settings['class_category_analysis'] == 7:
                return {'below3': labels_list[0],
                        'below2': labels_list[1],
                        'below1': labels_list[2],
                        'normal': labels_list[3],
                        'above1': labels_list[4],
                        'above2': labels_list[5],
                        'above3': labels_list[6]}
        return wrapper_func

    if env.config_run.settings['class_category_analysis'] == 3:
        if env.config_run.settings['var_I_category_labels'] == "default":
            env.config_run.settings['var_I_category_labels'] = env.globals_vars.generic_labels()
        else:
            if len(env.config_run.settings['var_I_category_labels']) == 3:
                env.config_run.settings['var_I_category_labels']\
                    = [unicode(label, 'utf-8') for label in env.config_run.settings['var_I_category_labels']]
            else:
                console.msg_error_configuration('var_I_category_labels',
                                                _("The 'var_I_category_labels' is not valid,\n"
                                                  "this should be 3 labels in different rows."))

    if env.config_run.settings['class_category_analysis'] == 7:
        if env.config_run.settings['var_I_category_labels'] == "default":
            env.config_run.settings['var_I_category_labels'] = env.globals_vars.generic_labels()
        else:
            if len(env.config_run.settings['var_I_category_labels']) == 7:
                env.config_run.settings['var_I_category_labels'] \
                    = [unicode(label, 'utf-8') for label in env.config_run.settings['var_I_category_labels']]
            else:
                console.msg_error_configuration('var_I_category_labels',
                                                _("The 'var_I_category_labels' is not valid,\n"
                                                  "this should be 7 labels in different rows."))

    @var_I_category_labels_dictionary
    def format_labels(labels_list):
        return labels_list

    env.config_run.settings['var_I_category_labels'] = format_labels(env.config_run.settings['var_I_category_labels'])

    # ------------------------
    # mode_calculation_series_D

    if env.config_run.settings['mode_calculation_series_D'] == 'default':
        if env.var_D.TYPE_SERIES in env.var_D.MODE_CALCULATION_SERIES:
            env.config_run.settings['mode_calculation_series_D'] = env.var_D.MODE_CALCULATION_SERIES[env.var_D.TYPE_SERIES][0]
        else:
            env.config_run.settings['mode_calculation_series_D'] = 'mean'
        env.globals_vars.input_settings["mode_calculation_series_D"] = env.config_run.settings['mode_calculation_series_D']
    elif env.config_run.settings['mode_calculation_series_D'] in ['accumulate', 'mean']:
        if env.var_D.TYPE_SERIES in env.var_D.MODE_CALCULATION_SERIES:
            if env.config_run.settings['mode_calculation_series_D'] not in env.var_D.MODE_CALCULATION_SERIES[env.var_D.TYPE_SERIES]:
                console.msg_error_configuration('mode_calculation_series_D',
                    _("For {0} the 'mode_calculation_series_D' set as '{1}', but\n"
                      "this series not accept this mode to calculate the series.\n"
                      "For this series the options are: {2}")
                        .format(env.var_D.TYPE_SERIES, env.config_run.settings['mode_calculation_series_D'],
                                env.var_D.MODE_CALCULATION_SERIES[env.var_D.TYPE_SERIES]))
        env.globals_vars.input_settings["mode_calculation_series_D"] = colored.green(env.config_run.settings['mode_calculation_series_D'])
    else:
        console.msg_error_configuration('mode_calculation_series_D', _("The mode_calculation_series_D is wrong, the options are:\n"
                                                                       "default, accumulate or mean"))

    # ------------------------
    # limits var D

    # check and validate if file D is defined as particular file with
    # particular range validation

    # below var D
    if env.config_run.settings['limits_var_D']['below'] == "default":
        # validation type_D
        if env.var_D.TYPE_SERIES not in env.var_D.INTERNAL_TYPES:
            console.msg_error_configuration('type_var_D',
                _("{0} not is valid internal type for dependent variable if you\n"
                  "defined LIMIT VAR D BELOW/ABOVE as 'default'. If you want\n"
                  "define a particular type for dependent variable, you must define\n"
                  "as real values (or 'none') the LIMIT VAR D BELOW/ABOVE")
                .format(env.var_D.TYPE_SERIES))
    elif env.config_run.settings['limits_var_D']['below'] in ["none", "None", "NONE", None]:
        env.config_run.settings['limits_var_D']['below'] = None
    else:
        try:
            env.config_run.settings['limits_var_D']['below'] = format_in.to_float(env.config_run.settings['limits_var_D']['below'])
        except:
            console.msg_error_configuration('limits_var_D',
                (_("Problem with particular range validation for "
                   "dependent\nvariable: '{0}' this must be "
                   "a valid number, 'none' or 'default'.").format(env.config_run.settings['limits_var_D']['below'])))

    # above var D
    if env.config_run.settings['limits_var_D']['above'] == "default":
        # validation type_D
        if env.var_D.TYPE_SERIES not in env.var_D.INTERNAL_TYPES:
            console.msg_error_configuration('limits_var_D',
                _("{0} not is valid internal type for dependent variable if you\n"
                  "defined LIMIT VAR D BELOW/ABOVE as 'default'. If you want\n"
                  "define a particular type for dependent variable, you must define\n"
                  "as real values (or 'none') the LIMIT VAR D BELOW/ABOVE")
                .format(env.var_D.TYPE_SERIES))
    elif env.config_run.settings['limits_var_D']['above'] in ["none", "None", "NONE", None]:
        env.config_run.settings['limits_var_D']['above'] = None
    else:
        try:
            env.config_run.settings['limits_var_D']['above'] = format_in.to_float(env.config_run.settings['limits_var_D']['above'])
        except:
            console.msg_error_configuration('limits_var_D',
                (_("Problem with particular range validation for "
                   "dependent\nvariable: '{0}' this must be "
                   "a valid number, 'none' or 'default'.").format(env.config_run.settings['limits_var_D']['above'])))

    env.config_run.settings['limits_var_D']['ready'] = False

    # ------------------------
    # thresholds var_D

    if not env.config_run.settings["thresholds_var_D"] == "default" and \
       len(env.config_run.settings["thresholds_var_D"]) != env.config_run.settings['class_category_analysis']-1:
            console.msg_error_configuration('thresholds_var_D',
                                            _("The thresholds for {0} categories must have {1} thresholds,\n"
                                              "or 'default' for use thresholds by default defined for this variable.")
                                            .format(env.config_run.settings['class_category_analysis'], env.config_run.settings['class_category_analysis']-1))

    # ------------------------
    # mode_calculation_series_I

    if env.config_run.settings['mode_calculation_series_I'] == 'default':
        if env.var_I.TYPE_SERIES in env.var_I.MODE_CALCULATION_SERIES:
            env.config_run.settings['mode_calculation_series_I'] = env.var_I.MODE_CALCULATION_SERIES[env.var_I.TYPE_SERIES][0]
        else:
            env.config_run.settings['mode_calculation_series_I'] = 'mean'
        env.globals_vars.input_settings["mode_calculation_series_I"] = env.config_run.settings['mode_calculation_series_I']
    elif env.config_run.settings['mode_calculation_series_I'] in ['accumulate', 'mean']:
        if env.var_I.TYPE_SERIES in env.var_I.MODE_CALCULATION_SERIES:
            if env.config_run.settings['mode_calculation_series_I'] not in env.var_I.MODE_CALCULATION_SERIES[env.var_I.TYPE_SERIES]:
                console.msg_error_configuration('mode_calculation_series_I',
                    _("For {0} the 'mode_calculation_series_I' set as '{1}', but\n"
                      "this series not accept this mode to calculate the series.\n"
                      "For {0} series the options are: {2}")
                        .format(env.var_I.TYPE_SERIES, env.config_run.settings['mode_calculation_series_I'],
                                env.var_I.MODE_CALCULATION_SERIES[env.var_I.TYPE_SERIES]))
        env.globals_vars.input_settings["mode_calculation_series_I"] = colored.green(env.config_run.settings['mode_calculation_series_I'])
    else:
        console.msg_error_configuration('mode_calculation_series_I', _("The mode_calculation_series_I is wrong, the options are:\n"
                                                                       "default, accumulate or mean"))

    # ------------------------
    # limits var I

    # check and validate if file I is defined as particular file with
    # particular range validation

    # below var I
    if env.config_run.settings['limits_var_I']['below'] == "default":
        # validation type_I
        if env.var_I.TYPE_SERIES not in env.var_I.INTERNAL_TYPES:
            console.msg_error_configuration('type_var_I',
                _("{0} not is valid internal type for independent variable if you\n"
                  "defined LIMIT VAR I BELOW/ABOVE as 'default'. If you want\n"
                  "define a particular type for independent variable, you must define\n"
                  "as real values (or 'none') the LIMIT VAR I BELOW/ABOVE")
                .format(env.var_I.TYPE_SERIES))
    elif env.config_run.settings['limits_var_I']['below'] in ["none", "None", "NONE", None]:
        env.config_run.settings['limits_var_I']['below'] = None
    else:
        try:
            env.config_run.settings['limits_var_I']['below'] = format_in.to_float(env.config_run.settings['limits_var_I']['below'])
        except:
            console.msg_error_configuration('limits_var_I',
                (_("Problem with particular range validation for "
                   "independent\nvariable: '{0}' this must be "
                   "a valid number, 'none' or 'default'.").format(env.config_run.settings['limits_var_I']['below'])))
    # above var I
    if env.config_run.settings['limits_var_I']['above'] == "default":
        # validation type_I
        if env.var_I.TYPE_SERIES not in env.var_I.INTERNAL_TYPES:
            console.msg_error_configuration('limits_var_I',
                _("{0} not is valid internal type for independent variable if you\n"
                  "defined LIMIT VAR I BELOW/ABOVE as 'default'. If you want\n"
                  "define a particular type for independent variable, you must define\n"
                  "as real values (or 'none') the LIMIT VAR I BELOW/ABOVE")
                .format(env.var_I.TYPE_SERIES))
    elif env.config_run.settings['limits_var_I']['above'] in ["none", "None", "NONE", None]:
        env.config_run.settings['limits_var_I']['above'] = None
    else:
        try:
            env.config_run.settings['limits_var_I']['above'] = format_in.to_float(env.config_run.settings['limits_var_I']['above'])
        except:
            console.msg_error_configuration('limits_var_I',
                (_("Problem with particular range validation for "
                   "independent\nvariable: '{0}' this must be "
                   "a valid number, 'none' or 'default'.").format(env.config_run.settings['limits_var_I']['above'])))

    env.config_run.settings['limits_var_I']['ready'] = False

    # ------------------------
    # path_to_file_var_I

    # read from internal variable independent files of Jaziku, check
    # and notify if Jaziku are using the independent variable inside
    # located in plugins/var_I/
    if env.config_run.settings["path_to_file_var_I"] == "internal":
        if env.config_run.settings["type_var_I"] not in env.var_I.INTERNAL_TYPES:
            console.msg_error_configuration('path_to_file_var_I',
                _("The 'path_to_file_var_I' is defined as 'internal' but the\n"
                  "type of independent variable '{0}' not is a valid internal\n"
                  "type. Please change type I to valid internal type, or define\n"
                  "a valid path to file var I.").format(env.config_run.settings["type_var_I"]))
    else:
        if not os.path.isfile(env.config_run.settings["path_to_file_var_I"]):
            console.msg_error_configuration('path_to_file_var_I',
                _("Can't open file '{0}' for var I,\n"
                  "please check filename and check that its path is relative (to runfile) or\n"
                  "absolute. If you want run var I with internals files\n"
                  "of jaziku you need set 'PATH TO FILE VAR I' as 'internal'").format(
                    env.config_run.settings["path_to_file_var_I"]))

    # ------------------------
    # thresholds var_I

    if not env.config_run.settings["thresholds_var_I"] == "default" and \
       len(env.config_run.settings["thresholds_var_I"]) != env.config_run.settings['class_category_analysis']-1:
            console.msg_error_configuration('thresholds_var_I',
                _("The thresholds for {0} categories must have {1} thresholds,\n"
                  "or 'default' for use thresholds by default defined for this variable.")
            .format(env.config_run.settings['class_category_analysis'], env.config_run.settings['class_category_analysis']-1))

    # ------------------------
    # check when use special internal variables (ONI1, ONI2, CAR) these series have trimester values
    # in this case only can use trimester for analysis interval

    if env.config_run.settings['analysis_interval'] != "trimester" and env.config_run.settings["type_var_I"] in ['ONI1', 'ONI2', 'CAR']:
        console.msg_error_configuration('analysis_interval',
                                        _("For the internals variables: ONI1, ONI2 or CAR you need\n"
                                          "defined 'analysis_interval' as 'trimester' because these\n"
                                          "time series have trimester values")
                                        .format(env.var_D.TYPE_SERIES))

    # ------------------------
    # check the probability_forecast_values and forecast date

    # if forecast_process is activated
    if env.config_run.settings['forecast_process']:

        # ------------------------
        ## check and reset the values for forecast process, 3x3, 3x7 or 7x7
        for lag in [str(lag) for lag in env.globals_vars.ALL_LAGS]:
            try:
                env.config_run.settings['forecast_var_I_lag_'+lag] \
                    = [format_in.to_float(item) for item in env.config_run.settings['forecast_var_I_lag_'+lag]]
                if env.config_run.settings['class_category_analysis'] == 3:
                    # check if all values are valid (float or int)
                    if False in [isinstance(value, (float, int)) for value in array.clean(env.config_run.settings['forecast_var_I_lag_'+lag])]:
                        raise ValueError('3')
                    # check if amount of values is correct
                    if len(array.clean(env.config_run.settings['forecast_var_I_lag_'+lag])) == 3:
                        env.globals_vars.forecast_contingency_table['type'] = '3x3'
                        env.config_run.settings['forecast_var_I_lag_'+lag] = array.clean(env.config_run.settings['forecast_var_I_lag_'+lag])
                        env.globals_vars.input_settings['forecast_var_I_lag_'+lag] = env.config_run.settings['forecast_var_I_lag_'+lag]
                    else:
                        raise ValueError('3')
                if env.config_run.settings['class_category_analysis'] == 7:
                    # check if all values are valid (float or int)
                    if False in [isinstance(value, (float, int)) for value in array.clean(env.config_run.settings['forecast_var_I_lag_'+lag])]:
                        raise ValueError('3 or 7')
                    # check if amount of values is correct
                    if len(array.clean(env.config_run.settings['forecast_var_I_lag_'+lag])) == 3:
                        env.globals_vars.forecast_contingency_table['type'] = '3x7'
                    elif len(array.clean(env.config_run.settings['forecast_var_I_lag_'+lag])) == 7:
                        env.globals_vars.forecast_contingency_table['type'] = '7x7'
                    else:
                        raise ValueError('3 or 7')
            except ValueError as error:
                console.msg_error_configuration('forecast_var_I_lag_'+lag,
                                                _("The 'forecast_var_I_lag_{0}' should be a {1} valid\n"
                                                  "values (int or float).").format(lag, error))

            # check that sum of all values in forecast_var_I_lag_N is equal to 100 (+-1)
            if not (99 < sum(array.clean(env.config_run.settings['forecast_var_I_lag_'+lag])) < 101):
                console.msg_error_configuration('forecast_var_I_lag_'+lag,
                                                _("The sum for the values of 'forecast_var_I_lag_{0}'\n"
                                                  "in 'forecast options' in runfile, must be\nequal to 100.")
                                                .format(lag))

        # ------------------------
        ## forecast date
        try:
            if isinstance(env.config_run.settings['forecast_date'], list):
                env.config_run.settings['forecast_date'][0] = int(env.config_run.settings['forecast_date'][0])
                forecast_month = env.config_run.settings['forecast_date'][0]
            else:
                env.config_run.settings['forecast_date'] = int(env.config_run.settings['forecast_date'])
                forecast_month = env.config_run.settings['forecast_date']
        except:
            console.msg_error_configuration('forecast_date',
                                            _("The month for forecast '{0}' is invalid, "
                                              "must be a integer: month or month;day")
                                            .format(env.config_run.settings['forecast_date']))

        if not (1 <= forecast_month <= 12):
            console.msg_error_configuration('forecast_date',
                                            _("The month for forecast '{0}' is invalid, "
                                              "must be a valid month number (1-12)")
                                            .format(forecast_month))

        if isinstance(env.config_run.settings['forecast_date'], list):
            if not isinstance(env.config_run.settings['forecast_date'][1], (float, int)):
                console.msg_error_configuration('forecast_date',
                                                _("The day for forecast process '{0}' is invalid, \n"
                                                  "must be a valid day number (1-31)")
                                                .format(env.config_run.settings['forecast_date'][1]))
            if not (1 <= env.config_run.settings['forecast_date'][1] <= 31):
                console.msg_error_configuration('forecast_date',
                                                _("The day for forecast process '{0}' is invalid, \n"
                                                  "must be a valid day number (1-31)")
                                                .format(env.config_run.settings['forecast_date'][1]))

            forecast_day = int(env.config_run.settings['forecast_date'][1])
            env.config_run.settings['forecast_date'] = {'month':forecast_month,'day':forecast_day}

            if env.config_run.settings['forecast_date']['day'] not in analysis_interval.get_range_analysis_interval():
                console.msg_error_configuration('forecast_date',
                                                _("Start day (month/day) for forecast process '{0}'\nis invalid, "
                                                  "must be a valid start day based on\nrange analysis "
                                                  "interval, the valid start days for\n{1} are: {2}")
                                                .format(env.config_run.settings['forecast_date']['day'],
                                                        env.globals_vars.analysis_interval_i18n,
                                                        analysis_interval.get_range_analysis_interval()))

            env.config_run.settings['forecast_date']['text'] \
                = format_out.month_in_initials(env.config_run.settings['forecast_date']['month']-1) \
                + ' ' + str(env.config_run.settings['forecast_date']['day'])

        else:
            if env.config_run.settings['analysis_interval'] != 'trimester':
                console.msg_error_configuration('forecast_date',
                                                _("The 'analysis_interval' is {0} but the 'forecast_date'\n"
                                                  "only have the month, please define the month and start day\n"
                                                  "for {0} (in different row) for the forecast date.")
                                                .format(env.config_run.settings['analysis_interval']))

            env.config_run.settings['forecast_date'] = {'month':forecast_month}

            env.config_run.settings['forecast_date']['text'] \
                = format_out.month_in_initials(env.config_run.settings['forecast_date']['month']-1)

        env.globals_vars.input_settings["forecast_date"] = colored.green(env.config_run.settings['forecast_date']['text'])


def grids_list():
    # TODO
    pass


def stations_list(stations_list):

    console.msg(_("\nChecking the stations list:"), newline=False)

    # -------------------------------------------------------------------------
    # check the code and/or name of stations don't repeat, exit or show warning
    # depending on the case.

    # first check error
    list_codes = []
    list_names = []
    for station in stations_list:
        if station.code in list_codes and station.name in list_names:
            console.msg_error_line_stations(station, _("The combination of the code and name of the station can't repeat,\n"
                                                       "many result will be replaced with the same code-name of station." ))
        else:
            list_codes.append(station.code)
            list_names.append(station.name)

    # check warnings, show and return with the first warning
    list_codes = []
    list_names = []
    for station in stations_list:
        if station.code in list_codes and not station.name in list_names:
            console.msg(_("WARNING:"), color='yellow')
            console.msg(_("   The code {0} of the station {1} is repeat\n"
                          "   with other stations, is recommend that the code and name\n"
                          "   of stations be different. This is only a recommendation,\n"
                          "   you can continue.").format(station.code, station.name), color='yellow')
            return
        elif not station.code in list_codes and station.name in list_names:
            console.msg(_("WARNING:"), color='yellow')
            console.msg(_("   The name {0} of the station with code {1} is repeat\n"
                          "   with other stations, is recommend that the code and name\n"
                          "   of stations be different. This is only a recommendation,\n"
                          "   you can continue.").format(station.name, station.code), color='yellow')
            return
        else:
            list_codes.append(station.code)
            list_names.append(station.name)

    # finish, check all good
    console.msg(_("done"), color='green')
