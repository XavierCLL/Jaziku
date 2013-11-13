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


#==============================================================================
# types and units for internal VAR I

# globals vars for all var I
TYPE_SERIES = None

#
FREQUENCY_DATA = None

def get_FREQUENCY_DATA():
    global FREQUENCY_DATA
    _freq_data ={'daily': _('daily'),
                 'monthly': _('monthly'),
                 'bimonthly': _('bimonthly'),
                 'trimonthly': _('trimonthly')}
    return _freq_data[FREQUENCY_DATA]

# Valid input types for independent variable, known and internal for jaziku

INTERNAL_TYPES = [
    'ONI1',         # Oceanic Nino Index
    'ONI2',         # Oceanic Nino Index
    'SOI',          # Index of the Southern Oscillation NOAA
    'SOI_TROUP',    # Index of the Southern Oscillation calculated between Tahiti and Darwin
    'MEI',          # Multivariate ENSO index
    'OLR',          # Radiation wavelength Long tropical
    'W200',         # Index of wind anomaly to 200 hpa
    'W850w',        # Index of wind anomaly to 850 hpa west
    'W850c',        # Index of wind anomaly to 850 hpa center
    'W850e',        # Index of wind anomaly to 850 hpa east
    'SST12',        # Sea surface temperature area 1-2
    'SST3',         # Sea surface temperature area 3
    'SST4',         # Sea surface temperature area 4
    'SST34',        # Sea surface temperature area 3-4
    'ASST12',       # Anomaly Sea surface temperature area 1-2
    'ASST3',        # Anomaly Sea surface temperature area 3
    'ASST4',        # Anomaly Sea surface temperature area 4
    'ASST34',       # Anomaly Sea surface temperature area 3-4
    'ARH',          # % Amazon relative humidity
    'QBO',          # quasibienal oscillation index
    'NAO',          # North atlantic oscillation index
    'CAR',          # Caribbean (CAR) Index
    'AREA_WHWP'     # Monthly anomaly of the ocean surface area Ocean region
]

# Units for types for independent variable, known and internal for jaziku
INTERNAL_UNITS = {
    'ONI1':         'anomaly',
    'ONI2':         'anomaly',
    'SOI':          'Std anomaly',
    'SOI_TROUP':    'Std anomaly',
    'MEI':          '-',
    'OLR':          'W/m2',
    'W200':         'Std anomaly',
    'W850w':        'anomaly',
    'W850c':        'anomaly',
    'W850e':        'anomaly',
    'SST12':        'Celsius',
    'SST3':         'Celsius',
    'SST4':         'Celsius',
    'SST34':        'Celsius',
    'ASST12':       'anomaly',
    'ASST3':        'anomaly',
    'ASST4':        'anomaly',
    'ASST34':       'anomaly',
    'ARH':          '%',
    'QBO':          'Km/h',
    'NAO':          'anomaly',
    'CAR':          'Celsius',
    'AREA_WHWP':    'anomaly scaled 10e6 km^2'
}

# translate internal units
def INTERNAL_UNITS_i18n():
    global INTERNAL_UNITS
    INTERNAL_UNITS['ONI1'] = _('anomaly')
    INTERNAL_UNITS['ONI2'] = _('anomaly')
    INTERNAL_UNITS['SOI'] = _('Std anomaly')
    INTERNAL_UNITS['SOI_TROUP'] = _('Std anomaly')
    INTERNAL_UNITS['W200'] = _('Std anomaly')
    INTERNAL_UNITS['W850w'] = _('anomaly')
    INTERNAL_UNITS['W850c'] = _('anomaly')
    INTERNAL_UNITS['W850e'] = _('anomaly')
    INTERNAL_UNITS['ASST12'] = _('anomaly')
    INTERNAL_UNITS['ASST3'] = _('anomaly')
    INTERNAL_UNITS['ASST4'] = _('anomaly')
    INTERNAL_UNITS['ASST34'] = _('anomaly')
    INTERNAL_UNITS['NAO'] = _('anomaly')
    INTERNAL_UNITS['AREA_WHWP'] = _('anomaly scaled 10e6 km^2')

    if TYPE_SERIES in INTERNAL_UNITS:
        global UNITS
        UNITS = INTERNAL_UNITS[TYPE_SERIES]

