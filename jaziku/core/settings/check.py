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

from jaziku.core import analysis_interval
from jaziku.env import config_run, globals_vars
from jaziku.utils import console, format_out


def configuration_run():

    # -------------------------------------------------------------------------
    # limits var D

    # check and validate if file D is defined as particular file with
    # particular range validation

    # below var D
    if config_run.settings['limit_var_D_below'] == "default":
        # validation type_D
        if config_run.settings['type_var_D'] not in globals_vars.TYPES_VAR_D:
            console.msg_error_configuration('type_var_D',
                _("{0} not is valid internal type for dependent variable if you\n"
                  "defined LIMIT VAR D BELOW/ABOVE as 'default'. If you want\n"
                  "define a particular type for dependent variable, you must define\n"
                  "as real values (or 'none') the LIMIT VAR D BELOW/ABOVE")
                .format(config_run.settings['type_var_D']))
    elif config_run.settings['limit_var_D_below'] in ["none", "None", "NONE", None]:
        config_run.settings['limit_var_D_below'] = None
    else:
        try:
            config_run.settings['limit_var_D_below'] = float(str(config_run.settings['limit_var_D_below']).replace(',', '.'))
        except:
            console.msg_error_configuration('limit_var_D_below',
                (_("Problem with particular range validation for "
                   "dependent\nvariable: '{0}' this must be "
                   "a valid number, 'none' or 'default'.").format(config_run.settings['limit_var_D_below'],)))
    # above var D
    if config_run.settings['limit_var_D_above'] == "default":
        # validation type_D
        if config_run.settings['type_var_D'] not in globals_vars.TYPES_VAR_D:
            console.msg_error_configuration('limit_var_D_above',
                _("{0} not is valid internal type for dependent variable if you\n"
                  "defined LIMIT VAR D BELOW/ABOVE as 'default'. If you want\n"
                  "define a particular type for dependent variable, you must define\n"
                  "as real values (or 'none') the LIMIT VAR D BELOW/ABOVE")
                .format(config_run.settings['type_var_D']))
    elif config_run.settings['limit_var_D_above'] in ["none", "None", "NONE", None]:
        config_run.settings['limit_var_D_above'] = None
    else:
        try:
            config_run.settings['limit_var_D_above'] = float(str(config_run.settings['limit_var_D_above']).replace(',', '.'))
        except:
            console.msg_error_configuration('limit_var_D_above',
                (_("Problem with particular range validation for "
                   "dependent\nvariable: '{0}' this must be "
                   "a valid number, 'none' or 'default'.").format(config_run.settings['limit_var_D_above'],)))

    # -------------------------------------------------------------------------
    # limits var I

    # check and validate if file I is defined as particular file with
    # particular range validation

    # below var I
    if config_run.settings['limit_var_I_below'] == "default":
        # validation type_I
        if config_run.settings['type_var_I'] not in globals_vars.TYPES_VAR_I:
            console.msg_error_configuration('type_var_I',
                _("{0} not is valid internal type for independent variable if you\n"
                  "defined LIMIT VAR I BELOW/ABOVE as 'default'. If you want\n"
                  "define a particular type for independent variable, you must define\n"
                  "as real values (or 'none') the LIMIT VAR I BELOW/ABOVE")
                .format(config_run.settings['type_var_I']))
    elif config_run.settings['limit_var_I_below'] in ["none", "None", "NONE", None]:
        config_run.settings['limit_var_I_below'] = None
    else:
        try:
            config_run.settings['limit_var_I_below'] = float(str(config_run.settings['limit_var_I_below']).replace(',', '.'))
        except:
            console.msg_error_configuration('limit_var_I_below',
                (_("Problem with particular range validation for "
                   "independent\nvariable: '{0}' this must be "
                   "a valid number, 'none' or 'default'.").format(config_run.settings['limit_var_I_below'],)))
    # above var I
    if config_run.settings['limit_var_I_above'] == "default":
        # validation type_I
        if config_run.settings['type_var_I'] not in globals_vars.TYPES_VAR_I:
            console.msg_error_configuration('limit_var_I_above',
                _("{0} not is valid internal type for independent variable if you\n"
                  "defined LIMIT VAR I BELOW/ABOVE as 'default'. If you want\n"
                  "define a particular type for independent variable, you must define\n"
                  "as real values (or 'none') the LIMIT VAR I BELOW/ABOVE")
                .format(config_run.settings['type_var_I']))
    elif config_run.settings['limit_var_I_above'] in ["none", "None", "NONE", None]:
        config_run.settings['limit_var_I_above'] = None
    else:
        try:
            config_run.settings['limit_var_I_above'] = float(str(config_run.settings['limit_var_I_above']).replace(',', '.'))
        except:
            console.msg_error_configuration('limit_var_I_above',
                (_("Problem with particular range validation for "
                   "independent\nvariable: '{0}' this must be "
                   "a valid number, 'none' or 'default'.").format(config_run.settings['limit_var_I_above'],)))

    # -------------------------------------------------------------------------
    # path_to_file_var_I

    # read from internal variable independent files of Jaziku, check
    # and notify if Jaziku are using the independent variable inside
    # located in plugins/var_I/
    if config_run.settings["path_to_file_var_I"] == "internal":
        if config_run.settings["type_var_I"] not in globals_vars.TYPES_OF_INTERNAL_VAR_I:
            console.msg_error_configuration('path_to_file_var_I',
                _("The 'path_to_file_var_I' is defined as 'internal' but the\n"
                  "type of independent variable '{0}' not is a valid internal\n"
                  "type. Please change type I to valid internal type, or define\n"
                  "a valid path to file var I.").format(config_run.settings["type_var_I"]))
    else:
        if not os.path.isfile(config_run.settings["path_to_file_var_I"]):
            console.msg_error_configuration('path_to_file_var_I',
                _("Can't open file '{0}' for var I, \nplease check filename and check that its path is relative (to runfile) or\n"
                  "absolute. If you want run var I with internals files\n"
                  "of jaziku you need set 'PATH TO FILE VAR I' as 'internal'").format(
                    config_run.settings["path_to_file_var_I"]))

    # -------------------------------------------------------------------------
    # thresholds var_I

    if not config_run.settings["path_to_file_var_I"] == "internal" and \
       config_run.settings["type_var_I"] not in globals_vars.TYPES_OF_INTERNAL_VAR_I:
        if config_run.settings["threshold_below_var_I"] == "default":
            console.msg_error_configuration('threshold_below_var_I',
                _("The thresholds can't be define as 'default' if the\n"
                  "type of independent variable not is valid internal type."))
        if config_run.settings["threshold_above_var_I"] == "default":
            console.msg_error_configuration('threshold_above_var_I',
                _("The thresholds can't be define as 'default' if the\n"
                  "type of independent variable not is valid internal type."))

    # -------------------------------------------------------------------------
    # check the 9 forecast values and forecast date

    # if forecast_process is activated
    if config_run.settings['forecast_process']:
        # lag 0
        lag_0 = config_run.settings['lag_0_phen_below'] +\
                config_run.settings['lag_0_phen_normal'] +\
                config_run.settings['lag_0_phen_above']
        if not (99 < lag_0 < 101):
            console.msg_error_configuration('lag_0_phen',
                _("The sum for the 3 values of phenomenon for lag 0\n"
                  "in 'forecast options' in runfile must be\nequal to 100."))

        # lag 1
        lag_1 = config_run.settings['lag_1_phen_below'] +\
                config_run.settings['lag_1_phen_normal'] +\
                config_run.settings['lag_1_phen_above']
        if not (99 < lag_1 < 101):
            console.msg_error_configuration('lag_1_phen',
                _("The sum for the 3 values of phenomenon for lag 1\n"
                  "in 'forecast options' in runfile must be\nequal to 100."))

        # lag 2
        lag_2 = config_run.settings['lag_2_phen_below'] +\
                config_run.settings['lag_2_phen_normal'] +\
                config_run.settings['lag_2_phen_above']
        if not (99 < lag_2 < 101):
            console.msg_error_configuration('lag_2_phen',
                _("The sum for the 3 values of phenomenon for lag 2\n"
                  "in 'forecast options' in runfile must be\nequal to 100."))

        # forecast date
        try:
            if isinstance(config_run.settings['forecast_date'], list):
                config_run.settings['forecast_date'][0] = int(config_run.settings['forecast_date'][0])
                forecast_month = config_run.settings['forecast_date'][0]
            else:
                config_run.settings['forecast_date'] = int(config_run.settings['forecast_date'])
                forecast_month = config_run.settings['forecast_date']
        except:
            console.msg_error_configuration('forecast_date',
                                            _("The month for forecast '{0}' is invalid, "
                                              "must be a integer: month or month;day")
                                            .format(config_run.settings['forecast_date']))

        if not (1 <= forecast_month <= 12):
            console.msg_error_configuration('forecast_date',
                                            _("The month for forecast '{0}' is invalid, "
                                              "must be a valid month number (1-12)")
                                            .format(forecast_month))

        if isinstance(config_run.settings['forecast_date'], list):
            if not isinstance(config_run.settings['forecast_date'][1], (float, int)):
                console.msg_error_configuration('forecast_date',
                                                _("The day for forecast process '{0}' is invalid, \n"
                                                  "must be a valid day number (1-31)")
                                                .format(config_run.settings['forecast_date'][1]))
            if not (1 <= config_run.settings['forecast_date'][1] <= 31):
                console.msg_error_configuration('forecast_date',
                                                _("The day for forecast process '{0}' is invalid, \n"
                                                  "must be a valid day number (1-31)")
                                                .format(config_run.settings['forecast_date'][1]))

            forecast_day = int(config_run.settings['forecast_date'][1])
            config_run.settings['forecast_date'] = {'month':forecast_month,'day':forecast_day}

            if config_run.settings['forecast_date']['day'] not in analysis_interval.get_range_analysis_interval():
                console.msg_error_configuration('forecast_date',
                                                _("Start day (month/day) for forecast process '{0}'\nis invalid, "
                                                  "must be a valid start day based on\nrange analysis "
                                                  "interval, the valid start days for\n{1} are: {2}")
                                                .format(config_run.settings['forecast_date']['day'],
                                                        globals_vars.analysis_interval_i18n,
                                                        analysis_interval.get_range_analysis_interval()))

            config_run.settings['forecast_date']['text'] \
                = format_out.get_month_in_text(config_run.settings['forecast_date']['month']-1) \
                + ' ' + str(config_run.settings['forecast_date']['day'])

        else:
            config_run.settings['forecast_date'] = {'month':forecast_month}

            config_run.settings['forecast_date']['text'] \
                = format_out.get_month_in_text(config_run.settings['forecast_date']['month']-1)

        globals_vars.input_settings["forecast_date"] = colored.green(config_run.settings['forecast_date']['text'])


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