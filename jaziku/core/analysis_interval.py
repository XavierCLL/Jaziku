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

from datetime import date
from dateutil.relativedelta import relativedelta

from jaziku import env
from jaziku.utils import  console


#TODO
class PeriodOfAnalysisInterval(object):
    def __init__(self, type, month=None, day=None):
        self.type = type
        if type == "trimonthly":
            self.trimonthly = month
        if type == "15days":
            self.month = month
            self.day = day
        if type == "10days":
            self.month = month
            self.day = day
        if type == "5days":
            self.month = month
            self.day = day


def get_range_analysis_interval():
    """Return all start days of analysis interval, this is only
    for analysis interval 5days, 10days and 15days
    """

    if env.config_run.settings['analysis_interval'] not in ['monthly','bimonthly','trimonthly']:
        if env.globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL == 5:
            return [1, 6, 11, 16, 21, 26]
        if env.globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL == 10:
            return [1, 11, 21]
        if env.globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL == 15:
            return [1, 16]
    else:
        return None


def check_analysis_interval():
    # -------------------------------------------------------------------------
    # Types of data for process and their results:
    #
    # | var D      | var I      | possible results
    # _____________________________________________________________
    # | daily      | daily      | 5days, 10days, 15days,
    # |            | monthly    | monthly, bimonthly*, trimonthly*
    # |            | bimonthly* |
    # |            | trimonthly*|
    # _____________________________________________________________
    # | monthly    | daily      | monthly, bimonthly*, trimonthly*
    # |            | monthly    |
    # |            | bimonthly* |
    # |            | trimonthly*|
    # _____________________________________________________________
    # | bimonthly  | daily      | bimonthly
    # |            | monthly    |
    # |            | bimonthly  |
    # _____________________________________________________________
    # | trimonthly | daily      | trimonthly
    # |            | monthly    |
    # |            | trimonthly |
    # _____________________________________________________________
    #  * not combine bimonthly with trimonthly and vice versa
    #
    #
    # Special cases with bimonthly and trimonthly that is
    # impossible convert the time series, error:
    #
    # | var D      | var I      | possible results
    # ___________________________________________________________
    # | (any)      | bimonthly  | trimonthly
    # | (any)      | trimonthly | bimonthly
    # | bimonthly  | (any)      | trimonthly
    # | bimonthly  | trimonthly | (any)
    # ___________________________________________________________
    #

    # old state
    # | state |  var D  |  var I  |         possible results
    # |   1   | monthly | monthly |            trimonthly
    # |   2   |  daily  | monthly | 5days, 10days, 15days and trimonthly
    # |   3   | monthly |  daily  |            trimonthly
    # |   4   |  daily  |  daily  | 5days, 10days, 15days and trimonthly
    #
    # env.globals_vars.STATE_OF_DATA in [1, 3] =  if env.var_D.FREQUENCY_DATA in ['monthly'] and env.var_I.FREQUENCY_DATA in ['daily','monthly']
    # env.globals_vars.STATE_OF_DATA in [2, 4] =  if env.var_D.FREQUENCY_DATA in ['daily'] and env.var_I.FREQUENCY_DATA in ['daily','monthly']

    def analysis_interval_error(env_variable):
        console.msg_error(_("The var {0} ({1}) of stations have data {2}, but you\n"
                            "define in runfile the 'analysis_interval' as '{3}',\n"
                            "this is incompatible and Jaziku can't convert the times\n"
                            "series properly for this case. Or change the analysis\n"
                            "interval or change the data of var {0}.")
            .format(env.var_.keys()[env.var_.values().index(env_variable)], env_variable.TYPE_SERIES,
                    env_variable.FREQUENCY_DATA, env.config_run.settings['analysis_interval']))

    if env.var_I.FREQUENCY_DATA in ['bimonthly'] and env.config_run.settings['analysis_interval'] in ["trimonthly"]:
        analysis_interval_error(env.var_I)
    if env.var_D.FREQUENCY_DATA in ['bimonthly'] and env.config_run.settings['analysis_interval'] not in ["bimonthly"]:
        analysis_interval_error(env.var_D)
    if env.var_I.FREQUENCY_DATA in ['trimonthly'] and env.config_run.settings['analysis_interval'] in ["bimonthly"]:
        analysis_interval_error(env.var_I)
    if env.var_D.FREQUENCY_DATA in ['trimonthly'] and env.config_run.settings['analysis_interval'] not in ["trimonthly"]:
        analysis_interval_error(env.var_D)

    if env.var_D.FREQUENCY_DATA in ['monthly','bimonthly','trimonthly'] and env.config_run.settings['analysis_interval'] not in ["monthly","bimonthly","trimonthly"]:
        analysis_interval_error(env.var_D)


