========================
Jaziku documentation!
========================

Developers
--------------

Ines Sánchez Rodriguez < incsanchezro (a) gmail.com >
Xavier Corredor Llano < xcorredorl (a) ideam.gov.co >

Description
--------------

Jaziku is a software for the implementation of composite analysis
metodology between the major indices of climate variability and major
meteorological variables in puntual scale.

According to IDEAM’s commitment to promote and guide scientiﬁc research
about weather forecasting and climate, "Jazikü" is a program designed to
evaluate teleconnections between meteorological variables with the main
indices of climate variability aﬀecting climate in Colombia.

Jaziku, follows the composite methodology analysis proposed by The
University Corporation for Atmospheric Research (UCAR)), National Oceanic
and Atmospheric Administration (NOAA) & U.S. Department of Commerce
(DOC)[1][1, 2][1, 2, 3][1, 2, 3] and can produce probability scenarios
under which it is expected precipitation or any other variable for speciﬁc
sites or areas interpolated to behave, as a function of the probability
values predicted for each climate variability and the history of
involvement in the quarterly average level. Such scenarios become a
powerful tool for decision making by the national meteorological services

[1] National Oceanic and Atmospheric Administration (NOAA) , University
Corporation for Atmospheric Research (UCAR)). Creating a Local Climate
Product Using Composite Analysis - Print Version of Webcast -(En Linea).
1997-2010:COMET Website at http://meted.ucar.edu/, 1997.
[2] A. Leetmaa Barnston, A. G. NCEP Forecasts of the El Niño of 1997 1998
and Its U.S. Impacts. Bull. Amer. Met. Soc, 80:1829 – 1852, 1999.
[3] M. B. Richman Montroy, D.L. Observed Nonlinearities of Monthly
Teleconnections between Tropical Paciﬁc Sea Surface Temperature Anomalies
and Central and Eastern North American Precipitation. Journal of Climate,
11:1812 – 1835, 1998.

Source code
--------------

http://hg.ideam.gov.co:8000/meteorologia/jaziku/summary
    
Download
--------------

stable prepared package (for build and eggs packages):
http://hg.ideam.gov.co:8000/meteorologia/jaziku/files/tip/src/dist

Install
--------------

please read (files) `install.txt <http://hg.ideam.gov.co:8000/meteorologia/jaziku/files/tip/src/install.txt>`_


Synopsis run
--------------

- jaziku [-h] -stations STATIONS [-p_below P_BELOW] [-p_normal P_NORMAL] [-p_above P_ABOVE] [-c] [-f] [-period PERIOD] [-ra] [-l LANG]

Example
--------------

- jaziku -stations station.csv -c -f

- jaziku -stations station.csv -p_below "Debajo" -p_normal "Normal" -p_above "Encima" -c -f -period 1980-2009 -ra -l es

Licence
--------------

GNU General Public License - GPLv3
Copyright © 2011-2012 IDEAM
Instituto de Hidrología, Meteorología y Estudios Ambientales
Carrera 10 No. 20-30
Bogotá, Colombia