

class MadError(Exception):
    pass


class MadFailedHostsError(MadError):
    def __init__(self, hosts):
        self.hosts = hosts


class MadUnreachableHostsError(MadError):
    def __init__(self, hosts):
        self.hosts = hosts


class MadFilePathError(MadError):
    def __init__(self, filepath, msg=''):
        super(MadFilePathError, self).__init__(msg)
        self.filepath = filepath


class MadProviderMissingConfigurationKeys(MadError):
    def __init__(self, missing_overridden):
        super(MadProviderMissingConfigurationKeys, self).__init__(
            "Keys %s have to be overridden in the provider "
            "section of the reservation file."
            % missing_overridden)
        self.missing_ovorridden = missing_overridden
