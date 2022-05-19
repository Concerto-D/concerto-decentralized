import time
from typing import Callable

from concerto import communication_handler, assembly_config
from concerto.communication_handler import CONN, DECONN
from concerto.utility import Printer

WAITING_DELAY = 0.5


class RemoteSynchronization:
    """
    Class representing an asynchronous wait for an assembly to the other
    """
    is_asynchronous = True
    assembly = None

    @staticmethod
    def exit_reconf(assembly):
        assembly_config.save_config(assembly)
        Printer.st_tprint("Going sleeping bye")
        exit()

    @staticmethod
    def synchronize_connection(assembly, comp1_name: str, dep1_name: str, comp2_name: str, dep2_name: str, async_func: Callable):
        """
        Condition: No condition, directly call the async_func
        """
        Printer.st_tprint(f"{assembly.name} : Waiting CONN message from {comp2_name}")
        is_conn_synced = communication_handler.is_conn_synced(comp1_name, comp2_name, dep2_name, dep1_name, CONN)
        time.sleep(WAITING_DELAY)
        Printer.st_tprint("Executing async func while waiting:" + async_func.__name__)
        if not is_conn_synced:
            async_func(assembly)
            return False
        Printer.st_tprint(f"{assembly.name} : RECEIVED CONN message from {comp2_name}")
        return True

    @staticmethod
    def synchronize_disconnection(assembly, comp1_name: str, dep1_name: str, comp2_name: str, dep2_name: str, async_func: Callable):
        """
        Condition: No condition, directly call the async_func
        """
        Printer.st_tprint(f"{assembly.name} : Waiting DECONN message from {comp2_name}")
        is_deconn_synced = communication_handler.is_conn_synced(comp1_name, comp2_name, dep2_name, dep1_name, DECONN)
        time.sleep(WAITING_DELAY)
        Printer.st_tprint("Executing async func while waiting:" + async_func.__name__)
        if not is_deconn_synced:
            async_func(assembly)
            return False
        Printer.st_tprint(f"{assembly.name} : RECEIVED DECONN message from {comp2_name}")
        return True

    @staticmethod
    def synchronize_wait(assembly, async_func: Callable):
        """
        Condition: Need all local component to not be active
        """
        if len(assembly._p_act_components) == 0:
            async_func(assembly)
        return False

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

