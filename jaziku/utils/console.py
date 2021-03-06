#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2011-2017 Xavier Corredor Ll. - IDEAM
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

import csv
import os
import sys
from clint.textui import colored

from jaziku.env import globals_vars


# ==============================================================================
# PRINT FUNCTIONS
# color text console  #http://pypi.python.org/pypi/clint/

def msg(text, color=False, newline=True, indentation=0):
    """
    Print standard console message, this can print text in color
    and with the "newline" can print text without newline in end of stream.
    """

    if not color:
        if not newline:
            print((text), end=' ')
            sys.stdout.flush()
        else:
            print (text)

    if color == "yellow":
        if not newline:
            print(colored.yellow(text), end=' ')
            sys.stdout.flush()
        else:
            print(colored.yellow(text))
    if color == "cyan":
        if not newline:
            print(colored.cyan(text), end=' ')
            sys.stdout.flush()
        else:
            print(colored.cyan(text))

    if color == "green":
        if not newline:
            print(colored.green(text), end=' ')
            sys.stdout.flush()
        else:
            print(colored.green(text))

    if color == "red":
        if not newline:
            print(colored.red(text), end=' ')
            sys.stdout.flush()
        else:
            print(colored.red(text))


def msg_footer(text=False):
    footer = _("\nJaziku, version {0} - {1}.\nCopyright (C) 2011-2018 Xavier Corredor & Ines Sanchez\nIDEAM - Colombia") \
        .format(globals_vars.VERSION, globals_vars.VERSION_DATE)

    if text:
        return footer
    else:
        print(footer)


def msg_error(text_error, wait_value=True):
    """
    Print error generic function, this is called on any error occurred in
    Jaziku
    """

    if wait_value:
        print(colored.red(_('fail\n\nERROR:\n{0}\n\n').format(text_error)))
    else:
        print(colored.red(_('\nERROR:\n{0}\n').format(text_error)))
    print(_("Please check the error and read the manual if is necessary.\n"
            "If this is an error of Jaziku, please report it with Jaziku developers."))
    msg_footer()
    sys.exit()


def msg_error_line_stations(station, text_error):
    """
    Print error generic function occurred in a line from stations file.
    """

    msg_error(_("Reading the station from the runfile in line {0}:\n")
              .format(station.line_num) + ' > ' +
              ' '.join(station.line_station) + "\n\n" + str(text_error))


def msg_error_configuration(variable, text_error, show_settings=True, stop_in_grid=None):
    """Print error generic function occurred in configuration run.
    """
    if show_settings:
        from jaziku.core import settings
        settings.show.configuration_run(stop_in=variable, stop_in_grid=stop_in_grid)

    runfile_open = open(globals_vars.ARGS.runfile, 'r')
    runfile = csv.reader(runfile_open, delimiter=globals_vars.INPUT_CSV_DELIMITER)

    stop_in_grid_counter = 0

    for num_line, line_in_run_file in enumerate(runfile):
        # if line is null o empty, e.g. empty but with tabs or spaces
        if not line_in_run_file or not line_in_run_file[0].strip() or line_in_run_file == []:
            continue

        if line_in_run_file[0] == variable:
            # if the error is in any variable in grid, continue until find the correct grid
            if stop_in_grid != stop_in_grid_counter:
                stop_in_grid_counter += 1
                continue
            msg_error(_("The Configuration run from the runfile in line {0}:\n")
                      .format(num_line + 1) + ' > ' + line_in_run_file[0] + ' = ' +
                      ' '.join(line_in_run_file[1::]) + "\n\n" + str(text_error), False)

    # else
    msg_error(_("Error in configuration run from the runfile:\n")
              + "\n" + str(text_error), False)

    runfile_open.close()
    del runfile


# ==============================================================================
# OTHERS

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
        self.old_stdout.flush()
        self.old_stderr.flush()
        self.normal_stdout = os.dup(1)
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, 1)
        os.close(devnull)
        sys.stdout, sys.stderr = self._stdout, self._stderr

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout = os.fdopen(self.normal_stdout, 'w')
        os.dup2(self.normal_stdout, 1)
        self._stdout.flush()
        self._stderr.flush()
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr


def which(program):
    """
    Test if external program exists and return path
    """
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None
