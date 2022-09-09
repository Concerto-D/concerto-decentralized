import traceback
from functools import wraps

from flask import Flask, request
from threading import Thread

from concerto.debug_logger import log
from concerto.rest_communication import ACTIVE
import logging

# TODO: refacto with rest_communication
CONN = "CONN"
DECONN = "DECONN"


PORT_BY_ASSEMBLY = {
    "server_assembly": 5000,
    **{f"dep_assembly_{i}": 5001+i for i in range(20)}  # TODO: change magic number of deps
}


def run_api_in_thread(assembly):
    thread = Thread(target=run_flask_api, args=(assembly,))
    thread.setDaemon(True)  # Required to make the program exit when main thread exit
    thread.start()


def catch_exceptions(func):
    """
    Permet de catcher les exceptions des routes TODO: comprendre pk need de les catcher explicitement
    """
    # wraps: Permet de renommer la fonction, pour ne pas avoir de redondance quand on utilise
    # plusieurs fois le même décorateur dans le code
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            log.exception(e)
            traceback.print_exc()

    return wrapper


def run_flask_api(assembly):
    app = Flask(__name__)

    @app.route("/get_nb_dependency_users/<component_name>/<dependency_name>")
    @catch_exceptions
    def get_nb_dependency_users(component_name: str, dependency_name: str):
        for conn in set(assembly._p_component_connections[component_name]):
            if conn._use_dep.get_name() == dependency_name:
                return str(conn._use_dep._p_nb_users)
            if conn._provide_dep.get_name() == dependency_name:
                return str(conn._provide_dep._p_nb_users)

    @app.route("/get_refusing_state/<component_name>/<dependency_name>")
    @catch_exceptions
    def get_refusing_state(component_name: str, dependency_name: str):
        # log.debug(f"API Request: get_refusing_state for {component_name}, {dependency_name}")
        for conn in set(assembly._p_component_connections[component_name]):
            if conn._use_dep.get_name() == dependency_name:
                result = str(conn._use_dep._p_is_refusing)
                # log.debug(f"API Response: {result}")
                return result
            if conn._provide_dep.get_name() == dependency_name:
                result = str(conn._provide_dep._p_is_refusing)
                # log.debug(f"API Response: {result}")
                return result

    @app.route("/get_data_dependency/<component_name>/<dependency_name>")
    @catch_exceptions
    def get_data_dependency(component_name: str, dependency_name: str):
        for conn in set(assembly._p_component_connections[component_name]):
            if conn._use_dep.get_name() == dependency_name:
                return str(conn._use_dep._p_data)
            if conn._provide_dep.get_name() == dependency_name:
                return str(conn._provide_dep._p_data)

    @app.route("/is_conn_synced/<syncing_component>/<component_to_sync>/<dep_to_sync>/<syncing_dep>/<action>")
    @catch_exceptions
    def is_conn_synced(syncing_component: str, component_to_sync: str, dep_to_sync: str, syncing_dep: str, action: str):
        # log.debug(f"API Request: is_conn_synced {syncing_component} {component_to_sync} {dep_to_sync} {syncing_dep} {action}")
        for conn in set(assembly._p_component_connections[component_to_sync]):
            use, provide = (conn.get_use_dep(), conn.get_provide_dep())
            # log.debug("---- Checking for conn with: -----")
            # log.debug(f"use comp name: {use.get_component_name()}")
            # log.debug(f"provide comp name: {provide.get_component_name()}")
            # log.debug(f"use name: {use.get_name()}")
            # log.debug(f"provide name: {provide.get_name()}")
            # log.debug(f"action: {action}, CONN: {CONN}, action==CONN: {str(action == CONN)}")
            if (use.get_component_name() in [component_to_sync, syncing_component]
            and provide.get_component_name() in [component_to_sync, syncing_component]
            and use.get_name() in [dep_to_sync, syncing_dep]
            and provide.get_name() in [dep_to_sync, syncing_dep]):
                result = str(action == CONN)
                # log.debug(f"API Response: {result}")
                return result
        result = str(action == DECONN)
        # log.debug(f"API Response: {result}")
        return result

    @app.route("/get_remote_component_state/<component_name>/<id_sync>")
    @catch_exceptions
    def get_remote_component_state(component_name: str, id_sync: int):
        # TODO: to refacto
        if component_name + str(id_sync) not in assembly._p_components_states.keys():
            return ACTIVE
        else:
            # TODO: ad-hoc, to refacto
            if str(id_sync) == "1":
                calling_assembly_name = request.args.get("calling_assembly_name")
                if calling_assembly_name is not None:
                    assembly.add_to_remote_confirmations(calling_assembly_name)
            return assembly._p_components_states[component_name + str(id_sync)]

    print("lets go app")

    # Remove logging of each HTTP transactions
    werkzeug_log = logging.getLogger('werkzeug')
    werkzeug_log.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=PORT_BY_ASSEMBLY[assembly.get_name()])
