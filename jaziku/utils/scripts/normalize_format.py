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


# Normalize the format and data inside of time series, convert the
# date character division in date, convert space between date and
# data, fill the nan values and empty dates, and others.
#
# Open terminal where saved the time series file (i.e TimeSeries.txt)
# and run:
#
#     normalize_format TimeSeries.txt
#
# Attention!: this script overwrite the same file, please make backup first

import sys
from datetime import date
from dateutil.relativedelta import relativedelta
from jaziku.utils import output 


def external_run():
    all_input_files = sys.argv[1::]
    for time_series_file in all_input_files:
        print 'processing file: ' + time_series_file


def main(time_series_file):

    input_file = open(time_series_file, 'rU')

    lines = input_file.readlines()

    input_file.close()

    output_file = open(time_series_file, 'w')
    old_date_value = False

    for line in lines:

        if not line or not line[0].strip() or line == []:
            continue

        is_daily = False
        is_monthly = False

        # normalize characters and divisions, and clean
        line = line.replace('/','-')
        line = line.replace('\t',' ')
        line = line.replace(';',' ')
        line = line.replace('  ',' ')
        line = line.replace('\"','')
        line = line.replace('\'','')
        line = line.strip()

        year = line.split(' ')[0].split('-')[0]
        month = line.split(' ')[0].split('-')[1]
        try:
            month = output.fix_zeros(int(month))
        except:
            pass

        if len(line.split(' ')[0].split('-')) == 3:
            day = line.split(' ')[0].split('-')[2]
            day = output.fix_zeros(int(day))
            is_daily = True
        else:
            day = 1
            is_monthly = True

        # detect if value is not empty, else put 'nan' as value
        if len(line.split(' ')) >= 2 and line.split(' ')[1].strip() != '':
            value = line.split(' ')[1]
        else:
            value = 'nan'

        date_value = date(int(year),int(month),int(day))

        # fill the empty months or days with nan if not exists
        if old_date_value is not False:
            if is_monthly:
                while date_value > old_date_value + relativedelta(months=1):
                    old_date_value = old_date_value + relativedelta(months=1)
                    output_file.write(str(old_date_value.year)+'-'+output.fix_zeros(old_date_value.month)+' '+'nan'+'\n')
            if is_daily:
                while date_value > old_date_value + relativedelta(days=1):
                    old_date_value = old_date_value + relativedelta(days=1)
                    output_file.write(str(old_date_value.year)+'-'+output.fix_zeros(old_date_value.month)+'-'+output.fix_zeros(old_date_value.day)+' '+'nan'+'\n')

        old_date_value = date_value

        if is_monthly:
            output_file.write(year+'-'+str(month)+' '+str(value)+'\n')
        if is_daily:
            output_file.write(year+'-'+str(month)+'-'+str(day)+' '+str(value)+'\n')

    output_file.close()