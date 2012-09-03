#from __future__ import absolute_import

import sys
import platform

from jaziku import main
#from jaziku.utils import globals_vars
#from jaziku.i18n import i18n

#VERSION = (1, 4, 0, 'b')


#__version__ = ('.'.join((str(each) for each in VERSION[:3])) +
#               '.'.join(VERSION[3:]))

__platform__ = platform.system()
__license__ = 'GPLv3'
__py_version__ = sys.version_info
__author__ = 'Xavier Corredor & Ines Sanchez'
__url__ = ''

PLATFORM_WIN = ('Windows')
PLATFORM_OTHERS = ('Linux', 'Darwin', 'FreeBSD', 'OpenBSD', 'SunOS')

is_windows = __platform__ in PLATFORM_WIN
is_unix = not is_windows