#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains the mechanisms to automatically and efficiently deploy MAD
(Madeus Application Deployer) components.

An efficient deployment is characterized by the possibility to finely manage
the deployent processes in parallel. This is done here through multi-threading.
We define two types of threads: the first one is used to handle the parallel
deployment of multiple components, the second one handles the management of
multiple transitions.

"""

import time
import copy
import yaml
import os, sys
import queue, threading
import traceback
from random import uniform
from utils.extra import bcolors
from utils.extra import printerr
from utils.exceptions import NetError, NetConditionError, NetCallbackError

import plotly 
from plotly.figure_factory import create_gantt

from mad import MadException

lock = threading.Lock()

fname = "result_tasks.txt"
fname2 = "result_components.txt"

thread_queue = []


class _TransitionThread(threading.Thread):
    """
    Define the threads used to run transition callbacks.

    Args:
        model (:obj:`PetriNet`): A reference to a PetriNet model.
        tname (str): Name of the treated transition.
        exec_queue (:obj:`queue.Queue`): This queue is used to exchange
            information between the children threads and the main thread (for
            instance, when the callback in the child thread fails).
        dry_run (bool, optional): If True, no callback is called during the
            transition (default=False).
    """

    def __init__(self, model, tname, exec_queue, dry_run=False, profiling=False):
        threading.Thread.__init__(self, name=tname)
        self.model = model
        self.tname = tname
        self.exec_queue = exec_queue
        self.dry_run = dry_run
        self.profiling = profiling

    def run(self):
        return_code = 0
        func = getattr(self.model, self.tname)
        transition = self.model.net.transitions[self.tname]
        # Set a lock or something on the transition to handle
        # TODO: manage it in a better way than this ugly mechanism:
        while transition.inUse:
            time.sleep(uniform(.1,.5))
        transition.inUse = 1
        try:
            # Start a timer before firing the callback for profiling:
            start = time.localtime()
            # Run the callback:
            return_code = func(self.dry_run)
        except NetError:
            # Add the exception in the queue:
            self.exec_queue.put(sys.exc_info())
            return_code = 1
        except MadException:
            pass
        except Exception as e:
            traceback.print_exception(*sys.exc_info())
            os.abort()
        transition.inUse = 0
        if self.profiling:
            end = time.localtime()

            # Transition profiling:
            if not return_code:
                results = {
                        "Task": self.model.__class__.__name__ + " " + self.tname,
                        "Component": self.model.__class__.__name__,
                        "Start": time.strftime("%Y-%m-%d %H:%M:%S", start),
                        "Finish": time.strftime("%Y-%m-%d %H:%M:%S", end),
                        "ElapsedTime": time.mktime(end) - time.mktime(start),
                        "Result": "Not Complete" if return_code else "Complete"
                }

                # Write profiling information on disk:
                lock.acquire()
                with open(fname, "a") as of:
                    yaml.dump([results], of, width = 72)
                lock.release()

        return return_code


class _PetriNetThread(threading.Thread):
    """
    Define the threads used to manage assembly's components.

    Args:
        automaton (:obj:`Automaton`): A reference to the used automaton.
        model_name (str): Name of the treated PetriNet model.

    """

    def __init__(self, automaton, name):
        threading.Thread.__init__(self, name=name)
        self.automaton = automaton
        self.model_name = name

    def run(self):
        self.automaton.run(self.name)


class Automaton(object):
    """
    Define an automaton to deploy multiple MAD components.

    Args:
        components (list(list(:obj:`PetriNet`), str), optional): List of
            components managed by the automaton.
        step (bool, optional): If True, run the deployment process step by step
            (default=False)
        dry_run (bool, optional): If True, no callback is triggered when
            transitions are fired (default=False).
    """

    def __init__(self, components=None, step=False, dry_run=False,
                profiling=False):
        self.components = {}
        if components:
            self.add_components(components)
        self.step = step
        self.dry_run = dry_run
        self.profiling = profiling

        # Delete previous profiling records if existing:
        # TODO: there should be a better way to manage profiling information.
        if os.path.isfile(fname):
            os.remove(fname)
        if os.path.isfile(fname2):
            os.remove(fname2)

    def add_component(self, component, name):
        """Add a component to be managed by the automaton."""
        # TODO: should find a way to check that components are really components
        if name in self.components:
            raise Exception("Error: trying to add an instance with name"
                            "'%s' while this name is already used."%(name))
        self.components[name] = component
        component.net.automaton = self
        component.net.name = name

    def add_components(self, components_with_names):
        """
        Add a list of components to the automaton.

        Args:
            components_with_names (list(list(:obj:`PetriNet`, str)))
        """
        for component_w_n in components_with_names:
            self.add_component(component_w_n[0], component_w_n[1])

    def run_place(self, model, place):
        """
        This method triggers a thread for each outgoing transition, for a given
        place.

        Args:
            model (:obj:`PetriNet`): A reference to the PetriNet model.
            place (:obj:`Place`): A reference to the given place.
        """
        # Block the program if run in step mode:
        if self.step:
            input("Press Enter to continue...")

        class_name = model.__class__.__name__
        # Look at the place's transitions only if this place is validated:
        if place.state == True:
            infos = {}      # infos: keep transitions' thread and related queue
            threads = []    # threads: list of existing threads
            # First, a copy of the current available place's transitions is kept:
            current_transitions = copy.copy(model.net.get_transitions(place))
            # A thread is created for each transition:
            for tname, transition in current_transitions.items():
                # If the transition is still activated
                if transition.state == True:
                    # If dry_run = 3: no thread + empty transition
                    if self.dry_run == 3:
                        func = getattr(model, tname)
                        transition = model.net.transitions[tname]
                        # TODO: we need something better again here...
                        while transition.inUse:
                            time.sleep(randint(.1,.5))
                        transition.inUse = 1
                        try:
                            return_code = func(self.dry_run)
                        except NetError:
                            return_code = 1
                        transition.inUse = 0
                    # Else, the threads are created and added to the list:
                    else:
                        exec_queue = queue.Queue()
                        thread = _TransitionThread(model, tname, exec_queue,
                                self.dry_run, self.profiling)
                        threads.append(thread)
                        infos[tname] = {'queue': exec_queue,
                                        'thread': thread}

            if self.dry_run != 3:
                # Run all the threads from the list:
                for thread in threads:
                    thread.start()

                # Check for each transition the stat of the related thread:
                for tname, info in infos.items():
                    thread = info['thread']
                    r_queue = info['queue']
                    transition = model.net.transitions[tname]

                    while True:
                        # The following is used to unburden CPU cores:
                        time.sleep(0.2)
                        try:
                            # Check if there's something in the queue
                            exc = r_queue.get(block=False, timeout=0.1)
                        except queue.Empty:
                            pass
                        else:
                            # Exception was raised:
                            exc_type, exc_obj, exc_trace = exc
#                            printerr("fail: "+str(exc_obj))
#                            printerr(bcolors.FAIL + "[" + class_name + "]"
#                                + bcolors.ENDC
#                                + " Failed to move from " + place.name
#                                + " to " + transition.dst + "\n")
                            # Deal with the exception:
                            break # Move out of the 'while' loop

                        if thread.isAlive():
                            continue
                        else:
                            # If a thread finished and no exception was raised:
#                            printerr(bcolors.OKBLUE + "[" + class_name + "]"
#                                + bcolors.ENDC
#                                + " Successfully moved from " + place.name
#                                + " to " + transition.dst + "\n")
                            next_place = model.net.get_place(transition.dst)
                            if next_place.outgoing > 0:
                                self.run_place(model,
                                        model.net.get_place(transition.dst))
                            break # Move out of the 'while' loop

#        else:
#            printerr('Place "%s" of "%s" is not activated for now.'
#                    % (place.name, class_name))


    def run(self, name):
        """
        This method deploys an assembly component.

        Args:
            name (str): Name of the component to deploy.
        """
        model = self.components[name]
        class_name = model.__class__.__name__

        # First, a copy of the current available model's places is kept:
        current_places = copy.copy(model.net.current_places)
        for pname, place in current_places.items():
            self.run_place(model, place)
#        if model.net.get_current_transitions() == [] \
#                and model.net.is_initialized():
#            printerr(bcolors.OKGREEN + "[" + class_name + "]" + bcolors.ENDC
#                + " Reach the final place.\n")
#        else:
#            printerr(bcolors.FAIL + "[" + class_name + "]" + bcolors.ENDC
#                + " Deployment is not finished\n  Current status: "
#                    + str(model.current_places or 'Not initialized'))

    def autorun(self):
        """This method is meant to deploy multiple components in parallel."""
        if self.dry_run == 3:
            for cname, component in self.components.items():
                self.run(cname)
        else:
            threads = []
            # First, a PetriNet thread is created per component:
            for cname, component in self.components.items():
                thread = _PetriNetThread(self, cname)
                threads.append(thread)
                thread_queue.append(thread)
            # Then each thread is triggered:
            for thread in threads:
                thread.start()
            # Wait for all the threads to finished their work:
            for thread in thread_queue:
                thread.join()

    def notify(self, port):
        """
        This method is triggered by some events (e.g. port connection) to
        potentially unlock a stuck deployment process (stuck for instance due
        to an unfulfilled dependency).

        Args:
            port (:obj:`Port`): A reference to a port.
        """
        threads = []
        for rport in port.outside_links:
            rcomponent = rport.net
            rtransition = rcomponent.transitions[rport.inside_link]
            # Check if transition is valid:
            if rtransition:
                thread = threading.Thread(target=self.run_place,
                        args=(rcomponent.model,
                            rcomponent.get_place(rtransition.src),))
                threads.append(thread)
                thread_queue.append(thread)
        for thread in threads:
            thread.start()
        # The calling thread should return before its child returns, to that
        # end, the join phase is managed in the `autorun` method by
        # gathering all the threads in the 'thread_queue' list
        #for thread in threads:
        #    thread.join()

    def per_component_results(self):
        """This method records profiling results per component."""
        components = {}
        task_resuls = None

        with open(fname, "r") as f:
            task_results = yaml.load(f)

        for task in task_results:
            if not task['Component'] in components:
                components[task['Component']] = 0
            components[task['Component']] = components[task['Component']] \
                    + task['ElapsedTime']

        with open(fname2, "w") as of:
            yaml.dump([components], of, width = 72)

    def plot_gantt(self, title="Gantt Chart", colors=None):
        """
        This method plots a Gantt diagram of the deployment process.

        Args:
            title (str): Title of the Gantt diagram.
            colors (dict(str, str)): A dictionary mapping component names to
                    their Plotly color definition (hexa, rgb, colorscale).

            Examples:

            >>> title = 'DAG n-Transitional OpenStack Deployment'
            >>> colors = dict(Nova = '#E6194B',
            ...     Neutron = '#3CB44B',
            ...     Glance = '#FFE119',
            ...     OpenVSwitch = '#0082C8')
            >>> assembly.automaton.plot_gantt(title, colors)
        """
        with open(fname, "r") as f:
            df = yaml.load(f)

        fig = create_gantt(df, title=title,
                colors=colors, index_col='Component',
                show_colorbar=True,
                showgrid_x=True, showgrid_y=True) 
        plotly.offline.plot(fig, filename='gantt.html', auto_open=False,
                image='svg')

