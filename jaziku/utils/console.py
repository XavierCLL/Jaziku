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
import csv

import os
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

def msg_footer(text=False):

    footer = _(u"\nJaziku, version {0} - {1}.\nCopyright © 2011-2012 IDEAM - Colombia")\
              .format(globals_vars.VERSION, globals_vars.COMPILE_DATE)

    if text:
        return footer
    else:
        print footer

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
            "If this is an error of Jaziku, please report it with Jaziku developers.")
    msg_footer()
    sys.exit()


def msg_error_line_stations(station, text_error):
    """
    Print error generic function occurred in a line from stations file.
    """

    msg_error(_("Reading the stations from the runfile in line {0}:\n")
                .format(station.line_num) + ' > ' +
                ' '.join(station.line_station) + "\n\n" + str(text_error))


def msg_error_configuration(variable, text_error, show_settings=True):
    """
    Print error generic function occurred in configuration run.
    """
    if show_settings:
        from jaziku.utils import settings_run
        settings_run.show(stop_in=variable)

    runfile_open = open(globals_vars.runfile_path, 'rb')
    runfile = (x.replace('\0', '') for x in runfile_open)
    runfile = csv.reader(runfile, delimiter=';')

    for num_line, line_in_run_file in enumerate(runfile):
        if line_in_run_file[0] == variable:
            msg_error(_("The Configuration run from the runfile in line {0}:\n")
                      .format(num_line+1) + ' > ' +
                      ' '.join(line_in_run_file) + "\n\n" + str(text_error), False)

class redirectStdStreams(object):
    """
    Redirect standard out and error to devnull (nothing), with
     this the functions, libraries or applications not display on
     console any message (stdout, stderr or warnings).

    :Use:
        with console.redirectStdStreams():
            put_here_code
    """

    normal_stdout = None

    def __init__(self):
        devnull = open(os.devnull, 'w')
        self._stdout = devnull
        self._stderr = devnull

    def __enter__(self):
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
        self.old_stdout.flush(); self.old_stderr.flush()
        self.normal_stdout = os.dup(1)
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, 1)
        os.close(devnull)
        sys.stdout, sys.stderr = self._stdout, self._stderr

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout = os.fdopen(self.normal_stdout, 'w')
        os.dup2(self.normal_stdout, 1)
        self._stdout.flush(); self._stderr.flush()
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
