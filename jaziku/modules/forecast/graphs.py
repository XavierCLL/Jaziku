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
# Generate pies charts and mosaics for forecast
# http://matplotlib.sourceforge.net/api/pyplot_api.html

import os
from matplotlib import pyplot
from Image import open as img_open

from jaziku.env import globals_vars, config_run
from jaziku.utils import  watermarking, format_out


def forecast_graphs(station):
    """
    Generate pie charts and mosaics of probability for below, normal and
    above for independent variable for the composite analysis.
    """

    image_open_list = []

    for lag in config_run.settings['lags']:

        if globals_vars.STATE_OF_DATA in [1, 3]:
            title_date_graphic = _("trim {0} ({1})").format(config_run.settings['forecast_date']['month'],
                format_out.get_trimester_in_text(config_run.settings['forecast_date']['month'] - 1))
            filename_date_graphic = _("trim_{0}").format(config_run.settings['forecast_date']['month'])

        if globals_vars.STATE_OF_DATA in [2, 4]:
            title_date_graphic = "{0} {1}"\
                .format(format_out.get_month_in_text(config_run.settings['forecast_date']['month'] - 1),
                        config_run.settings['forecast_date']['day'])
            filename_date_graphic = "{0}_{1}"\
                .format(format_out.get_month_in_text(config_run.settings['forecast_date']['month'] - 1),
                        config_run.settings['forecast_date']['day'])

        ## Options for graphics pie
        # make a square figure and axes
        pyplot.figure(figsize=(5, 5))
        # colors for paint pie: below, normal , above
        colours = ['#DD4620', '#62AD29', '#6087F1']

        labels = (_('Decrease'), _('Normal'), _('Exceed'))
        values_pie = [station.prob_decrease_var_D[lag],
                      station.prob_normal_var_D[lag],
                      station.prob_exceed_var_D[lag]]

        explode = (0.03, 0.03, 0.03)

        # assign value for piece of pie
        def autopct_funt(pct):
            total = sum(values_pie)
            val = pct * total / 100.0
            return '{p:1.1f}%\n({v:1.2f})'.format(p=pct, v=val)

        pyplot.pie(values_pie, colors=colours, explode=explode, labels=labels,
            autopct='%1.1f%%', shadow=True)  # '%1.1f%%'

        pyplot.title(unicode(_('Probability forecasted of {0} - {1}\n{2} - lag {3} - {4} - ({5}-{6})')
            .format(station.var_D.type_series, station.name, station.var_I.type_series, lag, title_date_graphic,
                    station.process_period['start'], station.process_period['end']),
                    'utf-8'), fontsize=13)

        ## Save image
        # pyplot.subplot(111)
        image_dir_save \
            = os.path.join(station.forecast_dir, _('prob_of_{0}_lag_{1}_{2}_({3}-{4}).png')
                .format(station.var_D.type_series, lag, filename_date_graphic,
                        station.process_period['start'], station.process_period['end']))

        # save image
        pyplot.savefig(image_dir_save, dpi=75)

        pyplot.clf()

        # save dir image for mosaic
        image_open_list.append(image_dir_save)

    ## Create mosaic

    if len(config_run.settings['lags']) != 1:
        # definition height and width of individual image
        # image_height = 375
        image_width = 375
        mosaic_dir_save \
            = os.path.join(station.forecast_dir, _('mosaic_prob_of_{0}_{1}_({3}-{4}).png')
                .format(station.var_D.type_series, lag, filename_date_graphic,
                        station.process_period['start'], station.process_period['end']))
        # http://stackoverflow.com/questions/4567409/python-image-library-how-to-combine-4-images-into-a-2-x-2-grid
        # http://www.classical-webdesigns.co.uk/resources/pixelinchconvert.html
        pyplot.figure(figsize=(3.75 * len(config_run.settings['lags']), 3.75))
        pyplot.savefig(mosaic_dir_save, dpi=100)
        mosaic = img_open(mosaic_dir_save)
        for lag_iter in range(len(config_run.settings['lags'])):
            mosaic.paste(img_open(image_open_list[lag_iter]), (image_width * lag_iter, 0))
        # save
        mosaic.save(mosaic_dir_save)
        # stamp logo
        watermarking.logo(mosaic_dir_save)

        pyplot.clf()

        # clear and delete all instances of graphs created by pyplot
        pyplot.close('all')

    # apply stamp logo
    for image in image_open_list:
        watermarking.logo(image)