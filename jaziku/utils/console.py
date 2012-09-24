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


#==============================================================================
# PRINT FUNCTIONS
# color text console  #http://pypi.python.org/pypi/clint/

import sys
from clint.textui import colored

import globals_vars

def msg(text, color=False, newline=True, indentation=0):
    """
    Print standard console message, this can print text in color
    and with the "newline" can print text without newline in end of stream.
    """

    if not color:
        if not newline:
            print (text),
            sys.stdout.flush()
        else:
            print (text)

    if color == "yellow":
        if not newline:
            print colored.yellow(text),
            sys.stdout.flush()
        else:
            print colored.yellow(text)
    if color == "cyan":
        if not newline:
            print colored.cyan(text),
            sys.stdout.flush()
        else:
            print colored.cyan(text)

    if color == "green":
        if not newline:
            print colored.green(text),
            sys.stdout.flush()
        else:
            print colored.green(text)

    if color == "red":
        if not newline:
            print colored.red(text),
            sys.stdout.flush()
        else:
            print colored.red(text)

def msg_error(text_error, wait_value=True):
    """
    Print error generic function, this is called on any error occurred in
    Jaziku
    """

    if wait_value:
        print colored.red(_('fail\n\nERROR:\n{0}\n\n').format(text_error))
    else:
        print colored.red(_('\nERROR:\n{0}\n').format(text_error))
    print _("Please check the error and read the manual if is necessary.\n"
            "If this is an error of Jaziku, please report it with Jaziku developers.\n\n"
            "Jaziku, version {0} - {1}.\n"
            "Copyright © 2011-2012 IDEAM - Colombia")\
    .format(globals_vars.VERSION, globals_vars.COMPILE_DATE)
    sys.exit()


def msg_error_line_stations(station, text_error):
    """
    Print error generic function occurred in a line from stations file.
    """

    msg_error(_("Reading stations from file \"{0}\" in line {1}:\n")
                .format(globals_vars.args.runfile.name, station.line_num) +
                ';'.join(station.line_station) + "\n\n" + str(text_error))


