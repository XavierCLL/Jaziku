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

from datetime import date

from jaziku.env import globals_vars, config_run


#==============================================================================
# VALIDATION FOR DEPENDENT AND INDEPENDENT VARIABLE


#==============================================================================
# Validation var_D (dependent variable)
#
# If inputs are monthly:
#
#     Variable        Abbreviation   Units          Range of variation
#  Precipitation----------PPT         mm             0mm<=Ppt<=3500mm
#  Num. of days
#   with rain------------NDPPT        -     (0 or num of days valid for month/year)
#  Temp. min-------------TMIN        °C             -15°C<=Tmin<=50°C
#  Temp. max-------------TMAX        °C             -15°C<=Tmin<=50°C
#  Temp. medium----------TEMP        °C             -15°C<=Tmin<=50°C
#  Atmosfere pressure----PATM        mb              400mb<=P<=1100mb
#  % relative humidity----RH          -                0%<=RH<=100%
#  Runoff---------------RUNOFF      m^3/s                0 to 3300
#
# If inputs are daily:
#
#     Variable        Abbreviation   Units          Range of variation
#  Precipitation----------PPT         mm             0mm<=Ppt<=200mm
#  Num. of days
#   with rain------------NDPPT        #     (0 or num of days valid for month/year)
#  Temp. min-------------TMIN        °C             -15°C<=Tmin<=22°C
#  Temp. max-------------TMAX        °C             -15°C<=Tmin<=34°C
#  Temp. medium----------TEMP        °C             -15°C<=Tmin<=34°C
#  Atmosfere pressure----PATM        mb              400mb<=P<=1100mb
#  % relative humidity----RH          %                0%<=RH<=100%
#  Runoff---------------RUNOFF      m^3/s                0 to 3300


