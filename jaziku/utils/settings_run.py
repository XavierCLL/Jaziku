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
import sys

from jaziku.utils import globals_vars, console


def get():

    # set settings default
    settings = {"data_analysis": colored.red(_("disabled")),
                "climate_process": colored.red(_("disabled")),
                "forecasting_process": colored.red(_("disabled")),
                "process_period": colored.red(_("disabled")),
                "analog_year": colored.red(_("disabled")),
                "lags": None,
                "language": globals_vars.config_run['language'],
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

    globals_vars.settings = settings

    ## general options
    # data_analysis
    if globals_vars.config_run['data_analysis'] == True:
        settings["data_analysis"] = colored.green(_("enabled"))
    elif not globals_vars.config_run['data_analysis'] == False:
        console.msg_error_configuration('data_analysis', _("'data_analysis' variable in runfile is wrong,\n"
                                                           "this must be 'enable' or 'disable'"))
    # climate_process
    if globals_vars.config_run['climate_process'] == True:
        settings["climate_process"] = colored.green(_("enabled"))
    elif not globals_vars.config_run['climate_process'] == False:
        console.msg_error_configuration('climate_process', _("'climate_process' variable in runfile is wrong,\n"
                            "this must be 'enable' or 'disable'"))
    # forecasting_process
    if globals_vars.config_run['forecasting_process'] == True:
        settings["forecasting_process"] = colored.green(_("enabled"))
    elif not globals_vars.config_run['forecasting_process'] == False:
        console.msg_error_configuration('forecasting_process', _("'forecasting_process' variable in runfile is wrong,\n"
                            "this must be 'enable' or 'disable'"))

    # analysis interval
    if globals_vars.config_run['analysis_interval'] not in globals_vars.options_analysis_interval:
        console.msg_error_configuration('analysis_interval',
            _("The 'analysis_interval' defined in runfile {0} is invalid,\nmust be one of these: {1}")
            .format(globals_vars.config_run['analysis_interval'], ', '.join(globals_vars.options_analysis_interval)))

    if globals_vars.config_run['analysis_interval'] != "trimester":
        # detect analysis_interval number from string
        _count = 0
        for digit in globals_vars.config_run['analysis_interval']:
            try:
                int(digit)
                _count += 1
            except:
                pass
        globals_vars.analysis_interval_num_days = int(globals_vars.config_run['analysis_interval'][0:_count])

    translate_analysis_interval = [_("5days"), _("10days"), _("15days"), _("trimester")]
    globals_vars.translate_analysis_interval\
    = translate_analysis_interval[globals_vars.options_analysis_interval.index(globals_vars.config_run['analysis_interval'])]
    # analysis_interval setting
    if globals_vars.config_run['analysis_interval']:
        settings["analysis_interval"] = colored.green(globals_vars.config_run['analysis_interval'])


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
            console.msg_error_configuration('process_period',
                _("The period must be: year_start-year_end (ie. 1980-2008)\n"
                  "or 'maximum' for take the process period maximum possible.\n\n{0}").format(e))
    # analog_year
    if globals_vars.config_run['analog_year']:
        try:
            globals_vars.config_run['analog_year'] = int(globals_vars.config_run['analog_year'])
        except:
            console.msg_error_configuration('analog_year', "the analog_year must be a valid year")
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
            console.msg_error_configuration('lags', _("The lags may be: 0, 1 and/or 2 (comma separated), 'all' or 'default'"))
        settings["lags"] = colored.green(','.join(map(str, globals_vars.lags)))
    # languages
    settings["language"] = globals_vars.config_run['language']
    ## input options
    # type var D
    if globals_vars.config_run['type_var_D']:
        settings["type_var_D"] = colored.green(globals_vars.config_run['type_var_D']) + " ({0})".format(globals_vars.units_var_D)
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
        settings["type_var_I"] = colored.green(globals_vars.config_run['type_var_I']) + " ({0})".format(globals_vars.units_var_I)
    # path_to_file_var_I
    if globals_vars.config_run['path_to_file_var_I'] == 'internal':
        settings["path_to_file_var_I"] = colored.green(globals_vars.config_run['path_to_file_var_I'])
    else:
        settings["path_to_file_var_I"] = globals_vars.config_run['path_to_file_var_I']
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

    ## forecasting settings
    if globals_vars.config_run['forecasting_process']:
        settings["lag_0_phen_below"] = globals_vars.config_run['lag_0_phen_below']
        settings["lag_0_phen_normal"] = globals_vars.config_run['lag_0_phen_normal']
        settings["lag_0_phen_above"] = globals_vars.config_run['lag_0_phen_above']
        settings["lag_1_phen_below"] = globals_vars.config_run['lag_1_phen_below']
        settings["lag_1_phen_normal"] = globals_vars.config_run['lag_1_phen_normal']
        settings["lag_1_phen_above"] = globals_vars.config_run['lag_1_phen_above']
        settings["lag_2_phen_below"] = globals_vars.config_run['lag_2_phen_below']
        settings["lag_2_phen_normal"] = globals_vars.config_run['lag_2_phen_normal']
        settings["lag_2_phen_above"] = globals_vars.config_run['lag_2_phen_above']
        settings["forecasting_date"] = colored.green(globals_vars.config_run['forecasting_date'])

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
                console.msg_error_configuration('maps',_("the maps options are: 'climate', 'forecasting', "
                    "'correlation' (comma separated), or 'all'."))
            settings["maps"] = colored.green(','.join(map(str, [m for m in globals_vars.maps if globals_vars.maps[m]])))

        # marks_stations
        if globals_vars.config_run['marks_stations'] in ["enable", "default", True]:
            settings["marks_stations"] = colored.green(_("enabled"))
            globals_vars.config_run['marks_stations'] = True
        elif globals_vars.config_run['marks_stations'] in ["disable", False]:
            globals_vars.config_run['marks_stations'] = False
        else:
            console.msg_error_configuration('marks_stations', _("The marks_stations is wrong, the options are:\n"
                                                                "disable, enable or default."))
        # set the overlapping solution
        if globals_vars.config_run['overlapping'] == "default" or not globals_vars.config_run['overlapping']:
            globals_vars.config_run['overlapping'] = "average"
            settings['overlapping'] = globals_vars.config_run['overlapping']
        elif globals_vars.config_run['overlapping'] in ["average", "maximum", "minimum", "neither"]:
            settings['overlapping'] = colored.green(globals_vars.config_run['overlapping'])
        else:
            console.msg_error_configuration('overlapping', _("The overlapping solution is wrong, the options are:\n"
                                "default, average, maximum, minimum or neither"))
        # shape_boundary method
        # TODO: add more method for cut map interpolation around shape
        if globals_vars.config_run['shape_boundary'] in ["enable", True]:
            settings["shape_boundary"] = colored.green(_("enabled"))
        elif globals_vars.config_run['shape_boundary'] in ["default", False]:
            globals_vars.config_run['shape_boundary'] = False
        else:
            console.msg_error_configuration('shape_boundary', _("The shape_boundary is wrong, the options are:\n"
                                "disable, enable or default."))

    # when climate is disable:
    if not globals_vars.config_run['climate_process']:
        console.msg(_("\nClimate process is disable, then forecasting and maps\n"
                      "process will be disabled."), color="yellow")
        settings["forecasting_process"] = colored.red(_("disabled"))
        settings["maps"] = colored.red(_("disabled"))


    return settings


def show(stop_in=None):

    settings = globals_vars.settings

    if stop_in != None:
        settings[stop_in] = '?'

    print _("\nConfiguration run:")
    console.msg("   General options", color='cyan')
    print "   {0} --------- {1}".format("data analysis", settings["data_analysis"])
    if stop_in == "data_analysis": return
    print "   {0} ------- {1}".format("climate process", settings["climate_process"])
    if stop_in == "climate_process": return
    print "   {0} --- {1}".format("forecasting process", settings["forecasting_process"])
    if stop_in == "forecasting_process": return
    print "   {0} ----- {1}".format("analysis interval", settings["analysis_interval"])
    if stop_in == "analysis_interval": return
    print "   {0} -------- {1}".format("process period", settings["process_period"])
    if stop_in == "process_period": return
    print "   {0} ----------- {1}".format("analog year", settings["analog_year"])
    if stop_in == "analog_year": return
    print "   {0} ------------------ {1}".format("lags", settings["lags"])
    if stop_in == "lags": return
    print "   {0} -------------- {1}".format("language", settings["language"])
    if stop_in == "language": return
    console.msg("   Var D options", color='cyan')
    print "   {0} ------------ {1}".format("type var D", settings["type_var_D"])
    if stop_in == "type_var_D": return
    print "   {0} ----- {1}".format("limit var D below", settings["limit_var_D_below"])
    if stop_in == "limit_var_D_below": return
    print "   {0} ----- {1}".format("limit var D above", settings["limit_var_D_above"])
    if stop_in == "limit_var_D_above": return
    print "   {0} - {1}".format("threshold below var D", settings["threshold_below_var_D"])
    if stop_in == "threshold_below_var_D": return
    print "   {0} - {1}".format("threshold above var D", settings["threshold_above_var_D"])
    if stop_in == "threshold_above_var_D": return
    console.msg("   Var I options", color='cyan')
    print "   {0} ------------ {1}".format("type var I", settings["type_var_I"])
    if stop_in == "type_var_I": return
    print "   {0} ---- {1}".format("path to file var I", settings["path_to_file_var_I"])
    if stop_in == "path_to_file_var_I": return
    print "   {0} ----- {1}".format("limit var I below", settings["limit_var_I_below"])
    if stop_in == "limit_var_I_below": return
    print "   {0} ----- {1}".format("limit var I above", settings["limit_var_I_above"])
    if stop_in == "limit_var_I_above": return
    print "   {0} - {1}".format("threshold below var I", settings["threshold_below_var_I"])
    if stop_in == "threshold_below_var_I": return
    print "   {0} - {1}".format("threshold above var I", settings["threshold_above_var_I"])
    if stop_in == "threshold_above_var_I": return
    console.msg("   Check options", color='cyan')
    print "   {0} ------- {1}".format("consistent data", settings["consistent_data"])
    if stop_in == "consistent_data": return
    print "   {0} --------- {1}".format("risk analysis", settings["risk_analysis"])
    if stop_in == "risk_analysis": return
    console.msg("   Output options", color='cyan')
    print "   {0} -------------- {1}".format("graphics", settings["graphics"])
    if stop_in == "graphics": return
    print "   {0} ------ {1}".format("phen below label", settings["phen_below_label"])
    if stop_in == "phen_below_label": return
    print "   {0} ----- {1}".format("phen normal label", settings["phen_normal_label"])
    if stop_in == "phen_normal_label": return
    print "   {0} ------ {1}".format("phen above label", settings["phen_above_label"])
    if stop_in == "phen_above_label": return
    if globals_vars.config_run['forecasting_process']:
        console.msg("   Forecasting options", color='cyan')
        print "   {0} ------ {1}".format("lag 0 phen below", settings["lag_0_phen_below"])
        if stop_in == "lag_0_phen_below": return
        print "   {0} ----- {1}".format("lag 0 phen normal", settings["lag_0_phen_normal"])
        if stop_in == "lag_0_phen_normal": return
        print "   {0} ------ {1}".format("lag 0 phen above", settings["lag_0_phen_above"])
        if stop_in == "lag_0_phen_above": return
        if stop_in == "lag_0_phen": return
        print "   {0} ------ {1}".format("lag 1 phen below", settings["lag_1_phen_below"])
        if stop_in == "lag_1_phen_below": return
        print "   {0} ----- {1}".format("lag 1 phen normal", settings["lag_1_phen_normal"])
        if stop_in == "lag_1_phen_normal": return
        print "   {0} ------ {1}".format("lag 1 phen above", settings["lag_1_phen_above"])
        if stop_in == "lag_1_phen_above": return
        if stop_in == "lag_1_phen": return
        print "   {0} ------ {1}".format("lag 2 phen below", settings["lag_2_phen_below"])
        if stop_in == "lag_2_phen_below": return
        print "   {0} ----- {1}".format("lag 2 phen normal", settings["lag_2_phen_normal"])
        if stop_in == "lag_2_phen_normal": return
        print "   {0} ------ {1}".format("lag 2 phen above", settings["lag_2_phen_above"])
        if stop_in == "lag_2_phen_above": return
        if stop_in == "lag_2_phen": return
        print "   {0} ------ {1}".format("forecasting date", settings["forecasting_date"])
        if stop_in == "forecasting_date": return
    console.msg("   Maps options", color='cyan')
    print "   {0} ------------------ {1}".format("maps", settings["maps"])
    if stop_in == "maps": return
    if globals_vars.config_run['maps']:
        print "   {0} -------- {1}".format("marks_stations", settings["marks_stations"])
        if stop_in == "marks_stations": return
        print "   {0} ----------- {1}".format("overlapping", settings["overlapping"])
        if stop_in == "overlapping": return
        print "   {0} -------- {1}".format("shape boundary", settings["shape_boundary"])
        if stop_in == "shape_boundary": return

    # Print some warnings and notifications

    if globals_vars.config_run['path_to_file_var_I'] == 'internal':
        internal_file_I_name = globals_vars.internal_var_I_files[globals_vars.config_run['type_var_I']]
        split_internal_var_I = internal_file_I_name.split(".")[0].split("_")
        console.msg(
            _("\n > You are using internal files for independent\n"
              "   variable defined as {0} which has data from\n"
              "   {1} to {2} and the source of data was\n"
              "   obtained in {3}.\n"
              "   url: {4}")
            .format(split_internal_var_I[0], split_internal_var_I[1],
                split_internal_var_I[2], ' '.join(split_internal_var_I[3::]),
                globals_vars.internal_var_I_urls[globals_vars.config_run['type_var_I']]), color='yellow')

    if (not globals_vars.config_run['limit_var_D_below'] or
        not globals_vars.config_run['limit_var_D_above'] or
        not globals_vars.config_run['limit_var_I_below'] or
        not globals_vars.config_run['limit_var_I_above']):
        console.msg(_("\n > WARNING: you are using one or more limits as\n"
                      "   'none' value, this means that series values\n"
                      "   will not be checked if they are valid in\n"
                      "   its limits coherent. This option is not\n"
                      "   recommended, use it with precaution"), color='yellow')


def check():

    # -------------------------------------------------------------------------
    # limits var D

    # check and validate if file D is defined as particular file with
    # particular range validation

    # below var D
    if globals_vars.config_run['limit_var_D_below'] == "default":
        # validation type_D
        if globals_vars.config_run['type_var_D'] not in globals_vars.types_var_D:
            console.msg_error_configuration('type_var_D',
                _("{0} not is valid internal type for dependent variable if you\n"
                  "defined LIMIT VAR D BELOW/ABOVE as 'default'. If you want\n"
                  "define a particular type for dependent variable, you must define\n"
                  "as real values (or 'none') the LIMIT VAR D BELOW/ABOVE")
                .format(globals_vars.config_run['type_var_D']))
    elif globals_vars.config_run['limit_var_D_below'] in ["none", "None", "NONE", None]:
        globals_vars.config_run['limit_var_D_below'] = None
    else:
        try:
            globals_vars.config_run['limit_var_D_below'] = float(str(globals_vars.config_run['limit_var_D_below']).replace(',', '.'))
        except:
            console.msg_error_configuration('limit_var_D_below',
                (_("Problem with particular range validation for "
                   "dependent\nvariable: '{0}' this must be "
                   "a valid number, 'none' or 'default'.").format(globals_vars.config_run['limit_var_D_below'],)))
    # above var D
    if globals_vars.config_run['limit_var_D_above'] == "default":
        # validation type_D
        if globals_vars.config_run['type_var_D'] not in globals_vars.types_var_D:
            console.msg_error_configuration('limit_var_D_above',
                _("{0} not is valid internal type for dependent variable if you\n"
                  "defined LIMIT VAR D BELOW/ABOVE as 'default'. If you want\n"
                  "define a particular type for dependent variable, you must define\n"
                  "as real values (or 'none') the LIMIT VAR D BELOW/ABOVE")
                .format(globals_vars.config_run['type_var_D']))
    elif globals_vars.config_run['limit_var_D_above'] in ["none", "None", "NONE", None]:
        globals_vars.config_run['limit_var_D_above'] = None
    else:
        try:
            globals_vars.config_run['limit_var_D_above'] = float(str(globals_vars.config_run['limit_var_D_above']).replace(',', '.'))
        except:
            console.msg_error_configuration('limit_var_D_above',
                (_("Problem with particular range validation for "
                   "dependent\nvariable: '{0}' this must be "
                   "a valid number, 'none' or 'default'.").format(globals_vars.config_run['limit_var_D_above'],)))

    # -------------------------------------------------------------------------
    # limits var I

    # check and validate if file I is defined as particular file with
    # particular range validation

    # below var I
    if globals_vars.config_run['limit_var_I_below'] == "default":
        # validation type_I
        if globals_vars.config_run['type_var_I'] not in globals_vars.types_var_I:
            console.msg_error_configuration('type_var_I',
                _("{0} not is valid internal type for independent variable if you\n"
                  "defined LIMIT VAR I BELOW/ABOVE as 'default'. If you want\n"
                  "define a particular type for independent variable, you must define\n"
                  "as real values (or 'none') the LIMIT VAR I BELOW/ABOVE")
                .format(globals_vars.config_run['type_var_I']))
    elif globals_vars.config_run['limit_var_I_below'] in ["none", "None", "NONE", None]:
        globals_vars.config_run['limit_var_I_below'] = None
    else:
        try:
            globals_vars.config_run['limit_var_I_below'] = float(str(globals_vars.config_run['limit_var_I_below']).replace(',', '.'))
        except:
            console.msg_error_configuration('limit_var_I_below',
                (_("Problem with particular range validation for "
                   "independent\nvariable: '{0}' this must be "
                   "a valid number, 'none' or 'default'.").format(globals_vars.config_run['limit_var_I_below'],)))
    # above var I
    if globals_vars.config_run['limit_var_I_above'] == "default":
        # validation type_I
        if globals_vars.config_run['type_var_I'] not in globals_vars.types_var_I:
            console.msg_error_configuration('limit_var_I_above',
                _("{0} not is valid internal type for independent variable if you\n"
                  "defined LIMIT VAR I BELOW/ABOVE as 'default'. If you want\n"
                  "define a particular type for independent variable, you must define\n"
                  "as real values (or 'none') the LIMIT VAR I BELOW/ABOVE")
                .format(globals_vars.config_run['type_var_I']))
    elif globals_vars.config_run['limit_var_I_above'] in ["none", "None", "NONE", None]:
        globals_vars.config_run['limit_var_I_above'] = None
    else:
        try:
            globals_vars.config_run['limit_var_I_above'] = float(str(globals_vars.config_run['limit_var_I_above']).replace(',', '.'))
        except:
            console.msg_error_configuration('limit_var_I_above',
                (_("Problem with particular range validation for "
                   "independent\nvariable: '{0}' this must be "
                   "a valid number, 'none' or 'default'.").format(globals_vars.config_run['limit_var_I_above'],)))

    # -------------------------------------------------------------------------
    # path_to_file_var_I

    # read from internal variable independent files of Jaziku, check
    # and notify if Jaziku are using the independent variable inside
    # located in plugins/var_I/
    if globals_vars.config_run["path_to_file_var_I"] == "internal":
        if globals_vars.config_run["type_var_I"] not in globals_vars.internal_var_I_types:
            console.msg_error_configuration('path_to_file_var_I',
                _("The 'path_to_file_var_I' is defined as 'internal' but the\n"
                  "type of independent variable '{0}' not is a valid internal\n"
                  "type. Please change type I to valid internal type, or define\n"
                  "a valid path to file var I.").format(globals_vars.config_run["type_var_I"]))
    else:
        if not os.path.isfile(globals_vars.config_run["path_to_file_var_I"]):
            console.msg_error_configuration('path_to_file_var_I',
                _("Can't open file '{0}' for var I, \nplease check filename and check path relative (to runfile) or\n"
                  "absolute to var I. If you want run var I with internals files\n"
                  "of jaziku you need set 'PATH TO FILE VAR I' as 'internal'").format(globals_vars.config_run["path_to_file_var_I"]))

    # -------------------------------------------------------------------------
    # thresholds var_I

    if not globals_vars.config_run["path_to_file_var_I"] == "internal" and \
       globals_vars.config_run["type_var_I"] not in globals_vars.internal_var_I_types:
        if globals_vars.config_run["threshold_below_var_I"] == "default":
            console.msg_error_configuration('threshold_below_var_I',
                _("The thresholds can't be define as 'default' if the\n"
                  "type of independent variable not is valid internal type."))
        if globals_vars.config_run["threshold_above_var_I"] == "default":
            console.msg_error_configuration('threshold_above_var_I',
                _("The thresholds can't be define as 'default' if the\n"
                  "type of independent variable not is valid internal type."))

    # -------------------------------------------------------------------------
    # check the 9 forecasting values

    # if forecasting_process is activated
    if globals_vars.config_run['forecasting_process']:
        # lag 0
        lag_0 = globals_vars.config_run['lag_0_phen_below'] +\
                globals_vars.config_run['lag_0_phen_normal'] +\
                globals_vars.config_run['lag_0_phen_above']
        if not (99 < lag_0 < 101):
            console.msg_error_configuration('lag_0_phen',
                _("The sum for the 3 values of phenomenon for lag 0\n"
                  "in 'forecasting options' in runfile must be\nequal to 100."))

        # lag 1
        lag_1 = globals_vars.config_run['lag_1_phen_below'] +\
                globals_vars.config_run['lag_1_phen_normal'] +\
                globals_vars.config_run['lag_1_phen_above']
        if not (99 < lag_1 < 101):
            console.msg_error_configuration('lag_1_phen',
                _("The sum for the 3 values of phenomenon for lag 1\n"
                  "in 'forecasting options' in runfile must be\nequal to 100."))

        # lag 2
        lag_2 = globals_vars.config_run['lag_2_phen_below'] +\
                globals_vars.config_run['lag_2_phen_normal'] +\
                globals_vars.config_run['lag_2_phen_above']
        if not (99 < lag_2 < 101):
            console.msg_error_configuration('lag_2_phen',
                _("The sum for the 3 values of phenomenon for lag 2\n"
                  "in 'forecasting options' in runfile must be\nequal to 100."))


def check_station_list(stations):

    console.msg(_("\nChecking the stations list:"), newline=False)

    # -------------------------------------------------------------------------
    # check the code and/or name of stations don't repeat, exit or show warning
    # depending on the case.

    # first check error
    list_codes = []
    list_names = []
    for station in stations:
        if station.code in list_codes and station.name in list_names:
            console.msg_error_line_stations(station, _("The combination of the code and name of the station can't repeat,\n"
                                                       "many result will be replaced with the same code-name of station." ))
        else:
            list_codes.append(station.code)
            list_names.append(station.name)

    # check warnings, show and return with the first warning
    list_codes = []
    list_names = []
    for station in stations:
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


def query_yes_no(question, default="yes"):
    """
    Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes":True, "y":True, "YES":True, "Y":True,
             "no":False, "n":False, "NO":False, "N":False}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write(_("Please respond with 'y' or 'n'.\n"))

def continue_run():

    if not globals_vars.ARGS.force:

        query = query_yes_no(_("\nPlease check the configuration to run, continue?"))

        if not query:
            console.msg(_("\nexit"),color='red')
            console.msg_footer()
            sys.exit()