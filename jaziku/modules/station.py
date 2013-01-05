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

from datetime import date

from jaziku.utils import globals_vars, console
from jaziku.modules.input.input_check import check_consistent_data
from jaziku.modules.input import input_vars
from jaziku.modules.climate import climate
from jaziku.modules.forecasting import forecasting
from jaziku.modules.variable import Variable

#==============================================================================
# STATION CLASS
# for storage several variables of each station


class Station:
    """
    Generic station class for save several variables, configuration and
    properties for each station
    """

    # counter stations processed
    stations_processed = 0

    def __init__(self):

        Station.stations_processed += 1

        self.var_D = Variable(type='D')
        self.var_I = Variable(type='I')


    def calculate_common_and_process_period(self):
        """
        Calculate common period (interception) in years of dates from
        dependent and independent variable. And the process period is the
        common period below + 1 year and common period above - 1 year.

        :return by reference:
            STATION.common_period [[  date ,  var_D ,  var_I ],... ]
            STATION.process_period {'start','end'}
        """

        # interceptions values of date_D and date_I (python set functions wuau!!)
        common_date = list(set(self.var_D.date) & set(self.var_I.date))
        # sort common date
        common_date.sort()

        # initialized variable common_period
        # format list: [[  date ,  var_D ,  var_I ],... ]
        if globals_vars.config_run['process_period']:
            if (globals_vars.config_run['process_period']['start'] < common_date[0].year + 1 or
                globals_vars.config_run['process_period']['end'] > common_date[-1].year - 1):
                console.msg(_("\nCalculating the process period ................ "), newline=False)
                console.msg_error(_(
                    "The period defined in argument {0}-{1} is outside in the\n"
                    "maximum possible period for this station: {2}-{3}.")
                .format(globals_vars.config_run['process_period']['start'],
                    globals_vars.config_run['process_period']['end'],
                    common_date[0].year + 1, common_date[-1].year - 1))

            common_date = common_date[common_date.index(date(globals_vars.config_run['process_period']['start'] - 1, 1, 1)):
            common_date.index(date(globals_vars.config_run['process_period']['end'] + 1, 12, 1)) + 1]

        self.common_period = []
        # set values matrix for common_period
        for date_period in common_date:
            # common_period format list: [[  date ,  var_D ,  var_I ],... ]
            self.common_period.append([date_period,
                                      self.var_D.data[self.var_D.date.index(date_period)],
                                      self.var_I.data[self.var_I.date.index(date_period)]])

        # check if the common period at least 3 years before calculate the process period
        if len(common_date) < 36:
            console.msg(_("Calculating the common period ................. "), newline=False)

            console.msg_error(_("The common period calculated {0}-{1} has not at "
                                "least 3 years.").format(common_date[0].year,
                common_date[-1].year))

        # calculate the process period
        self.process_period = {'start': self.common_period[0][0].year + 1,
                               'end': self.common_period[-1][0].year - 1}


    def get_state_of_data(self):
        """
        Calculate and write output based on type of data (daily or monthly)
        of dependent and independent variable.

        :return by reference:
            STATION.state_of_data
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
        if self.var_D.frequency_data == "monthly" and self.var_I.frequency_data == "monthly":
            self.state_of_data = 1
        if self.var_D.frequency_data == "daily" and self.var_I.frequency_data == "monthly":
            self.state_of_data = 2
        if self.var_D.frequency_data == "monthly" and self.var_I.frequency_data == "daily":
            self.state_of_data = 3
        if self.var_D.frequency_data == "daily" and self.var_I.frequency_data == "daily":
            self.state_of_data = 4


    def pre_process(self):
        """
        Read, validated and check data
        """
        if globals_vars.config_run['data_analysis']:
            process = False
        else:
            process = True

        self.var_D.read_data_from_file(self, process=process, messages=True)
        self.var_I.read_data_from_file(self, process=process, messages=True)

        if not globals_vars.config_run['data_analysis']:
            self.calculate_common_and_process_period()

            self.var_D.data_and_null_in_process_period(self)
            self.var_I.data_and_null_in_process_period(self)

        if globals_vars.config_run['consistent_data']:
            check_consistent_data(self.var_D)
            check_consistent_data(self.var_I)


    def process(self):
        """
        Run climate and forecasting process for this station.
        """

        # restore threshold problem values
        globals_vars.threshold_problem = [False, False, False]

        self.get_state_of_data()

        # define if results will made by trimester or every n days
        if self.state_of_data in [1, 3]:
            console.msg(_("Results will be made by trimesters"), color='cyan')
            if globals_vars.config_run['analysis_interval'] != "trimester":
                console.msg_error(_("The var_D of stations have data monthly, but you define\n"
                                    "in runfile the analysis interval as '{0}', this must be,\n"
                                    "in this case, as 'trimester' or use data daily.").format(globals_vars.config_run['analysis_interval']))
        if self.state_of_data in [2, 4]:
            # if analysis_interval is defined by trimester but var_I or/and var_D has data
            # daily, first convert in data monthly and continue with results by trimester
            if globals_vars.config_run['analysis_interval'] == "trimester":
                console.msg(_("Results will be made by trimesters"), color='cyan')
                if self.var_D.frequency_data == "daily":
                    console.msg(_("Converting all var D to data monthly"), color='cyan')
                    self.var_D.daily2monthly()
                    self.var_D.frequency_data = "monthly"
                if self.var_I.frequency_data == "daily":
                    console.msg(_("Converting all var I to data monthly"), color='cyan')
                    self.var_I.daily2monthly()
                    self.var_I.frequency_data = "monthly"
                self.state_of_data = 1
            else:
                console.msg(_("Results will be made every {} days").format(globals_vars.analysis_interval_num_days), color='cyan')

        if self.state_of_data == 3:
            console.msg(_("Converting all var I to data monthly"), color='cyan')
            self.var_I.daily2monthly()
            self.var_I.frequency_data = "monthly"

        # inform the period to process
        console.msg(_("Period to process: {0}-{1}").format(self.process_period['start'], self.process_period['end']), color='cyan')

        # run climate process
        if globals_vars.config_run['climate_process']:
            climate.climate(self)

        # run forecasting process
        if globals_vars.config_run['forecasting_process']:
            # TODO: run forecasting without climate¿?
            forecasting.forecasting(self)