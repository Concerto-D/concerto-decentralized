#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. module:: engine
   :synopsis: this file contains the Mad class.
"""

from utility import Messages
import sys
from configuration import Configuration


class Mad (object):
    """
    This class is the engine of the Madeus model. When running it first check
    if the assembly has warnings, then it calls the mad_engine method to run
    the semantics on the assembly.
    """

    def __init__(self, ass):
        self.assembly = ass
        init_transitions = []
        init_places = []
        for c in self.assembly.get_components():
            places = c.get_places()
            for p in places:
                if len(places[p].get_inputdocks()) == 0:
                    init_places.append(places[p])
        init_idocks = []
        init_odocks = []
        init_conn = []

        self.configuration = Configuration(init_transitions, init_places,
                                           init_idocks, init_odocks, init_conn)

    def check_warnings(self):
        """
        This method is called before runing an assembly. It checks components
        and their connections. The default behavior is to block the run if
        some warnings are detected.

        :return: True if no WARNINGS, False otherwise
        """

        check = self.assembly.check_warnings()
        return check

    def mad_engine(self):
        """
        This is the main function to run the operational semantics of the
        Madeus formal model. This is the heart of the coordination engine.
        """
        ended = False

        # main loop of the deployment process
        while not ended:

            # enable/disable connections
            new_connections = self.assembly.disable_enable_connections(
                self.configuration)
            # highest priority according to the model to guarantee the
            # disconnection of services when no more provided
            # before doing anything else
            self.configuration.update_connections(new_connections)

            new_transitions = []
            new_places = []
            new_idocks = []
            new_odocks = []

            # for each component perform operational semantics
            for c in self.assembly.get_components():
                (c_transitions, c_places, c_idocks, c_odocks) = \
                    c.semantics(self.configuration)
                new_transitions = new_transitions + c_transitions
                new_places = new_places + c_places
                new_idocks = new_idocks + c_idocks
                new_odocks = new_odocks + c_odocks

            # build the new configuration / ended
            self.configuration.update_transitions(new_transitions)
            self.configuration.update_places(new_places)
            self.configuration.update_input_docks(new_idocks)
            self.configuration.update_output_docks(new_odocks)

            if self.assembly.is_finish(self.configuration):
                ended = True

        print(Messages.ok() + "[Mad] Successful deployment" +
              Messages.endc())

    def run(self, force=False):
        """
        This method run the assembly after checking its validity
        """
        check = self.check_warnings()

        if check or (not check and force):
            print(Messages.ok() + "[Mad] Assembly checked" + Messages.endc())
            print(Messages.ok() + "[Mad] Start assembly deployment" +
                  Messages.endc())
            self.mad_engine()

        elif not check and not force:
            print(Messages.fail() + "ERROR - The engine is not able to launch "
                                  "your assembly because some WARNINGS or "
                                  "ERRORS have been detected. You can force "
                                  "the deployment execution by calling run(True)."
                  + Messages.endc())
            sys.exit(0)