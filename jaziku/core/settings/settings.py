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

import sys

from jaziku.env import globals_vars
from jaziku.utils import  console
from jaziku.utils.query import yes_no
from jaziku.core import settings


def main(stations_list):
    """
    Get, set and check settings to run
    """

    # -------------------------------------------------------------------------
    # GET/SET SETTINGS

    settings.get()

    # -------------------------------------------------------------------------
    # PRINT AND CHECK SETTINGS

    settings.check.configuration_run()

    settings.show()

    settings.check.stations_list(stations_list)

    # -------------------------------------------------------------------------
    # CONTINUE TO RUN

    if not globals_vars.ARGS.force:

        query = yes_no(_("\nPlease check the configuration to run, continue?"))

        if not query:
            console.msg(_("\nexit"),color='red')
            console.msg_footer()
            sys.exit()





