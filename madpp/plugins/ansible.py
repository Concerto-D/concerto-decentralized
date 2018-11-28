from subprocess import run, CompletedProcess
import sys

class AnsibleCallResult:
    def __init__(self, command : str, return_code : int, stdout : str = None, stderr : str = None):
        self.command = command
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr

def call_ansible_on_host(host, playbook, tag="all", extra_vars=None, capture_output=False) -> AnsibleCallResult:
    if extra_vars is None:
        extra_vars_string = ""
    else:
        extra_vars_string = " --extra-vars \"%s\"" % ' '.join(["%s=%s"%(key, str(value)) for key,value in extra_vars.items()])
    command = "ansible-playbook -i %s, %s --tags \"%s\"%s" % (host,playbook,tag,extra_vars_string)
    if sys.version_info >= (3, 7):
        completed_process = run(command, shell=True, check=False, capture_output=capture_output)
        return AnsibleCallResult(
            command = command,
            return_code = completed_process.returncode,
            stdout = completed_process.stdout,
            stderr = completed_process.stderr
        )
    else:
        completed_process = run(command, shell=True, check=False)
        return AnsibleCallResult(
            command = command,
            return_code = completed_process.returncode,
        )
