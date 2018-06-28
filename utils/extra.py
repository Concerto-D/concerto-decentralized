# -*- coding: utf-8 -*-

import os, sys
import logging
from subprocess import run
from collections import namedtuple
from utils.constants import (ENOS_DIR, OPENSTACK_DIR)
from utils.errors import (MadFailedHostsError, MadUnreachableHostsError,
                          MadProviderMissingConfigurationKeys,
                          MadFilePathError)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def listify(obj):
    """ Returns a list from `obj`. """
    return obj if isinstance(obj, list) or obj is None else [obj]

def printerr(str):
    """
    Print to stderr (unbuferred) instead of stdout (buffered) -- better with
    threaded code!.
    """
    print(str, file=sys.stderr)

