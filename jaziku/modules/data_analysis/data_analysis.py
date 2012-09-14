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
import gettext

from jaziku.utils import  console
from jaziku.modules.input.input_vars import read_var_D, read_var_I
from jaziku.modules.station import Station
import eda

def main(stations):
    """
    In jaziku-Data Analysis, the outliers are reported, is made the assessing the homogeneity of
    the series and is made known to the user of statistical values that will allow discerning, in
    respect of their research objective, the use of a series or another, also directly obtaining the
    files folder of time series.
    """

    console.msg(_("\nReading var D and var I of all stations ......... "), newline=False)

    for station in stations:

        station.var_D.read_data_from_file(station, process=True, messages=False)
        station.var_I.read_data_from_file(station, process=True, messages=False)

        station.calculate_common_and_process_period()

        station.var_D.data_and_null_in_process_period(station)
        station.var_I.data_and_null_in_process_period(station)

        station.var_D.do_some_statistic_of_data(station)
        station.var_I.do_some_statistic_of_data(station)


    console.msg(_("done"), color='green')
    console.msg(gettext.ngettext(
        "   {0} station readed.",
        "   {0} stations readed.",
        Station.stations_processed).format(Station.stations_processed), color='cyan')

    # -------------------------------------------------------------------------
    # Exploratory data analysis process

    eda.main(stations)


