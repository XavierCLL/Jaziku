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
from jaziku.modules.maps import maps
from jaziku.modules.maps.grid import search_and_set_internal_grid, set_particular_grid
from jaziku.utils import console, output, input, array

# TODO: merge with get.py


def configuration_run():

    # ------------------------
    # class_category_analysis

    env.config_run.settings['class_category_analysis'] = input.to_int(env.config_run.settings['class_category_analysis'])

    if env.config_run.settings['class_category_analysis'] not in [3,7]:
        console.msg_error_configuration('class_category_analysis',
            _("The 'class_category_analysis' not is valid,\n"
              "this should be 3 or 7.").format(env.config_run.settings['class_category_analysis']))

    def categories_labels_var_I_dictionary(func):
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
        if env.config_run.settings['categories_labels_var_I'] == "default":
            env.config_run.settings['categories_labels_var_I'] = env.globals_vars.categories()
        else:
            if len(env.config_run.settings['categories_labels_var_I']) == 3:
                env.config_run.settings['categories_labels_var_I']\
                    = [unicode(label, 'utf-8') for label in env.config_run.settings['categories_labels_var_I']]
            else:
                console.msg_error_configuration('categories_labels_var_I',
                    _("The 'categories_labels_var_I' is not valid,\n"
                      "this should be 3 labels in different column."))

    if env.config_run.settings['class_category_analysis'] == 7:
        if env.config_run.settings['categories_labels_var_I'] == "default":
            env.config_run.settings['categories_labels_var_I'] = env.globals_vars.categories()
        else:
            if len(env.config_run.settings['categories_labels_var_I']) == 7:
                env.config_run.settings['categories_labels_var_I'] \
                    = [unicode(label, 'utf-8') for label in env.config_run.settings['categories_labels_var_I']]
            else:
                console.msg_error_configuration('categories_labels_var_I',
                    _("The 'categories_labels_var_I' is not valid,\n"
                      "this should be 7 labels in different column."))

    # ------------------------
    # consistent_data

    if env.config_run.settings['consistent_data'] is not False:
        try:
            env.config_run.settings['consistent_data'] = input.to_float(env.config_run.settings['consistent_data'])
            if env.config_run.settings['consistent_data'] < 0 or \
               env.config_run.settings['consistent_data'] > 100 or\
               env.config_run.settings['consistent_data'] is True:
                raise
        except:
            console.msg_error_configuration('consistent_data',
                    _("The 'consistent_data' is not valid,\n"
                      "this should be 'disable', 'default' or\n"
                      "valid percentage between 0 to 100."))

    # ------------------------
    # graphics
    if env.config_run.settings['graphics'] is None:
        console.msg_error_configuration('graphics',
            _("The '{0}' no was defined.")
            .format('graphics'))

    # ------------------------
    # categories_labels_var_I

    @categories_labels_var_I_dictionary
    def format_labels(labels_list):
        return labels_list

    env.config_run.settings['categories_labels_var_I'] = format_labels(env.config_run.settings['categories_labels_var_I'])

    # ------------------------
    # relevant_climate_categories_var_I

    labels = env.globals_vars.categories(translated=False)

    if not env.config_run.settings['relevant_climate_categories_var_I'] == "all":
        # check dimension
        if len(env.config_run.settings['relevant_climate_categories_var_I']) not in [1,2]:
            console.msg_error_configuration('relevant_climate_categories_var_I',
                _("The 'relevant_climate_categories_var_I' should be\n"
                  "'all' or one or two valid labels for {0} categories\n"
                  "(in different column), such as:\n\n{1}")
                .format(env.config_run.settings['class_category_analysis'], labels.values()))
        # check if are valid labels
        for _label in env.config_run.settings['relevant_climate_categories_var_I']:
            if _label not in labels.values():
                console.msg_error_configuration('relevant_climate_categories_var_I',
                    _("The '{0}' in 'relevant_climate_categories_var_I'\n"
                      "not is a valid label for {1} categories, should be\n"
                      "one of these:\n\n{2}")
                    .format(_label, env.config_run.settings['class_category_analysis'], labels.values()))

    # ------------------------
    # type_var_D
    if env.config_run.settings['type_var_D'] is None:
        console.msg_error_configuration('type_var_D',
            _("The '{0}' no was defined.")
            .format('type_var_D'))

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
                      "this type of series not accept this calculation mode.\n"
                      "For {0} the options are: {2}")
                        .format(env.var_D.TYPE_SERIES, env.config_run.settings['mode_calculation_series_D'],
                                env.var_D.MODE_CALCULATION_SERIES[env.var_D.TYPE_SERIES]))
        env.globals_vars.input_settings["mode_calculation_series_D"] = colored.green(env.config_run.settings['mode_calculation_series_D'])
    else:
        console.msg_error_configuration('mode_calculation_series_D', _("The 'mode_calculation_series_D' is invalid, the options are:\n"
                                                                       "default, accumulate or mean"))

    mode_calculation_series_i18n = [_('accumulate'), _('mean')]
    env.config_run.settings['mode_calculation_series_D_i18n']\
        = mode_calculation_series_i18n[['accumulate', 'mean'].index(env.config_run.settings['mode_calculation_series_D'])]

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
            env.config_run.settings['limits_var_D']['below'] = input.to_float(env.config_run.settings['limits_var_D']['below'])
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
            env.config_run.settings['limits_var_D']['above'] = input.to_float(env.config_run.settings['limits_var_D']['above'])
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
                _("The thresholds for {0} categories must have {1} values,\n"
                  "or use 'default' for thresholds by default defined for this variable.")
                .format(env.config_run.settings['class_category_analysis'], env.config_run.settings['class_category_analysis']-1))

    # ------------------------
    # type_var_I
    if env.config_run.settings['type_var_I'] is None:
        console.msg_error_configuration('type_var_I',
            _("The '{0}' no was defined.")
            .format('type_var_I'))

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

    env.config_run.settings['mode_calculation_series_I_i18n']\
        = mode_calculation_series_i18n[['accumulate', 'mean'].index(env.config_run.settings['mode_calculation_series_I'])]

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
            env.config_run.settings['limits_var_I']['below'] = input.to_float(env.config_run.settings['limits_var_I']['below'])
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
            env.config_run.settings['limits_var_I']['above'] = input.to_float(env.config_run.settings['limits_var_I']['above'])
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
    # located in data/var_I/
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
    # check the probability_forecast_values and forecast date

    # if forecast_process is activated
    if env.config_run.settings['forecast_process']:

        # ------------------------
        ## check and reset the values for forecast process, 3x3, 3x7 or 7x7
        for lag in [str(lag) for lag in env.globals_vars.ALL_LAGS]:
            try:
                env.config_run.settings['forecast_var_I_lag_'+lag] \
                    = [input.to_float(item) for item in env.config_run.settings['forecast_var_I_lag_'+lag]]
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
                        # complete arrays if is needed for the last items with ''
                        for idx in range(7):
                            try:
                                env.config_run.settings['forecast_var_I_lag_'+lag][idx]
                            except:
                                env.config_run.settings['forecast_var_I_lag_'+lag].append('')
                        env.globals_vars.input_settings['forecast_var_I_lag_'+lag] = env.config_run.settings['forecast_var_I_lag_'+lag]

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
                if env.config_run.settings['analysis_interval'] in ['monthly', 'bimonthly', 'trimonthly']:
                    raise

                forecast_month = int(env.config_run.settings['forecast_date'][0])
                forecast_day = int(env.config_run.settings['forecast_date'][1])

                env.config_run.settings['forecast_date'][0] = int(env.config_run.settings['forecast_date'][0])
            else:
                if env.config_run.settings['analysis_interval'] in ['5days', '10days', '15days']:
                    raise

                if env.config_run.settings['analysis_interval'] in ['monthly']:
                    env.config_run.settings['forecast_date'] = int(float(env.config_run.settings['forecast_date']))
                else:
                    if len(env.config_run.settings['forecast_date']) == 2:
                        env.config_run.settings['forecast_date'] = input.bimonthly_char2int(env.config_run.settings['forecast_date'])
                    if len(env.config_run.settings['forecast_date']) == 3:
                        env.config_run.settings['forecast_date'] = input.trimonthly_char2int(env.config_run.settings['forecast_date'])
                forecast_month = int(env.config_run.settings['forecast_date'])
        except:
            if env.config_run.settings['analysis_interval'] in ['monthly', 'bimonthly', 'trimonthly']:
                if env.config_run.settings['analysis_interval'] in ['monthly']:
                    console.msg_error_configuration('forecast_date',
                        _("The date for forecast '{0}' is invalid, "
                          "must be a valid integer of month (e.g. 2 for february).")
                        .format(env.config_run.settings['forecast_date']))
                else:
                    if env.config_run.settings['analysis_interval'] in ['bimonthly']:
                        example =  _("(e.g. 'as' for august and september)")
                    if env.config_run.settings['analysis_interval'] in ['trimonthly']:
                        example =  _("(e.g. 'aso' for august, september and october).")
                    console.msg_error_configuration('forecast_date',
                        _("The date for forecast '{0}' is invalid, must be a\n"
                          "valid characters for {1} {2}.")
                        .format(env.config_run.settings['forecast_date'],
                                env.config_run.settings['analysis_interval'],
                                example))
            elif env.config_run.settings['analysis_interval'] in ['5days', '10days', '15days']:
                if env.config_run.settings['analysis_interval'] in ['5days']:
                    example =  _("(e.g. '10;16' for period 16 to 20 of october)")
                if env.config_run.settings['analysis_interval'] in ['10days']:
                    example =  _("(e.g. '10;11' for period 11 to 20 of october)")
                if env.config_run.settings['analysis_interval'] in ['15days']:
                    example =  _("(e.g. '10;1' for period 1 to 15 of october)")
                console.msg_error_configuration('forecast_date',
                    _("The date for forecast '{0}' is invalid, must be a\n"
                      "valid month and start day for {1} 'month;day' where\n"
                      "the month is a integer and the day is a start day of\n"
                      "interval analysis {2}.")
                    .format(env.config_run.settings['forecast_date'],
                            env.config_run.settings['analysis_interval'], example))

        if env.config_run.settings['analysis_interval'] in ['5days', '10days', '15days', 'monthly']:
            if not (1 <= forecast_month <= 12):
                console.msg_error_configuration('forecast_date',
                    _("The month for forecast '{0}' is invalid, "
                      "must be a valid month number (1-12)")
                    .format(forecast_month))

        # set the forecast date by days
        if isinstance(env.config_run.settings['forecast_date'], list):

            if not (1 <= env.config_run.settings['forecast_date'][1] <= 31):
                console.msg_error_configuration('forecast_date',
                    _("The day for forecast process '{0}' is invalid, \n"
                      "must be a valid day number (1-31)")
                    .format(env.config_run.settings['forecast_date'][1]))

            env.config_run.settings['forecast_date'] = {'month':forecast_month,'day':forecast_day}

            if env.config_run.settings['forecast_date']['day'] not in analysis_interval.get_range_analysis_interval():
                console.msg_error_configuration('forecast_date',
                    _("Start day (month/day) for forecast process '{0}'\nis invalid, "
                      "must be a valid start day based on\nrange analysis "
                      "interval, the valid start days for\n{1} are: {2}")
                    .format(env.config_run.settings['forecast_date']['day'],
                            env.config_run.settings['analysis_interval_i18n'],
                            analysis_interval.get_range_analysis_interval()))

            env.config_run.settings['forecast_date']['text'] \
                = output.analysis_interval_text(env.config_run.settings['forecast_date']['month'],
                                                env.config_run.settings['forecast_date']['day'])

        # set the forecast date by month
        else:
            env.config_run.settings['forecast_date'] = {'month':forecast_month}

            env.config_run.settings['forecast_date']['text'] \
                = output.analysis_interval_text(env.config_run.settings['forecast_date']['month'])

        env.globals_vars.input_settings["forecast_date"] = colored.green(env.config_run.settings['forecast_date']['text'])


