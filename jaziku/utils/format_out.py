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

import globals_vars

def number(num, accuracy=False):
    """
    Return the number after formatted according to accuracy (default or particular)
    and fix decimal character.
    """
    if accuracy:
        return str(round(float(num), accuracy)).replace('.', ',')
    else:
        return str(round(float(num), globals_vars.ACCURACY)).replace('.', ',')