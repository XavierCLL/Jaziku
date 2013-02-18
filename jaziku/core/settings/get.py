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

from jaziku.env import config_run, globals_vars
from jaziku.utils import console


def get():

    # set settings by default
    settings = {"data_analysis": colored.red(_("disabled")),
                "climate_process": colored.red(_("disabled")),
                "forecast_process": colored.red(_("disabled")),
                "process_period": colored.red(_("disabled")),
                "analog_year": colored.red(_("disabled")),
                "lags": None,
                "language": config_run.settings['language'],
                "consistent_data": colored.red(_("disabled")),
                "risk_analysis": colored.red(_("disabled")),
                "graphics": colored.red(_("disabled")),
                "phen_below_label": "-",
                "phen_normal_label": "-",
                "phen_above_label": "-",
                "maps": colored.red(_("disabled")),
                "marks_stations": colored.green(_("enabled")),
                "overlapping": None,
                "shape_boundary": colored.red(_("disabled"))}

    globals_vars.input_settings = settings

    ## general options
    # ------------------------
    # data_analysis
    if config_run.settings['data_analysis'] == True:
        settings["data_analysis"] = colored.green(_("enabled"))
    elif not config_run.settings['data_analysis'] == False:
        console.msg_error_configuration('data_analysis', _("'data_analysis' variable in runfile is wrong,\n"
                                                           "this must be 'enable' or 'disable'"))

    # ------------------------
    # climate_process
    if config_run.settings['climate_process'] == True:
        settings["climate_process"] = colored.green(_("enabled"))
    elif not config_run.settings['climate_process'] == False:
        console.msg_error_configuration('climate_process', _("'climate_process' variable in runfile is wrong,\n"
                            "this must be 'enable' or 'disable'"))

    # ------------------------
    # forecast_process
    if config_run.settings['forecast_process'] == True:
        settings["forecast_process"] = colored.green(_("enabled"))
    elif not config_run.settings['forecast_process'] == False:
        console.msg_error_configuration('forecast_process', _("'forecast_process' variable in runfile is wrong,\n"
                            "this must be 'enable' or 'disable'"))

    # ------------------------
    # analysis interval
    if config_run.settings['analysis_interval'] not in globals_vars.ALL_ANALYSIS_INTERVALS:
        console.msg_error_configuration('analysis_interval',
            _("The 'analysis_interval' defined in runfile {0} is invalid,\nmust be one of these: {1}")
            .format(config_run.settings['analysis_interval'], ', '.join(globals_vars.ALL_ANALYSIS_INTERVALS)))

    if config_run.settings['analysis_interval'] != "trimester":
        # detect analysis_interval number from string
        _count = 0
        for digit in config_run.settings['analysis_interval']:
            try:
                int(digit)
                _count += 1
            except:
                pass
        globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL = int(config_run.settings['analysis_interval'][0:_count])

    translate_analysis_interval = [_("5days"), _("10days"), _("15days"), _("trimester")]
    globals_vars.analysis_interval_i18n\
        = translate_analysis_interval[globals_vars.ALL_ANALYSIS_INTERVALS.index(config_run.settings['analysis_interval'])]
    # analysis_interval setting
    if config_run.settings['analysis_interval']:
        settings["analysis_interval"] = colored.green(config_run.settings['analysis_interval'])

    # ------------------------
    # process_period
    if config_run.settings['process_period'] == "maximum":
        settings["process_period"] = "maximum"
        config_run.settings['process_period'] = False
    else:
        try:
            args_period_start = int(config_run.settings['process_period'].split('-')[0])
            args_period_end = int(config_run.settings['process_period'].split('-')[1])
            config_run.settings['process_period'] = {'start': args_period_start,
                                                         'end': args_period_end}
            settings["process_period"] = colored.green("{0}-{1}".format(args_period_start, args_period_end))
        except Exception, e:
            console.msg_error_configuration('process_period',
                _("The period must be: year_start-year_end (ie. 1980-2008)\n"
                  "or 'maximum' for take the process period maximum possible.\n\n{0}").format(e))

    # ------------------------
    # analog_year
    if config_run.settings['analog_year']:
        try:
            config_run.settings['analog_year'] = int(config_run.settings['analog_year'])
        except:
            console.msg_error_configuration('analog_year', "the analog_year must be a valid year")
        settings["analog_year"] = colored.green(config_run.settings['analog_year'])

    # ------------------------
    # lags
    if config_run.settings['lags'] in ['default', 'all']:
        config_run.settings['lags'] = globals_vars.ALL_LAGS
        settings["lags"] = ','.join(map(str, config_run.settings['lags']))
    else:
        try:
            lags = []
            for lag in str(config_run.settings['lags']).split(","):
                lag = int(float(lag))
                if lag not in [0, 1, 2]:
                    raise
                lags.append(lag)
            config_run.settings['lags'] = lags
        except:
            console.msg_error_configuration('lags', _("The lags may be: 0, 1 and/or 2 (comma separated), 'all' or 'default'"))
        settings["lags"] = colored.green(','.join(map(str, config_run.settings['lags'])))

    # ------------------------
    # languages
    settings["language"] = config_run.settings['language']

    ## input options
    # ------------------------
    # type var D
    if config_run.settings['type_var_D']:
        settings["type_var_D"] = colored.green(config_run.settings['type_var_D']) + " ({0})".format(globals_vars.units_var_D)

    # ------------------------
    # limits var D below
    if not isinstance(config_run.settings['limits_var_D'], list):
        if config_run.settings['limits_var_D'] == 'none':
            config_run.settings['limits_var_D'] = {'below': None, 'above': None}
            settings["limits_var_D"] = colored.red('none')
        elif config_run.settings['limits_var_D'] == 'default':
            config_run.settings['limits_var_D'] = {'below': 'default', 'above': 'default'}
            settings["limits_var_D"] = _('default')
        else:
            console.msg_error_configuration('limits_var_D',
                (_("Problem with particular range validation for "
                   "dependent\nvariable: '{0}' this must be "
                   "a valid number: <below>;<above>,\n'none' or 'default'.").format(config_run.settings['limits_var_D'])))
    else:
        config_run.settings['limits_var_D'] = {'below': config_run.settings['limits_var_D'][0],
                                               'above': config_run.settings['limits_var_D'][1]}
        # below
        if config_run.settings['limits_var_D']['below'] == 'none':
            config_run.settings['limits_var_D']['below'] = None
            settings["limits_var_D"] = colored.red('none')
        elif config_run.settings['limits_var_D']['below'] == 'default':
            settings["limits_var_D"] = _('default')
        else:
            settings["limits_var_D"] = colored.green(config_run.settings['limits_var_D']['below'])

        settings["limits_var_D"] += ' - '

        # above
        if config_run.settings['limits_var_D']['above'] == 'none':
            config_run.settings['limits_var_D']['above'] = None
            settings["limits_var_D"] += colored.red('none')
        elif config_run.settings['limits_var_D']['above'] == 'default':
            settings["limits_var_D"] += _('default')
        else:
            settings["limits_var_D"] += colored.green(config_run.settings['limits_var_D']['above'])


    # ------------------------
    # threshold var D
    if config_run.settings['threshold_below_var_D'] == 'default':
        settings["threshold_below_var_D"] = _('default')
    else:
        settings["threshold_below_var_D"] = colored.green(config_run.settings['threshold_below_var_D'])
    if config_run.settings['threshold_above_var_D'] == 'default':
        settings["threshold_above_var_D"] = _('default')
    else:
        settings["threshold_above_var_D"] = colored.green(config_run.settings['threshold_above_var_D'])

    # ------------------------
    # type var I
    if config_run.settings['type_var_I']:
        settings["type_var_I"] = colored.green(config_run.settings['type_var_I']) + " ({0})".format(globals_vars.units_var_I)

    # ------------------------
    # path_to_file_var_I
    if config_run.settings['path_to_file_var_I'] == 'internal':
        settings["path_to_file_var_I"] = colored.green(config_run.settings['path_to_file_var_I'])
    else:
        #settings["path_to_file_var_I"] = config_run.settings['path_to_file_var_I']
        settings["path_to_file_var_I"] = os.path.relpath(config_run.settings['path_to_file_var_I'], os.path.abspath(os.path.dirname(globals_vars.ARGS.runfile)))

    # ------------------------
    # limits var I below
    if not isinstance(config_run.settings['limits_var_I'], list):
        if config_run.settings['limits_var_I'] == 'none':
            config_run.settings['limits_var_I'] = {'below': None, 'above': None}
            settings["limits_var_I"] = colored.red('none')
        elif config_run.settings['limits_var_I'] == 'default':
            config_run.settings['limits_var_I'] = {'below': 'default', 'above': 'default'}
            settings["limits_var_I"] = _('default')
        else:
            console.msg_error_configuration('limits_var_I',
                (_("Problem with particular range validation for "
                   "independent\nvariable: '{0}' this must be "
                   "a valid number: <below>;<above>,\n'none' or 'default'.").format(config_run.settings['limits_var_I'])))
    else:
        config_run.settings['limits_var_I'] = {'below': config_run.settings['limits_var_I'][0],
                                               'above': config_run.settings['limits_var_I'][1]}
        # below
        if config_run.settings['limits_var_I']['below'] == 'none':
            config_run.settings['limits_var_I']['below'] = None
            settings["limits_var_I"] = colored.red('none')
        elif config_run.settings['limits_var_I']['below'] == 'default':
            settings["limits_var_I"] = _('default')
        else:
            settings["limits_var_I"] = colored.green(config_run.settings['limits_var_I']['below'])

        settings["limits_var_I"] += ' - '

        # above
        if config_run.settings['limits_var_I']['above'] == 'none':
            config_run.settings['limits_var_I']['above'] = None
            settings["limits_var_I"] += colored.red('none')
        elif config_run.settings['limits_var_I']['above'] == 'default':
            settings["limits_var_I"] += _('default')
        else:
            settings["limits_var_I"] += colored.green(config_run.settings['limits_var_I']['above'])

    # ------------------------
    # threshold var I
    if config_run.settings['threshold_below_var_I'] == 'default':
        settings["threshold_below_var_I"] = _('default')
    else:
        settings["threshold_below_var_I"] = colored.green(config_run.settings['threshold_below_var_I'])
    if config_run.settings['threshold_above_var_I'] == 'default':
        settings["threshold_above_var_I"] = _('default')
    else:
        settings["threshold_above_var_I"] = colored.green(config_run.settings['threshold_above_var_I'])

    ## check options
    # ------------------------
    # consistent_data
    if config_run.settings['consistent_data']:
        settings["consistent_data"] = colored.green(_("enabled"))

    # ------------------------
    # risk_analysis
    if config_run.settings['risk_analysis']:
        settings["risk_analysis"] = colored.green(_("enabled"))

    ## graphics settings
    # ------------------------
    if config_run.settings['graphics']:
        settings["graphics"] = colored.green(_("enabled"))


    # if phenomenon below is defined inside arguments, else default value
    if config_run.settings['phen_below_label'] and config_run.settings['phen_below_label'] != "default":
        config_run.settings['phen_below_label'] = unicode(config_run.settings['phen_below_label'], 'utf-8')
        settings["phen_below_label"] = colored.green(config_run.settings['phen_below_label'])
    else:
        config_run.settings['phen_below_label'] = unicode(_('var_I_below'), 'utf-8') # label by default
        settings["phen_below_label"] = config_run.settings['phen_below_label']
    # if phenomenon normal is defined inside arguments, else default value
    if config_run.settings['phen_normal_label'] and config_run.settings['phen_normal_label'] != "default":
        config_run.settings['phen_normal_label'] = unicode(config_run.settings['phen_normal_label'], 'utf-8')
        settings["phen_normal_label"] = colored.green(config_run.settings['phen_normal_label'])
    else:
        config_run.settings['phen_normal_label'] = unicode(_('var_I_normal'), 'utf-8') # label by default
        settings["phen_normal_label"] = config_run.settings['phen_normal_label']
    # if phenomenon above is defined inside arguments, else default value
    if config_run.settings['phen_above_label'] and config_run.settings['phen_above_label'] != "default":
        config_run.settings['phen_above_label'] = unicode(config_run.settings['phen_above_label'], 'utf-8')
        settings["phen_above_label"] = colored.green(config_run.settings['phen_above_label'])
    else:
        config_run.settings['phen_above_label'] = unicode(_('var_I_above'), 'utf-8') # label by default
        settings["phen_above_label"] = config_run.settings['phen_above_label']

    # ------------------------
    # forecast settings
    if config_run.settings['forecast_process']:
        # forecast date
        settings["forecast_date"] = colored.green(config_run.settings['forecast_date'])
        # 9 values for forecast
        settings['forecast_var_I_lag_0'] = config_run.settings['forecast_var_I_lag_0']
        settings['forecast_var_I_lag_1'] = config_run.settings['forecast_var_I_lag_1']
        settings['forecast_var_I_lag_2'] = config_run.settings['forecast_var_I_lag_2']

    # ------------------------
    # maps settings
    if config_run.settings['maps']:
        if config_run.settings['maps'] == "all":
            config_run.settings['maps'] = {'climate': True, 'forecast': True, 'correlation': True}
            settings["maps"] = ','.join(map(str, [m for m in config_run.settings['maps'] if config_run.settings['maps'][m]]))
        else:
            try:
                config_run.settings['maps'] = {'climate': False, 'forecast': False, 'correlation': False}
                input_maps_list = config_run.settings['maps'].split(",")
                for map_to_run in input_maps_list:
                    map_to_run = map_to_run.strip()
                    if map_to_run not in ['climate', 'forecast', 'correlation']:
                        raise
                    config_run.settings['maps'][map_to_run] = True
            except:
                console.msg_error_configuration('maps',_("the maps options are: 'climate', 'forecast', "
                    "'correlation' (comma separated), or 'all'."))
            settings["maps"] = colored.green(','.join(map(str, [m for m in config_run.settings['maps'] if config_run.settings['maps'][m]])))

        # marks_stations
        if config_run.settings['marks_stations'] in ["enable", "default", True]:
            settings["marks_stations"] = colored.green(_("enabled"))
            config_run.settings['marks_stations'] = True
        elif config_run.settings['marks_stations'] in ["disable", False]:
            config_run.settings['marks_stations'] = False
        else:
            console.msg_error_configuration('marks_stations', _("The marks_stations is wrong, the options are:\n"
                                                                "disable, enable or default."))
        # set the overlapping solution
        if config_run.settings['overlapping'] == "default" or not config_run.settings['overlapping']:
            config_run.settings['overlapping'] = "average"
            settings['overlapping'] = config_run.settings['overlapping']
        elif config_run.settings['overlapping'] in ["average", "maximum", "minimum", "neither"]:
            settings['overlapping'] = colored.green(config_run.settings['overlapping'])
        else:
            console.msg_error_configuration('overlapping', _("The overlapping solution is wrong, the options are:\n"
                                "default, average, maximum, minimum or neither"))
        # shape_boundary method
        # TODO: add more method for cut map interpolation around shape
        if config_run.settings['shape_boundary'] in ["enable", True]:
            settings["shape_boundary"] = colored.green(_("enabled"))
        elif config_run.settings['shape_boundary'] in ["default", False]:
            config_run.settings['shape_boundary'] = False
        else:
            console.msg_error_configuration('shape_boundary', _("The shape_boundary is wrong, the options are:\n"
                                "disable, enable or default."))

    ## post-get
    # ------------------------
    # when climate is disable:
    if not config_run.settings['climate_process']:
        console.msg(_("\nClimate process is disable, then forecast and maps\n"
                      "process will be disabled."), color="yellow")
        settings["forecast_process"] = colored.red(_("disabled"))
        settings["maps"] = colored.red(_("disabled"))

    # save input settings
    globals_vars.input_settings = settings