# variable use for set units for var I, known and unknown for jaziku
# for particular units set it in runfile, please read jaziku's manual
UNITS = None

# available mode calculation series for internal independent variable
# the fist element is by default (options: ['mean', 'accumulate'],)
MODE_CALCULATION_SERIES = {
    'ONI1':         ['mean'],
    'ONI2':         ['mean'],
    'SOI':          ['mean'],
    'SOI_TROUP':    ['mean'],
    'MEI':          ['mean'],
    'OLR':          ['mean'],
    'W200':         ['mean'],
    'W850w':        ['mean'],
    'W850c':        ['mean'],
    'W850e':        ['mean'],
    'SST12':        ['mean'],
    'SST3':         ['mean'],
    'SST4':         ['mean'],
    'SST34':        ['mean'],
    'ASST12':       ['mean'],
    'ASST3':        ['mean'],
    'ASST4':        ['mean'],
    'ASST34':       ['mean'],
    'ARH':          ['mean'],
    'QBO':          ['mean'],
    'NAO':          ['mean'],
    'CAR':          ['mean'],
    'AREA_WHWP':    ['mean'],
}

# Internal limits for var_I (independent variable)
#
#     Variable                     Abbreviation     Units          Range of variation
# Oceanic Nino Index--------------ONI1 and ONI2    anomaly             -5 to 5
# Index of the Southern
# Oscillation NOAA--------------------SOI        std anomaly           -7 to 7
# Index of the Southern
# Oscillation (TROUP)--------------SOI_TROUP     std anomaly          -35 to 35
# Multivariate ENSO index------------ MEI            #             -4.552 to 6.078
# Radiation wavelength
# Long tropical---------------------- OLR           W/m2               -6 to 6
# Index of wind anomaly 200hpa--------W200       std anomaly         -7.5 to 7.5
# Index of wind anomaly 850hpa-------W850w         anomaly         -7.5 to 7.5
# Index of wind anomaly 850hpa-------W850c         anomaly          -21 to 21
# Index of wind anomaly 850hpa-------W850e         anomaly        -15.1 to 15.1
# Sea surface temperature-------------SST           °C                -60 to 60
# Anomaly sea surface temperature----ASST12        anomaly          -10 to 10
# Anomaly sea surface temperature----ASST3         anomaly           -7 to 7
# Anomaly sea surface temperature----ASST4         anomaly           -3 to 3
# Anomaly sea surface temperature----ASST34        anomaly          -10 to 10
# % Amazon relative humidity----------ARH             %              -100 to 100
# quasibienal oscillation index-------QBO           m/s            -59.1 to 33.24
# North atlantic oscillation index----NAO         anomaly           -6.36 to 6.08
# Caribbean (CAR) Index------------CAR         °C               -1.3 to 1.3
# Monthly anomaly of the
# ocean surface area Ocean                    Area anomaly scaled
# region >28.5C--------------------AREA_WHWP     by 10e6 km^2         -13 to 14

