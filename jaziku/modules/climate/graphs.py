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

#===============================================================================
# GRAPHS
# Generate bar charts and mosaics for climate
# http://matplotlib.sourceforge.net/api/pyplot_api.html

import os
import copy
from numpy import array
from matplotlib import pyplot
from Image import open as img_open

from jaziku import env
from jaziku.core.analysis_interval import get_range_analysis_interval
from jaziku.utils import  watermarking, format_out, output
from jaziku.utils.matrix import transpose

image_height = None
image_width = None


def climate_graphs(station):
    """Generate bar charts and mosaics of probability for labels in 3 or 7 categories
    for independent variable for the composite analysis.
    """

    # main directory for save graphics
    graphics_dir = _('graphics')

    # directory for save composite analysis graphics
    graphics_dir_ca \
        = os.path.join(station.climate_dir, graphics_dir, _('composite_analysis'))

    # create dir
    output.make_dirs(graphics_dir_ca)

    def create_chart():
        global image_height
        global image_width

        # function that assign value for each bar
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

        # defined some variables that depended of 'class_category_analysis' and 'relevant_climate_categories_var_I'
        if env.config_run.settings['class_category_analysis'] == 3:

            ## graphics options for plot:
            # the width of the bars
            width = 0.18
            all_groups_distance = [0, width*3.5, width*7]

            all_categories = env.globals_vars.categories(translated=False, as_list=True)

            if env.config_run.settings['relevant_climate_categories_var_I'] == 'all':
                relevant_climate_categories_var_I = all_categories
            else:
                relevant_climate_categories_var_I = env.config_run.settings['relevant_climate_categories_var_I']

            enable_categories = [False] * env.config_run.settings['class_category_analysis']
            for idx, category in enumerate(relevant_climate_categories_var_I):
                enable_categories[all_categories.index(category)] = True

            # number of categories activated
            num_categ = len(env.config_run.settings['relevant_climate_categories_var_I'])

            _CT = copy.deepcopy(specific_contingency_table['in_percentage'])
            _CT_p = copy.deepcopy(specific_contingency_table['in_percentage_formatted'])
            _CL_I = copy.deepcopy(env.config_run.get_categories_labels_var_I_list())

            # delete columns (var I) deactivated, in reversed order is needed
            # because if any element is delete in the first columns, the side of
            # matrix is reduced and the index change for a column to right side
            for idx, enable in reversed(list(enumerate(enable_categories))):
                if not enable:
                    del _CT[idx]
                    del _CT_p[idx]
                    del _CL_I[idx]

            _var_D_values = transpose(_CT)
            _colLabels = (_CL_I)
            _table_values = transpose(_CT_p)

            image_width_by_categ = {1:375, 2:375, 3:450}

            # the x locations for the groups
            var_I_bars_groups_distance =  array(all_groups_distance[0:num_categ])

            dpi = 75.0
            image_height = 375
            image_width = image_width_by_categ[num_categ]
            fig = pyplot.figure(figsize=((image_width) / dpi, (image_height) / dpi))
            #fig = pyplot.figure()

            ax = fig.add_subplot(111)

            # graphics title
            fig.suptitle(unicode(_('Composite analysis - {0} ({1})\n{2} - {3} - lag {6} - {7} - ({4}-{5})').
                format(station.name, station.code, station.var_I.type_series,
                    station.var_D.type_series, station.process_period['start'],
                    station.process_period['end'], lag, title_period), 'utf-8'), fontsize=14)

            # label for axis Y
            ax.set_ylabel(_('probability (%)'))
            #  adjust the max leaving min unchanged in Y
            ax.set_ylim(ymin=0, ymax=100)
            #  adjust the max leaving min unchanged in X
            ax.set_xlim(xmin= -(width/4), xmax=width*(num_categ*3+(num_categ-1)*0.5+0.25))
            # pyplot.xticks([0.3, 1.1, 1.9], ('var Ind Below', 'var Ind Normal', 'var Ind Above'),)
            ax.set_xticks([])
            #ax.set_yticks(range(0,101,10))
            # colors for paint bars and labels: below, normal , above
            colours = ['#DD4620', '#62AD29', '#6087F1']
            # assigning values for plot:

            var_D_below = pyplot.bar(var_I_bars_groups_distance, _var_D_values[0],
                width, color=colours[0])
            var_D_normal = pyplot.bar(var_I_bars_groups_distance + width, _var_D_values[1],
                width, color=colours[1])
            var_D_above = pyplot.bar(var_I_bars_groups_distance + 2 * width, _var_D_values[2],
                width, color=colours[2])

            auto_label(var_D_below)
            auto_label(var_D_normal)
            auto_label(var_D_above)

            rowLabels = [_('var D below'), _('var D normal'), _('var D above')]

            # Add a table at the bottom of the axes
            table = ax.table(
                cellText=_table_values,
                rowLabels=rowLabels,
                rowColours=colours,
                colLabels=_colLabels,
                loc='bottom', cellLoc='center')

            # set some properties to the table
            table_props = table.properties()
            table_cells = table_props['child_artists']
            for cell in table_cells:
                cell.set_fontsize(12)
                cell.set_height(0.06)

            ## Save image
            image_dir_save \
                = os.path.join(graphics_dir_ca, _('lag_{0}').format(lag),
                               _('ca_lag_{0}_{1}_{2}_{3}_{4}_{5}_({6}-{7}).png')
                              .format(lag, filename_period, station.code, station.name, station.var_D.type_series,
                                      station.var_I.type_series, station.process_period['start'], station.process_period['end']))

            ax.grid(True, color='gray')
            fig.tight_layout()

            left_by_categ = {1:0.345, 2:0.28, 3:0.23}
            right_by_categ = {1:0.655, 2:0.87, 3:0.98}
            #pyplot.subplots_adjust(bottom=0.25, left=0.22, right=0.97)
            pyplot.subplots_adjust(bottom=0.18, top=0.85, left=left_by_categ[num_categ], right=right_by_categ[num_categ])

        # save image
        pyplot.savefig(image_dir_save, dpi=dpi)
        pyplot.clf()
        pyplot.close('all')
        # save dir image for mosaic
        image_open_list.append(image_dir_save)

    for lag in env.config_run.settings['lags']:

        # create dir for lag
        output.make_dirs(os.path.join(graphics_dir_ca, _('lag_{0}').format(lag)))

        image_open_list = list()

        # all months in year 1->12
        for month in range(1, 13):

            if env.globals_vars.STATE_OF_DATA in [1, 3]:

                specific_contingency_table = station.contingency_tables[lag][month-1]

                title_period = _("trim {0} ({1})").format(month, format_out.trimester_in_initials(month-1))
                filename_period = _("trim_{0}").format(month)
                create_chart()

            if env.globals_vars.STATE_OF_DATA in [2, 4]:

                for idx_day, day in enumerate(get_range_analysis_interval()):

                    specific_contingency_table = station.contingency_tables[lag][month-1][idx_day]

                    title_period = format_out.month_in_initials(month-1) + " " + str(day)
                    filename_period = format_out.month_in_initials(month-1) + "_" + str(day)

                    create_chart()

        ## create mosaic
        # definition height and width of individual image

        mosaic_dir_save \
            = os.path.join(graphics_dir_ca, _('mosaic_lag_{0}_{1}_{2}_{3}_{4}_{5}_({6}-{7}).png')
                          .format(lag, env.globals_vars.analysis_interval_i18n, station.code, station.name,
                                  station.var_D.type_series, station.var_I.type_series, station.process_period['start'],
                                  station.process_period['end']))

        if env.globals_vars.STATE_OF_DATA in [1, 3]:
            # http://stackoverflow.com/questions/4567409/python-image-library-how-to-combine-4-images-into-a-2-x-2-grid
            dpi = 100.0
            mosaic_plots = pyplot.figure(figsize=((image_width * 3) / dpi, (image_height * 4) / dpi))
            mosaic_plots.savefig(mosaic_dir_save, dpi=dpi)
            mosaic = img_open(mosaic_dir_save)
            i = 0
            # add image in mosaic based on trimester, vertical(v) and horizontal(h)
            for v in range(4):
                for h in range(3):
                    mosaic.paste(img_open(image_open_list[i]), (image_width * h, image_height * v))
                    i += 1

        if env.globals_vars.STATE_OF_DATA in [2, 4]:
            # http://stackoverflow.com/questions/4567409/python-image-library-how-to-combine-4-images-into-a-2-x-2-grid
            dpi = 100.0
            mosaic_plots = pyplot.figure(figsize=((image_width * len(get_range_analysis_interval())) / dpi,
                                                  (image_height * 12) / dpi))
            mosaic_plots.savefig(mosaic_dir_save, dpi=dpi)
            mosaic = img_open(mosaic_dir_save)
            i = 0
            # add image in mosaic based on months(m) and days(d)
            for m in range(12):
                for d in range(len(get_range_analysis_interval())):
                    mosaic.paste(img_open(image_open_list[i]), (image_width * d, image_height * m))
                    i += 1

        mosaic.save(mosaic_dir_save)

        # stamp logo
        watermarking.logo(mosaic_dir_save)

        # apply stamp logo for all image in this lag
        for image in image_open_list:
            watermarking.logo(image)

        del mosaic
        #del image_open_list
        pyplot.clf()
        pyplot.close('all')

    # clear and delete all instances of graphs created by pyplot
    pyplot.close('all')