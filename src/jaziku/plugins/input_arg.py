#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2011 IDEAM
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
import argparse  #http://docs.python.org/py3k/library/argparse.html
import global_var

#=============================================================================== 
# Parser and check arguments

#Create parser arguments
arguments = argparse.ArgumentParser(
                                 prog = global_var.PROG_NAME,
                                 description = _("Jaziku is a software for the implementation of composite analysis\n"  
                                                 "metodology between the major indices of climate variability and\n" 
                                                 "major meteorological variables in puntual scale.\n"),
                                 epilog = "Jaziku, version {0} - {1}\n" \
                                          "Copyright © 2011 IDEAM - Colombia"
                                          .format(global_var.VERSION, global_var.COMPILE_DATE),
                                          formatter_class = argparse.RawTextHelpFormatter)
        
### Input arguments for dependent variable
#Set path to file of stations list
arguments.add_argument('-stations', type = argparse.FileType('r'), required = True,
                    default = sys.stdin, help = _('Path absolute or relative to file stations list'))

### climate and forecasting set
#enable/disable climate process
arguments.add_argument('-c', '--climate', action = 'store_true', default = False,
                    help = _('Enable climate process'), required = False)
#enable/disable forescasting process
arguments.add_argument('-f', '--forecasting', action = 'store_true', default = False,
                    help = _('Enable forecasting process'), required = False)

#Valid input types for dependent variable
types_var_D = ['PPT', 'NDPPT', 'TMIN', 'TMAX', 'TEMP', 'PATM', 'HR']
##Input type for dependent variable from argument -type_D
#arguments.add_argument('-type_D', choices = types_var_D, type = str,
#                    help = 'Type to depent variable', required = False)
##Set path to file of dependent variable from argument -file_D
#arguments.add_argument('-file_D', type = argparse.FileType('r'), required = False,
#                    default = sys.stdin, help = 'Path to file depent variable')

### Input arguments for independent variable
#Valid input types for independent variable
types_var_I = ['ONI', 'SOI', 'MEI', 'OLR', 'W200', 'SST', 'ARH', 'QBO', 'NAO']
##Input type for independent variable from argument -type_I
#arguments.add_argument('-type_I', choices = types_var_I, type = str,
#                    help = 'Type to depent variable', required = False)
##Set path to file of independent variable from argument -file_I
#arguments.add_argument('-file_I', type = argparse.FileType('r'), required = False,
#                    default = sys.stdin, help = 'Path to file indepent variable')
#Set phenomenon below (optional)
arguments.add_argument('-p_below', type = str,
                    help = _('Set phenomenon below label'))
#Set phenomenon normal (optional)
arguments.add_argument('-p_normal', type = str,
                    help = _('Set phenomenon normal label'))
#Set phenomenon above (optional)
arguments.add_argument('-p_above', type = str,
                    help = _('Set phenomenon above label'))
#
##Forecasting probability below
#arguments.add_argument('-f_var_I_B', type = float,
#                    help = 'Forecasting probability below', required = False)
##Forecasting probability normal
#arguments.add_argument('-f_var_I_N', type = float,
#                    help = 'Forecasting probability normal', required = False)
##Forecasting probability above
#arguments.add_argument('-f_var_I_A', type = float,
#                    help = 'Forecasting probability above', required = False)

##Trimester
#arguments.add_argument('-trim', type = int, choices = range(1, 13),
#                    help = 'Set trimester for calculate forecasting', required = False)

#set period process
arguments.add_argument('-period', type = str,
                    help = _('Set specific period for process, e.g. 1980-2010'), required = False)

#enable/disable forescasting process
arguments.add_argument('-ra', '--risk-analysis', action = 'store_true', default = False,
                    help = _('Enable risk analysis for forecasting process'), required = False)

