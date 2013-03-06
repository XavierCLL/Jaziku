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
FREQUENCY_DATA = None

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
    'NDPPT':        '#',
    'TMIN':         'Celsius',
    'TMAX':         'Celsius',
    'TEMP':         'Celsius',
    'PATM':         'mb',
    'RH':           '%',
    'RUNOFF':       'm^3/s'
}

# variable use for set units for var D, known and unknown for jaziku
# for particular units set it in runfile, please read jaziku's manual
units = None

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
    'PPT':          {'daily':   [0,200],       'monthly': [0,3500]},
    'NDPPT':        {'daily':   None,          'monthly': [0,31]},
    'TMIN':         {'daily':   [-15,22],      'monthly': [-15,50]},
    'TMAX':         {'daily':   [-15,34],      'monthly': [-15,50]},
    'TEMP':         {'daily':   [-15,34],      'monthly': [-15,50]},
    'PATM':         {'daily':   [400,1100],    'monthly': [400,1100]},
    'RH':           {'daily':   [0,100],       'monthly': [0,100]},
    'RUNOFF':       {'daily':   [0,3300],      'monthly': [0,3300]},
}


# thresholds when class_category_analysis is 3
INTERNAL_THRESHOLDS_3_CATEGORIES = {}

# thresholds when class_category_analysis is 7
INTERNAL_THRESHOLDS_7_CATEGORIES = {}


#==============================================================================
# functions

def get_internal_limits():
    global FREQUENCY_DATA
    global TYPE_SERIES

    if TYPE_SERIES in INTERNAL_LIMITS:
        return INTERNAL_LIMITS[TYPE_SERIES][FREQUENCY_DATA]
    else:
        return [None,None]

def is_daily():
    global FREQUENCY_DATA
    if FREQUENCY_DATA == 'daily':
        return True
    else:
        return False

def is_monthly():
    global FREQUENCY_DATA
    if FREQUENCY_DATA == 'monthly':
        return True
    else:
        return False

def set_FREQUENCY_DATA(new_freq_data, check=True):
    global FREQUENCY_DATA
    global TYPE_SERIES
    if FREQUENCY_DATA is None or check is False:
        FREQUENCY_DATA = new_freq_data
    else:
        if not FREQUENCY_DATA == new_freq_data:
            raise ValueError(_("The frequency data '{0}' for the var D is different\n"
                               "for the others stations before assigned as '{2}'.\n\n"
                               "Jaziku requires that all stations for var D\n"
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