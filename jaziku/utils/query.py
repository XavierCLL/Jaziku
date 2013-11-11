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

import shutil
from clint.textui import colored

from jaziku import env
from jaziku.utils import console
from jaziku.utils.output import make_dirs

def true(): return True
def false(): return False

def base_query(question, prompt, options, default, wrong_ans):

    if not default in options:
        raise ValueError("invalid default answer: {0}".format(default))

    while True:
        console.msg(colored.yellow(question) + colored.yellow(prompt), newline=False)

        if env.globals_vars.ARGS.force:
            print default
            return options[default]()
        else:
            choice = raw_input().lower()
            if choice in options:
                return options[choice]()
            else:
                console.msg(wrong_ans)


def yes_no(question, default="y"):

    options = {"yes":true, "y":true, "YES":true, "Y":true,
               "no":false, "n":false, "NO":false, "N":false}

    prompt = " [y/n]"

    wrong_ans = _("Please respond with 'y' or 'n'")

    return base_query(question, prompt, options, default, wrong_ans)


def directory(question, dirs, default="m"):

    def replace():
        for _dir in dirs:
            # delete
            shutil.rmtree(_dir, ignore_errors=True)
            # create
            make_dirs(_dir)
        return True

    options = {"r":replace, "R":replace, "m":true, "M":true, "c":false, "C":false}

    prompt = " [r/m/c]"

    wrong_ans = _("   Please respond with 'r', 'm' or 'c'")

    return base_query(question, prompt, options, default, wrong_ans)