def validation_var_D(type_var_D, var_D, date_D, frequency_data_of_var_D):
    '''
    Function for validation (dependent variable) depending on the type of
    variable
    '''

    # define generic text for generate exception
    def returnError(e, limit_below, limit_above):
        # generation exception
        raise ValueError(_("exception validation in dependent variable:\n"
                           "The value {0} is out of range {1} to {2} for {3}.\n\n{4}")
                         .format(var_D, limit_below, limit_above, type_var_D, e))

    # first test if the value is a valid null
    if globals_vars.is_valid_null(var_D):
        return var_D

    # if both were defined as particular range
    if config_run.settings['limits_var_D']['below'] != "default" and config_run.settings['limits_var_D']['above'] != "default":
        if config_run.settings['limits_var_D']['below'] is not None and config_run.settings['limits_var_D']['above'] is not None:
            if (config_run.settings['limits_var_D']['below'] <= var_D <= config_run.settings['limits_var_D']['above']):
                return var_D
            else:
                returnError(_("{0} not valid in particular limits defined in runfile").format(type_var_D),
                    config_run.settings['limits_var_D']['below'], config_run.settings['limits_var_D']['above'])
        elif config_run.settings['limits_var_D']['below'] is None and config_run.settings['limits_var_D']['above'] is not None:
            if (var_D <= config_run.settings['limits_var_D']['above']):
                return var_D
            else:
                returnError(_("{0} not valid in particular limits defined in runfile").format(type_var_D),
                    'none', config_run.settings['limits_var_D']['above'])
        elif config_run.settings['limits_var_D']['above'] is None and config_run.settings['limits_var_D']['below'] is not None:
            if (config_run.settings['limits_var_D']['below'] <= var_D):
                return var_D
            else:
                returnError(_("{0} not valid in particular limits defined in runfile").format(type_var_D),
                    config_run.settings['limits_var_D']['below'], 'none')
        else:  # this is that both are equal to "none"
            return var_D

    # validation for precipitation
    def if_var_D_is_PPT():
        if frequency_data_of_var_D == "daily":
            # default values
            limit_below = 0
            limit_above = 200
            # if one of limits was defined as particular range
            if config_run.settings['limits_var_D']['below'] not in ["default", None]:
                limit_below = config_run.settings['limits_var_D']['below']
            if config_run.settings['limits_var_D']['above'] not in ["default", None]:
                limit_above = config_run.settings['limits_var_D']['above']

            if (limit_below <= var_D <= limit_above):
                return var_D
            else:
                returnError(_("precipitation not valid"), limit_below, limit_above)
        if frequency_data_of_var_D == "monthly":
            # default values
            limit_below = 0
            limit_above = 3500
            # if one of limits was defined as particular range
            if config_run.settings['limits_var_D']['below'] not in ["default", None]:
                limit_below = config_run.settings['limits_var_D']['below']
            if config_run.settings['limits_var_D']['above'] not in ["default", None]:
                limit_above = config_run.settings['limits_var_D']['above']

            if (limit_below <= var_D <= limit_above):
                return var_D
            else:
                returnError(_("precipitation not valid"), limit_below, limit_above)

    # validation for number of days with rain
    def if_var_D_is_NDPPT():
        if frequency_data_of_var_D == "daily":
            raise Exception(_("validation: (NDPPT) number of days with rain must have\n"
                              "data monthly"))
        if frequency_data_of_var_D == "monthly":
            # default values
            limit_below = 0
            limit_above = 31
            # if one of limits was defined as particular range
            if config_run.settings['limits_var_D']['below'] not in ["default", None]:
                limit_below = config_run.settings['limits_var_D']['below']
            if config_run.settings['limits_var_D']['above'] not in ["default", None]:
                limit_above = config_run.settings['limits_var_D']['above']
            try:
                if date_D is None:
                    if limit_below > int(var_D) > limit_above:
                        raise
                else:
                    date(date_D.year, date_D.month, int(var_D))
                return var_D
            except Exception, e:
                if globals_vars.is_valid_null(var_D) or int(var_D) == 0:
                    return var_D
                else:
                    returnError(e, limit_below, limit_above)

    # validation for minimum temperature
    def if_var_D_is_TMIN():
        if frequency_data_of_var_D == "daily":
            # default values
            limit_below = -15
            limit_above = 22
            # if one of limits was defined as particular range
            if config_run.settings['limits_var_D']['below'] not in ["default", None]:
                limit_below = config_run.settings['limits_var_D']['below']
            if config_run.settings['limits_var_D']['above'] not in ["default", None]:
                limit_above = config_run.settings['limits_var_D']['above']

            if (limit_below <= var_D <= limit_above):
                return var_D
            else:
                returnError(_("minimum temperature not valid"), limit_below, limit_above)
        if frequency_data_of_var_D == "monthly":
            # default values
            limit_below = -15
            limit_above = 50
            # if one of limits was defined as particular range
            if config_run.settings['limits_var_D']['below'] not in ["default", None]:
                limit_below = config_run.settings['limits_var_D']['below']
            if config_run.settings['limits_var_D']['above'] not in ["default", None]:
                limit_above = config_run.settings['limits_var_D']['above']

            if (limit_below <= var_D <= limit_above):
                return var_D
            else:
                returnError(_("minimum temperature not valid"), limit_below, limit_above)

    # validation for maximum temperature
    def if_var_D_is_TMAX():
        if frequency_data_of_var_D == "daily":
            # default values
            limit_below = -15
            limit_above = 34
            # if one of limits was defined as particular range
            if config_run.settings['limits_var_D']['below'] not in ["default", None]:
                limit_below = config_run.settings['limits_var_D']['below']
            if config_run.settings['limits_var_D']['above'] not in ["default", None]:
                limit_above = config_run.settings['limits_var_D']['above']

            if (limit_below <= var_D <= limit_above):
                return var_D
            else:
                returnError(_("maximum temperature not valid"), limit_below, limit_above)
        if frequency_data_of_var_D == "monthly":
            # default values
            limit_below = -15
            limit_above = 50
            # if one of limits was defined as particular range
            if config_run.settings['limits_var_D']['below'] not in ["default", None]:
                limit_below = config_run.settings['limits_var_D']['below']
            if config_run.settings['limits_var_D']['above'] not in ["default", None]:
                limit_above = config_run.settings['limits_var_D']['above']

            if (limit_below <= var_D <= limit_above):
                return var_D
            else:
                returnError(_("maximum temperature not valid"), limit_below, limit_above)

    # validation for medium temperature
    def if_var_D_is_TEMP():
        if frequency_data_of_var_D == "daily":
            # default values
            limit_below = -15
            limit_above = 34
            # if one of limits was defined as particular range
            if config_run.settings['limits_var_D']['below'] not in ["default", None]:
                limit_below = config_run.settings['limits_var_D']['below']
            if config_run.settings['limits_var_D']['above'] not in ["default", None]:
                limit_above = config_run.settings['limits_var_D']['above']

            if (limit_below <= var_D <= limit_above):
                return var_D
            else:
                returnError(_("medium temperature not valid"), limit_below, limit_above)
        if frequency_data_of_var_D == "monthly":
            # default values
            limit_below = -15
            limit_above = 50
            # if one of limits was defined as particular range
            if config_run.settings['limits_var_D']['below'] not in ["default", None]:
                limit_below = config_run.settings['limits_var_D']['below']
            if config_run.settings['limits_var_D']['above'] not in ["default", None]:
                limit_above = config_run.settings['limits_var_D']['above']
            if (limit_below <= var_D <= limit_above):
                return var_D
            else:
                returnError(_("medium temperature not valid"), limit_below, limit_above)

    # validation for atmosfere pressure
    def if_var_D_is_PATM():
        # default values
        limit_below = 400
        limit_above = 1100
        # if one of limits was defined as particular range
        if config_run.settings['limits_var_D']['below'] not in ["default", None]:
            limit_below = config_run.settings['limits_var_D']['below']
        if config_run.settings['limits_var_D']['above'] not in ["default", None]:
            limit_above = config_run.settings['limits_var_D']['above']

        if (limit_below <= var_D <= limit_above):
            return var_D
        else:
            returnError(_("atmosfere pressure not valid"), limit_below, limit_above)

    # validation for % of relative humidity
    def if_var_D_is_RH():
        # default values
        limit_below = 0
        limit_above = 100
        # if one of limits was defined as particular range
        if config_run.settings['limits_var_D']['below'] not in ["default", None]:
            limit_below = config_run.settings['limits_var_D']['below']
        if config_run.settings['limits_var_D']['above'] not in ["default", None]:
            limit_above = config_run.settings['limits_var_D']['above']

        if (limit_below <= var_D <= limit_above):
            return var_D
        else:
            returnError(_("% of relative humidity not valid"), limit_below, limit_above)

    # validation for Runoff
    def if_var_D_is_RUNOFF():
        # default values
        limit_below = 0
        limit_above = 3300
        # if one of limits was defined as particular range
        if config_run.settings['limits_var_D']['below'] not in ["default", None]:
            limit_below = config_run.settings['limits_var_D']['below']
        if config_run.settings['limits_var_D']['above'] not in ["default", None]:
            limit_above = config_run.settings['limits_var_D']['above']

        if (limit_below <= var_D <= limit_above):
            return var_D
        else:
            returnError(_("Runoff not valid"), limit_below, limit_above)

    # switch validation
    validation = {
      "PPT": if_var_D_is_PPT,
      "NDPPT": if_var_D_is_NDPPT,
      "TMIN": if_var_D_is_TMIN,
      "TMAX": if_var_D_is_TMAX,
      "TEMP": if_var_D_is_TEMP,
      "PATM": if_var_D_is_PATM,
      "RH": if_var_D_is_RH,
      "RUNOFF": if_var_D_is_RUNOFF
    }
    return validation[type_var_D]()


