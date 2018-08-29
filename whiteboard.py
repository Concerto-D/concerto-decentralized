#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. module:: whiteboard
   :synopsis: this file contains the WhiteBoard class.
"""

class WhiteBoard (object):
    """ This class is used to implement data dependencies of the Madeus model.
    Each connection between two components is associated to a white board
    able to contain one value of any type. The provider component will write
    data inside its transitions while the user components will read data.
    """

    def __init__(self):
        pass

    def write(self, data):
        self.data = data

    def read(self):
        return self.data