INTERNAL_LIMITS = {
    'ONI1':      {'daily': None,
                   'monthly': [-5,5],
                   'bimonthly': [-5,5],
                   'trimonthly': [-5,5]},

    'ONI2':      {'daily': None,
                   'monthly': [-5,5],
                   'bimonthly': [-5,5],
                   'trimonthly': [-5,5]},

    'SOI':       {'daily': None,
                   'monthly': [-7,7],
                   'bimonthly': [-7,7],
                   'trimonthly': [-7,7]},

    'SOI_TROUP': {'daily': None,
                   'monthly': [-35,35],
                   'bimonthly': [-35,35],
                   'trimonthly': [-35,35]},

    'MEI':        {'daily': None,
                    'bimonthly': [-4,4]},

    'OLR':       {'daily': None,
                   'monthly': [-5.2,5.2],
                   'bimonthly': [-5.2,5.2],
                   'trimonthly': [-5.2,5.2]},

    'W200':      {'daily': None,
                   'monthly': [-7.5,7.5],
                   'bimonthly': [-7.5,7.5],
                   'trimonthly': [-7.5,7.5]},

    'W850w':     {'daily': None,
                   'monthly': [-7.5,7.5],
                   'bimonthly': [-7.5,7.5],
                   'trimonthly': [-7.5,7.5]},

    'W850c':     {'daily': None,
                   'monthly': [-21,21],
                   'bimonthly': [-21,21],
                   'trimonthly': [-21,21]},

    'W850e':     {'daily': None,
                   'monthly': [-15.1,15.1],
                   'bimonthly': [-15.1,15.1],
                   'trimonthly': [-15.1,15.1]},

    'SST12':     {'daily': None,
                   'monthly': [-60,60],
                   'bimonthly': [-60,60],
                   'trimonthly': [-60,60]},

    'SST3':      {'daily': None,
                   'monthly': [-60,60],
                   'bimonthly': [-60,60],
                   'trimonthly': [-60,60]},

    'SST4':      {'daily': None,
                   'monthly': [-60,60],
                   'bimonthly': [-60,60],
                   'trimonthly': [-60,60]},

    'SST34':     {'daily': None,
                   'monthly': [-60,60],
                   'bimonthly': [-60,60],
                   'trimonthly': [-60,60]},

    'ASST12':    {'daily': None,
                   'monthly': [-10,10],
                   'bimonthly': [-10,10],
                   'trimonthly': [-10,10]},

    'ASST3':     {'daily': None,
                   'monthly': [-7,7],
                   'bimonthly': [-7,7],
                   'trimonthly': [-7,7]},

    'ASST4':     {'daily': None,
                   'monthly': [-3,3],
                   'bimonthly': [-3,3],
                   'trimonthly': [-3,3]},

    'ASST34':    {'daily': None,
                   'monthly': [-5.6,5.6],
                   'bimonthly': [-5.6,5.6],
                   'trimonthly': [-5.6,5.6]},

    'ARH':       {'daily': None,
                   'monthly': [-100,100],
                   'bimonthly': [-100,100],
                   'trimonthly': [-100,100]},

    'QBO':       {'daily': None,
                   'monthly': [-40,40],
                   'bimonthly': [-40,40],
                   'trimonthly': [-40,40]},

    'NAO':       {'daily': None,
                   'monthly': [-11.9,11.9],
                   'bimonthly': [-11.9,11.9],
                   'trimonthly': [-11.9,11.9]},

    'CAR':       {'daily': None,
                   'monthly': [-1.3,1.3],
                   'bimonthly': [-1.3,1.3],
                   'trimonthly': [-1.3,1.3]},

    'AREA_WHWP': {'daily': None,
                   'monthly': [-13,14],
                   'bimonthly': [-13,14],
                   'trimonthly': [-13,14]},
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
    'default':   {'daily': ['p33','p66'],
                   'monthly': ['p33','p66'],
                   'bimonthly': ['p33','p66'],
                   'trimonthly': ['p33','p66'],
                   'normal_inclusive': True},

    ## thresholds by type of internal series  (if was not defined here, will use thresholds by default)
    'ONI1':      {'daily': [-0.5,0.5],
                   'monthly': [-0.5,0.5],
                   'bimonthly': [-0.5,0.5],
                   'trimonthly': [-0.5,0.5],
                   'normal_inclusive': False},

    'ONI2':      {'daily': [-0.5,0.5],
                   'monthly': [-0.5,0.5],
                   'bimonthly': [-0.5,0.5],
                   'trimonthly': [-0.5,0.5],
                   'normal_inclusive': False},

    'SOI':       {'daily': [-1,1],
                   'monthly': [-1,1],
                   'bimonthly': [-1,1],
                   'trimonthly': [-1,1],
                   'normal_inclusive': False},

    'SOI_TROUP': {'daily': [-8,8],
                   'monthly': [-8,8],
                   'bimonthly': [-8,8],
                   'trimonthly': [-8,8],
                   'normal_inclusive': False},

    'MEI':        {'daily': None,
                   'bimonthly': [-0.1,0.1],
                   'normal_inclusive': False},

    'OLR':       {'daily': [-0.1,0.2],
                   'monthly': [-0.1,0.2],
                   'bimonthly': [-0.1,0.2],
                   'trimonthly': [-0.1,0.2],
                   'normal_inclusive': True},

    'ASST12':    {'daily': ['sd-0.4','sd0.4'],
                   'monthly': ['sd-0.4','sd0.4'],
                   'bimonthly': ['sd-0.4','sd0.4'],
                   'trimonthly': ['sd-0.4','sd0.4'],
                   'normal_inclusive': True},

    'ASST3':     {'daily': ['sd-0.4','sd0.4'],
                   'monthly': ['sd-0.4','sd0.4'],
                   'bimonthly': ['sd-0.4','sd0.4'],
                   'trimonthly': ['sd-0.4','sd0.4'],
                   'normal_inclusive': True},

    'ASST4':     {'daily': ['sd-0.4','sd0.4'],
                   'monthly': ['sd-0.4','sd0.4'],
                   'bimonthly': ['sd-0.4','sd0.4'],
                   'trimonthly': ['sd-0.4','sd0.4'],
                   'normal_inclusive': True},

    'ASST34':    {'daily': ['sd-0.4','sd0.4'],
                   'monthly': ['sd-0.4','sd0.4'],
                   'bimonthly': ['sd-0.4','sd0.4'],
                   'trimonthly': ['sd-0.4','sd0.4'],
                   'normal_inclusive': True},

    'QBO':       {'daily': [-4,4],
                   'monthly': [-4,4],
                   'bimonthly': [-4,4],
                   'trimonthly': [-4,4],
                   'normal_inclusive': True},

    'NAO':       {'daily': [-1,1],
                   'monthly': [-1,1],
                   'bimonthly': [-1,1],
                   'trimonthly': [-1,1],
                   'normal_inclusive': True},
}

