
raw = """####################;CONFIGURATION RUN
## MODULES
data_analysis
climate_process
forecast_process

## GENERAL OPTIONS
analysis_interval
class_category_analysis
process_period
analog_year
lags
language

## CHECK OPTIONS
consistent_data
risk_analysis

## OUTPUT OPTIONS
graphics
categories_labels_var_I
relevant_climate_categories_var_I

## VAR D OPTIONS
type_var_D
mode_calculation_series_D
limits_var_D
thresholds_var_D

## VAR I OPTIONS
type_var_I
mode_calculation_series_I
path_to_file_var_I
limits_var_I
thresholds_var_I

## FORECAST OPTIONS
forecast_date
# (3 categories);;;- below -;- normal -;- above -
# (7 categories);- strong below -;- moderate below -;- weak below -;- normal -;- weak above -;- moderate above -;- strong above -
forecast_var_I_lag_0
forecast_var_I_lag_1
forecast_var_I_lag_2

####################;MAPS

## MAPS OPTIONS
maps
overlapping
marks_stations
shape_boundary

## GRID DEFINITION
grid
shape_path
latitude
longitude
grid_resolution
semivariogram_type
radiuses
max_neighbours

####################;STATIONS LIST

## CODE STATION;## NAME STATION;## LAT;## LON;## ALT;## PATH TO FILE VAR D
"""