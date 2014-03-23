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

from math import isnan

#==============================================================================
# GLOBAL VARIABLES AND FUNCTIONS
#==============================================================================

#==============================================================================
# general

PROG_NAME = "jaziku"

VERSION = "0.9.1"

VERSION_DATE = "11/02/2014"

# absolute directory where is installed Jaziku in your system,
# this variable is set in jaziku.py
JAZIKU_DIR = None

# default of number of significant figures, only for output result
DEFAULT_N_SIG_FIGS = 4

#==============================================================================
# arguments, inputs and outputs

# delimiter for inputs and outputs
INPUT_CSV_DELIMITER = ";"
OUTPUT_CSV_DELIMITER = ";"

# run arguments
ARGS = None

# absolute directory to save all result,
# this is absolute directory where is the runfile + filename of runfile,
# this variable is set in jaziku.py
OUTPUT_DIR = None

#==============================================================================
# valid nulls

OLD_VALID_NULL = [99999, -99999]  # these are deprecate valid null but now used for maps files interpolation

def is_valid_null(value):
    """
    Check if value is a valid null value for variables dependent and independent (inside files input)

    return True if value is: 'nan', 'NaN', 'NAN', float('nan'), (deprecate: 99999, -99999)
    else return False
    """

    if value in ['nan', 'NaN', 'NAN']:
        return True
    else:
        try:
            if isinstance(value,(float,int)) and isnan(value):
                return True
            if int(float(value)) in OLD_VALID_NULL: # TODO: delete deprecated valid null
                return True
        except:
            return False
    return False

#==============================================================================
# analysis_interval
ALL_ANALYSIS_INTERVALS = ["5days", "10days", "15days", "monthly", "bimonthly", "trimonthly"]
NUM_DAYS_OF_ANALYSIS_INTERVAL = None

#==============================================================================
# categories of var I

def categories(key_label=False, include_normal=True, translated=True, as_list=False):
    from jaziku.env.config_run import settings
    if settings['class_category_analysis'] == 3:
        if translated:
            labels = {'below':unicode(_('below'), 'utf-8'),
                      'normal':unicode(_('normal'), 'utf-8'),
                      'above':unicode(_('above'), 'utf-8')}
        else:
            labels = {'below':'below',
                      'normal':'normal',
                      'above':'above'}
    if settings['class_category_analysis'] == 7:
        if translated:
            labels = {'below3':unicode(_('strong below'), 'utf-8'),
                      'below2':unicode(_('moderate below'), 'utf-8'),
                      'below1':unicode(_('weak below'), 'utf-8'),
                      'normal':unicode(_('normal'), 'utf-8'),
                      'above1':unicode(_('weak above'), 'utf-8'),
                      'above2':unicode(_('moderate above'), 'utf-8'),
                      'above3':unicode(_('strong above'), 'utf-8')}
        else:
            labels = {'below3':'strong below',
                      'below2':'moderate below',
                      'below1':'weak below',
                      'normal':'normal',
                      'above1':'weak above',
                      'above2':'moderate above',
                      'above3':'strong above'}

    if include_normal is False:
        del labels['normal']

    if key_label in labels:
        return labels[key_label]
    elif key_label is None:
        return float('nan')

    if as_list is True:
        if include_normal is True:
            if settings['class_category_analysis'] == 3:
                return [labels['below'],
                        labels['normal'],
                        labels['above']]
            if settings['class_category_analysis'] == 7:
                return [labels['below3'],
                        labels['below2'],
                        labels['below1'],
                        labels['normal'],
                        labels['above1'],
                        labels['above2'],
                        labels['above3']]
        else:
            if settings['class_category_analysis'] == 3:
                return [labels['below'],
                        labels['above']]
            if settings['class_category_analysis'] == 7:
                return [labels['below3'],
                        labels['below2'],
                        labels['below1'],
                        labels['above1'],
                        labels['above2'],
                        labels['above3']]
    else:
        return labels

