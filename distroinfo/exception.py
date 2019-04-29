# Copyright (c) 2019 Red Hat
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


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
    msg_fmt = "Circular info include: %(info)s"


class InvalidQuery(DistroInfoException):
    msg_fmt = "Invalid query: %(why)s"


class InvalidPackageFilter(DistroInfoException):
    msg_fmt = "Invalid package filter: %(why)s"


class InvalidRemoteInfoRef(DistroInfoException):
    msg_fmt = ("Remote info referenced but not defined in 'remote-info' "
               "section: %(remote)s")


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
