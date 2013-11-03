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
        main(time_series_file)

def get_int_month(month):
    if isinstance(month, str) and len(month) in [2,3]:
        bim_char = {1:'jf', 2: 'fm', 3: 'ma',4: 'am', 5: 'mj', 6: 'jj', 7: 'ja', 8: 'as', 9: 'so', 10: 'on', 11: 'nd', 12: 'dj'}
        trim_char = {1:'jfm', 2: 'fma', 3: 'mam',4: 'amj', 5: 'mjj', 6: 'jja', 7: 'jas', 8: 'aso', 9: 'son', 10: 'ond', 11: 'ndj', 12: 'djf'}

        if len(month) == 2:
            return bim_char.keys()[bim_char.values().index(month)]
        if len(month) == 3:
            return trim_char.keys()[trim_char.values().index(month)]
    else:
        return int(month)

def get_char_month(month, type_of_month):
    if type_of_month == 'monthly':
        return output.fix_zeros(month)
    if type_of_month == 'bimonthly':
        bim_char = {1:'jf', 2: 'fm', 3: 'ma',4: 'am', 5: 'mj', 6: 'jj', 7: 'ja', 8: 'as', 9: 'so', 10: 'on', 11: 'nd', 12: 'dj'}
        return bim_char[month]
    if type_of_month == 'trimester':
        trim_char = {1:'jfm', 2: 'fma', 3: 'mam',4: 'amj', 5: 'mjj', 6: 'jja', 7: 'jas', 8: 'aso', 9: 'son', 10: 'ond', 11: 'ndj', 12: 'djf'}
        return trim_char[month]

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
        type_of_month = False

        # normalize characters and divisions, and clean
        line = line.replace('/','-')
        line = line.replace('\t',' ')
        line = line.replace(';',' ')
        line = line.replace('  ',' ')
        line = line.replace('\"','')
        line = line.replace('\'','')
        line = line.replace('NaN','nan')
        line = line.replace('NAN','nan')
        line = line.strip()

        year = line.split(' ')[0].split('-')[0]
        month = line.split(' ')[0].split('-')[1]
        try:
            month = int(month)
            type_of_month = 'monthly'
        except:
            if isinstance(month, str) and len(month) in [2,3]:
                month = month.lower()
                if len(month) == 2:
                    type_of_month = 'bimonthly'
                if len(month) == 3:
                    type_of_month = 'trimester'

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

        date_value = date(int(year),get_int_month(month),int(day))

        # fill the empty months or days with nan if not exists
        if old_date_value is not False:
            if is_monthly:
                while date_value > old_date_value + relativedelta(months=1):
                    old_date_value = old_date_value + relativedelta(months=1)
                    output_file.write(str(old_date_value.year)+'-'+get_char_month(old_date_value.month, type_of_month)+' '+'nan'+'\n')
            if is_daily:
                while date_value > old_date_value + relativedelta(days=1):
                    old_date_value = old_date_value + relativedelta(days=1)
                    output_file.write(str(old_date_value.year)+'-'+output.fix_zeros(old_date_value.month)+'-'+output.fix_zeros(old_date_value.day)+' '+'nan'+'\n')

        old_date_value = date_value

        if type_of_month == 'monthly':
            month = output.fix_zeros(int(month))

        if is_monthly:
            output_file.write(year+'-'+str(month)+' '+str(value)+'\n')
        if is_daily:
            output_file.write(year+'-'+str(month)+'-'+str(day)+' '+str(value)+'\n')

    output_file.close()