#==============================================================================
# maps

# maps files for climate:
maps_files_climate = {}  # [lag][month][var_I_labels]
# maps files for correlation:
#maps_files_correlation = {'5days': None, '10days': None, '15days': None, 'trimonthly': None}  # [lag][month][var_I_labels]
maps_files_correlation = {}  # [lag][month][var_I_labels]
# maps files for forecast:
#maps_files_forecast = {'5days': {}, '10days': {}, '15days': {}, 'trimonthly': {}}  # [lag][month][var_I_labels]
maps_files_forecast = {}  # [lag][month][var_I_labels]

#==============================================================================
# graphics properties

colors = {
    'plt_default': '#638786',

    'grey_W2': '#F0F0F0',  # Weak
    'grey_W1': '#D8D8D8',
    'grey_S1': '#8A8A8A',
    'grey_S2': '#646464',
    'grey_S3': '#535353',
    'grey_S4': '#4E4E4E',
    'grey_S5': '#3F3F3F',  # Strong
}

def graphs_subplot_properties(bg_color=colors['grey_W2']):
    subplot_properties = {}
    subplot_properties["axisbg"] = bg_color
    return subplot_properties

def graphs_axis_properties(fs=15, fa='center', fw='bold', fc=colors['grey_S2']):
    axis_properties = {}
    axis_properties["fontsize"] = fs
    axis_properties["multialignment"] = fa
    axis_properties["weight"] = fw
    axis_properties["color"] = fc
    return axis_properties

def graphs_title_properties(fs=17, fa='center', fva='bottom', ff='sans-serif', fw='bold', fc=colors['grey_S5']):
    title_properties = {}
    title_properties["fontsize"] = fs
    title_properties["multialignment"] = fa
    title_properties["verticalalignment"] = fva
    title_properties["family"] = ff
    title_properties["weight"] = fw
    title_properties["color"] = fc
    return title_properties

def figure_plot_properties(color=colors['plt_default'], mec=colors['plt_default'], ms=8):
    plot_properties = {}
    plot_properties["color"] = color
    plot_properties["markersize"] = ms
    plot_properties["mec"] = mec
    return plot_properties

def figure_bar_properties(color=colors['plt_default'], eg_color='none', align='center'):
    bar_properties = {}
    bar_properties["color"] = color
    bar_properties["edgecolor"] = eg_color
    bar_properties["align"] = align
    return bar_properties

def set_others_properties(ax, ts=14.5):
    # text in axes
    ax.tick_params(axis='both', which='major', labelsize=ts, labelcolor=colors['grey_S3'])
    #ax.tick_params(axis='both', which='minor', labelsize=8)
    # line border of box of subplot
    for spine in ax.spines.values():
        spine.set_edgecolor(colors['grey_S1'])
        spine.set_linewidth(1.2)


#==============================================================================
# settings to run, this si a global variable of 'settings' inside of settings_to_run
input_settings = {}

#==============================================================================
# globals variable for defined lags, lags = [ 0, 1 and/or 2 ]
ALL_LAGS = [0, 1, 2]

#==============================================================================
# globals directories

CLIMATE_DIR = None

FORECAST_DIR = None

DATA_ANALYSIS_DIR = None

#==============================================================================
# this is the probability_forecast_values for forecast process to use in
# the forecast_contingency_table.
# probability_forecast_values:
#   3x3 -> [lags]['below','normal','above']
#   3x7 -> [lags]['below3','normal','above2',  'below'='below3','above'='above2]  # e.g. values in 'below3','normal','above2'
#   7x7 -> [lags]['below3','below2','below1','normal','above1','above2','above3']

probability_forecast_values = {'type': None}

#==============================================================================
# this is the forecast_contingency_table for forecast process
# type = '3x3' '3x7' '7x7'

forecast_contingency_table = {'type': None}
