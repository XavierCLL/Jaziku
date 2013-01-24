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

VERSION = "0.6.0"

VERSION_DATE = "12/01/2013"

# absolute directory where is installed Jaziku in your system,
# this variable is set in jaziku.py
JAZIKU_DIR = None

# accuracy of number decimal places, only for print result
ACCURACY = 4

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
WORK_DIR = None

#==============================================================================
# valid nulls

VALID_NULL = [99999, -99999]  # these are deprecate valid null but now used for maps files interpolation

def is_valid_null(value):
    """
    Check if value is a valid null value for variables dependent and independent (inside files input)

    return True if value is: 'nan', 'NaN', 'NAN', float('nan'), (deprecate: 99999, -99999)
    else return False
    """

    if isnan(value) or value in ['nan', 'NaN', 'NAN']:
        return True
    else:
        try:
            if int(float(value)) in VALID_NULL: # TODO: delete deprecated valid null
                return True
        except:
            return False
    return False

#==============================================================================

# trimester text for print
def get_trimester_in_text(trimester):
    _trim_text = {-2: _('NDJ'), -1: _('DJF'), 0: _('JFM'), 1: _('FMA'), 2: _('MAM'),
                 3: _('AMJ'), 4: _('MJJ'), 5: _('JJA'), 6: _('JAS'), 7: _('ASO'),
                 8: _('SON'), 9: _('OND'), 10: _('NDJ'), 11: _('DJF')}
    return _trim_text[trimester]


# month text for print
def get_month_in_text(month):
    _month_text = {-2: _('Nov'), -1: _('Dec'), 0: _('Jan'), 1: _('Feb'), 2: _('Mar'),
                  3: _('Apr'), 4: _('May'), 5: _('Jun'), 6: _('Jul'), 7: _('Aug'),
                  8: _('Sep'), 9: _('Oct'), 10: _('Nov'), 11: _('Dec')}
    return _month_text[month]

#==============================================================================
# types and units - VAR D

# Valid input types for dependent variable, known for jaziku
TYPES_VAR_D = ['PPT', 'NDPPT', 'TMIN', 'TMAX', 'TEMP', 'PATM', 'RH', 'RUNOFF']

# Units for types of dependent variable, known for jaziku
UNITS_FOR_TYPES_VAR_D = {'PPT':'mm', 'NDPPT':'#', 'TMIN':'Celsius', 'TMAX':'Celsius', 'TEMP':'Celsius',
                        'PATM':'mb', 'RH':'%', 'RUNOFF':'m^3/s'}

# variable use for set units for var D, known and unknown for jaziku
# for particular units set it in runfile, please read jaziku's manual
units_var_D = None

#==============================================================================
# types and units - VAR I

# Valid input types for independent variable, known and internal for jaziku
TYPES_VAR_I = ['ONI1', 'ONI2', 'SOI', 'SOI_TROUP', 'OLR', 'W200', 'W850w', 'W850c', 'W850e', 'SST12',
               'SST3', 'SST4', 'SST34', 'ASST12', 'ASST3', 'ASST4', 'ASST34', 'ARH', 'QBO', 'NAO', 'CAR', 'AREA_WHWP']

# Units for types for independent variable, known and internal for jaziku
UNITS_FOR_TYPES_VAR_I = {'ONI1':'anomaly', 'ONI2':'anomaly', 'SOI':'Std anomaly', 'SOI_TROUP':'Std anomaly', 'OLR':'W/m2',
                         'W200':'Std anomaly', 'W850w':'anomaly', 'W850c':'anomaly', 'W850e':'anomaly',
                         'SST12':'Celsius', 'SST3':'Celsius', 'SST4':'Celsius', 'SST34':'Celsius', 'ASST12':'anomaly',
                         'ASST3':'anomaly', 'ASST4':'anomaly', 'ASST34':'anomaly', 'ARH':'%', 'QBO':'Km/h',
                         'NAO':'anomaly', 'CAR':'Celsius', 'AREA_WHWP':'anomaly scaled 10e6 km^2'}

# variable use for set units for var I, known and unknown for jaziku
# for particular units set it in runfile, please read jaziku's manual
units_var_I = None

#==============================================================================
# VAR I internal

# types of internal independent variables (only internal variables for jaziku)
TYPES_OF_INTERNAL_VAR_I = ['ONI1', 'ONI2', 'SOI', 'SOI_TROUP', 'OLR', 'W200', 'W850w', 'W850c', 'W850e', 'SST12',
                           'SST3', 'SST4', 'SST34', 'ASST12', 'ASST3', 'ASST4', 'ASST34', 'ARH', 'QBO', 'NAO',
                           'CAR', 'AREA_WHWP']

