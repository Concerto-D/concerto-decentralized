#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. module:: engine
   :synopsis: this file contains the Mad class.
"""

from utility import Messages
import sys


class Mad (object):
    """
    This class is the engine of the Madeus model. When running it first check
    if the assembly has warnings, then it calls the mad_engine method to run
    the semantics on the assembly.
    """

    # list used to check if the set of active places has changed
    old_places = []

    def __init__(self, ass):
        self.assembly = ass
        self.assembly.init_semantics()

    def check_warnings(self):
        """
        This method is called before runing an assembly. It checks components
        and their connections. The default behavior is to block the run if
        some warnings are detected.

        :return: True if no WARNINGS, False otherwise
        """

        check = self.assembly.check_warnings()
        return check

    def _mad_engine(self, dryrun, printing):
        """
        This is the main function to run the operational semantics of the
        Madeus formal model. This is the heart of the coordination engine.
        """

        ended = False

        # main loop of the deployment process
        while not ended:

            self.assembly.semantics(dryrun, printing)
            if self.assembly.is_finish():
                ended = True

        if printing:
            print(Messages.ok() + "[Mad] Successful deployment" +
                  Messages.endc())

    def run(self, force=False, dryrun=False, printing=True):
        """
        This method run the assembly after checking its validity
        """
        check = self.check_warnings()

        if check or (not check and force):
            if printing:
                print(Messages.ok() + "[Mad] Assembly checked" + Messages.endc())
                print(Messages.ok() + "[Mad] Start assembly deployment" +
                      Messages.endc())
            self._mad_engine(dryrun, printing)

        elif not check and not force:
            if printing:
                print(Messages.fail() + "ERROR - The engine is not able to launch "
                                      "your assembly because some WARNINGS or "
                                      "ERRORS have been detected. You can force "
                                      "the deployment execution by calling run(True)."
                      + Messages.endc())
            sys.exit(0)
