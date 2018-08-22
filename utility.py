#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. module:: utility
   :synopsis: this file contains utility classes.
"""

class Messages():
    """
    This class is not instanciated. It is used for valid, warning, and fail
    color-printed messages.
    """
    @staticmethod
    def ok():
        return '\033[1;30;42m'

    @staticmethod
    def warning():
        return '\033[1;30;43m'

    @staticmethod
    def fail():
        return '\033[1;30;41m'

    @staticmethod
    def endc():
        return '\033[0m'


# global list of colors used for printing colors of components
COLORS = ['\33[34m', #blue
          '\33[35m', # magenta
          '\33[36m', # cyan
          '\33[31m', # red
          '\33[32m', # green
          '\33[33m', # yellow
         ]