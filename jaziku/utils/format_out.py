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

from jaziku.env import globals_vars

def number(num, accuracy=False):
    """
    Return the number after formatted according to accuracy (default or particular)
    and fix decimal character.
    """
    if accuracy:
        return str(round(float(num), accuracy)).replace('.', ',')
    else:
        return str(round(float(num), globals_vars.ACCURACY)).replace('.', ',')

def trimester_in_initials(trimester):
    """
    Return the three first letters of three months of trimester
    """
    _trim_text = {-2: _('NDJ'), -1: _('DJF'), 0: _('JFM'), 1: _('FMA'), 2: _('MAM'),
                 3: _('AMJ'), 4: _('MJJ'), 5: _('JJA'), 6: _('JAS'), 7: _('ASO'),
                 8: _('SON'), 9: _('OND'), 10: _('NDJ'), 11: _('DJF')}
    return _trim_text[trimester]


def month_in_initials(month):
    """
    Return the initials of month (first three letters)
    """
    _month_text = {-2: _('Nov'), -1: _('Dec'), 0: _('Jan'), 1: _('Feb'), 2: _('Mar'),
                  3: _('Apr'), 4: _('May'), 5: _('Jun'), 6: _('Jul'), 7: _('Aug'),
                  8: _('Sep'), 9: _('Oct'), 10: _('Nov'), 11: _('Dec')}
    return _month_text[month]


