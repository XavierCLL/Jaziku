.. _incoming_plans:

=====================
Incoming Plans / TODO
=====================

0.8 (**2013-xx-xx**)
--------------------
:Exploratory data analysis consolidation:
- **Correlation:** Autocorrelogram, Cross Correlogram (Var INDP), cross-correlation matrix between all series
- **Outliers:** Diagram 4-band dispersion, series plot with standard fixed threshold vs time
- **Missing values for each variable and Test bias:** List of missing values, time series vs time ( with shade
 for missing values),% pie chart for more missing value repeated, the year with the highest number with missing
 values, filling series with mean and median (entire series), frequency histogram pre and post after fill each series
- Standardized variables graphic option (Dependent variable transformation to the same format of Independent Variable)

0.9 (**2013-xx-xx**)
--------------------
:Homogeneity analysis:
- Stability in mean (Tes-t)
- Stability in median (Test MWW)
- Randomness (Test Runs)
- Changing trend (Fisher test)
- Mass curve for (Q, HR, PPT)
- Migrate/make manual, documentation and main page of Jaziku to sphinx using reStructuredTex http://sphinx-doc.org/

0.10 (**2013-XX-XX**)
--------------------
- Inclusion of spectral analysis

0.11 (**2013-XX-XX**)
--------------------
- Inclusion of wavelete analysis

===============================
TO RE-CHECK AND RE-VERIFICATION
===============================

from v0.6
---------
- difference of deterministic and probabilistic maps

from v0.7
---------
- outliers with monthly and bimonthly as analysis interval and as type of data
- monthly and bimonthly time series with lags 1 and 2
- contingency table for monthly and bimonthly
- monthly and bimonthly with analog year
- bimonthly and trimonthly climatology

===========
Others TODO
===========

To be included
--------------
- use the global_common_process for maps (climate, correlation, forecast)
  and put the global_common_process in subtitles inside maps
- adjust the PPT var for accumulate the data daily by default
- to able to change the labels for var D
- include the shapes maps for protected regions of Colombia
- save log
- Colombia with San Andres and Providencia
- print console through classes
- merge points when the values of two points were merged
- accept combine thresholds
- auto-validations (skills)
- metadata inside time series files
- more interpolations
- parallelize several part of code with MPI (PyMPI) or multi-thread,
  for example: best period to process, interpolations, maps.
- ability to change units for dependent and independent variables
- settings class

To be analyzed
--------------
- partial run, if a station has an error continue with other station, alert in final message
- Add altitude parameter for stations and print in results (maps files)
- NCL scripts port to pyngl
- Tool for the creation of a typical meteorological year:
    Skeiker, K., & Ghani, B. A. (2008). Advanced software tool for the creation of a typical meteorological year.
    Energy Conversion and Management, 49(10), 2581–2587. Retrieved from http://www.sciencedirect.com/science/article/pii/S0196890408002045

Arts and promotions
-------------------
- logo (DONE)
- webpage
- ISBN
- mail jaziku@ideam.gov.co
- usability poll