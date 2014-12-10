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

from jaziku.env import config_run

#==============================================================================
# types and units for internal VAR D

# globals vars for all var I
TYPE_SERIES = None

#
FREQUENCY_DATA = None

#
was_converted = False

def get_FREQUENCY_DATA(adverb=True):
    global FREQUENCY_DATA
    if adverb:
        _freq_data ={'daily': _('daily'),
                     '5days': _('5 days'),
                     '10days': _('10 days'),
                     '15days': _('15 days'),
                     'monthly': _('monthly'),
                     'bimonthly': _('bimonthly'),
                     'trimonthly': _('trimonthly')}
    else:
        _freq_data ={'daily': _('days'),
                     '5days': _('5 days'),
                     '10days': _('10 days'),
                     '15days': _('15 days'),
                     'monthly': _('months'),
                     'bimonthly': _('2 months'),
                     'trimonthly': _('3 months')}
    return _freq_data[FREQUENCY_DATA]

# Valid input types for dependent variable, known for jaziku
INTERNAL_TYPES = [
    'PPT',          # precipitation
    'NDPPT',        # number of days with rain
    'TMIN',         # minimum temperature
    'TMAX',         # maximum temperature
    'TEMP',         # medium temperature
    'PATM',         # atmosphere pressure
    'RH',           # % of relative humidity
    'RUNOFF'        # Runoff
]

# Units for types of dependent variable, known for jaziku
INTERNAL_UNITS = {
    'PPT':          'mm',
    'NDPPT':        'days',
    'TMIN':         'Celsius',
    'TMAX':         'Celsius',
    'TEMP':         'Celsius',
    'PATM':         'mb',
    'RH':           '%',
    'RUNOFF':       'm^3/s'
}

# translate internal units
def INTERNAL_UNITS_i18n():
    global INTERNAL_UNITS
    INTERNAL_UNITS['NDPPT'] = _('days')

    if TYPE_SERIES in INTERNAL_UNITS:
        global UNITS
        UNITS = INTERNAL_UNITS[TYPE_SERIES]

# variable use for set units for var D, known and unknown for jaziku
# for particular units set it in runfile, please read jaziku's manual
UNITS = None

# available mode calculation series for internal dependent variable
# the fist element is by default (options: ['mean', 'accumulate'],)
MODE_CALCULATION_SERIES = {
    'PPT':      ['accumulate', 'mean'],
    'NDPPT':    ['accumulate', 'mean'],
    'TMIN':     ['mean'],
    'TMAX':     ['mean'],
    'TEMP':     ['mean'],
    'PATM':     ['mean'],
    'RH':       ['mean'],
    'RUNOFF':   ['mean'],
}

# Internal limits for var_D (dependent variable)
#
# If inputs are monthly:
#
#     Variable        Abbreviation   Units          Range of variation
#  Precipitation----------PPT         mm             0mm<=Ppt<=3500mm
#  Num. of days
#   with rain------------NDPPT        -     (0 or num of days valid for month/year)
#  Temp. min-------------TMIN        °C             -15°C<=Tmin<=50°C
#  Temp. max-------------TMAX        °C             -15°C<=Tmin<=50°C
#  Temp. medium----------TEMP        °C             -15°C<=Tmin<=50°C
#  Atmosfere pressure----PATM        mb              400mb<=P<=1100mb
#  % relative humidity----RH          -                0%<=RH<=100%
#  Runoff---------------RUNOFF      m^3/s                0 to 3300
#
# If inputs are daily:
#
#     Variable        Abbreviation   Units          Range of variation
#  Precipitation----------PPT         mm             0mm<=Ppt<=200mm
#  Num. of days
#   with rain------------NDPPT        #     (0 or num of days valid for month/year)
#  Temp. min-------------TMIN        °C             -15°C<=Tmin<=22°C
#  Temp. max-------------TMAX        °C             -15°C<=Tmin<=34°C
#  Temp. medium----------TEMP        °C             -15°C<=Tmin<=34°C
#  Atmosfere pressure----PATM        mb              400mb<=P<=1100mb
#  % relative humidity----RH          %                0%<=RH<=100%
#  Runoff---------------RUNOFF      m^3/s                0 to 3300

INTERNAL_LIMITS = {
    'PPT':      {'daily': [0,200],
                  'monthly': [0,3500],
                  'bimonthly': [0,3500],
                  'trimonthly': [0,3500]},

    'NDPPT':    {'daily': None,
                  'monthly': [0,31],
                  'bimonthly': [0,62],
                  'trimonthly': [0,93]},

    'TMIN':     {'daily': [-15,25],
                  'monthly': [-15,50],
                  'bimonthly': [-15,50],
                  'trimonthly': [-15,50]},

    'TMAX':     {'daily': [-15,35],
                  'monthly': [-15,50],
                  'bimonthly': [-15,50],
                  'trimonthly': [-15,50]},

    'TEMP':     {'daily': [-15,35],
                  'monthly': [-15,50],
                  'bimonthly': [-15,50],
                  'trimonthly': [-15,50]},

    'PATM':     {'daily': [400,1100],
                  'monthly': [400,1100],
                  'bimonthly': [400,1100],
                  'trimonthly': [400,1100]},

    'RH':       {'daily': [0,100],
                  'monthly': [0,100],
                  'bimonthly': [0,100],
                  'trimonthly': [0,100]},

    'RUNOFF':   {'daily': [0,3300],
                  'monthly': [0,3300],
                  'bimonthly': [0,3300],
                  'trimonthly': [0,3300]},
}

