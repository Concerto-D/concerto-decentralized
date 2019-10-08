from enum import Enum
import subprocess

from execo.action import Put, Get, Remote
from execo.host import Host


class RemoteHost:
    class Backend(Enum):
        SSH = 0
        EXECO = 1

    class _ExecoBackend:
        def __init__(self, remote_address, remote_user):
            self._remote_address = remote_address
            self._remote_user = remote_user
            self._host = Host(remote_address, user=remote_user)

        def run(self, command):
            act = Remote(
                cmd=command,
                hosts=[self._host]
            ).run()

        def send_files(self, local_files, remote_location):
            act = Put(
                hosts=[self._host],
                local_files=local_files,
                remote_location=remote_location
            ).run()

        def get_files(self, remote_files, local_location):
            act = Get(
                hosts=[self._host],
                remote_files=remote_files,
                local_location=local_location
            ).run()

    class _SSHBackend:
        def __init__(self, remote_address, remote_user):
            self._remote_address = remote_address
            self._remote_user = remote_user
            self._ssh_adr = '%s@%s' % (remote_user, remote_address)

        def run(self, command):
            cproc = subprocess.run(['ssh', self._ssh_adr, command], check=True)

        def send_files(self, local_files, remote_location):
            args = ['scp']
            for lf in local_files:
                args.append(lf)
            args.append("%s:%s" % (self._ssh_adr, remote_location))
            cproc = subprocess.run(args, check=True)

        def get_files(self, remote_files, local_location):
            args = ['scp']
            for rf in remote_files:
                args.append("%s:%s" % (self._ssh_adr, rf))
            args.append(local_location)
            cproc = subprocess.run(args, check=True)

    def __init__(self, remote_address, remote_user='root', backend=Backend.EXECO):
        self._remote_address = remote_address
        if backend is RemoteHost.Backend.EXECO:
            self._backend = self._ExecoBackend(remote_address, remote_user)
        else:
            self._backend = self._SSHBackend(remote_address, remote_user)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def run(self, command):
        self._backend.run(command)

    def send_files(self, local_files, remote_location='.'):
        self._backend.send_files(local_files, remote_location)

    def get_files(self, remote_files, local_location='.'):
        self._backend.get_files(remote_files, local_location)

    def write_file(self, text, remote_file_location):
        import tempfile, os
        (fd, fpath) = tempfile.mkstemp(text=True)
        b = str.encode(text)
        os.write(fd, b)
        os.close(fd)
        self.send_files([fpath], remote_file_location)
        os.remove(fpath)

    def write_jinja2(self, template_text, parameters, remote_file_location):
        from jinja2 import Template
        template = Template(template_text)
        final_text = template.render(parameters)
        self.write_file(final_text, remote_file_location)

    def write_jinja2_file(self, local_jinja2_file, parameters, remote_file_location):
        with open(local_jinja2_file) as f:
            self.write_jinja2(f.read(), parameters, remote_file_location)

    def wait_for_port(self, port, sleep=1., timeout=300):
        from exepriment_utilities.wait_for import wait_for_port
        wait_for_port(port, self._remote_address, sleep=sleep, timeout=timeout)
