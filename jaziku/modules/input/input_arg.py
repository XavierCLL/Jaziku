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


import argparse  # http://docs.python.org/py3k/library/argparse.html

from jaziku.utils import globals_vars, console

#==============================================================================
# PARSER AND CHECK ARGUMENTS

# Create parser arguments
arguments = argparse.ArgumentParser(
                 prog=globals_vars.PROG_NAME,
                 description=_("Jaziku is statistical inference software for the\nteleconnections analysis"),
                 epilog=console.msg_footer(text=True),
                 formatter_class=argparse.RawTextHelpFormatter)

# Runfile argument
arguments.add_argument('runfile', type=str,
                       help=_('path absolute or relative to configuration run file'))

# enable/disable force all ask to default answer for continue
arguments.add_argument('-f','--force', action='store_true', default=False,
    help=_('force all ask to default answer for continue'), required=False)