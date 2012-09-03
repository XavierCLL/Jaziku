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

from ...utils import globals_vars

#==============================================================================
# PARSER AND CHECK ARGUMENTS

# Create parser arguments
arguments = argparse.ArgumentParser(
                 prog=globals_vars.PROG_NAME,
                 description=_("Jaziku is a software for the implementation "
                                 "of composite analysis\n metodology between "
                                 "the major indices of climate variability "
                                 "and\n major meteorological variables in "
                                 "puntual scale.\n"),
                 epilog="Jaziku, version {0} - {1}\n" \
                          "Copyright © 2011-2012 IDEAM - Colombia"
                          .format(globals_vars.VERSION, globals_vars.COMPILE_DATE),
                          formatter_class=argparse.RawTextHelpFormatter)

### Input arguments for dependent variable
# Set path toxx configuration run file
arguments.add_argument('-runfile', type=argparse.FileType('r'),
                       required=True, default=sys.stdin,
                       help=_('Path absolute or relative to configuration run file'))

