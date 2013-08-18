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
        if type == "trimester":
            self.trimester = month
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
    """Return all start days of analysis interval
    """

    if env.config_run.settings['analysis_interval'] != "trimester":
        if env.globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL == 5:
            return [1, 6, 11, 16, 21, 26]
        if env.globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL == 10:
            return [1, 11, 21]
        if env.globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL == 15:
            return [1, 16]
    else:
        return None


def get_state_of_data():
    """Calculate and define the state of data based on type of data (daily or monthly)
    of dependent and independent variable.

    :return:
        int (1, 2, 3 or 4)
    """
    # -------------------------------------------------------------------------
    # State of the data for process, calculate and write output based on type
    # of data (daily or monthly) of dependent and independent variable
    #
    # | state |  var D  |  var I  |         possible results
    # |   1   | monthly | monthly |            trimester
    # |   2   |  daily  | monthly | 5days, 10days, 15days and trimester
    # |   3   | monthly |  daily  |            trimester
    # |   4   |  daily  |  daily  | 5days, 10days, 15days and trimester
    #
    if env.var_D.is_monthly() and env.var_I.is_monthly():
        return 1
    if env.var_D.is_daily() and env.var_I.is_monthly():
        return 2
    if env.var_D.is_monthly() and env.var_I.is_daily():
        return 3
    if env.var_D.is_daily() and env.var_I.is_daily():
        return 4


def check_analysis_interval():

    if env.globals_vars.STATE_OF_DATA in [1, 3] and env.config_run.settings['analysis_interval'] != "trimester":
        console.msg_error(_("The var_D of stations have data monthly, but you define\n"
                            "in runfile the analysis interval as '{0}', this must be,\n"
                            "in this case, as 'trimester' or use data daily.").format(
            env.config_run.settings['analysis_interval']))


def adjust_data_of_variables(stations_list):

    if env.globals_vars.STATE_OF_DATA == 3:
        console.msg(_("   Converting var I of all stations to data monthly ..... "), color='cyan', newline=False)
        for station in stations_list:
            station.var_I.daily2monthly()
            env.var_I.set_FREQUENCY_DATA("monthly", check=False)

        # recalculate global STATE_OF_DATA
        env.globals_vars.STATE_OF_DATA = get_state_of_data()
        console.msg(_("done"), color='green')

        return True

    if env.globals_vars.STATE_OF_DATA in [2, 4]:
        # if analysis_interval is defined by trimester but var_I or/and var_D has data
        # daily, first convert in data monthly and continue with results by trimester
        if env.config_run.settings['analysis_interval'] == "trimester":
            console.msg(_("   Converting var D of all stations to data monthly ..... "), color='cyan', newline=False)
            for station in stations_list:
                station.var_D.daily2monthly()
                env.var_D.set_FREQUENCY_DATA("monthly", check=False)
            console.msg(_("done"), color='green')
            if env.globals_vars.STATE_OF_DATA == 4:
                console.msg(_("   Converting var I of all stations to data monthly ..... "), color='cyan', newline=False)
                for station in stations_list:
                    station.var_I.daily2monthly()
                    env.var_I.set_FREQUENCY_DATA("monthly", check=False)
                console.msg(_("done"), color='green')

            # recalculate global STATE_OF_DATA
            env.globals_vars.STATE_OF_DATA = get_state_of_data()

            return True

    return False


def locate_day_in_analysis_interval(day_for_locate):
    """Return corresponding start day of analysis interval where
    the day_for_locate is inside.
    """
    range_analysis_interval = get_range_analysis_interval()
    range_analysis_interval.reverse()
    for range_item in range_analysis_interval:
        if day_for_locate >= range_item:
            return range_item


def get_values_in_range_analysis_interval(station, type, year, month, day=None, lag=None):
    """Get all values inside range analysis interval in specific year, month, day or lag.
    The "type" must be "D" or "I". For trimester the "month" is the start month of
    trimester, for 5, 10, or 15 days the "day" is a start day in the range analysis
    interval. The "lag" is only affect for the independent variable and it must
    be 0, 1 or 2.
    """

    range_analysis_interval = get_range_analysis_interval()

    # first fix if day not is a valid start day in analysis interval
    if day and  range_analysis_interval:
        if day not in range_analysis_interval:
            day = locate_day_in_analysis_interval(day)

    if type == 'D':
        var_D_values = []
        if env.var_D.is_daily():
            # clone range for add the last day (32) for calculate interval_day_var_D
            rai_plus = list(range_analysis_interval)
            rai_plus.append(32)
            # from day to next iterator based on analysis interval
            # e.g. [0,1,2,3,4] for first iteration for 5 days
            interval_day_var_D = range(day - 1, rai_plus[rai_plus.index(day) + 1] - 1)

            for iter_day in interval_day_var_D:
                now = date(year, month, 1) + relativedelta(days=iter_day)
                # check if continues with the same month
                if now.month == month:
                    index_var_D = station.var_D.date.index(now)
                    var_D_values.append(station.var_D.data[index_var_D])
        if env.var_D.is_monthly():
            # get the three values for var_D in this month
            for iter_month in range(3):
                var_D_values.append(station.var_D.data[station.var_D.date.index(
                    date(year, month, 1) + relativedelta(months=iter_month))])

        return var_D_values

    if type == 'I':
        var_I_values = []
        if env.var_I.is_daily():
            # from day to next iterator based on analysis interval
            start_interval = range_analysis_interval[range_analysis_interval.index(day) - lag]
            try:
                end_interval = range_analysis_interval[range_analysis_interval.index(day) + 1 - lag]
            except:
                end_interval = range_analysis_interval[0]

            start_date = date(year, month, start_interval)

            if range_analysis_interval.index(day) - lag < 0:
                start_date += relativedelta(months= -1)

            iter_date = start_date

            while iter_date.day != end_interval:
                index_var_I = station.var_I.date.index(iter_date)
                var_I_values.append(station.var_I.data[index_var_I])
                iter_date += relativedelta(days=1)

        if env.var_I.is_monthly():
            if env.globals_vars.STATE_OF_DATA in [1, 3]:
                # get the three values for var_I in this month
                for iter_month in range(3):
                    var_I_values.append(station.var_I.data[station.var_I.date.index(
                        date(year, month, 1) + relativedelta(months=iter_month - lag))])
            if env.globals_vars.STATE_OF_DATA in [2]:
                # keep constant value for month
                if env.config_run.settings['analysis_interval'] == "trimester":
                    var_I_values.append(station.var_I.data[station.var_I.date.index(
                        date(year, month, 1) + relativedelta(months= -lag))])
                else:
                    real_date = date(year, month, day) + relativedelta(days= -env.globals_vars.NUM_DAYS_OF_ANALYSIS_INTERVAL * lag)
                    # e.g if lag 2 in march and calculate to 15days go to february and not january
                    if month - real_date.month > 1:
                        real_date = date(real_date.year, real_date.month + 1, 1)

                    var_I_values.append(station.var_I.data[station.var_I.date.index(
                        date(real_date.year, real_date.month, 1))])

        return var_I_values