# When the 'normal_inclusive' is True this mean that for the normal values the thresholds
# are inclusive:
#
# if 'normal_inclusive' == True:
#   threshold_below* <= normal <= threshold_above*
# if 'normal_inclusive' == False:
#   threshold_below* < normal < threshold_above*

# thresholds when class_category_analysis is 3
THRESHOLDS_3_CATEGORIES = {
    ## thresholds by default
    'default':  {'daily': ['p33','p66'],
                  '5days': ['p33','p66'],
                  '10days': ['p33','p66'],
                  '15days': ['p33','p66'],
                  'monthly': ['p33','p66'],
                  'bimonthly': ['p33','p66'],
                  'trimonthly': ['p33','p66'],
                  'normal_inclusive': True},

    ## thresholds by type of internal series  (if was not defined here, will use thresholds by default)
    'PPT':      {'daily': ['90%','110%'],
                  '5days': ['90%','110%'],
                  '10days': ['90%','110%'],
                  '15days': ['90%','110%'],
                  'monthly': ['90%','110%'],
                  'bimonthly': ['90%','110%'],
                  'trimonthly': ['90%','110%'],
                  'normal_inclusive': True},

    'TMIN':     {'daily': [-1,1],
                  '5days': [-1,1],
                  '10days': [-1,1],
                  '15days': [-1,1],
                  'monthly': [-1,1],
                  'bimonthly': [-1,1],
                  'trimonthly': [-1,1],
                  'normal_inclusive': True},

    'TMAX':     {'daily': [-1,1],
                  '5days': [-1,1],
                  '10days': [-1,1],
                  '15days': [-1,1],
                  'monthly': [-1,1],
                  'bimonthly': [-1,1],
                  'trimonthly': [-1,1],
                  'normal_inclusive': True},

    'TEMP':     {'daily': [-1,1],
                  '5days': [-1,1],
                  '10days': [-1,1],
                  '15days': [-1,1],
                  'monthly': [-1,1],
                  'bimonthly': [-1,1],
                  'trimonthly': [-1,1],
                  'normal_inclusive': True},
}

# thresholds when class_category_analysis is 7
THRESHOLDS_7_CATEGORIES = {
    ## thresholds by default
    'default':  {'daily': ['p11','p22','p33','p66','p77','p88'],
                  '5days': ['p11','p22','p33','p66','p77','p88'],
                  '10days': ['p11','p22','p33','p66','p77','p88'],
                  '15days': ['p11','p22','p33','p66','p77','p88'],
                  'monthly': ['p11','p22','p33','p66','p77','p88'],
                  'bimonthly': ['p11','p22','p33','p66','p77','p88'],
                  'trimonthly': ['p11','p22','p33','p66','p77','p88'],
                  'normal_inclusive': True},

    ## thresholds by type of internal series  (if was not defined here, will use thresholds by default)
    'PPT':      {'daily': ['30%','60%','90%','110%','140%','170%'],
                  '5days': ['30%','60%','90%','110%','140%','170%'],
                  '10days': ['30%','60%','90%','110%','140%','170%'],
                  '15days': ['30%','60%','90%','110%','140%','170%'],
                  'monthly': ['30%','60%','90%','110%','140%','170%'],
                  'bimonthly': ['30%','60%','90%','110%','140%','170%'],
                  'trimonthly': ['30%','60%','90%','110%','140%','170%'],
                  'normal_inclusive': True},

    'TMIN':     {'daily': [-2,-1.5,-1,1,1.5,2],
                  '5days': [-2,-1.5,-1,1,1.5,2],
                  '10days': [-2,-1.5,-1,1,1.5,2],
                  '15days': [-2,-1.5,-1,1,1.5,2],
                  'monthly': [-2,-1.5,-1,1,1.5,2],
                  'bimonthly': [-2,-1.5,-1,1,1.5,2],
                  'trimonthly': [-2,-1.5,-1,1,1.5,2],
                  'normal_inclusive': True},

    'TMAX':     {'daily': [-2,-1.5,-1,1,1.5,2],
                  '5days': [-2,-1.5,-1,1,1.5,2],
                  '10days': [-2,-1.5,-1,1,1.5,2],
                  '15days': [-2,-1.5,-1,1,1.5,2],
                  'monthly': [-2,-1.5,-1,1,1.5,2],
                  'bimonthly': [-2,-1.5,-1,1,1.5,2],
                  'trimonthly': [-2,-1.5,-1,1,1.5,2],
                  'normal_inclusive': True},

    'TEMP':     {'daily': [-2,-1.5,-1,1,1.5,2],
                  '5days': [-2,-1.5,-1,1,1.5,2],
                  '10days': [-2,-1.5,-1,1,1.5,2],
                  '15days': [-2,-1.5,-1,1,1.5,2],
                  'monthly': [-2,-1.5,-1,1,1.5,2],
                  'bimonthly': [-2,-1.5,-1,1,1.5,2],
                  'trimonthly': [-2,-1.5,-1,1,1.5,2],
                  'normal_inclusive': True},
}


