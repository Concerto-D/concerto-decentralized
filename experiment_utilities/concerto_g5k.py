from typing import List, Optional
from experiment_utilities.remote_host import RemoteHost


class ConcertoG5k:
    DEFAULT_LOCAL_WD: str = '.'
    DEFAULT_REMOTE_WD: str = '~/concertonode'
    DEFAULT_CONCERTO_GIT: str = 'https://gitlab.inria.fr/mchardet/madpp.git'
    DEFAULT_CONCERTO_DIR_IN_GIT: str = 'madpp'

    def __init__(self, remote_host: RemoteHost, remote_exp_dir: str, python_file: str, concerto_config,
                 local_wd: str = DEFAULT_LOCAL_WD,
                 remote_wd: str = DEFAULT_REMOTE_WD,
                 concerto_git: str = DEFAULT_CONCERTO_GIT,
                 concerto_dir_in_git: str = DEFAULT_CONCERTO_DIR_IN_GIT,
                 send_ssh_keys: bool = False,
                 print_commands: bool = True):
        """

        :param remote_host: RemoteHost object for the remote machine which is going to run Concerto
        :param remote_exp_dir: Directory in which to perform the experiment on the remote machine, relative to the
        remote working directory
        :param python_file: Python file to run on the remote server inside the experiment directory
        :param concerto_config: object which will be serialized to JSON and sent to the experiment directory as
        "concerto_config.json"
        :param local_wd: Local working directory
        :param remote_wd: Remote working directory
        :param concerto_git: Concerto git repository to clone
        :param concerto_dir_in_git: Location of Concerto inside the git repository
        :param additional_git_clone: Additional git repositories to clone inside the remote working directory
        :param send_ssh_keys: Whether or not to send the local public and private SSH keys to the remote machine
        """
        self.full_concerto_dir = '%s/%s' % (remote_wd, concerto_dir_in_git)
        self.full_remote_exp_dir = '%s/%s' % (remote_wd, remote_exp_dir)
        self.concerto_host: RemoteHost = remote_host
        self.local_wd: str = local_wd
        self.remote_wd: str = remote_wd
        self.concerto_git: str = concerto_git
        self.concerto_config = concerto_config
        self.send_ssh_keys: bool = send_ssh_keys
        self.print_commands: bool = print_commands
        self.python_file: str = python_file

        self.remote_exp_dir_created = False
        self.concerto_cloned = False

    def _ensure_exp_dir_exists(self):
        if not self.remote_exp_dir_created:
            command = "mkdir -p %s" % self.full_remote_exp_dir
            with self.concerto_host as concerto_host:
                self.run_command(command)
            self.remote_exp_dir_created = True

    def _ensure_concerto_cloned(self):
        if not self.concerto_cloned:
            self.clone_git(self.concerto_git)
        self.concerto_cloned = True

    def clone_git(self, git_url: str, location: Optional[str] = None):
        if not location:
            location = self.remote_wd
        git_clone_cmd = "mkdir -p %s; cd %s; " % (location, location) +\
                        "git clone %s;" % git_url
        self.run_command(git_clone_cmd)

    def run_command(self, command: str, override_print_command: Optional[bool] = None):
        print_command = self.print_commands
        if override_print_command is not None:
            print_command = override_print_command
        if print_command:
            print("Running command: %s" % command)
        with self.concerto_host as concerto_host:
            concerto_host.run(command, wait=True)

    def get_concerto(self):
        self._ensure_concerto_cloned()

    def send_files(self, files_list: List[str]):
        """
        Sends a list of file to the remote experiment directory
        :param files_list: List of files to send, relative to the local working directory
        """
        self._ensure_exp_dir_exists()
        with self.concerto_host as concerto_host:
            concerto_host.send_files(
                local_files=[self.local_wd + "/" + file for file in files_list],
                remote_location=self.full_remote_exp_dir
            )

    def get_files(self, files_list: List[str]):
        """
        Gets a list of file to the local working directory
        :param files_list: List of files to get, relative to the remote experiment directory
        """
        self._ensure_exp_dir_exists()
        with self.concerto_host as concerto_host:
            concerto_host.get_files(
                remote_files=["%s/%s" % (self.full_remote_exp_dir, fn) for fn in files_list],
                local_location=self.local_wd
            )

    def execute(self, timeout: Optional[str] = None, timeout_graceful_exit_time: str = "10s"):
        """
        Executes Concerto on the remote machine after sending the necessary files and cloning the Concerto git
        repository
        :param timeout: If not None, string in the timeout shell command format giving the maximum execution time.
        :param timeout_graceful_exit_time: String in the timeout shell command format giving the time given by timeout
        to the Concerto process to exit gracefully before being killed (only relevant if timeout is not None)
        """
        self._ensure_concerto_cloned()
        self._ensure_exp_dir_exists()
        with self.concerto_host as concerto_host:
            with open(self.local_wd + "/concerto_config.json", "w") as concerto_config_file:
                from json import dump
                dump(self.concerto_config, concerto_config_file)
            concerto_host.send_files(
                local_files=[self.local_wd + "/concerto_config.json"],
                remote_location=self.full_remote_exp_dir
            )
            if self.send_ssh_keys:
                concerto_host.send_files(
                    local_files=["~/.ssh/id_rsa", "~/.ssh/id_rsa.pub"],
                    remote_location="~/.ssh"
                )
            run_cmd = "cd %s;" % self.full_concerto_dir +\
                      "source source_dir.sh;" +\
                      "cd %s;" % self.full_remote_exp_dir
            if timeout:
                run_cmd += "timeout -k %s %s python3 %s >stdout 2>stderr" % (timeout_graceful_exit_time,
                                                                             timeout,
                                                                             self.python_file)
            else:
                run_cmd += "python3 %s >stdout 2>stderr" % self.python_file
            self.run_command(run_cmd)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
