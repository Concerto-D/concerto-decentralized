import json
import queue
import time
from typing import Callable

import concerto
from concerto import communication_handler
from concerto.communication_handler import CONN
from concerto.component import Component, Group
from concerto.connection import Connection
from concerto.dependency import Dependency, DepType
from concerto.internal_instruction import InternalInstruction
from concerto.place import Dock, Place
from concerto.transition import Transition
from concerto.utility import Printer

WAITING_DELAY = 1


class FixedEncoder(json.JSONEncoder):
    def default(self, obj):
        if any(isinstance(obj, k) for k in [concerto.assembly.Assembly, Component, Dependency, Dock, Connection, Place, Transition, InternalInstruction, Group]):
            identifier = obj._p_id
            d = obj.__dict__
            output = {}
            output["_p_id"] = identifier
            for k, v in d.items():
                if k.startswith("_p_"):
                    output[k] = v
            return output
        elif isinstance(obj, DepType) or isinstance(obj, InternalInstruction.Type):
            return obj.name
        elif isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, queue.Queue):
            return list(obj.queue)
        else:
            return obj


class RemoteSynchronization:
    """
    Class representing an asynchronous wait for an assembly to the other
    """
    is_asynchronous = True
    assembly = None

    @staticmethod
    def exit_reconf(assembly):
        Printer.st_tprint("Saving current conf ...")
        with open("saved_config.json", "w") as outfile:
            json.dump(assembly, outfile, cls=FixedEncoder, indent=4)
        Printer.st_tprint("Going sleeping bye")
        exit()

    @staticmethod
    def synchronize_connection(assembly, comp1_name: str, dep1_name: str, comp2_name: str, dep2_name: str, async_func: Callable):
        """
        Condition: No condition, directly call the async_func
        """
        is_conn_synced = False
        while not is_conn_synced:
            Printer.st_tprint(f"{assembly.name} : Waiting CONN message from {comp2_name}")
            is_conn_synced = communication_handler.is_conn_synced(comp1_name, comp2_name, dep2_name, dep1_name, CONN)
            time.sleep(WAITING_DELAY)
            Printer.st_tprint("Executing async func while waiting:" + async_func.__name__)
            async_func(assembly)
        Printer.st_tprint(f"{assembly.name} : RECEIVED CONN message from {comp2_name}")
        return

    @staticmethod
    def synchronize_disconnection(async_func: Callable):
        """
        Condition: No condition, directly call the async_func
        """
        return

    @staticmethod
    def synchronize_wait(async_func: Callable):
        """
        Condition: Need all local component to not be active
        """
        return

    @staticmethod
    def synchronize_wait_all(async_func: Callable):
        """
        Condition: Need all local component to not be active
        """
        return

    @staticmethod
    def synchronize_is_served(async_func: Callable):
        """
        Condition: Need to finish every other behavior than the blocked one
        """
        return

    @staticmethod
    def synchronize_is_in_use(async_func: Callable):
        """
        Condition: Need to finish every other behavior than the blocked one
        """
        return

