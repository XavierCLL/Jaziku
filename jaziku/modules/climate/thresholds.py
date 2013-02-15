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

import math
from scipy import stats
from datetime import date
from dateutil.relativedelta import relativedelta

from jaziku.core.input import input_validation
from jaziku.env import config_run, globals_vars
from jaziku.utils import console


def get_thresholds_var_D(station):
    """
    Calculate and return threshold by below and above
    of dependent variable, the type of threshold as
    defined by the user in station file, these may be:
    "default", "pNN" (percentile NN), "sdN" (standard
    deviation N) and particular value.
    """

    # Calculate percentile "below" and "above"
    def percentiles(below, above):

        threshold_below_var_D = stats.scoreatpercentile(station.var_D_values, below)
        threshold_above_var_D = stats.scoreatpercentile(station.var_D_values, above)
        return threshold_below_var_D, threshold_above_var_D

    # thresholds by below and by above of var D by default
    def thresholds_by_default():
        # check if analog_year is defined
        if config_run.settings['analog_year']:
            # check if analog_year is inside in process period
            if station.process_period['start'] <= config_run.settings['analog_year'] <= station.process_period['end']:

                _iter_date = date(config_run.settings['analog_year'], 1, 1)
                var_D_values_of_analog_year = []
                # get all raw values of var D only in analog year, ignoring null values
                while _iter_date <= date(config_run.settings['analog_year'], 12, 31):
                    if not globals_vars.is_valid_null(station.var_D.data[station.var_D.date.index(_iter_date)]):
                        var_D_values_of_analog_year.append(station.var_D.data[station.var_D.date.index(_iter_date)])
                    if station.var_D.frequency_data== "daily":
                        _iter_date += relativedelta(days=1)
                    if station.var_D.frequency_data== "monthly":
                        _iter_date += relativedelta(months=1)
                threshold_below_var_D = stats.scoreatpercentile(var_D_values_of_analog_year, 33)
                threshold_above_var_D = stats.scoreatpercentile(var_D_values_of_analog_year, 66)

                # check if thresholds are valid
                if math.isnan(threshold_below_var_D) or math.isnan(threshold_above_var_D):
                    if station.first_iter:
                        console.msg(_("\n > WARNING: Thresholds calculated with analog year for var_D are wrong,\n"
                                      "   using default thresholds instead"), color='yellow'),

                    return percentiles(33, 66)
                else:
                    if station.first_iter:
                        console.msg(_("\n   Using thresholds with analog year for var_D "), color='cyan'),

                    return threshold_below_var_D, threshold_above_var_D
            else:
                if station.first_iter:
                    console.msg(_("\n > WARNING: The analog year ({0}) for this\n"
                                   "   station is outside of process period {1} to\n"
                                   "   {2}. The process continue but using the\n"
                                   "   default thresholds .........................")
                    .format(config_run.settings['analog_year'],
                        station.process_period['start'],
                        station.process_period['end']), color='yellow', newline=False)
                return percentiles(33, 66)
        else:
            return percentiles(33, 66)

    # thresholds by below and by above of var D with standard deviation
    def thresholds_with_std_deviation(below, above):
        values_without_nulls = []
        for value in station.var_D_values:
            if not globals_vars.is_valid_null(value):
                values_without_nulls.append(value)

        def func_standard_deviation(values):
            avg = float((sum(values))) / len(values)
            sums = 0
            for value in values:
                sums += (value - avg) ** 2
            return (sums / (len(values) - 1)) ** 0.5

        if below not in [1, 2, 3] or above not in [1, 2, 3]:
            console.msg_error(_("thresholds of dependent variable were defined as "
                                "N standard deviation\n but are outside of range, "
                                "this values must be 1, 2 or 3:\nsd{0} sd{1}")
            .format(below, above))
        p50 = stats.scoreatpercentile(values_without_nulls, 50)
        std_deviation = func_standard_deviation(values_without_nulls)

        return p50 - below * std_deviation, p50 + above * std_deviation

    # thresholds by below and by above of var D with particular values,
    # these values validation with type of var D
    def thresholds_with_particular_values(below, above):

        try:
            below = float(below)
            above = float(above)
        except:
            console.msg_error(_("thresholds could not were identified:\n{0} - {1}")
            .format(below, above))

        if below > above:
            console.msg_error(_("threshold below of dependent variable can't be "
                                "greater than threshold above:\n{0} - {1}")
            .format(below, above))
        try:
            threshold_below_var_D = input_validation.validation_var_D(station.var_D.type_series,
                below,
                None,
                station.var_D.frequency_data)
            threshold_above_var_D = input_validation.validation_var_D(station.var_D.type_series,
                above,
                None,
                station.var_D.frequency_data)
            return threshold_below_var_D, threshold_above_var_D
        except Exception, e:
            console.msg_error(_("Problem with thresholds of dependent "
                                "variable:\n\n{0}").format(e))

    ## now analysis threshold input in arguments
    # if are define as default
    if (config_run.settings['threshold_below_var_D'] == "default" and
        config_run.settings['threshold_above_var_D'] == "default"):
        return thresholds_by_default()

    # check if analog_year is defined but thresholds aren't equal to "default"
    if config_run.settings['analog_year']:
        if station.first_iter:
            console.msg(_("\n > WARNING: You have defined the analog year,\n"
                           "   but the thresholds of var D must be\n"
                           "   'default' for use the analog year .........."), color='yellow', newline=False)

    # if are define as percentile or standard deviation
    if isinstance(config_run.settings['threshold_below_var_D'], str) and\
       isinstance(config_run.settings['threshold_above_var_D'], str):

        # if are define as percentile
        if (''.join(list(config_run.settings['threshold_below_var_D'])[0:1]) == "p" and
            ''.join(list(config_run.settings['threshold_above_var_D'])[0:1]) == "p"):
            below = int(''.join(list(config_run.settings['threshold_below_var_D'])[1::]))
            above = int(''.join(list(config_run.settings['threshold_above_var_D'])[1::]))
            if not (0 <= below <= 100) or not (0 <= above <= 100):
                console.msg_error(_("thresholds of dependent variable were defined as "
                                    "percentile\nbut are outside of range 0-100:\n{0} - {1}")
                .format(below, above))
            if below > above:
                console.msg_error(_("threshold below of dependent variable can't be "
                                    "greater than threshold above:\n{0} - {1}")
                .format(below, above))
            return percentiles(below, above)

        # if are define as standard deviation
        if (''.join(list(config_run.settings['threshold_below_var_D'])[0:2]) == "sd" and
            ''.join(list(config_run.settings['threshold_above_var_D'])[0:2]) == "sd"):
            below = int(''.join(list(config_run.settings['threshold_below_var_D'])[2::]))
            above = int(''.join(list(config_run.settings['threshold_above_var_D'])[2::]))
            return thresholds_with_std_deviation(below, above)

    # if are define as particular values
    if isinstance(config_run.settings['threshold_below_var_D'], (int, float)) and\
       isinstance(config_run.settings['threshold_above_var_D'], (int, float)):
        return thresholds_with_particular_values(config_run.settings['threshold_below_var_D'],
                                                 config_run.settings['threshold_above_var_D'])

    # unrecognizable thresholds
    console.msg_error(_("unrecognizable thresholds '{0}' and/or '{1}' for var D").
                        format(config_run.settings['threshold_below_var_D'],
                               config_run.settings['threshold_above_var_D']))


