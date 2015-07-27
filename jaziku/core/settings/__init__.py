#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2011-2014 IDEAM
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

from jaziku.core.settings import get, check_and_set, show


def main(stations_list):
    """
    Get, set and check settings to run
    """

    import sys

    from jaziku.utils import console, query

    # -------------------------------------------------------------------------
    # GET/SET SETTINGS

    get.configuration_run()

    # -------------------------------------------------------------------------
    # PRINT AND CHECK SETTINGS

    check_and_set.configuration_run()

    check_and_set.grids_list()

    show.configuration_run()

    check_and_set.stations_list(stations_list)

    # -------------------------------------------------------------------------
    # CONTINUE TO RUN

    query_check_continue = query.yes_no(_("\nPlease check the configuration to run, continue?"))

    if not query_check_continue:
        console.msg(_("\nexit"), color='red')
        console.msg_footer()
        sys.exit()
