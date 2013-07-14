.. _installation:

============
Installation
============

``Jaziku`` is written entirely in Python but use some libraries and programs 
for make calculations, graphics, maps and other. You need install all requires
for run Jaziku.


Libraries requires
------------------

Is recommended install these libraries from repositories of your Linux
distribution.

- python (version 2.6 or 2.7)
- python-setuptools (or python-distribute)
- scipy (or python-scipy)
- argparse (or python-argparse, or if used ubuntu this inside in python package)
- matplotlib (or python-matplotlib)
- numpy (or python-numpy)
- PIL (or python-image or python-imaging)
- python-dateutil
- imagemagick
- `python-clint <http://pypi.python.org/pypi/clint>`_ [1]_
- `hpgl <http://hpgl.aoizora.org>`_ [2]_
- `ncl <http://www.ncl.ucar.edu>`_ [3]_

.. [1] you can install this using easy install:
       "easy_install clint"
.. [2] this is need for interpolation for maps
.. [3] this is for make maps, ignore this and hpgl if you don't need maps

    Note: Sure that the version of these packages are for python version 2.6 or 2.7

Download Jaziku (egg version)
-----------------------------

- `jaziku 0.6.1 <https://docs.google.com/uc?id=0B2KQf7Dbx7DUcnJ1RnNlVG0td3c&export=download>`_


Install Jaziku (egg version)
----------------------------

- Go into downloaded file an run this command to install
  (as root or use sudo):

    easy_install jaziku-0.6.1-py2.7.egg

- Test if jaziku has installed correctly running:

    jaziku -h

    check the version in the end of message.

- If you have installed old version, for update to new version use (using egg):

    easy_install -U jaziku-0.6.1-py2.7.egg

Windows and Mac
---------------

Jaziku only test work and very recommend run in Linux, but in theory also work in Mac and Windows.