# namefiles of internal independent variables for each type
FILES_FOR_INTERNAL_VAR_I = {
    "ONI1": "ONI1_1950_2012_CPC.txt",
    "ONI2": "ONI2_1950_2012_CPC_corr2012.txt",
    "SOI": "SOI_1951_2011_CPC_NOAA.txt",
    "SOI_TROUP": "SOI_TROUP_1876_2012_AustralinaBureau.txt",
    #"MEI": "MEI_1950_2011_ESRL_NOAA.txt",
    "OLR": "OLR_1974_2012_CPC_NCEP_NOAA.txt",
    "W200": "W200_1979_2012_CPC_NCEP_NOAA.txt",
    "W850w": "W850w_1979_2012_CPC_NCEP_NOAA.txt",
    "W850c": "W850c_1979_2012_CPC_NCEP_NOAA.txt",
    "W850e": "W850e_1979_2012_CPC_NCEP_NOAA.txt",
    "SST12": "SST12_1982_2012_CPC_NCEP_NOAA.txt",
    "SST3": "SST3_1982_2012_CPC_NCEP_NOAA.txt",
    "SST4": "SST4_1982_2012_CPC_NCEP_NOAA.txt",
    "SST34": "SST34_1982_2012_CPC_NCEP_NOAA.txt",
    "ASST12": "ASST12_1982_2012_CPC_NCEP_NOAA.txt",
    "ASST3": "ASST3_1982_2012_CPC_NCEP_NOAA.txt",
    "ASST4": "ASST4_1982_2012_CPC_NCEP_NOAA.txt",
    "ASST34": "ASST34_1982_2012_CPC_NCEP_NOAA.txt",
    "ARH": "ARH_DIPOLE_1979_2009_NCEPNCAR_REAL.txt", #TODO: update series
    "NAO": "NAO_1865_2012_Hurrel1995.txt",
    "QBO": "QBO_1979_2012_CPC_NOAA.txt",
    "CAR": "CAR_1951_2010_ESRL_NOAA.txt",
    "AREA_WHWP": "AREA_WHWP_1948_2012_ESRL_NOAA.txt"
}

# urls where get the internal files for independent variables for each type
URLS_FOR_INTERNAL_VAR_I = {
    "ONI1": "http://goo.gl/6tXjh", # http://www.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ensoyears_1971-2000_climo.shtml
    "ONI2": "http://goo.gl/e7unc", # http://www.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ensoyears.shtml
    "SOI": "http://goo.gl/scbO7", # http://www.cpc.ncep.noaa.gov/data/indices/soi
    "SOI_TROUP": "http://goo.gl/2hDk8", # http://www.bom.gov.au/climate/current/soihtm1.shtml
    #"MEI": "http://goo.gl/dQsdb", # http://www.esrl.noaa.gov/psd/enso/mei/table.html
    "OLR": "http://goo.gl/goMpA", # http://www.cpc.ncep.noaa.gov/data/indices/olr
    "W200": "http://goo.gl/aliLh", # http://www.cpc.ncep.noaa.gov/data/indices/zwnd200
    "W850w": "http://goo.gl/w4yiO", # http://www.cpc.ncep.noaa.gov/data/indices/wpac850
    "W850c": "http://goo.gl/gks7x", # http://www.cpc.ncep.noaa.gov/data/indices/cpac850
    "W850e": "http://goo.gl/N7cQ5", # http://www.cpc.ncep.noaa.gov/data/indices/epac850
    "SST12": "http://goo.gl/WcYSg", # http://www.cpc.ncep.noaa.gov/data/indices/
    "SST3": "http://goo.gl/WcYSg", # http://www.cpc.ncep.noaa.gov/data/indices/
    "SST4": "http://goo.gl/WcYSg", # http://www.cpc.ncep.noaa.gov/data/indices/
    "SST34": "http://goo.gl/WcYSg", # http://www.cpc.ncep.noaa.gov/data/indices/
    "ASST12": "http://goo.gl/WcYSg", # http://www.cpc.ncep.noaa.gov/data/indices/
    "ASST3": "http://goo.gl/WcYSg", # http://www.cpc.ncep.noaa.gov/data/indices/
    "ASST4": "http://goo.gl/WcYSg", # http://www.cpc.ncep.noaa.gov/data/indices/
    "ASST34": "http://goo.gl/WcYSg", # http://www.cpc.ncep.noaa.gov/data/indices/
    "ARH": "http://goo.gl/5oiZJ", # http://nomad1.ncep.noaa.gov/ncep_data/index.html
    "NAO": "http://goo.gl/ArdVn", # http://climatedataguide.ucar.edu/sites/default/files/cas_data_files/asphilli/nao_station_monthly_2.txt
    "QBO": "http://goo.gl/erjsJ and http://goo.gl/qKTrT", # http://www.cpc.ncep.noaa.gov/data/indices/qbo.u50.index and http://www.cpc.ncep.noaa.gov/data/indices/qbo.u30.index
    "CAR": "http://goo.gl/c0Xbv", # http://www.esrl.noaa.gov/psd/forecasts/sstlim/Globalsst.html
    "AREA_WHWP": "http://goo.gl/mV4QI"  # http://www.esrl.noaa.gov/psd/data/correlation/whwp.data
}

#==============================================================================
# analysis_interval
ALL_ANALYSIS_INTERVALS = ["5days", "10days", "15days", "trimester"]
NUM_DAYS_OF_ANALYSIS_INTERVAL = None
analysis_interval_i18n = None

STATE_OF_DATA = None

#==============================================================================
# forecast
forecast_phen_below = None
forecast_phen_normal = None
forecast_phen_above = None

#==============================================================================
# maps

# maps files for climate:
maps_files_climate = {'5days': None, '10days': None, '15days': None, 'trimester': None}
# maps files for correlation:
maps_files_correlation = {'5days': None, '10days': None, '15days': None, 'trimester': None}
# maps files for forecast:
maps_files_forecast = {'5days': {}, '10days': {}, '15days': {}, 'trimester': {}}

#==============================================================================
# graphics properties

def graphs_axis_properties(afs=15, ma='center'):
    axis_properties = {}
    axis_properties["fontsize"] = afs
    axis_properties["multialignment"] = ma
    return axis_properties

def graphs_title_properties(tfs=18, ma='center'):
    title_properties = {}
    title_properties["fontsize"] = tfs
    title_properties["multialignment"] = ma
    return title_properties


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
# threshold_problem is global variable for detect problem with
# threshold of independent variable, if a problem is detected
# show message and print "nan" (this mean null value for
# division by zero) in contingency tabla percent in result
# table, jaziku continue but the graphics will not be created
# because "nan"  character could not be calculate.
threshold_problem = [False, False, False]