#==============================================================================
# Validation var_I (independent variable)
#
#     Variable                     Abbreviation     Units          Range of variation
# Oceanic Nino Index--------------ONI1 and ONI2    anomaly             -5 to 5
# Index of the Southern
# Oscillation NOAA--------------------SOI        std anomaly           -7 to 7
# Index of the Southern
# Oscillation (TROUP)--------------SOI_TROUP     std anomaly          -35 to 35
# Multivariate ENSO index------------ MEI            #             -4.552 to 6.078
# Radiation wavelength
# Long tropical---------------------- OLR           W/m2               -6 to 6
# Index of wind anomaly 200hpa--------W200       std anomaly         -7.5 to 7.5
# Index of wind anomaly 850hpa-------W850w         anomaly         -7.5 to 7.5
# Index of wind anomaly 850hpa-------W850c         anomaly          -21 to 21
# Index of wind anomaly 850hpa-------W850e         anomaly        -15.1 to 15.1
# Sea surface temperature-------------SST           °C                -60 to 60
# Anomaly sea surface temperature----ASST12        anomaly          -10 to 10
# Anomaly sea surface temperature----ASST3         anomaly           -7 to 7
# Anomaly sea surface temperature----ASST4         anomaly           -3 to 3
# Anomaly sea surface temperature----ASST34        anomaly          -10 to 10
# % Amazon relative humidity----------ARH             %              -100 to 100
# quasibienal oscillation index-------QBO           m/s            -59.1 to 33.24
# North atlantic oscillation index----NAO         anomaly           -6.36 to 6.08
# Caribbean (CAR) Index------------CAR         °C               -1.3 to 1.3
# Monthly anomaly of the
# ocean surface area Ocean                    Area anomaly scaled
# region >28.5C--------------------AREA_WHWP     by 10e6 km^2         -13 to 14


