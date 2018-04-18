class DistroInfoException(Exception):
    msg_fmt = "An unknown error occurred"

    def __init__(self, msg=None, **kwargs):
        self.kwargs = kwargs
        if not msg:
            try:
                msg = self.msg_fmt % kwargs
            except Exception:
                msg = self.msg_fmt
        super(DistroInfoException, self).__init__(msg)


class InfoFetcherRequired(DistroInfoException):
    msg_fmt = "No info fetcher was selected."


class InvalidInfoFormat(DistroInfoException):
    msg_fmt = "Invalid info format."


class MissingRequiredSection(InvalidInfoFormat):
    msg_fmt = "Info is missing required section: %(section)s"


class MissingRequiredItem(InvalidInfoFormat):
    msg_fmt = "Required item missing: %(item)s"


class UndefinedPackageConfig(InvalidInfoFormat):
    msg_fmt = "Package config isn't defined: %(conf)s"


class SubstitutionFailed(InvalidInfoFormat):
    msg_fmt = "Substitution failed for string: %(txt)s"


class DuplicatedProject(InvalidInfoFormat):
    msg_fmt = "Duplicated project: %(prj)s"


class CircularInfoInclude(InvalidInfoFormat):
    msg_fmt = "Circular info include: %(info1)s -> %(info2)s"


class InvalidQuery(DistroInfoException):
    msg_fmt = "Invalid query: %(why)s"


class InvalidPackageFilter(DistroInfoException):
    msg_fmt = "Invalid package filter: %(why)s"


class RepoError(DistroInfoException):
    msg_fmt = "Repository error: %(what)s"


class NotADirectory(DistroInfoException):
    msg_fmt = "Not a directory: %(path)s"


class CommandNotFound(DistroInfoException):
    msg_fmt = "Command not found: %(cmd)s"


class CommandFailed(DistroInfoException):
    msg_fmt = "Command failed with return code %(code)s: %(cmd)s"


class RemoteFetchError(DistroInfoException):
    msg_fmt = "Failed to fetch remote file: %(code)s %(reason)s %(url)s"
