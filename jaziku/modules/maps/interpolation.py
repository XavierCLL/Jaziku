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
import geo_bsd as hpgl
from geo_bsd.routines import *

from jaziku import env
from jaziku.utils import  console


def ordinary_kriging(base_grid, inc_file):

    # redirect output (HPGL stdout)
    with console.redirectStdStreams():
        size = (base_grid.lat_size, base_grid.lon_size, 1)  # (alto, ancho, paso)
        grid = SugarboxGrid(base_grid.lat_size, base_grid.lon_size, 1)
        data = load_cont_property(os.path.abspath(inc_file.encode('utf-8')), env.globals_vars.VALID_NULL[1], size)

        semivariogram = CovarianceModel(type=base_grid.num_semivariogram_type,
                                     ranges=(base_grid.radiuses[0] / 2,
                                             base_grid.radiuses[1] / 2, 1), sill=1)

        ik_result = hpgl.ordinary_kriging(data,
                                          grid,
                                          radiuses=(base_grid.radiuses[0],
                                                    base_grid.radiuses[1], 1),
                                          max_neighbours=base_grid.max_neighbours,
                                          cov_model=semivariogram)


        #from matplotlib import *
        #from pylab import *
        #import pylab

        #write_property(ik_result, os.path.abspath(inc_out), "OK_RESULT", globals_vars.VALID_NULL[1])

        #figure()
        #pylab.imshow(ik_result[0][:, :, 0])
        #pylab.savefig(os.path.abspath(inc_file) + "_plot.png")
        #clf()

        #figure()
        #pylab.imshow(data[0][:, :, 0])
        #pylab.savefig(os.path.abspath(inc_file) + "_origin.png")
        #clf()

    return ik_result[0][:, :, 0]

