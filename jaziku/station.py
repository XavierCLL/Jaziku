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

import sys

from utils import globals_vars, console
from utils.daily2monthly import daily2monthly
from utils.calculate_common_period import calculate_common_period
from modules.input.input_check import check_consistent_data
from modules.input import input_vars
from modules.climate import climate
from modules.forecasting import forecasting

#==============================================================================
# STATION CLASS
# for storage several variables of each station


class Station:
    """
    Generic station class
    """

    # counter stations processed
    stations_processed = 0

    def __init__(self):
        Station.stations_processed += 1


    #==============================================================================
    # PRE-PROCESS: READ, VALIDATED AND CHECK DATA

    def pre_process(self):
        """
        Read var I and varD from files, validated and check consistent
        """

        # -------------------------------------------------------------------------
        # Reading the variables from files and check based on range validation

        # var D
        sys.stdout.write(_("Read and check(range validation) var D ........ "))
        sys.stdout.flush()
        self = input_vars.read_var_D(self)  # <--
        if not self.range_below_D or not self.range_above_D:
            console.msg(_("\n > WARNING: you are using one or both limit as\n"
                           "   \"none\" value, this means that series values\n"
                           "   will not be checked if they are valid in\n"
                           "   its limits coherent. This option is not\n"
                           "   recommended, use it with precaution ........"), color='yellow', newline=False)
        console.msg(_("done"), color='green')

        if self.data_of_var_D == "daily":
            console.msg(_("   the dependent variable has data daily"), color='cyan')
        if self.data_of_var_D == "monthly":
            console.msg(_("   the dependent variable has data monthly"), color='cyan')

        # var I
        sys.stdout.write(_("Read and check(range validation) var I ........ "))
        sys.stdout.flush()
        self = input_vars.read_var_I(self)  # <--
        if not self.range_below_I or not self.range_above_I:
            console.msg(_("\n > WARNING: you are using one or both limit as\n"
                           "   \"none\" value, this means that series values\n"
                           "   will not be checked if they are valid in\n"
                           "   its limits coherent. This option is not\n"
                           "   recommended, use it with precaution ........"), color='yellow', newline=False)
        console.msg(_("done"), color='green')

        if self.data_of_var_I == "daily":
            console.msg(_("   the independent variable has data daily"), color='cyan')
        if self.data_of_var_I == "monthly":
            console.msg(_("   the independent variable has data monthly"), color='cyan')

        # -------------------------------------------------------------------------
        # Calculating common period and process period
        self.common_period = calculate_common_period(self)

        self.process_period = {'start': self.common_period[0][0].year + 1,
                                  'end': self.common_period[-1][0].year - 1}

        if globals_vars.config_run['consistent_data']:
            # -------------------------------------------------------------------------
            # check if the data are consistent for var D
            sys.stdout.write(_("Check if var D are consistent"))
            sys.stdout.flush()

            check_consistent_data(self, "D")

            console.msg(_("done"), color='green')

            # -------------------------------------------------------------------------
            # check if the data are consistent for var I
            sys.stdout.write(_("Check if var I are consistent"))
            sys.stdout.flush()

            check_consistent_data(self, "I")

            console.msg(_("done"), color='green')


    #==============================================================================
    # PROCESS:


    def process(self):

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
        if self.data_of_var_D == "monthly" and self.data_of_var_I == "monthly":
            self.state_of_data = 1
        if self.data_of_var_D == "daily" and self.data_of_var_I == "monthly":
            self.state_of_data = 2
        if self.data_of_var_D == "monthly" and self.data_of_var_I == "daily":
            self.state_of_data = 3
        if self.data_of_var_D == "daily" and self.data_of_var_I == "daily":
            self.state_of_data = 4

        # define if results will made by trimester or every n days
        if self.state_of_data in [1, 3]:
            console.msg(_("   Results will be made by trimesters"), color='cyan')
            if self.analysis_interval != "trimester":
                text_error = _("var_D (and or not var_I) has data monthly but you define the\n"
                               "analysis interval as \"{0}\", this must be, in this\n"
                               "case, as \"trimester\".").format(self.analysis_interval)
                console.msg_error_line_selfs(self, text_error)
        if self.state_of_data in [2, 4]:
            # if analysis_interval is defined by trimester but var_I or/and var_D has data
            # daily, first convert in data monthly and continue with results by trimester
            if self.analysis_interval == "trimester":
                console.msg(_("   Results will be made by trimesters"), color='cyan')
                if self.data_of_var_D == "daily":
                    console.msg(_("   Converting all var D to data monthly"), color='cyan')
                    self.var_D, self.date_D = daily2monthly(self.var_D, self.date_D)
                    self.data_of_var_D = "monthly"
                if self.data_of_var_I == "daily":
                    console.msg(_("   Converting all var I to data monthly"), color='cyan')
                    self.var_I, self.date_I = daily2monthly(self.var_I, self.date_I)
                    self.data_of_var_I = "monthly"
                self.state_of_data = 1
            else:
                console.msg(_("   Results will be made every {} days").format(self.analysis_interval_num_days), color='cyan')

        if self.state_of_data == 3:
            console.msg(_("   Converting all var I to data monthly"), color='cyan')
            self.var_I, self.date_I = daily2monthly(self.var_I, self.date_I)
            self.data_of_var_I = "monthly"

        # run process (climate, forecasting) from input arguments
        if not globals_vars.config_run['climate_process'] and not globals_vars.config_run['forecasting_process']:
            console.msg_error(_(
                "Neither process (climate, forecasting) were executed, "
                "\nplease enable this process in arguments: \n'-c, "
                "--climate' for climate and/or '-f, --forecasting' "
                "for forecasting."))
        if globals_vars.config_run['climate_process']:
            climate.climate(self)

        if globals_vars.config_run['forecasting_process']:
            # TODO: run forecasting without climate¿?
            if not globals_vars.config_run['climate_process']:
                console.msg_error(_("sorry, Jaziku can't run forecasting process "
                                    "without climate, this issue has not been implemented "
                                    "yet, \nplease run again with the option \"-c\""))
            forecasting.forecasting(self)