#==============================================================================
# functions

def get_internal_limits():
    global FREQUENCY_DATA
    global TYPE_SERIES

    if TYPE_SERIES in INTERNAL_LIMITS:
        if FREQUENCY_DATA in ['5days','10days','15days']:
            return INTERNAL_LIMITS[TYPE_SERIES]['daily']
        return INTERNAL_LIMITS[TYPE_SERIES][FREQUENCY_DATA]
    else:
        return [None,None]

def get_default_thresholds():
    from jaziku.env import config_run
    global FREQUENCY_DATA
    global TYPE_SERIES

    thresholds_by_category = {3:THRESHOLDS_3_CATEGORIES,
                              7:THRESHOLDS_7_CATEGORIES}

    THRESHOLDS = thresholds_by_category[config_run.settings['class_category_analysis']]

    if TYPE_SERIES in THRESHOLDS and \
       THRESHOLDS[TYPE_SERIES][FREQUENCY_DATA] != 'default':
        return THRESHOLDS[TYPE_SERIES][FREQUENCY_DATA]
    else:
        return THRESHOLDS['default'][FREQUENCY_DATA]

def get_global_thresholds():
    from jaziku.env import config_run
    if config_run.settings['thresholds_var_D'] == 'default':
        return get_default_thresholds()
    else:
        return config_run.settings['thresholds_var_D']

def is_n_daily():
    global FREQUENCY_DATA
    if FREQUENCY_DATA in ["daily", "5days", "10days", "15days"]:
        return True
    else:
        return False

def is_daily():
    global FREQUENCY_DATA
    if FREQUENCY_DATA == 'daily':
        return True
    else:
        return False

def is_n_monthly():
    global FREQUENCY_DATA
    if FREQUENCY_DATA in ['monthly', 'bimonthly', 'trimonthly']:
        return True
    else:
        return False

def is_monthly():
    global FREQUENCY_DATA
    if FREQUENCY_DATA == 'monthly':
        return True
    else:
        return False

def is_bimonthly():
    global FREQUENCY_DATA
    if FREQUENCY_DATA == 'bimonthly':
        return True
    else:
        return False

def is_trimonthly():
    global FREQUENCY_DATA
    if FREQUENCY_DATA == 'trimonthly':
        return True
    else:
        return False

def is_normal_inclusive():
    global TYPE_SERIES
    from jaziku.env import config_run

    if config_run.settings['class_category_analysis'] == 3:
        if TYPE_SERIES in THRESHOLDS_3_CATEGORIES:
            return THRESHOLDS_3_CATEGORIES[TYPE_SERIES]['normal_inclusive']
        else:
            return THRESHOLDS_3_CATEGORIES['default']['normal_inclusive']
    if config_run.settings['class_category_analysis'] == 7:
        if TYPE_SERIES in THRESHOLDS_7_CATEGORIES:
            return THRESHOLDS_7_CATEGORIES[TYPE_SERIES]['normal_inclusive']
        else:
            return THRESHOLDS_7_CATEGORIES['default']['normal_inclusive']

def set_FREQUENCY_DATA(new_freq_data, check=True):
    global FREQUENCY_DATA
    global TYPE_SERIES

    if new_freq_data not in ["daily", "5days", "10days", "15days", "monthly", "bimonthly", "trimonthly"]:
        raise

    if FREQUENCY_DATA is None or check is False:
        FREQUENCY_DATA = new_freq_data
    else:
        if not FREQUENCY_DATA == new_freq_data:
            raise ValueError(_("The new frequency data '{0}' for the var {1} is different\n"
                               "for the others stations before assigned as '{2}'.\n\n"
                               "Jaziku requires that all stations for var {1}\n"
                               "have identical frequency data.")
            .format(new_freq_data, TYPE_SERIES, FREQUENCY_DATA))

def get_generic_labels(upper=False):
    # generic labels for var D
    LABELS_3_CATEGORIES = [_('var D below'), _('var D normal'), _('var D above')]
    LABELS_7_CATEGORIES = [_('var D strong below'), _('var D moderate below'), _('var D weak below'), _('var D normal'),
                           _('var D weak above'), _('var D moderate above'), _('var D strong above')]

    if config_run.settings['class_category_analysis'] == 3:
        if upper:
            return [label.upper() for label in LABELS_3_CATEGORIES]
        else:
            return LABELS_3_CATEGORIES
    if config_run.settings['class_category_analysis'] == 7:
        if upper:
            return [label.upper() for label in LABELS_7_CATEGORIES]
        else:
            return LABELS_7_CATEGORIES