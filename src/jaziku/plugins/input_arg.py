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

import sys
import argparse  # http://docs.python.org/py3k/library/argparse.html
import globals

#==============================================================================
# PARSER AND CHECK ARGUMENTS

# Create parser arguments
arguments = argparse.ArgumentParser(
                 prog=globals.PROG_NAME,
                 description=_("Jaziku is a software for the implementation "
                                 "of composite analysis\n metodology between "
                                 "the major indices of climate variability "
                                 "and\n major meteorological variables in "
                                 "puntual scale.\n"),
                 epilog="Jaziku, version {0} - {1}\n" \
                          "Copyright © 2011-2012 IDEAM - Colombia"
                          .format(globals.VERSION, globals.COMPILE_DATE),
                          formatter_class=argparse.RawTextHelpFormatter)

### Input arguments for dependent variable
# Set path to file of stations list
arguments.add_argument('-stations', type=argparse.FileType('r'),
                       required=True, default=sys.stdin,
                       help=_('Path absolute or relative to file stations list'))
### climate and forecasting set
# enable/disable climate process
arguments.add_argument('-c', '--climate', action='store_true', default=False,
                       help=_('Enable climate process'), required=False)
# enable/disable forescasting process
arguments.add_argument('-f', '--forecasting', action='store_true', default=False,
                       help=_('Enable forecasting process'), required=False)
# Valid input types for dependent variable
types_var_D = ['PPT', 'NDPPT', 'TMIN', 'TMAX', 'TEMP', 'PATM', 'HR', 'RUNOFF']
### Input arguments for independent variable
# Valid input types for independent variable
types_var_I = ['ONI', 'SOI', 'MEI', 'OLR', 'W200', 'SST', 'ARH', 'QBO', 'NAO', 'SSTA_CAR', 'AREA_WHWP']

# Set phenomenon below (optional)
arguments.add_argument('-p_below', type=str,
                       help=_('Set phenomenon (var I) below label (e.g. \'-p_below "el niño"\')'))
# Set phenomenon normal (optional)
arguments.add_argument('-p_normal', type=str,
                       help=_('Set phenomenon (var I) normal label (e.g. \'-p_normal "normal"\')'))
# Set phenomenon above (optional)
arguments.add_argument('-p_above', type=str,
                       help=_('Set phenomenon (var I) above label (e.g. \'-p_above "la niña"\')'))
# set period process
arguments.add_argument('-period', type=str, required=False,
                       help=_('Set specific period for process (e.g. 1980-2010)'))
# enable/disable forescasting process
arguments.add_argument('-ra', '--risk-analysis', action='store_true',
                       default=False, required=False,
                       help=_('Enable risk analysis for forecasting process'))
# Set language (optional), if not set get language from system
arguments.add_argument('-l', type=str, help=_('Set language (e.g. \'-l en\' for english, \'-l es\' spanish,...)'))
