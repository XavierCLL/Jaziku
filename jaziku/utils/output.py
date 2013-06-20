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

import os
import sys

from jaziku import env
from jaziku.utils import console


def make_dirs(_dir):
    if not os.path.isdir(_dir):
        try:
            os.makedirs(_dir)
        except Exception as error:
            console.msg_error(_("Problems creating the directory: {0}\n"
                                "\n{1}").format(_dir, error), False)


def prepare_dirs():
    from jaziku.utils import query
    # -------------------------------------------------------------------------
    # main output directory
    console.msg(_("\nDirectory where to save all results:"), newline=False)
    console.msg(env.globals_vars.OUTPUT_DIR, color='cyan')
    make_dirs(env.globals_vars.OUTPUT_DIR)

    # -------------------------------------------------------------------------
    # output directory by module activated

    dirs_existent = []

    # data analysis dir output result
    if env.config_run.settings['data_analysis']:
        env.globals_vars.DATA_ANALYSIS_DIR \
            = os.path.join(env.globals_vars.OUTPUT_DIR, _('Jaziku_Data_Analysis'))
        if os.path.isdir(env.globals_vars.DATA_ANALYSIS_DIR):
            dirs_existent.append(env.globals_vars.DATA_ANALYSIS_DIR)

    # climate dir output result
    if env.config_run.settings['climate_process']:
        env.globals_vars.CLIMATE_DIR \
            = os.path.join(env.globals_vars.OUTPUT_DIR, _('Jaziku_Climate'))
        if os.path.isdir(env.globals_vars.CLIMATE_DIR):
            dirs_existent.append(env.globals_vars.CLIMATE_DIR)

    # directory for the forecast results
    if env.config_run.settings['forecast_process']:
        env.globals_vars.FORECAST_DIR \
            = os.path.join(env.globals_vars.OUTPUT_DIR, _('Jaziku_Forecast'))
        if os.path.isdir(env.globals_vars.FORECAST_DIR):
            dirs_existent.append(env.globals_vars.FORECAST_DIR)

    if not len(dirs_existent) == 0:
        console.msg(_(" > WARNING: the following output directories already exist:"), color='yellow')
        for dir in dirs_existent:
            console.msg("   "+dir, color='cyan')

        query_output_directory \
            = query.directory(_("   What do you like to do? [r]eplace, [m]erge or [c]ancel"),
                              dirs_existent)

        if not query_output_directory:
            console.msg(_("\nexit"),color='red')
            console.msg_footer()
            sys.exit()