def adjust_data_of_variables(stations_list, force_same_frequencies=False, messages=True):
    '''
    Adjust the var D and/or var I for all stations to frequency
    data defined in runfile as analysis_interval
    '''

    def convert_stations_2(variable, new_freq_data):
        if messages:
            console.msg(_("   Converting var {0} of all stations to data {1} ..... ")
                        .format(variable, new_freq_data), color='cyan', newline=False)
        for station in stations_list:
            station.var_[variable].convert2(new_freq_data)
        env.var_[variable].set_FREQUENCY_DATA(new_freq_data, check=False)
        if messages:
            console.msg(_("done"), color='green')

    was_converted_to = {'D':False, 'I':False}

    freq_order = ["daily", "monthly", "bimonthly", "trimonthly"]

    freq_analysis_interval = env.config_run.settings['analysis_interval']
    if freq_analysis_interval in ["5days", "10days", "15days"] and not force_same_frequencies:
        env.var_D.was_converted, env.var_I.was_converted = was_converted_to['D'], was_converted_to['I']
        return

    if force_same_frequencies:
        if freq_analysis_interval in ["5days", "10days", "15days"]:
            freq_analysis_interval = "daily"
        max_freq = freq_order[max(freq_order.index(env.var_D.FREQUENCY_DATA),
                                  freq_order.index(env.var_I.FREQUENCY_DATA),
                                  freq_order.index(freq_analysis_interval))]
        freq_analysis_interval = max_freq

    for variable in ['D', 'I']:
        if freq_order.index(env.var_[variable].FREQUENCY_DATA) < freq_order.index(freq_analysis_interval):
            convert_stations_2(variable, freq_analysis_interval)
            was_converted_to[variable] = True

    env.var_D.was_converted, env.var_I.was_converted = was_converted_to['D'], was_converted_to['I']


def get_text_of_frequency_data(var, ndays=False):

    if env.var_[var].FREQUENCY_DATA == "daily":
        if ndays:
            text_of_frequency_data = _("*calculated from data every {0}").format(env.config_run.settings['analysis_interval_i18n'])
        else:
            text_of_frequency_data = _("*calculated from daily data")
    else:
        if env.var_[var].FREQUENCY_DATA == "monthly":
            text_of_frequency_data = _("*calculated from monthly data")
        if env.var_[var].FREQUENCY_DATA == "bimonthly":
            text_of_frequency_data = _("*calculated from bimonthly data")
        if env.var_[var].FREQUENCY_DATA == "trimonthly":
            text_of_frequency_data = _("*calculated from trimonthly data")

    if env.var_[var].was_converted:
        text_of_frequency_data += _( " (converted)")

    return text_of_frequency_data


def locate_day_in_analysis_interval(day_for_locate):
    """Return corresponding start day of analysis interval where
    the day_for_locate is inside.
    """
    range_analysis_interval = get_range_analysis_interval()
    range_analysis_interval.reverse()
    for range_item in range_analysis_interval:
        if day_for_locate >= range_item:
            return range_item


def get_values_in_range_analysis_interval(variable, year, n_month, day=None, lag=None):
    """Get all values inside range analysis interval in specific year, month, day or lag.
    The "type" must be "D" or "I". For bimonthly and trimonthly the "n_month" is the start
    of month of bimonthly or trimonthly respective, for 5, 10, or 15 days the "day" is a
    start day in the range analysis interval. The "lag" is only affect for the independent
    variable and it must be 0, 1 or 2.
    """

    range_analysis_interval = get_range_analysis_interval()

    # first fix if day not is a valid start day in analysis interval
    if day and range_analysis_interval:
        if day not in range_analysis_interval:
            day = locate_day_in_analysis_interval(day)

    if variable.type == 'D':
        var_D_values = []
        if env.var_D.is_daily():
            # clone range for add the last day (32) for calculate interval_day_var_D
            rai_plus = list(range_analysis_interval)
            rai_plus.append(32)
            # from day to next iterator based on analysis interval
            # e.g. [0,1,2,3,4] for first iteration for 5 days
            interval_day_var_D = range(day - 1, rai_plus[rai_plus.index(day) + 1] - 1)

            for iter_day in interval_day_var_D:
                now = date(year, n_month, 1) + relativedelta(days=iter_day)
                # check if continues with the same month
                if now.month == n_month:
                    index_var_D = variable.date.index(now)
                    var_D_values.append(variable.data[index_var_D])
        if env.var_D.is_n_monthly():
            var_D_values.append(variable.data[variable.date.index(date(year, n_month, 1))])

        return var_D_values

    if variable.type == 'I':
        var_I_values = []
        if env.var_I.is_daily():
            # from day to next iterator based on analysis interval
            start_interval = range_analysis_interval[range_analysis_interval.index(day) - lag]
            try:
                end_interval = range_analysis_interval[range_analysis_interval.index(day) + 1 - lag]
            except:
                end_interval = range_analysis_interval[0]

            start_date = date(year, n_month, start_interval)

            if range_analysis_interval.index(day) - lag < 0:
                start_date += relativedelta(months= -1)

            iter_date = start_date

            while iter_date.day != end_interval:
                index_var_I = variable.date.index(iter_date)
                var_I_values.append(variable.data[index_var_I])
                iter_date += relativedelta(days=1)

        if env.var_I.is_n_monthly():
            if env.config_run.settings['analysis_interval'] in ["5days", "10days", "15days"]:
                real_date = date(year, n_month, day) + relativedelta(days= -env.globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL * lag)
                # e.g if lag 2 in march and calculate to 15days go to february and not january
                if n_month - real_date.month > 1:
                    real_date = date(real_date.year, real_date.month + 1, 1)

                var_I_values.append(variable.data[variable.date.index(
                    date(real_date.year, real_date.month, 1))])
            else:
                var_I_values.append(variable.data[variable.date.index(
                        date(year, n_month, 1) + relativedelta(months=-lag))])

        return var_I_values

