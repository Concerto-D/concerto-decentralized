#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. module:: transition
   :synopsis: this file contains the Transition class.
"""

import threading

class Transition (object):
    """This Transition class is used to create a transition.

        A transition is an action, represented by the 'run' function. This
        action is performed between a source and destination dock, each of
        which is attached to a place.

        This is an abstract class that need to be override. In particular,
        the method 'run' must be override
    """

    """
    BUILD TRANSITION
    """

    def __init__(self, name, code, src, dst, places):
        self.name = name
        self.src_place = src
        self.dst_place = dst
        self.code = code
        self.bind_docks(places)

    def bind_docks(self, places):
        """This method is called from the Component class to create
        docks into places associated to the transition. Once created
        these docks are bound to the transition.

        :param places: the dictionary of all places declared for the component
        """

        for key in places:
            # create output dock in the src place and bind it
            if key == self.src_place:
                self.src_dock = places[key].create_output_dock(self)
            # create input dock in the dst place and bind it
            if key == self.dst_place:
                self.dst_dock = places[key].create_input_dock(self)

    def setname(self, name):
        """
        This method set the name of the transition

        :param name: tha name (string) to set
        """
        self.name = name

    def getname(self):
        """
        This method returns the name of the transition

        :return: name (string)
        """
        return self.name

    def get_src_dock(self):
        """
        This method returns the source dock of the transition

        :return: the source dock self.src_dock
        """
        return self.src_dock

    def get_dst_dock(self):
        """
        This method returns the destination dock of the transition

        :return: the destination dock self.dst_dock
        """
        return self.dst_dock

    def start_thread(self):
        """
        This method creates the thread of the transition

        :return: the Thread of the transition
        """
        self.thread = threading.Thread(target=self.code.run)
        self.thread.start()

    def join_thread(self):
        """
        This method tries to join self.thread. The default behavior has no
        timeout.

        :return: True if the tread has been joined, False othwise
        """
        if not self.thread.is_alive():
            self.thread.join()
            return True
        else:
            return False