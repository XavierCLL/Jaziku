.. _installation:

============
Installation
============

``Jaziku`` is written entirely in Python but use some libraries and programs 
for make calculations, graphics, maps and other. You need install all requires
for run Jaziku.


Libraries requires
------------------

Is recommended install this libraries from repositories of you Linux 
distribution.

- python (version 2.6 or 2.7)
- python-setuptools (or python-distribute)
- scipy (or python-scipy)
- argparse (or python-argparse)
- python-dateutil
- matplotlib (or python-matplotlib)
- numpy (or python-numpy)
- PIL (or python-image)
- python-dateutil
- `python-clint <http://pypi.python.org/pypi/clint>`_ [1]_
- `hpgl <http://hpgl.aoizora.org>`_
- `ncl <http://www.ncl.ucar.edu>`_

.. [1] you can install this using easy install:
       "easy_install clint"

Download Jaziku (egg version)
-----------------------------

- `jaziku 0.4.2 <https://dl.dropbox.com/u/3383807/jaziku-0.4.2-py2.7.egg>`_


Install Jaziku (egg version)
----------------------------

- Go into downloaded file an run this command to install
  (as root or use sudo):

    easy_install jaziku-0.4.2-py2.7.egg

- Test if jaziku has installed correctly running:

    jaziku -h

    check the version in the end of message.

- For update new version of jaziku (using egg)

    easy_install -U jaziku-x.x.egg

Windows and Mac
---------------

Jaziku only test work in Linux, but in theory also work in Mac and Windows.