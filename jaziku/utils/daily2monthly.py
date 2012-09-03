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

from mean import mean

def daily2monthly(var_daily, date_daily):
    """
    Convert the data daily to monthly using the mean
    """
    var_monthly = []
    date_monthly = []

    _iter = 0
    for year in range(date_daily[0].year, date_daily[-1].year + 1):
        for month in range(1, 13):
            var_month_list = []
            while date_daily[_iter].month == month:
                var_month_list.append(var_daily[_iter])
                _iter += 1
                if _iter > date_daily.index(date_daily[-1]):
                    break
            var_monthly.append(mean(var_month_list))
            date_monthly.append(date(year, month, 1))

    return var_monthly, date_monthly
