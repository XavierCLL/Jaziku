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

import os
from subprocess import call

from jaziku.env import globals_vars
from jaziku.utils import console


def logo(image, gravity='southeast', dissolve=100):
    """
    stamp logo of Jaziku
    """

    if not console.which('composite'):
        return 1

    watermarking_logo = os.path.abspath(os.path.join(globals_vars.JAZIKU_DIR, 'data', 'watermarking', 'logo.png'))

    image_dir = os.path.abspath(image)

    call("composite -gravity {0} -dissolve {1} '{2}' '{3}' '{3}'".format(gravity, dissolve, watermarking_logo,
                                                                         image_dir), shell=True)