def get_thresholds_var_I(station):
    """
    Calculate and return threshold by below and above
    of independent variable, the type of threshold as
    defined by the user in station file, these may be:
    "default", "pNN" (percentile NN), "sdN" (standard
    deviation N) and particular value.
    """

    # Calculate percentile "below" and "above"
    def percentiles(below, above):

        threshold_below_var_I = stats.scoreatpercentile(station.var_I_values, below)
        threshold_above_var_I = stats.scoreatpercentile(station.var_I_values, above)
        return threshold_below_var_I, threshold_above_var_I

    # thresholds by below and by above of var I by default
    def thresholds_by_default():

        # thresholds for Oceanic Nino Index
        def if_var_I_is_ONI1():
            return -0.5, 0.5

        # thresholds for Oceanic Nino Index
        def if_var_I_is_ONI2():
            return -0.5, 0.5

        # thresholds for Index of the Southern Oscillation NOAA
        def if_var_I_is_SOI():
            return -0.9, 0.9

        # thresholds for Index of the Southern Oscillation calculated between Tahití and Darwin
        def if_var_I_is_SOI_TROUP():
            return -8, 8

        # thresholds for Multivariate ENSO index
        def if_var_I_is_MEI():
            return percentiles(33, 66)

        # thresholds for Radiation wavelength Long tropical
        def if_var_I_is_OLR():
            return -0.1, 0.2

        # thresholds for Index of wind anomaly to 200 hpa
        def if_var_I_is_W200():
            return percentiles(33, 66)

        # thresholds for Index of wind anomaly to 850 hpa west
        def if_var_I_is_W850w():
            return percentiles(33, 66)

        # thresholds for Index of wind anomaly to 850 hpa center
        def if_var_I_is_W850c():
            return percentiles(33, 66)

        # thresholds for Index of wind anomaly to 850 hpa east
        def if_var_I_is_W850e():
            return percentiles(33, 66)

        # thresholds for Sea surface temperature
        def if_var_I_is_SST():
            return percentiles(33, 66)

        # thresholds for Anomaly Sea surface temperature
        def if_var_I_is_ASST():
            return percentiles(33, 66)

        # thresholds for % Amazon relative humidity
        def if_var_I_is_ARH():
            return percentiles(33, 66)

        # thresholds for quasibienal oscillation index
        def if_var_I_is_QBO():
            return -4, 4

        # thresholds for North atlantic oscillation index
        def if_var_I_is_NAO():
            return -1, 1

        # thresholds for Caribbean (CAR) Index
        def if_var_I_is_CAR():
            return percentiles(33, 66)

        # thresholds for Monthly anomaly of the ocean surface area Ocean region
        def if_var_I_is_AREA_WHWP():
            return percentiles(33, 66)

        # switch validation
        select_threshold_var_I = {
            "ONI1": if_var_I_is_ONI1,
            "ONI2": if_var_I_is_ONI2,
            "SOI": if_var_I_is_SOI,
            "SOI_TROUP": if_var_I_is_SOI_TROUP,
            #"MEI": if_var_I_is_MEI,
            "OLR": if_var_I_is_OLR,
            "W200": if_var_I_is_W200,
            "W850w": if_var_I_is_W850w,
            "W850c": if_var_I_is_W850c,
            "W850e": if_var_I_is_W850e,
            "SST12": if_var_I_is_SST,
            "SST3": if_var_I_is_SST,
            "SST4": if_var_I_is_SST,
            "SST34": if_var_I_is_SST,
            "ASST12": if_var_I_is_ASST,
            "ASST3": if_var_I_is_ASST,
            "ASST4": if_var_I_is_ASST,
            "ASST34": if_var_I_is_ASST,
            "ARH": if_var_I_is_ARH,
            "QBO": if_var_I_is_QBO,
            "NAO": if_var_I_is_NAO,
            "CAR": if_var_I_is_CAR,
            "AREA_WHWP": if_var_I_is_AREA_WHWP
        }

        threshold_below_var_I, threshold_above_var_I = select_threshold_var_I[station.var_I.type_series]()
        return threshold_below_var_I, threshold_above_var_I

    # thresholds by below and by above of var I with standard deviation
    def thresholds_with_std_deviation(below, above):

        values_without_nulls = []
        for value in station.var_I_values:
            if not globals_vars.is_valid_null(value):
                values_without_nulls.append(value)

        def func_standard_deviation(values):
            avg = float((sum(values))) / len(values)
            sums = 0
            for value in values:
                sums += (value - avg) ** 2
            return (sums / (len(values) - 1)) ** 0.5

        if below not in [1, 2, 3] or above not in [1, 2, 3]:
            console.msg_error(_(
                "thresholds of independent variable were defined as "
                "N standard deviation\n but are outside of range, "
                "this values must be 1, 2 or 3:\nsd{0} sd{1}")
            .format(below, above))
        p50 = stats.scoreatpercentile(values_without_nulls, 50)
        std_deviation = func_standard_deviation(values_without_nulls)

        return p50 - below * std_deviation, p50 + above * std_deviation

    # thresholds by below and by above of var I with particular values,
    # these values validation with type of var I
    def thresholds_with_particular_values(below, above):

        try:
            below = float(below)
            above = float(above)
        except:
            console.msg_error(_(
                "thresholds could not were identified:\n{0} - {1}")
            .format(below, above))

        if below > above:
            console.msg_error(_(
                "threshold below of independent variable can't be "
                "greater than threshold above:\n{0} - {1}")
            .format(below, above))
        try:
            threshold_below_var_I = input_validation.validation_var_I(station.var_I.type_series, below)
            threshold_above_var_I = input_validation.validation_var_I(station.var_I.type_series, above)
            return threshold_below_var_I, threshold_above_var_I
        except Exception, e:
            console.msg_error(_(
                "Problem with thresholds of independent "
                "variable:\n\n{0}").format(e))

    ## now analysis threshold input in arguments
    # if are define as default
    if (config_run.settings['threshold_below_var_I'] == "default" and
        config_run.settings['threshold_above_var_I'] == "default"):
        return thresholds_by_default()

    # if are define as percentile or standard deviation
    if isinstance(config_run.settings['threshold_below_var_I'], str) and\
       isinstance(config_run.settings['threshold_above_var_I'], str):

        # if are define as percentile
        if (''.join(list(config_run.settings['threshold_below_var_I'])[0:1]) == "p" and
            ''.join(list(config_run.settings['threshold_above_var_I'])[0:1]) == "p"):
            below = float(''.join(list(config_run.settings['threshold_below_var_I'])[1::]))
            above = float(''.join(list(config_run.settings['threshold_above_var_I'])[1::]))
            if not (0 <= below <= 100) or not (0 <= above <= 100):
                console.msg_error(_(
                    "thresholds of independent variable were defined as "
                    "percentile\nbut are outside of range 0-100:\n{0} - {1}")
                .format(below, above))
            if below > above:
                console.msg_error(_(
                    "threshold below of independent variable can't be "
                    "greater than threshold above:\n{0} - {1}")
                .format(below, above))
            return percentiles(below, above)

        # if are define as standard deviation
        if (''.join(list(config_run.settings['threshold_below_var_I'])[0:2]) == "sd" and
            ''.join(list(config_run.settings['threshold_above_var_I'])[0:2]) == "sd"):
            below = int(''.join(list(config_run.settings['threshold_below_var_I'])[2::]))
            above = int(''.join(list(config_run.settings['threshold_above_var_I'])[2::]))
            return thresholds_with_std_deviation(below, above)

    # if are define as particular values
    if isinstance(config_run.settings['threshold_below_var_I'], (int, float)) and\
       isinstance(config_run.settings['threshold_above_var_I'], (int, float)):
        return thresholds_with_particular_values(config_run.settings['threshold_below_var_I'],
                                                 config_run.settings['threshold_above_var_I'])

    # unrecognizable thresholds
    console.msg_error(_("unrecognizable thresholds '{0}' and/or '{1}' for var I").
                        format(config_run.settings['threshold_below_var_I'],
                               config_run.settings['threshold_above_var_I']))