def grids_list():
    """Initialize all grids with its properties defined in runfile
    """

    # not check the grids list when maps options is disable
    if not env.config_run.settings['maps']:
        return

    # init the input_settings for show all grids in console
    env.globals_vars.input_settings["grid"] = []
    env.globals_vars.input_settings["shape_path"] = []
    env.globals_vars.input_settings["latitude"] = []
    env.globals_vars.input_settings["longitude"] = []
    env.globals_vars.input_settings["grid_resolution"] = []
    env.globals_vars.input_settings["semivariogram_type"] = []
    env.globals_vars.input_settings["radiuses"] = []
    env.globals_vars.input_settings["max_neighbours"] = []

    for grid in maps.Grid.all_grids:
        ## grid
        # set name_grid, country and grid_path
        if isinstance(grid.grid, list):
            if len(grid.grid) == 1:
                grid.grid_name = grid.grid_fullname = grid.country = grid.grid[0]
            else:
                grid.grid_name = grid.grid[0]
                grid.grid_fullname = grid.grid[0] + " (" + grid.grid[1] + ")"
                grid.country = grid.grid[1]
            if grid.shape_path == "internal":
                grid.grid_path = os.path.join(grid.grid[1], grid.grid[0])
        else:
            grid.grid_name = grid.grid_fullname = grid.country = grid.grid
            if grid.shape_path == "internal":
                grid.grid_path = os.path.join(grid.grid, grid.grid)

        env.globals_vars.input_settings["grid"].append(colored.green(grid.grid_fullname))

        ## shape_path
        # check if grid defined path to shape else search and set internal shape, lat and lon of grid
        if grid.shape_path == "internal":
            try:
                search_and_set_internal_grid(grid)
            except ValueError as error:
                console.msg_error_configuration("grid","\n"+str(error), stop_in_grid=grid.num)
            env.globals_vars.input_settings["shape_path"].append("internal")
        else:
            try:
                set_particular_grid(grid)
            except ValueError as error:
                console.msg_error_configuration("shape_path","\n"+str(error), stop_in_grid=grid.num)
            env.globals_vars.input_settings["shape_path"].append(grid.shape_path)

        ## latitude
        if not grid.latitude == "internal":
            if isinstance(grid.latitude, list) and len(grid.latitude) == 2 and not False in [isinstance(x, (int, float)) for x in grid.latitude]:
                grid.minlat = input.to_float(grid.latitude[0])
                grid.maxlat = input.to_float(grid.latitude[1])
            else:
                console.msg_error_configuration("latitude",
                    _("The latitude values are wrong, these must be\n"
                      "decimal degrees, and two values: minlat and maxlat\n"
                      "in different column."), stop_in_grid=grid.num)
        else:
            if not grid.is_internal:
                console.msg_error_configuration("latitude",
                    _("Can't defined 'latitude' as 'internal' if 'shape_path'\n"
                      "was not defined as 'internal'.\n"), stop_in_grid=grid.num)
        if grid.minlat >= grid.maxlat or\
           grid.minlat < -90 or grid.minlat > 90 or \
           grid.maxlat < -90 or grid.maxlat > 90:
            console.msg_error_configuration("latitude",
                _("The latitude values are wrong, the minlat must be\n"
                  "less to maxlat and their values must be between\n"
                  "-90 to 90."), stop_in_grid=grid.num)

        env.globals_vars.input_settings["latitude"].append('{0} | {1}'.format(grid.minlat, grid.maxlat))

        ## longitude
        if not grid.longitude == "internal":
            if isinstance(grid.longitude, list) and len(grid.longitude) == 2 and not False in [isinstance(x, (int, float)) for x in grid.longitude]:
                grid.minlon = input.to_float(grid.longitude[0])
                grid.maxlon = input.to_float(grid.longitude[1])
            else:
                console.msg_error_configuration("longitude",
                    _("The longitude values are wrong, these must be\n"
                      "decimal degrees, and two values: minlon and maxlon\n"
                      "in different column."), stop_in_grid=grid.num)
        else:
            if not grid.is_internal:
                console.msg_error_configuration("longitude",
                    _("Can't defined 'longitude' as 'internal' if 'shape_path'\n"
                      "was not defined as 'internal'.\n"), stop_in_grid=grid.num)
        if grid.minlon >= grid.maxlon or\
           grid.minlon < -180 or grid.minlon > 180 or \
           grid.minlon < -180 or grid.maxlon > 180:
            console.msg_error_configuration("longitude",
                _("The longitude values are wrong, the minlon must be\n"
                  "less to maxlon and their values must be between\n"
                  "-180 to 180."), stop_in_grid=grid.num)

        env.globals_vars.input_settings["longitude"].append('{0} | {1}'.format(grid.minlon, grid.maxlon))

        ## set the  mainly variables for grid
        grid.grid_properties()


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
            console.msg(_("   The code '{0}' of the station '{1}' is repeat\n"
                          "   with other stations, is recommend that the code and name\n"
                          "   of stations be different. This is only a recommendation,\n"
                          "   you can continue.").format(station.code, station.name), color='yellow')
            return
        elif not station.code in list_codes and station.name in list_names:
            console.msg(_("WARNING:"), color='yellow')
            console.msg(_("   The name '{0}' of the station with code '{1}' is repeat\n"
                          "   with other stations, is recommend that the code and name\n"
                          "   of stations be different. This is only a recommendation,\n"
                          "   you can continue.").format(station.name, station.code), color='yellow')
            return
        else:
            list_codes.append(station.code)
            list_names.append(station.name)

    # -------------------------------------------------------------------------
    # check the latitude, longitude and altitude for each stations

    if env.config_run.settings['maps']:
        for station in stations_list:

            if station.lat < -90 or station.lat > 90:
                console.msg_error_line_stations(station,
                    _("The latitude values are wrong, must be between\n"
                      "-90 to 90."))

            if station.lon < -180 or station.lon > 180:
                console.msg_error_line_stations(station,
                    _("The longitude values are wrong, must be between\n"
                      "-180 to 180."))

            if station.alt < -1000 or station.alt > 10000:
                console.msg_error_line_stations(station,
                    _("The altitude values are wrong, must be between\n"
                      "-1000 to 10000."))

    # finish, check all good
    console.msg(_("done"), color='green')
