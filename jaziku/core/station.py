#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2011-2014 IDEAM
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

from jaziku import env
from jaziku.utils import console
from jaziku.core.variable import Variable


# ==============================================================================
# STATION CLASS
# for storage several variables of each station


class Station(object):
    """Generic station class for save several variables, configuration and
    properties for each station
    """

    # counter stations processed
    stations_processed = 0

    def __init__(self):

        Station.stations_processed += 1

        self.var_D = Variable(type='D', station=self)
        self.var_I = Variable(type='I', station=self)

        self.var_ = {'D': self.var_D, 'I': self.var_I}

    def calculate_common_and_process_period(self):
        """Calculate common period (interception) in years of dates from
        dependent and independent variable. And the process period is the
        common period below + 1 year and common period above - 1 year.

        Return by reference:

        :ivar STATION.common_period: [[  date ,  var_D ,  var_I ],... ]
        :ivar STATION.process_period: {'start','end'}
        """

        # interceptions values of date_D and date_I (with python set functions wuau!!)
        common_date = list(set(self.var_D.date) & set(self.var_I.date))
        # sort common date
        common_date.sort()

        # check if common_date is empty
        if not common_date:
            console.msg_error(_("For the series '{0}-{1}' together with var I '{2}'\n"
                                "don't have any common period, Jaziku need at least \n"
                                "3 year of common period between the two series.").format(self.code, self.name,
                                                                                          self.var_I.type_series))

        # initialized variable common_period
        # format list: [[  date ,  var_D ,  var_I ],... ]
        if env.config_run.settings['process_period']:
            if (env.config_run.settings['process_period']['start'] < common_date[0].year + 1 or
                        env.config_run.settings['process_period']['end'] > common_date[-1].year - 1):
                console.msg_error(_(
                    "The period defined in argument {0}-{1} is outside in the\n"
                    "maximum possible period {2}-{3} of intersection between station\n"
                    "{4}-{5} and {6}.")
                                  .format(env.config_run.settings['process_period']['start'],
                                          env.config_run.settings['process_period']['end'],
                                          common_date[0].year + 1, common_date[-1].year - 1,
                                          self.code, self.name, self.var_I.type_series))

            common_date = common_date[
                          common_date.index(date(env.config_run.settings['process_period']['start'] - 1, 1, 1)):
                          common_date.index(date(env.config_run.settings['process_period']['end'] + 1, 12, 1)) + 1]

        self.common_period = []
        # set values matrix for common_period
        for date_period in common_date:
            # common_period format list: [[  date ,  var_D ,  var_I ],... ]
            self.common_period.append([date_period,
                                       self.var_D.data[self.var_D.date.index(date_period)],
                                       self.var_I.data[self.var_I.date.index(date_period)]])

        # calculate the process period
        self.process_period = {'start': self.common_period[0][0].year + 1,
                               'end': self.common_period[-1][0].year - 1}
