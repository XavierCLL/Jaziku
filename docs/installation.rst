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
- zlib or zlib1g-dev
- imagemagick
- `python-clint <http://pypi.python.org/pypi/clint>`_ [1]_
- `hpgl <http://hpgl.mit-ufa.com>`_ `hpgl download list <http://sourceforge.net/projects/hpgl/files/>`_ [2]_
- `ncl <http://www.ncl.ucar.edu>`_ [3]_

.. [1] you can install this using easy install:
       "pip2 install clint"
.. [2] this is need for maps interpolation
.. [3] this is for make maps, ignore this and hpgl if you don't need maps

    Note: Sure that the version of these packages are for python version 2.6 or 2.7

Download Jaziku
---------------

- `jaziku v1.0.0 <https://docs.google.com/uc?id=0B2KQf7Dbx7DUakRMcEM3WUstMFE&export=download>`_


Install Jaziku (installation with PIP)
--------------------------------------

- Go into downloaded file an run this command to install/update
  (as root or use sudo):

    pip2 install jaziku-1.0.0.tar.gz

- Test if jaziku has installed correctly running:

    jaziku -h

    check the version and compilation date in the end of message.


Windows and Mac
---------------

Jaziku only test work and very recommend run in Linux, but in theory also work in Mac and Windows.