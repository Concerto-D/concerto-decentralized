from concerto.madeus.all import *
from concerto.meta import ReconfigurationPerfAnalyzer
    
    
def sleep_print(component: MadeusComponent, start_message: str, time: float, end_message: str):
    from time import sleep
    component.print_color(start_message)
    sleep(time)
    component.print_color(end_message)


class Server(MadeusComponent):
    def create(self):
        self.places = ['undeployed', 'vm_started', 'downloaded', 'configured', 'running', 'running_checked']
        self.initial_place = "undeployed"
        self.transitions = {
            'start_vm': ('undeployed', 'vm_started', self.start_vm),
            'download': ('vm_started', 'downloaded', self.download),
            'configure': ('vm_started', 'configured', self.configure),
            'install': ('downloaded', 'configured', self.install),
            'run': ('configured', 'running', self.run),
            'check': ('running', 'running_checked', self.check),
        }
        self.groups = {
            'providing_service': ['running', 'running_checked']
        }
        self.dependencies = {
            'ip': (DepType.DATA_PROVIDE, ['vm_started']),
            'service': (DepType.PROVIDE, ['providing_service'])
        }
        
    def start_vm(self):
        sleep_print(self, "Starting VM...", 3, "VM started!")
        self.write("ip", "121.94.42.42")
        
    def download(self):
        sleep_print(self, "Downloading...", 3, "Downloaded!")
        
    def configure(self):
        sleep_print(self, "Configuring...", 3, "Configured!")
        
    def install(self):
        sleep_print(self, "Installing...", 4, "Installed!")
        
    def run(self):
        sleep_print(self, "Running...", 2, "Running!")

    def check(self):
        sleep_print(self, "Checking...", 5, "Checked!")
        

class Client(MadeusComponent):
    def create(self):
        self.places = ['undeployed', 'downloaded', 'configured', 'running']
        self.initial_place = "undeployed"
        self.transitions = {
            'download': ('undeployed', 'downloaded', self.download),
            'configure1': ('downloaded', 'configured', self.configure1),
            'configure2': ('downloaded', 'configured', self.configure2),
            'run': ('configured', 'running', self.run),
        }
        self.dependencies = {
            'server_ip': (DepType.DATA_USE, ['configure1']),
            'server_service': (DepType.USE, ['run'])
        }

    def download(self):
        sleep_print(self, "Downloading...", 1, "Downloaded!")

    def configure1(self):
        server_ip = self.read('server_ip')
        sleep_print(self, "Configuring (part 1) with server IP %s..." % server_ip, 2, "Configured (part 1)!")

    def configure2(self):
        sleep_print(self, "Configuring (part 2)...", 5, "Configured (part 2)!")

    def run(self):
        sleep_print(self, "Running...", 1, "Running!")


class ServerClientAssembly(MadeusAssembly):
    def create(self):
        self.components = {
            'server': Server(),
            'client': Client()
        }
        self.dependencies = [
            ('server', 'ip',
             'client', 'server_ip'),
            ('server', 'service',
             'client', 'server_service'),
        ]


if __name__ == '__main__':
    sca = ServerClientAssembly()

    # Analysis
    pa = ReconfigurationPerfAnalyzer(sca.get_concerto_reconfiguration())
    pa.get_graph().save_as_dot("graph.dot")

    # Running the deployment
    sca.set_print_time(True)
    sca.set_record_gantt(True)
    sca.run()

    # Gantt chart
    gc = sca.get_gantt_record().get_gantt_chart()
    gc.export_json("gantt_chart.json")
