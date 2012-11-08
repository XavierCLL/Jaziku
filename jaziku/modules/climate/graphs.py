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

#===============================================================================
# GRAPHS
# Generate bar charts and mosaics for climate
# http://matplotlib.sourceforge.net/api/pyplot_api.html

import os
from numpy import array
from matplotlib import pyplot
from Image import open as img_open

from jaziku.utils import globals_vars
from contingency_table import get_contingency_table


def column(matrix, i):
    """Return column i from matrix"""

    return [row[i] for row in matrix]


def climate_graphs(station):
    """
    Generate bar charts and mosaics of probability for below, normal and
    above for independent variable for the composite analysis.
    """

    # main directory for save graphics
    graphics_dir = _('graphics')

    # directory for save composite analysis graphics
    graphics_dir_ca \
        = os.path.join(station.climate_dir, graphics_dir, _('composite_analysis'))

    # create dir
    if not os.path.isdir(graphics_dir_ca):
        os.makedirs(graphics_dir_ca)

    def create_chart():
        ## graphics options for plot:
        # the x locations for the groups
        ind = array([0, 0.8, 1.6])
        # the width of the bars
        width = 0.2

        pyplot.figure()

        # graphics title
        pyplot.title(unicode(_('Composite analysis - {0} ({1})\n{2} - {3} - '
                            'lag {6} - {7} - ({4}-{5})')
        .format(station.name, station.code, station.type_I,
            station.type_D, station.process_period['start'],
            station.process_period['end'], lag,
            title_period), 'utf-8'))

        # label for axis Y
        pyplot.ylabel(_('probability (%)'))
        #  adjust the max leaving min unchanged in Y
        pyplot.ylim(ymin=0, ymax=100)
        #  adjust the max leaving min unchanged in X
        pyplot.xlim(xmin= -0.1, xmax=2.3)
        # pyplot.xticks([0.3, 1.1, 1.9], ('var Ind Below', 'var Ind Normal', 'var Ind Above'),)
        pyplot.xticks([])
        # colors for paint bars and labels: below, normal , above
        colours = ['#DD4620', '#62AD29', '#6087F1']
        # assigning values for plot:
        var_D_below = pyplot.bar(ind, column(contingency_table_percent, 0),
            width, color=colours[0])
        var_D_normal = pyplot.bar(ind + width, column(contingency_table_percent, 1),
            width, color=colours[1])
        var_D_above = pyplot.bar(ind + 2 * width, column(contingency_table_percent, 2),
            width, color=colours[2])

        # assign value for each bar
        def auto_label(rects):
            # attach some text labels
            temp = []
            for rect in rects:
                temp.append(rect.get_height())
            temp.sort(reverse=True)
            max_height = temp[0]

            for rect in rects:
                height = rect.get_height()
                pyplot.text(rect.get_x() + rect.get_width() / 2.0, 0.015 * max_height +
                                                                height, round(height, 1), ha='center', va='bottom')

        auto_label(var_D_below)
        auto_label(var_D_normal)
        auto_label(var_D_above)

        pyplot.subplots_adjust(bottom=0.15, left=0.22, right=0.97)
        # pyplot.legend((var_D_below[0], var_D_normal[0], var_D_above[0]),
        #            ('var Dep Below', 'var Dep Normal', 'var Dep Above'),
        #             shadow = True, fancybox = True)

        # table in graphic
        colLabels = (globals_vars.phenomenon_below, globals_vars.phenomenon_normal,
                     globals_vars.phenomenon_above)

        rowLabels = [_('var D below'), _('var D normal'), _('var D above')]

        contingency_table_percent_graph = [column(contingency_table_percent_print, 0),
                                           column(contingency_table_percent_print, 1),
                                           column(contingency_table_percent_print, 2)]

        # Add a table at the bottom of the axes
        pyplot.table(cellText=contingency_table_percent_graph,
                     rowLabels=rowLabels, rowColours=colours,
                     colLabels=colLabels, loc='bottom')
        ## Save image
        pyplot.subplot(111)
        image_dir_save \
            = os.path.join(graphics_dir_ca, _('lag_{0}').format(lag),
                           _('ca_lag_{0}_{1}_{2}_{3}_{4}_{5}_({6}-{7}).png')
                          .format(lag, filename_period, station.code, station.name, station.type_D,
                                  station.type_I, station.process_period['start'], station.process_period['end']))

        pyplot.savefig(image_dir_save, dpi=75)
        pyplot.clf()

        # save dir image for mosaic
        image_open_list.append(img_open(image_dir_save))

    for lag in globals_vars.lags:

        # create dir for lag
        if not os.path.isdir(os.path.join(graphics_dir_ca, _('lag_{0}').format(lag))):
            os.makedirs(os.path.join(graphics_dir_ca, _('lag_{0}').format(lag)))

        image_open_list = list()

        # all months in year 1->12
        for month in range(1, 13):

            if station.state_of_data in [1, 3]:
                contingency_table,\
                contingency_table_percent,\
                contingency_table_percent_print,\
                thresholds_var_D_var_I = get_contingency_table(station, lag, month)

                title_period = _("trim {0} ({1})").format(month, globals_vars.get_trimester_in_text(month - 1))
                filename_period = _("trim_{0}").format(month)
                create_chart()

            if station.state_of_data in [2, 4]:

                for day in station.range_analysis_interval:

                    contingency_table,\
                    contingency_table_percent,\
                    contingency_table_percent_print,\
                    thresholds_var_D_var_I = get_contingency_table(station, lag, month, day)

                    title_period = globals_vars.get_month_in_text(month - 1) + " " + str(day)
                    filename_period = globals_vars.get_month_in_text(month - 1) + "_" + str(day)

                    create_chart()

        ## create mosaic
        # definition height and width of individual image
        image_height = 450
        image_width = 600
        mosaic_dir_save \
            = os.path.join(graphics_dir_ca, _('mosaic_lag_{0}_{1}_{2}_{3}_{4}_{5}_({6}-{7}).png')
                          .format(lag, globals_vars.translate_analysis_interval, station.code, station.name,
                                  station.type_D, station.type_I, station.process_period['start'],
                                  station.process_period['end']))

        if station.state_of_data in [1, 3]:
            # http://stackoverflow.com/questions/4567409/python-image-library-how-to-combine-4-images-into-a-2-x-2-grid
            mosaic_plots = pyplot.figure(figsize=((image_width * 3) / 100, (image_height * 4) / 100))
            mosaic_plots.savefig(mosaic_dir_save, dpi=100)
            mosaic = img_open(mosaic_dir_save)
            i = 0
            # add image in mosaic based on trimester, vertical(v) and horizontal(h)
            for v in range(4):
                for h in range(3):
                    mosaic.paste(image_open_list[i], (image_width * h, image_height * v))
                    i += 1

        if station.state_of_data in [2, 4]:
            # http://stackoverflow.com/questions/4567409/python-image-library-how-to-combine-4-images-into-a-2-x-2-grid
            mosaic_plots = pyplot.figure(figsize=((image_width * len(station.range_analysis_interval))
                                             / 100, (image_height * 12) / 100))
            mosaic_plots.savefig(mosaic_dir_save, dpi=100)
            mosaic = img_open(mosaic_dir_save)
            i = 0
            # add image in mosaic based on months(m) and days(d)
            for m in range(12):
                for d in range(len(station.range_analysis_interval)):
                    mosaic.paste(image_open_list[i], (image_width * d, image_height * m))
                    i += 1

        mosaic.save(mosaic_dir_save)
        del mosaic
        pyplot.clf()
        #del image_open_list

    # clear and delete all instances of graphs created by pyplot
    pyplot.close('all')