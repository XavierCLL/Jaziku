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

def to_int(item):
    try:
        return int(float(str(item).replace(',', '.')))
    except:
        return item

def to_float(item):
    try:
        return float(str(item).replace(',', '.'))
    except:
        return item

def n_monthly_char2int(char_month, n_monthly):
    char_month = str(char_month).lower()
    if n_monthly == 2:
        # date_char = {1:'jf', 2: 'fm', 3: 'ma',4: 'am', 5: 'mj', 6: 'jj', 7: 'ja', 8: 'as', 9: 'so', 10: 'on', 11: 'nd', 12: 'dj'}
        char_month_dict = {'jf': 1, 'fm': 2, 'ma': 3, 'am': 4, 'mj': 5, 'jj': 6, 'ja': 7, 'as': 8, 'so': 9, 'on': 10, 'nd': 11, 'dj': 12, }
    if n_monthly == 3:
        # date_char = {1:'jfm', 2: 'fma', 3: 'mam',4: 'amj', 5: 'mjj', 6: 'jja', 7: 'jas', 8: 'aso', 9: 'son', 10: 'ond', 11: 'ndj', 12: 'djf'}
        char_month_dict = { 'jfm': 1, 'fma': 2, 'mam': 3, 'amj': 4, 'mjj': 5, 'jja': 6, 'jas': 7, 'aso': 8, 'son': 9, 'ond': 10, 'ndj': 11, 'djf': 12}

    if char_month in char_month_dict:
        return char_month_dict[char_month]
    else:
        return False

def bimonthly_char2int(char_month):
    return n_monthly_char2int(char_month, 2)

def trimonthly_char2int(char_month):
    return n_monthly_char2int(char_month, 3)
