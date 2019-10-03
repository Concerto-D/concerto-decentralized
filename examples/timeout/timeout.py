import time
from concerto.all import Component, Assembly


class SimpleComponent(Component):
    def __init__(self, deploy_time):
        self.deploy_time = deploy_time
        super().__init__()

    def create(self):
        self.places = [
            'undeployed',
            'deployed'
        ]

        self.transitions = {
            'deploy_transition': ('undeployed', 'deployed', 'deploy', 0, self.deploy_function)
        }

        self.initial_place = "undeployed"

    def deploy_function(self):
        time.sleep(self.deploy_time)


class SimpleAssembly(Assembly):
    def __init__(self, deploy_time):
        super().__init__()
        self.simple_component = SimpleComponent(deploy_time)

    def deploy(self):
        self.add_component("my_component", self.simple_component)
        self.push_b("my_component", "deploy")
        self.wait_all()


assembly = SimpleAssembly(5)
assembly.deploy()
finished, debug_info = assembly.synchronize_timeout(2)

if finished:
    print("Deployement successful")
    assembly.terminate()
else:
    print("Error! Timeout on deploy! Debug info:")
    print(debug_info)

    assembly.kill()
    # Transitions may still be running at this point because we can't simply kill the threads running the transitions
    print("Will terminate when the running transitions are over...")
