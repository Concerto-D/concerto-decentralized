from subprocess import run, CompletedProcess

class AnsibleCallResult:
    def __init__(self, command : str, return_code : int, stdout : str, stderr : str):
        self.command = command
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr

def call_ansible_on_host(host, playbook, tag="all", capture_output=False) -> AnsibleCallResult:
    command = "ansible-playbook -i %s, %s --tags \"%s\"" % (host,playbook,tag)
    #Commented: python 3.7 required
    #completed_process = run(command, shell=True, check=False, capture_output=capture_output)
    completed_process = run(command, shell=True, check=False)
    return AnsibleCallResult(
        command = command,
        return_code = completed_process.returncode,
        #stdout = completed_process.stdout,
        #stderr = completed_process.stderr
    )
