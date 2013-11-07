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

import os
import sys

from jaziku import env
from jaziku.utils import console


def number(num, accuracy=False):
    """
    Return the number after formatted according to accuracy (default or particular)
    and fix decimal character.
    """
    if accuracy:
        return str(round(float(num), accuracy)).replace('.', ',')
    else:
        return str(round(float(num), env.globals_vars.ACCURACY)).replace('.', ',')

def months_in_initials(month):
    """
    Return the initials of month (first three letters)
    """
    _month_text = {-2: _('Nov'), -1: _('Dec'), 0: _('Jan'), 1: _('Feb'), 2: _('Mar'),
                  3: _('Apr'), 4: _('May'), 5: _('Jun'), 6: _('Jul'), 7: _('Aug'),
                  8: _('Sep'), 9: _('Oct'), 10: _('Nov'), 11: _('Dec')}
    return _month_text[month]

def bi_months_in_initials(bimonthly):
    """
    Return the three first letters of two months of bimonthly
    """
    _bim_text = {-2: _('NovDic'), -1: _('DicJan'), 0: _('JanFeb'), 1: _('FebMar'), 2: _('MarApr'),
                 3: _('AprMay'), 4: _('MayJun'), 5: _('JunJul'), 6: _('JulAug'), 7: _('AugSep'),
                  8: _('SepOct'), 9: _('OctNov'), 10: _('NovDic'), 11: _('DecJan')}
    return _bim_text[bimonthly]

def tri_months_in_initials(trimonthly):
    """
    Return the three first letters of three months of trimonthly
    """
    _trim_text = {-2: _('NDJ'), -1: _('DJF'), 0: _('JFM'), 1: _('FMA'), 2: _('MAM'),
                 3: _('AMJ'), 4: _('MJJ'), 5: _('JJA'), 6: _('JAS'), 7: _('ASO'),
                 8: _('SON'), 9: _('OND'), 10: _('NDJ'), 11: _('DJF')}
    return _trim_text[trimonthly]

def n_months_in_initials(type, n_month):
    if env.var_[type].is_monthly():
        return months_in_initials(n_month)
    if env.var_[type].is_bimonthly():
        return bi_months_in_initials(n_month)
    if env.var_[type].is_trimonthly():
        return tri_months_in_initials(n_month)

def n_monthly_int2char(int_month, type=False, n_monthly=False):
    int_month = int(int_month)
    if (type and env.var_[type].is_monthly()) or n_monthly == 1:
        return fix_zeros(int_month)
    if (type and env.var_[type].is_bimonthly()) or n_monthly == 2:
        char_month_dict = {1:'jf', 2: 'fm', 3: 'ma',4: 'am', 5: 'mj', 6: 'jj', 7: 'ja', 8: 'as', 9: 'so', 10: 'on', 11: 'nd', 12: 'dj'}
    if (type and env.var_[type].is_trimonthly()) or n_monthly == 3:
        char_month_dict = {1:'jfm', 2: 'fma', 3: 'mam',4: 'amj', 5: 'mjj', 6: 'jja', 7: 'jas', 8: 'aso', 9: 'son', 10: 'ond', 11: 'ndj', 12: 'djf'}

    if int_month in char_month_dict:
        return char_month_dict[int_month]
    else:
        return False

def bimonthly_int2char(int_month):
    return n_monthly_int2char(int_month, n_monthly=2)

def trimonthly_int2char(int_month):
    return n_monthly_int2char(int_month, n_monthly=3)

def make_dirs(_dir):
    if not os.path.isdir(_dir):
        try:
            os.makedirs(_dir)
        except Exception as error:
            console.msg_error(_("Problems creating the directory: {0}\n"
                                "\n{1}").format(_dir, error), False)

def prepare_dirs():
    from jaziku.utils import query
    # -------------------------------------------------------------------------
    # main output directory
    console.msg(_("\nDirectory where to save all results:"), newline=False)
    console.msg(env.globals_vars.OUTPUT_DIR, color='cyan')
    make_dirs(env.globals_vars.OUTPUT_DIR)

    # -------------------------------------------------------------------------
    # output directory by module activated

    dirs_existent = []

    # data analysis dir output result
    if env.config_run.settings['data_analysis']:
        env.globals_vars.DATA_ANALYSIS_DIR \
            = os.path.join(env.globals_vars.OUTPUT_DIR, _('Jaziku_Data_Analysis'))
        if os.path.isdir(env.globals_vars.DATA_ANALYSIS_DIR):
            dirs_existent.append(env.globals_vars.DATA_ANALYSIS_DIR)

    # climate dir output result
    if env.config_run.settings['climate_process']:
        env.globals_vars.CLIMATE_DIR \
            = os.path.join(env.globals_vars.OUTPUT_DIR, _('Jaziku_Climate'))
        if os.path.isdir(env.globals_vars.CLIMATE_DIR):
            dirs_existent.append(env.globals_vars.CLIMATE_DIR)

    # directory for the forecast results
    if env.config_run.settings['forecast_process']:
        env.globals_vars.FORECAST_DIR \
            = os.path.join(env.globals_vars.OUTPUT_DIR, _('Jaziku_Forecast'))
        if os.path.isdir(env.globals_vars.FORECAST_DIR):
            dirs_existent.append(env.globals_vars.FORECAST_DIR)

    if not len(dirs_existent) == 0:
        console.msg(_(" > WARNING: the following output directories already exist:"), color='yellow')
        for dir in dirs_existent:
            console.msg("   "+dir, color='cyan')

        query_output_directory \
            = query.directory(_("   What do you like to do? [r]eplace, [m]erge or [c]ancel"),
                              dirs_existent)

        if not query_output_directory:
            console.msg(_("\nexit"),color='red')
            console.msg_footer()
            sys.exit()

def fix_zeros(dt):
    '''When the number is less to 10 put 0 before the number,
    e.g. 5 -> 05, 8 -> 08
    '''

    return '0'+str(dt) if len(str(dt))<2 else str(dt)