# thresholds when class_category_analysis is 7
THRESHOLDS_7_CATEGORIES = {
    ## thresholds by default
    'default':   {'daily': ['p11','p22','p33','p66','p77','p88'],
                   'monthly': ['p11','p22','p33','p66','p77','p88'],
                   'bimonthly': ['p11','p22','p33','p66','p77','p88'],
                   'trimonthly': ['p11','p22','p33','p66','p77','p88'],
                   'normal_inclusive': True},

    ## thresholds by type of internal series  (if was not defined here, will use thresholds by default)
    'ONI1':      {'daily': [-1.5,-1,-0.5,0.5,1,1.5],
                   'monthly': [-1.5,-1,-0.5,0.5,1,1.5],
                   'bimonthly': [-1.5,-1,-0.5,0.5,1,1.5],
                   'trimonthly': [-1.5,-1,-0.5,0.5,1,1.5],
                   'normal_inclusive':False},

    'ONI2':      {'daily': [-1.5,-1,-0.5,0.5,1,1.5],
                   'monthly': [-1.5,-1,-0.5,0.5,1,1.5],
                   'bimonthly': [-1.5,-1,-0.5,0.5,1,1.5],
                   'trimonthly': [-1.5,-1,-0.5,0.5,1,1.5],
                   'normal_inclusive': False},

    'SOI':       {'daily': [-2.86,-1.62,-1,1,1.62,2.86],
                   'monthly': [-2.86,-1.62,-1,1,1.62,2.86],
                   'bimonthly': [-2.86,-1.62,-1,1,1.62,2.86],
                   'trimonthly': [-2.86,-1.62,-1,1,1.62,2.86],
                   'normal_inclusive':False},

    'SOI_TROUP': {'daily': [-23,-13,-8,8,13,23],
                   'monthly': [-23,-13,-8,8,13,23],
                   'bimonthly': [-23,-13,-8,8,13,23],
                   'trimonthly': [-23,-13,-8,8,13,23],
                   'normal_inclusive':False},

    # 'MEI'  TODO: define the threshold for 7 cat, while by default

    'ASST12':    {'daily': ['sd-1','sd-0.6','sd-0.4','sd0.4','sd0.6','sd1'],
                   'monthly': ['sd-1','sd-0.6','sd-0.4','sd0.4','sd0.6','sd1'],
                   'bimonthly': ['sd-1','sd-0.6','sd-0.4','sd0.4','sd0.6','sd1'],
                   'trimonthly': ['sd-1','sd-0.6','sd-0.4','sd0.4','sd0.6','sd1'],
                   'normal_inclusive':True},

    'ASST3':     {'daily': ['sd-1','sd-0.6','sd-0.4','sd0.4','sd0.6','sd1'],
                   'monthly': ['sd-1','sd-0.6','sd-0.4','sd0.4','sd0.6','sd1'],
                   'bimonthly': ['sd-1','sd-0.6','sd-0.4','sd0.4','sd0.6','sd1'],
                   'trimonthly': ['sd-1','sd-0.6','sd-0.4','sd0.4','sd0.6','sd1'],
                   'normal_inclusive':True},

    'ASST4':     {'daily': ['sd-1','sd-0.6','sd-0.4','sd0.4','sd0.6','sd1'],
                   'monthly': ['sd-1','sd-0.6','sd-0.4','sd0.4','sd0.6','sd1'],
                   'bimonthly': ['sd-1','sd-0.6','sd-0.4','sd0.4','sd0.6','sd1'],
                   'trimonthly': ['sd-1','sd-0.6','sd-0.4','sd0.4','sd0.6','sd1'],
                   'normal_inclusive':True},

    'ASST34':    {'daily': ['sd-1','sd-0.6','sd-0.4','sd0.4','sd0.6','sd1'],
                   'monthly': ['sd-1','sd-0.6','sd-0.4','sd0.4','sd0.6','sd1'],
                   'bimonthly': ['sd-1','sd-0.6','sd-0.4','sd0.4','sd0.6','sd1'],
                   'trimonthly': ['sd-1','sd-0.6','sd-0.4','sd0.4','sd0.6','sd1'],
                   'normal_inclusive':True},
}

