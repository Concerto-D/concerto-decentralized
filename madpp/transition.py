#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. module:: transition
   :synopsis: this file contains the Transition class.
"""

import threading
from madpp.gantt_chart import GanttChart

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

    def __init__(self, name, src, dst, bhv, idset, func, args, places):
        self.name = name
        self.src_place = src
        self.dst_place = dst
        self.behavior = bhv
        self.dst_idset = idset
        self.code = func
        self.args = args
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

    def set_name(self, name):
        """
        This method set the name of the transition

        :param name: tha name (string) to set
        """
        self.name = name

    def get_name(self):
        """
        This method returns the name of the transition

        :return: name (string)
        """
        return self.name
    
    def get_dst_idset(self):
        return self.dst_idset

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

    def get_behavior(self):
        """
        This method returns the behavior of the transition

        :return: behavior (string)
        """
        return self.behavior

    def start_thread(self, gantt_tuple, dryrun):
        """
        This method creates the thread of the transition

        :return: the Thread of the transition
        """
        if not dryrun:
            self.thread = threading.Thread(target=self.code, args=self.args)
            if gantt_tuple is not None:
                (gantt_chart,args) = gantt_tuple
                gantt_chart.start_transition(*args)
            self.thread.start()
        else:
            pass

    def join_thread(self, gantt_tuple, dryrun):
        """
        This method tries to join self.thread. The default behavior has no
        timeout.

        :return: True if the tread has been joined, False othwise
        """
        if not dryrun:
            if not self.thread.is_alive():
                self.thread.join()
                if gantt_tuple is not None:
                    (gantt_chart,args) = gantt_tuple
                    gantt_chart.stop_transition(*args)
                return True
            else:
                return False
        else:
            return True