def validation_var_I(type_var_I, var_I):
    '''
    Function for validation (independent variable) depending on the type of
    variable
    '''

    # define generic text for generate exception
    def returnError(e, limit_below, limit_above):
        # generation exception
        raise ValueError(_("exception validation in independent variable:\n"
                           "The value {0} is out of range {1} to {2} for {3}.\n\n{4}")
        .format(var_I, limit_below, limit_above, type_var_I, e))

    # first test if the value is a valid null
    if globals_vars.is_valid_null(var_I):
        return var_I

    # if both were defined as particular range
    if config_run.settings['limits_var_I']['below'] != "default" and config_run.settings['limits_var_I']['above'] != "default":
        if config_run.settings['limits_var_I']['below'] is not None and config_run.settings['limits_var_I']['above'] is not None:
            if (config_run.settings['limits_var_I']['below'] <= var_I <= config_run.settings['limits_var_I']['above']):
                return var_I
            else:
                returnError(_("{0} not valid in particular limits defined in runfile").format(type_var_I),
                            config_run.settings['limits_var_I']['below'], config_run.settings['limits_var_I']['above'])
        elif config_run.settings['limits_var_I']['below'] is None and config_run.settings['limits_var_I']['above'] is not None:
            if (var_I <= config_run.settings['limits_var_I']['above']):
                return var_I
            else:
                returnError(_("{0} not valid in particular limits defined in runfile").format(type_var_I),
                            config_run.settings['limits_var_I']['below'], config_run.settings['limits_var_I']['above'])
        elif config_run.settings['limits_var_I']['above'] is None and config_run.settings['limits_var_I']['below'] is not None:
            if (config_run.settings['limits_var_I']['below'] <= var_I):
                return var_I
            else:
                returnError(_("{0} not valid in particular limits defined in runfile").format(type_var_I),
                            config_run.settings['limits_var_I']['below'], config_run.settings['limits_var_I']['above'])
        else:  # this is that both are equal to "none"
            return var_I

    # validation for Oceanic Nino Index
    def if_var_I_is_ONI1():
        # default values
        limit_below = -5
        limit_above = 5
        # if one of limits was defined as particular range
        if config_run.settings['limits_var_I']['below'] not in ["default", None]:
            limit_below = config_run.settings['limits_var_I']['below']
        if config_run.settings['limits_var_I']['above'] not in ["default", None]:
            limit_above = config_run.settings['limits_var_I']['above']

        if (limit_below <= var_I <= limit_above):
            return var_I
        else:
            returnError(_("Oceanic Nino Index not valid"), limit_below, limit_above)

    # validation for Oceanic Nino Index
    def if_var_I_is_ONI2():
        # default values
        limit_below = -5
        limit_above = 5
        # if one of limits was defined as particular range
        if config_run.settings['limits_var_I']['below'] not in ["default", None]:
            limit_below = config_run.settings['limits_var_I']['below']
        if config_run.settings['limits_var_I']['above'] not in ["default", None]:
            limit_above = config_run.settings['limits_var_I']['above']

        if (limit_below <= var_I <= limit_above):
            return var_I
        else:
            returnError(_("Oceanic Nino Index not valid"), limit_below, limit_above)

    # validation for Index of the Southern Oscillation NOAA
    def if_var_I_is_SOI():
        # default values
        limit_below = -7
        limit_above = 7
        # if one of limits was defined as particular range
        if config_run.settings['limits_var_I']['below'] not in ["default", None]:
            limit_below = config_run.settings['limits_var_I']['below']
        if config_run.settings['limits_var_I']['above'] not in ["default", None]:
            limit_above = config_run.settings['limits_var_I']['above']

        if (limit_below <= var_I <= limit_above):
            return var_I
        else:
            returnError(_("Index of the Southern Oscillation NOAA not valid"), limit_below, limit_above)

    # validation for Index of the Southern Oscillation calculated between Tahití and Darwin
    def if_var_I_is_SOI_TROUP():
        # default values
        limit_below = -35
        limit_above = 35
        # if one of limits was defined as particular range
        if config_run.settings['limits_var_I']['below'] not in ["default", None]:
            limit_below = config_run.settings['limits_var_I']['below']
        if config_run.settings['limits_var_I']['above'] not in ["default", None]:
            limit_above = config_run.settings['limits_var_I']['above']

        if (limit_below <= var_I <= limit_above):
            return var_I
        else:
            returnError(_("Index of the Southern Oscillation TROUP not valid"), limit_below, limit_above)

    # validation for Multivariate ENSO index
    def if_var_I_is_MEI():
        # default values
        limit_below = -4.552
        limit_above = 6.078
        # if one of limits was defined as particular range
        if config_run.settings['limits_var_I']['below'] not in ["default", None]:
            limit_below = config_run.settings['limits_var_I']['below']
        if config_run.settings['limits_var_I']['above'] not in ["default", None]:
            limit_above = config_run.settings['limits_var_I']['above']

        if (limit_below <= var_I <= limit_above):
            return var_I
        else:
            returnError(_("Multivariate ENSO index not valid"), limit_below, limit_above)

    # validation for Radiation wavelength Long tropical
    def if_var_I_is_OLR():
        # default values
        limit_below = -5.2
        limit_above = 5.2
        # if one of limits was defined as particular range
        if config_run.settings['limits_var_I']['below'] not in ["default", None]:
            limit_below = config_run.settings['limits_var_I']['below']
        if config_run.settings['limits_var_I']['above'] not in ["default", None]:
            limit_above = config_run.settings['limits_var_I']['above']

        if (limit_below <= var_I <= limit_above):
            return var_I
        else:
            returnError(_("Radiation wavelength Long tropical not valid"), limit_below, limit_above)

    # validation for Index of wind anomaly to 200 hpa
    def if_var_I_is_W200():
        # default values
        limit_below = -7.5
        limit_above = 7.5
        # if one of limits was defined as particular range
        if config_run.settings['limits_var_I']['below'] not in ["default", None]:
            limit_below = config_run.settings['limits_var_I']['below']
        if config_run.settings['limits_var_I']['above'] not in ["default", None]:
            limit_above = config_run.settings['limits_var_I']['above']

        if (limit_below <= var_I <= limit_above):
            return var_I
        else:
            returnError(_("Anomaly index of wind to 200 hpa not valid"), limit_below, limit_above)

    # validation for Index of wind anomaly to 850 hpa west
    def if_var_I_is_W850w():
        # default values
        limit_below = -7.5
        limit_above = 7.5
        # if one of limits was defined as particular range
        if config_run.settings['limits_var_I']['below'] not in ["default", None]:
            limit_below = config_run.settings['limits_var_I']['below']
        if config_run.settings['limits_var_I']['above'] not in ["default", None]:
            limit_above = config_run.settings['limits_var_I']['above']

        if (limit_below <= var_I <= limit_above):
            return var_I
        else:
            returnError(_("Anomaly index of wind to 850 hpa west not valid"), limit_below, limit_above)


    # validation for Index of wind anomaly to 850 hpa center
    def if_var_I_is_W850c():
        # default values
        limit_below = -21
        limit_above = 21
        # if one of limits was defined as particular range
        if config_run.settings['limits_var_I']['below'] not in ["default", None]:
            limit_below = config_run.settings['limits_var_I']['below']
        if config_run.settings['limits_var_I']['above'] not in ["default", None]:
            limit_above = config_run.settings['limits_var_I']['above']

        if (limit_below <= var_I <= limit_above):
            return var_I
        else:
            returnError(_("Anomaly index of wind to 850 hpa center not valid"), limit_below, limit_above)

    # validation for Index of wind anomaly to 850 hpa east
    def if_var_I_is_W850e():
        # default values
        limit_below = -15.1
        limit_above = 15.1
        # if one of limits was defined as particular range
        if config_run.settings['limits_var_I']['below'] not in ["default", None]:
            limit_below = config_run.settings['limits_var_I']['below']
        if config_run.settings['limits_var_I']['above'] not in ["default", None]:
            limit_above = config_run.settings['limits_var_I']['above']

        if (limit_below <= var_I <= limit_above):
            return var_I
        else:
            returnError(_("Anomaly index of wind to 850 hpa east not valid"), limit_below, limit_above)

    # validation for Sea surface temperature
    def if_var_I_is_SST():
        # default values
        limit_below = -60
        limit_above = 60
        # if one of limits was defined as particular range
        if config_run.settings['limits_var_I']['below'] not in ["default", None]:
            limit_below = config_run.settings['limits_var_I']['below']
        if config_run.settings['limits_var_I']['above'] not in ["default", None]:
            limit_above = config_run.settings['limits_var_I']['above']

        if (limit_below <= var_I <= limit_above):
            return var_I
        else:
            returnError(_("Sea surface temperature not valid"), limit_below, limit_above)

    # validation for anomaly sea surface temperature
    def if_var_I_is_ASST12():
        # default values
        limit_below = -10
        limit_above = 10
        # if one of limits was defined as particular range
        if config_run.settings['limits_var_I']['below'] not in ["default", None]:
            limit_below = config_run.settings['limits_var_I']['below']
        if config_run.settings['limits_var_I']['above'] not in ["default", None]:
            limit_above = config_run.settings['limits_var_I']['above']

        if (limit_below <= var_I <= limit_above):
            return var_I
        else:
            returnError(_("Anomaly sea surface temperature not valid"), limit_below, limit_above)

    # validation for anomaly sea surface temperature
    def if_var_I_is_ASST3():
        # default values
        limit_below = -7
        limit_above = 7
        # if one of limits was defined as particular range
        if config_run.settings['limits_var_I']['below'] not in ["default", None]:
            limit_below = config_run.settings['limits_var_I']['below']
        if config_run.settings['limits_var_I']['above'] not in ["default", None]:
            limit_above = config_run.settings['limits_var_I']['above']

        if (limit_below <= var_I <= limit_above):
            return var_I
        else:
            returnError(_("Anomaly sea surface temperature not valid"), limit_below, limit_above)

    # validation for anomaly sea surface temperature
    def if_var_I_is_ASST4():
        # default values
        limit_below = -3
        limit_above = 3
        # if one of limits was defined as particular range
        if config_run.settings['limits_var_I']['below'] not in ["default", None]:
            limit_below = config_run.settings['limits_var_I']['below']
        if config_run.settings['limits_var_I']['above'] not in ["default", None]:
            limit_above = config_run.settings['limits_var_I']['above']

        if (limit_below <= var_I <= limit_above):
            return var_I
        else:
            returnError(_("Anomaly sea surface temperature not valid"), limit_below, limit_above)

    # validation for anomaly sea surface temperature
    def if_var_I_is_ASST34():
        # default values
        limit_below = -5.6
        limit_above = 5.6
        # if one of limits was defined as particular range
        if config_run.settings['limits_var_I']['below'] not in ["default", None]:
            limit_below = config_run.settings['limits_var_I']['below']
        if config_run.settings['limits_var_I']['above'] not in ["default", None]:
            limit_above = config_run.settings['limits_var_I']['above']

        if (limit_below <= var_I <= limit_above):
            return var_I
        else:
            returnError(_("Anomaly sea surface temperature not valid"), limit_below, limit_above)

    # validation for % Amazon relative humidity
    def if_var_I_is_ARH():
        # default values
        limit_below = -100
        limit_above = 100
        # if one of limits was defined as particular range
        if config_run.settings['limits_var_I']['below'] not in ["default", None]:
            limit_below = config_run.settings['limits_var_I']['below']
        if config_run.settings['limits_var_I']['above'] not in ["default", None]:
            limit_above = config_run.settings['limits_var_I']['above']

        if (limit_below <= var_I <= limit_above):
            return var_I
        else:
            returnError(_("% Amazon relative humidity not valid"), limit_below, limit_above)

    # validation for North atlantic oscillation index
    def if_var_I_is_NAO():
        # default values
        limit_below = -11.9
        limit_above = 11.9
        # if one of limits was defined as particular range
        if config_run.settings['limits_var_I']['below'] not in ["default", None]:
            limit_below = config_run.settings['limits_var_I']['below']
        if config_run.settings['limits_var_I']['above'] not in ["default", None]:
            limit_above = config_run.settings['limits_var_I']['above']

        if (limit_below <= var_I <= limit_above):
            return var_I
        else:
            returnError(_("North Atlantic Oscillation index not valid"), limit_below, limit_above)

    # validation for quasibienal oscillation index
    def if_var_I_is_QBO():
        # default values
        limit_below = -40
        limit_above = 40
        # if one of limits was defined as particular range
        if config_run.settings['limits_var_I']['below'] not in ["default", None]:
            limit_below = config_run.settings['limits_var_I']['below']
        if config_run.settings['limits_var_I']['above'] not in ["default", None]:
            limit_above = config_run.settings['limits_var_I']['above']

        if (limit_below <= var_I <= limit_above):
            return var_I
        else:
            returnError(_("Quasibienal Oscillation Index not valid"), limit_below, limit_above)

    # validation for Caribbean (CAR) Index
    def if_var_I_is_CAR():
        # default values
        limit_below = -1.3
        limit_above = 1.3
        # if one of limits was defined as particular range
        if config_run.settings['limits_var_I']['below'] not in ["default", None]:
            limit_below = config_run.settings['limits_var_I']['below']
        if config_run.settings['limits_var_I']['above'] not in ["default", None]:
            limit_above = config_run.settings['limits_var_I']['above']

        if (limit_below <= var_I <= limit_above):
            return var_I
        else:
            returnError(_("Caribbean (CAR) Index not valid"), limit_below, limit_above)

    # validation for Monthly anomaly of the ocean surface area Ocean region
    def if_var_I_is_AREA_WHWP():
        # default values
        limit_below = -13
        limit_above = 14
        # if one of limits was defined as particular range
        if config_run.settings['limits_var_I']['below'] not in ["default", None]:
            limit_below = config_run.settings['limits_var_I']['below']
        if config_run.settings['limits_var_I']['above'] not in ["default", None]:
            limit_above = config_run.settings['limits_var_I']['above']

        if (limit_below <= var_I <= limit_above):
            return var_I
        else:
            returnError(_("Monthly anomaly of the ocean surface area ocean region not valid"), limit_below, limit_above)

    # switch validation
    validation = {
      "ONI1": if_var_I_is_ONI1,
      "ONI2": if_var_I_is_ONI2,
      "SOI": if_var_I_is_SOI,
      "SOI_TROUP": if_var_I_is_SOI_TROUP,
      #"MEI": if_var_I_is_MEI,
      "OLR": if_var_I_is_OLR,
      "W200": if_var_I_is_W200,
      "W850w": if_var_I_is_W850w,
      "W850c": if_var_I_is_W850c,
      "W850e": if_var_I_is_W850e,
      "SST12": if_var_I_is_SST,
      "SST3": if_var_I_is_SST,
      "SST4": if_var_I_is_SST,
      "SST34": if_var_I_is_SST,
      "ASST12": if_var_I_is_ASST12,
      "ASST3": if_var_I_is_ASST3,
      "ASST4": if_var_I_is_ASST4,
      "ASST34": if_var_I_is_ASST34,
      "ARH": if_var_I_is_ARH,
      "NAO": if_var_I_is_NAO,
      "QBO": if_var_I_is_QBO,
      "CAR": if_var_I_is_CAR,
      "AREA_WHWP": if_var_I_is_AREA_WHWP
    }
    return validation[type_var_I]()