# namefiles of internal independent variables for each type
INTERNAL_FILES = {
    "ONI1":      "ONI1_1950_2012_CPC.txt",
    "ONI2":      "ONI2_1950_2013_CPC_corr2012.txt",
    "SOI":       "SOI_1951_2013_CPC_NOAA.txt",
    "SOI_TROUP": "SOI_TROUP_1876_2013_AustralinaBureau.txt",
    "MEI":       "MEI_1950_2013_ESRL_NOAA.txt",
    "OLR":       "OLR_1974_2013_CPC_NCEP_NOAA.txt",
    "W200":      "W200_1979_2013_CPC_NCEP_NOAA.txt",
    "W850w":     "W850w_1979_2013_CPC_NCEP_NOAA.txt",
    "W850c":     "W850c_1979_2013_CPC_NCEP_NOAA.txt",
    "W850e":     "W850e_1979_2013_CPC_NCEP_NOAA.txt",
    "SST12":     "SST12_1982_2013_CPC_NCEP_NOAA.txt",
    "SST3":      "SST3_1982_2013_CPC_NCEP_NOAA.txt",
    "SST4":      "SST4_1982_2013_CPC_NCEP_NOAA.txt",
    "SST34":     "SST34_1982_2013_CPC_NCEP_NOAA.txt",
    "ASST12":    "ASST12_1982_2013_CPC_NCEP_NOAA.txt",
    "ASST3":     "ASST3_1982_2013_CPC_NCEP_NOAA.txt",
    "ASST4":     "ASST4_1982_2013_CPC_NCEP_NOAA.txt",
    "ASST34":    "ASST34_1982_2013_CPC_NCEP_NOAA.txt",
    "ARH":       "ARH_DIPOLE_1979_2009_NCEPNCAR_REAL.txt", #TODO: update series
    "NAO":       "NAO_1865_2013_Hurrel1995.txt",
    "QBO":       "QBO_1979_2013_CPC_NOAA.txt",
    "CAR":       "SSTA_CAR_1951_2010_ESRL_NOAA.txt",
    "AREA_WHWP": "AREA_WHWP_1948_2013_ESRL_NOAA.txt"
}

