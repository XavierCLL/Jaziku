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
- python-pip
- scipy (or python-scipy)
- argparse (or python-argparse, or if used ubuntu this inside in python package)
- matplotlib (or python-matplotlib)
- numpy (or python-numpy)
- python-pillow (or python-imaging, python-image)
- python-dateutil
- imagemagick
- `python-clint <http://pypi.python.org/pypi/clint>`_ [1]_
- `hpgl <http://hpgl.aoizora.org>`_ [2]_
- `ncl <http://www.ncl.ucar.edu>`_ [3]_

.. [1] you can install this using easy install:
       "pip clint"
.. [2] this is need for interpolation for maps
.. [3] this is for make maps, ignore this and hpgl if you don't need maps

    Note: Sure that the version of these packages are for python version 2.6 or 2.7

Download Jaziku
---------------

- `jaziku 1.0.0 <https://docs.google.com/uc?id=0B2KQf7Dbx7DUWml4NXB6TGktYmc&export=download>`_


Install Jaziku (installation with PIP)
--------------------------------------

- Go into downloaded file an run this command to install/update
  (as root or use sudo):

    pip jaziku-1.0.0.tar.gz

- Test if jaziku has installed correctly running:

    jaziku -h

    check the version and compilation date in the end of message.


Windows and Mac
---------------

Jaziku only test work and very recommend run in Linux, but in theory also work in Mac and Windows.