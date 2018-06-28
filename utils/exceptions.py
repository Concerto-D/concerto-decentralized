#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class NetError(Exception):
        """Base class for exceptions in this module."""
        def __init__(self, message):
            self.message = message

class NetConditionError(NetError):
        """Condition exception class"""

class NetCallbackError(NetError):
        """Callback exception class"""

