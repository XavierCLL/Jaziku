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
from jaziku.utils import console, input_format


def configuration_run():

    # set settings by default
    settings = {"data_analysis": colored.red(_("disabled")),
                "climate_process": colored.red(_("disabled")),
                "forecast_process": colored.red(_("disabled")),
                "process_period": colored.red(_("disabled")),
                "analog_year": colored.red(_("disabled")),
                "lags": None,
                "language": env.config_run.settings['language'],
                "consistent_data": colored.red(_("disabled")),
                "risk_analysis": colored.red(_("disabled")),
                "graphics": colored.red(_("disabled")),
                "maps": colored.red(_("disabled")),
                "marks_stations": colored.green(_("enabled")),
                "overlapping": None,
                "shape_boundary": colored.red(_("disabled"))}

    env.globals_vars.input_settings = settings

    ## MODULES
    # ------------------------
    # data_analysis
    if env.config_run.settings['data_analysis'] == True:
        settings["data_analysis"] = colored.green(_("enabled"))
    elif not env.config_run.settings['data_analysis'] == False:
        console.msg_error_configuration('data_analysis', _("'data_analysis' variable in runfile is wrong,\n"
                                                           "this must be 'enable' or 'disable'"))

    # ------------------------
    # climate_process
    if env.config_run.settings['climate_process'] == True:
        settings["climate_process"] = colored.green(_("enabled"))
    elif not env.config_run.settings['climate_process'] == False:
        console.msg_error_configuration('climate_process', _("'climate_process' variable in runfile is wrong,\n"
                            "this must be 'enable' or 'disable'"))

    # ------------------------
    # forecast_process
    if env.config_run.settings['forecast_process'] == True:
        settings["forecast_process"] = colored.green(_("enabled"))
    elif not env.config_run.settings['forecast_process'] == False:
        console.msg_error_configuration('forecast_process', _("'forecast_process' variable in runfile is wrong,\n"
                            "this must be 'enable' or 'disable'"))

    ## GENERAL OPTIONS
    # ------------------------
    # analysis interval
    if env.config_run.settings['analysis_interval'] not in env.globals_vars.ALL_ANALYSIS_INTERVALS:
        console.msg_error_configuration('analysis_interval',
            _("The 'analysis_interval' defined in runfile {0} is invalid,\nmust be one of these: {1}")
            .format(env.config_run.settings['analysis_interval'], ', '.join(env.globals_vars.ALL_ANALYSIS_INTERVALS)))

    if env.config_run.settings['analysis_interval'] != "trimester":
        # detect analysis_interval number from string
        _count = 0
        for digit in env.config_run.settings['analysis_interval']:
            try:
                int(digit)
                _count += 1
            except:
                pass
        env.globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL = int(env.config_run.settings['analysis_interval'][0:_count])

    analysis_interval_i18n = [_("5days"), _("10days"), _("15days"), _("trimester")]
    env.config_run.settings['analysis_interval_i18n']\
        = analysis_interval_i18n[env.globals_vars.ALL_ANALYSIS_INTERVALS.index(env.config_run.settings['analysis_interval'])]
    # analysis_interval setting
    if env.config_run.settings['analysis_interval']:
        settings["analysis_interval"] = colored.green(env.config_run.settings['analysis_interval'])

    # ------------------------
    # class_category_analysis
    env.config_run.settings['class_category_analysis'] = input_format.to_int(env.config_run.settings['class_category_analysis'])
    settings["class_category_analysis"] = colored.green(env.config_run.settings['class_category_analysis'])

    # ------------------------
    # process_period
    if env.config_run.settings['process_period'] == "maximum":
        settings["process_period"] = "maximum"
        env.config_run.settings['process_period'] = False
    else:
        try:
            args_period_start = int(env.config_run.settings['process_period'][0])
            args_period_end = int(env.config_run.settings['process_period'][1])
            env.config_run.settings['process_period'] = {'start': args_period_start,
                                                         'end': args_period_end}
            settings["process_period"] = colored.green("{0}-{1}".format(args_period_start, args_period_end))
        except:
            console.msg_error_configuration('process_period',
                _("The period must be: start_year and end_year (in different column)\n"
                  "or 'maximum' for take the process period maximum possible by station."))

    # ------------------------
    # analog_year
    if env.config_run.settings['analog_year']:
        try:
            env.config_run.settings['analog_year'] = int(env.config_run.settings['analog_year'])
        except:
            console.msg_error_configuration('analog_year', "the analog_year must be a valid year")
        settings["analog_year"] = colored.green(env.config_run.settings['analog_year'])

    # ------------------------
    # lags
    if env.config_run.settings['lags'] == 'all':
        env.config_run.settings['lags'] = env.globals_vars.ALL_LAGS
        settings["lags"] = ', '.join(map(str, env.config_run.settings['lags']))
    else:
        try:
            if not isinstance(env.config_run.settings['lags'], list):
                lags_list = [env.config_run.settings['lags']]
            else:
                lags_list = env.config_run.settings['lags']
            for lag in lags_list:
                if ',' in str(lag) or '.' in str(lag):
                    if float(lag) != int(lag):
                        raise

            env.config_run.settings['lags'] = [int(float(lag)) for lag in lags_list]

            for lag in env.config_run.settings['lags']:
                if lag not in [0, 1, 2]:
                    raise
        except:
            console.msg_error_configuration('lags', _("The lags may be: 0, 1 and/or 2 (in different column), 'all' or 'default'"))
        settings["lags"] = colored.green(', '.join(map(str, env.config_run.settings['lags'])))

    # ------------------------
    # languages
    settings["language"] = env.config_run.settings['language']

    ## CHECK OPTIONS
    # ------------------------
    # consistent_data
    if env.config_run.settings['consistent_data'] == "default":
        env.config_run.settings['consistent_data'] = 15
        settings["consistent_data"] = "15%"
    elif isinstance(env.config_run.settings['consistent_data'], (int,float)) and \
         env.config_run.settings['consistent_data'] not in [True, False]:
        settings["consistent_data"] = colored.green(str(env.config_run.settings['consistent_data'])+'%')


    # ------------------------
    # risk_analysis
    if env.config_run.settings['risk_analysis']:
        settings["risk_analysis"] = colored.green(_("enabled"))

    ## OUTPUT OPTIONS
    # ------------------------
    # graphics
    if env.config_run.settings['graphics']:
        settings["graphics"] = colored.green(_("enabled"))

    # ------------------------
    # categories_labels_var_I
    if env.config_run.settings['categories_labels_var_I'] == "default":
        settings["categories_labels_var_I"] = [env.config_run.settings['categories_labels_var_I']]
    else:
        settings["categories_labels_var_I"] = ["'"+label+"'" for label in env.config_run.settings['categories_labels_var_I']]

    # ------------------------
    # relevant_climate_categories_var_I
    if env.config_run.settings['relevant_climate_categories_var_I'] == "all":
        settings["relevant_climate_categories_var_I"] = "all"
    else:
        # convert to list if there is one category
        if not isinstance(env.config_run.settings['relevant_climate_categories_var_I'], list):
            l = []; l.append(env.config_run.settings['relevant_climate_categories_var_I'])
            env.config_run.settings['relevant_climate_categories_var_I'] = l
        # clean ' character
        env.config_run.settings['relevant_climate_categories_var_I'] = [s.replace("'","") for s in env.config_run.settings['relevant_climate_categories_var_I']]
        settings["relevant_climate_categories_var_I"] = colored.green(', '.join(env.config_run.settings['relevant_climate_categories_var_I']))

    ## VAR D OPTIONS
    # ------------------------
    # type var D
    if env.var_D.TYPE_SERIES:
        settings["type_var_D"] = colored.green(env.var_D.TYPE_SERIES) + " ({0})".format(env.var_D.units)

    # ------------------------
    # mode_calculation_series_D
    settings["mode_calculation_series_D"] = env.config_run.settings['mode_calculation_series_D']

    # ------------------------
    # limits var D below
    if not isinstance(env.config_run.settings['limits_var_D'], list):
        if env.config_run.settings['limits_var_D'] == 'none':
            env.config_run.settings['limits_var_D'] = {'below': None, 'above': None}
            settings["limits_var_D"] = colored.red('none')
        elif env.config_run.settings['limits_var_D'] == 'default':
            env.config_run.settings['limits_var_D'] = {'below': 'default', 'above': 'default'}
            settings["limits_var_D"] = _('default')
        else:
            console.msg_error_configuration('limits_var_D',
                (_("Problem with particular range validation for "
                   "dependent\nvariable: '{0}' this must be "
                   "a valid number: <below>;<above>,\n'none' or 'default'.").format(env.config_run.settings['limits_var_D'])))
    else:
        env.config_run.settings['limits_var_D'] = {'below': env.config_run.settings['limits_var_D'][0],
                                               'above': env.config_run.settings['limits_var_D'][1]}
        # below
        if env.config_run.settings['limits_var_D']['below'] == 'none':
            env.config_run.settings['limits_var_D']['below'] = None
            settings["limits_var_D"] = colored.red('none')
        elif env.config_run.settings['limits_var_D']['below'] == 'default':
            settings["limits_var_D"] = _('default')
        else:
            settings["limits_var_D"] = colored.green(env.config_run.settings['limits_var_D']['below'])

        settings["limits_var_D"] += ' | '

        # above
        if env.config_run.settings['limits_var_D']['above'] == 'none':
            env.config_run.settings['limits_var_D']['above'] = None
            settings["limits_var_D"] += colored.red('none')
        elif env.config_run.settings['limits_var_D']['above'] == 'default':
            settings["limits_var_D"] += _('default')
        else:
            settings["limits_var_D"] += colored.green(env.config_run.settings['limits_var_D']['above'])

    # ------------------------
    # thresholds var D
    if env.config_run.settings['thresholds_var_D'] == 'default':
        settings["thresholds_var_D"] = _('default')
    else:
        settings["thresholds_var_D"] = colored.green(' | '.join([str(thr) for thr in env.config_run.settings['thresholds_var_D']]))

    ## VAR I OPTIONS
    # ------------------------
    # type var I
    if env.var_I.TYPE_SERIES:
        settings["type_var_I"] = colored.green(env.var_I.TYPE_SERIES) + " ({0})".format(env.var_I.units)

    # ------------------------
    # mode_calculation_series_I
    settings["mode_calculation_series_I"] = env.config_run.settings['mode_calculation_series_I']

    # ------------------------
    # path_to_file_var_I
    if env.config_run.settings['path_to_file_var_I'] == 'internal':
        settings["path_to_file_var_I"] = colored.green(env.config_run.settings['path_to_file_var_I'])
    else:
        #settings["path_to_file_var_I"] = env.config_run.settings['path_to_file_var_I']
        settings["path_to_file_var_I"] = os.path.relpath(env.config_run.settings['path_to_file_var_I'], os.path.abspath(os.path.dirname(env.globals_vars.ARGS.runfile)))

    # ------------------------
    # limits var I below
    if not isinstance(env.config_run.settings['limits_var_I'], list):
        if env.config_run.settings['limits_var_I'] == 'none':
            env.config_run.settings['limits_var_I'] = {'below': None, 'above': None}
            settings["limits_var_I"] = colored.red('none')
        elif env.config_run.settings['limits_var_I'] == 'default':
            env.config_run.settings['limits_var_I'] = {'below': 'default', 'above': 'default'}
            settings["limits_var_I"] = _('default')
        else:
            console.msg_error_configuration('limits_var_I',
                (_("Problem with particular range validation for "
                   "independent\nvariable: '{0}' this must be "
                   "a valid number: <below>;<above>,\n'none' or 'default'.").format(env.config_run.settings['limits_var_I'])))
    else:
        env.config_run.settings['limits_var_I'] = {'below': env.config_run.settings['limits_var_I'][0],
                                               'above': env.config_run.settings['limits_var_I'][1]}
        # below
        if env.config_run.settings['limits_var_I']['below'] == 'none':
            env.config_run.settings['limits_var_I']['below'] = None
            settings["limits_var_I"] = colored.red('none')
        elif env.config_run.settings['limits_var_I']['below'] == 'default':
            settings["limits_var_I"] = _('default')
        else:
            settings["limits_var_I"] = colored.green(env.config_run.settings['limits_var_I']['below'])

        settings["limits_var_I"] += ' | '

        # above
        if env.config_run.settings['limits_var_I']['above'] == 'none':
            env.config_run.settings['limits_var_I']['above'] = None
            settings["limits_var_I"] += colored.red('none')
        elif env.config_run.settings['limits_var_I']['above'] == 'default':
            settings["limits_var_I"] += _('default')
        else:
            settings["limits_var_I"] += colored.green(env.config_run.settings['limits_var_I']['above'])

    # ------------------------
    # thresholds var I
    if env.config_run.settings['thresholds_var_I'] == 'default':
        settings["thresholds_var_I"] = _('default')
    else:
        settings["thresholds_var_I"] = colored.green(' | '.join([str(thr) for thr in env.config_run.settings['thresholds_var_I']]))

    ## FORECAST OPTION
    # ------------------------
    # forecast settings
    if env.config_run.settings['forecast_process']:
        # forecast date
        settings["forecast_date"] = colored.green(env.config_run.settings['forecast_date'])
        # 9 values for forecast
        settings['forecast_var_I_lag_0'] = env.config_run.settings['forecast_var_I_lag_0']
        settings['forecast_var_I_lag_1'] = env.config_run.settings['forecast_var_I_lag_1']
        settings['forecast_var_I_lag_2'] = env.config_run.settings['forecast_var_I_lag_2']

    ## MAPS OPTIONS
    # ------------------------
    # maps
    if env.config_run.settings['maps']:
        if env.config_run.settings['maps'] == "all":
            env.config_run.settings['maps'] = {'climate': True, 'forecast': True, 'correlation': True}
        else:
            try:
                if not isinstance(env.config_run.settings['maps'], list):
                    env.config_run.settings['maps'] = [env.config_run.settings['maps']]
                input_maps_list = [_map.strip() for _map in env.config_run.settings['maps']]
                env.config_run.settings['maps'] = {'climate': False, 'forecast': False, 'correlation': False}
                for map_to_run in input_maps_list:
                    if map_to_run not in ['climate', 'forecast', 'correlation']:
                        raise
                    env.config_run.settings['maps'][map_to_run] = True
            except:
                console.msg_error_configuration('maps',_("the maps options are: 'climate', 'forecast', "
                                                         "'correlation' (in different column), or 'all'."))

        settings["maps"] = colored.green(_("enabled")) + ' (' + \
                           (', '.join(map(str, [m for m in env.config_run.settings['maps'] if env.config_run.settings['maps'][m]]))) + \
                           ')'

    # maps settings
    if env.config_run.settings['maps']:

        # marks_stations
        if env.config_run.settings['marks_stations'] in ["enable", "default", True]:
            settings["marks_stations"] = colored.green(_("enabled"))
            env.config_run.settings['marks_stations'] = True
        elif env.config_run.settings['marks_stations'] in ["disable", False]:
            env.config_run.settings['marks_stations'] = False
        else:
            console.msg_error_configuration('marks_stations', _("The marks_stations is wrong, the options are:\n"
                                                                "disable, enable or default."))
        # set the overlapping solution
        if env.config_run.settings['overlapping'] == "default" or not env.config_run.settings['overlapping']:
            env.config_run.settings['overlapping'] = "average"
            settings['overlapping'] = env.config_run.settings['overlapping']
        elif env.config_run.settings['overlapping'] in ["average", "maximum", "minimum", "neither"]:
            settings['overlapping'] = colored.green(env.config_run.settings['overlapping'])
        else:
            console.msg_error_configuration('overlapping', _("The overlapping solution is wrong, the options are:\n"
                                "default, average, maximum, minimum or neither"))
        # shape_boundary method
        # TODO: add more method for cut map interpolation around shape
        if env.config_run.settings['shape_boundary'] in ["enable", True]:
            settings["shape_boundary"] = colored.green(_("enabled"))
        elif env.config_run.settings['shape_boundary'] in ["default", False]:
            env.config_run.settings['shape_boundary'] = False
        else:
            console.msg_error_configuration('shape_boundary', _("The shape_boundary is wrong, the options are:\n"
                                "disable, enable or default."))

    ## post-get
    # ------------------------
    # when climate is disable:
    if not env.config_run.settings['climate_process']:
        console.msg(_("\nClimate process is disable, then forecast and maps\n"
                      "process will be disabled."), color="yellow")
        settings["forecast_process"] = colored.red(_("disabled"))
        settings["maps"] = colored.red(_("disabled"))

    # save input settings
    env.globals_vars.input_settings = settings


def grids_list():
    # TODO
    pass
