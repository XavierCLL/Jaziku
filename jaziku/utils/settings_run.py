#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2011-2012 IDEAM
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
                "overlapping": None,
                "shape_boundary": colored.red(_("disabled"))}

    ## general options
    # data_analysis
    if globals_vars.config_run['data_analysis'] == True:
        settings["data_analysis"] = colored.green(_("enabled"))
    elif not globals_vars.config_run['data_analysis'] == False:
        console.msg_error(_("'data_analysis' variable in runfile is wrong,\n"
                            "this must be 'enable' or 'disable'"), False)
    # climate_process
    if globals_vars.config_run['climate_process'] == True:
        settings["climate_process"] = colored.green(_("enabled"))
    elif not globals_vars.config_run['climate_process'] == False:
        console.msg_error(_("'climate_process' variable in runfile is wrong,\n"
                            "this must be 'enable' or 'disable'"), False)
    # forecasting_process
    if globals_vars.config_run['forecasting_process'] == True:
        settings["forecasting_process"] = colored.green(_("enabled"))
    elif not globals_vars.config_run['forecasting_process'] == False:
        console.msg_error(_("'forecasting_process' variable in runfile is wrong,\n"
                            "this must be 'enable' or 'disable'"), False)
    # analysis_interval
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

    return settings

def show(settings):
    print _("\nConfiguration run:")
    console.msg("   General options", color='cyan')
    print "   {0} --------- {1}".format("data analysis", settings["data_analysis"])
    print "   {0} ------- {1}".format("climate process", settings["climate_process"])
    print "   {0} --- {1}".format("forecasting process", settings["forecasting_process"])
    print "   {0} ----- {1}".format("analysis interval", settings["analysis_interval"])
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
    if globals_vars.config_run['forecasting_process']:
        console.msg("   Forecasting options", color='cyan')
    console.msg("   Maps options", color='cyan')
    print "   {0} ------------------ {1}".format("maps", settings["maps"])
    if globals_vars.config_run['maps']:
        print "   {0} ----------- {1}".format("overlapping", settings["overlapping"])
        print "   {0} -------- {1}".format("shape boundary", settings["shape_boundary"])


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

    if not globals_vars.args.force:

        query = query_yes_no(_("\nPlease check the configuration to run, do you want to continue?"))

        if not query:
            console.msg(_("\nexit"),color='red')
            console.msg_footer()
            sys.exit()