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

import os
import locale
import gettext
from clint.textui import colored

# Change this variable to your app name!
#  The translation files will be under
#  @LOCALE_DIR@/@LANGUAGE@/LC_MESSAGES/@APP_NAME@.mo

APP_NAME = 'jaziku'

LOCALE_DIR = os.path.dirname(os.path.realpath(__file__))

# Now we need to choose the language. We will provide a list, and gettext
# will use the first translation available in the list

languages = [name for name in os.listdir(LOCALE_DIR) if os.path.isdir(os.path.join(LOCALE_DIR, name))]

#DEFAULT_LANGUAGES = ['en']

# Concat all languages (env + default locale),
#  and here we have the languages and location of the translations
#languages += DEFAULT_LANGUAGES

# Lets tell those details to gettext
#  (nothing to change here for you)

#gettext.install (True,localedir=None, unicode=1)

#gettext.find(APP_NAME, LOCALE_DIR)

#gettext.textdomain(APP_NAME)

#gettext.bind_textdomain_codeset(APP_NAME, "UTF-8")

#language = gettext.translation(APP_NAME, LOCALE_DIR, languages = languages, fallback = True)


# init languages

locale_language = locale.getdefaultlocale()[0][0:2]
try:
    lang = gettext.translation(APP_NAME, LOCALE_DIR,
        languages=[locale_language],
        codeset="utf-8")
    os.environ["LANG"] = locale_language
    lang.install()
except:
    lang = gettext.NullTranslations()
    os.environ["LANG"] = "en"
    lang.install()



# -------------------------------------------------------------------------
# Setting language

def set_language(language):
    """
    Set language on fly, language variable is a string of two character,
    i.e "es", and this language should exits in i18n directory, else
    return to english as default language.
    """
    #_ = language.ugettext

    from jaziku.utils import console

    if language and language != "autodetect":
        if language == "en" or language == "EN" or language == "En":
            settings_language = colored.green(language)
            lang = gettext.NullTranslations()
        else:
            try:
                lang = gettext.translation(APP_NAME, LOCALE_DIR,
                    languages=[language],
                    codeset="utf-8")
            except:
                console.msg_error(_("'{0}' language not available.").format(language), False)
    
        if 'lang' in locals():
            os.environ["LANG"] = language
            lang.install()
            settings_language = colored.green(language)
    else:
        # Setting language based on locale language system,
        # when not defined language in arguments
        try:
            locale_language = locale.getdefaultlocale()[0][0:2]
            settings_language = colored.green(locale_language) + _(" (system language)")
            try:
                if locale_language != "en":
                    lang = gettext.translation(APP_NAME, LOCALE_DIR,
                        languages=[locale_language],
                        codeset="utf-8")
                    os.environ["LANG"] = locale_language
                    lang.install()
            except:
                settings_language = colored.green("en") + _(" (language \'{0}\' has not was translated yet)").format(locale_language)
                lang = gettext.NullTranslations()
                os.environ["LANG"] = "en"
                lang.install()
        except:
            settings_language = colored.green("en") + _(" (other languages were not detected)")
            lang = gettext.NullTranslations()
            os.environ["LANG"] = "en"
            lang.install()

    return settings_language