# urls where get the internal files for independent variables for each type
INTERNAL_URLS = {
    "ONI1":      "http://goo.gl/6tXjh", # http://www.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ensoyears_1971-2000_climo.shtml
    "ONI2":      "http://goo.gl/e7unc", # http://www.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ensoyears.shtml
    "SOI":       "http://goo.gl/scbO7", # http://www.cpc.ncep.noaa.gov/data/indices/soi
    "SOI_TROUP": "http://goo.gl/2hDk8", # http://www.bom.gov.au/climate/current/soihtm1.shtml
    "MEI":       "http://goo.gl/0IAItw", # http://www.esrl.noaa.gov/psd/enso/mei/table.html
    "OLR":       "http://goo.gl/goMpA", # http://www.cpc.ncep.noaa.gov/data/indices/olr
    "W200":      "http://goo.gl/aliLh", # http://www.cpc.ncep.noaa.gov/data/indices/zwnd200
    "W850w":     "http://goo.gl/w4yiO", # http://www.cpc.ncep.noaa.gov/data/indices/wpac850
    "W850c":     "http://goo.gl/gks7x", # http://www.cpc.ncep.noaa.gov/data/indices/cpac850
    "W850e":     "http://goo.gl/N7cQ5", # http://www.cpc.ncep.noaa.gov/data/indices/epac850
    "SST12":     "http://goo.gl/6vzgrB", # http://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices
    "SST3":      "http://goo.gl/6vzgrB", # http://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices
    "SST4":      "http://goo.gl/6vzgrB", # http://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices
    "SST34":     "http://goo.gl/6vzgrB", # http://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices
    "ASST12":    "http://goo.gl/6vzgrB", # http://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices
    "ASST3":     "http://goo.gl/6vzgrB", # http://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices
    "ASST4":     "http://goo.gl/6vzgrB", # http://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices
    "ASST34":    "http://goo.gl/6vzgrB", # http://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices
    "ARH":       "http://goo.gl/5oiZJ", # http://nomad1.ncep.noaa.gov/ncep_data/index.html
    "NAO":       "http://goo.gl/ArdVn", # http://climatedataguide.ucar.edu/sites/default/files/cas_data_files/asphilli/nao_station_monthly_2.txt
    "QBO":       "http://goo.gl/erjsJ and http://goo.gl/qKTrT", # http://www.cpc.ncep.noaa.gov/data/indices/qbo.u50.index and http://www.cpc.ncep.noaa.gov/data/indices/qbo.u30.index
    "CAR":       "http://goo.gl/zeY7eP", # http://www.esrl.noaa.gov/psd/data/correlation/CAR.data
    "AREA_WHWP": "http://goo.gl/mV4QI"  # http://www.esrl.noaa.gov/psd/data/correlation/whwp.data
}


#==============================================================================
# functions

def get_internal_limits():
    global FREQUENCY_DATA
    global TYPE_SERIES

    if TYPE_SERIES in INTERNAL_LIMITS:
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
    if config_run.settings['thresholds_var_I'] == 'default':
        return get_default_thresholds()
    else:
        return config_run.settings['thresholds_var_I']

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

    if new_freq_data not in ['daily','monthly','bimonthly','trimonthly']:
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
