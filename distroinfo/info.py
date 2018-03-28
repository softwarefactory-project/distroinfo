import fetch
import parse
import six


class DistroInfo(object):
    def __init__(self,
                 info_files,
                 fetcher=None,
                 local_info=None,
                 remote_info=None,
                 remote_git_info=None):
        """
        Specify distroinfo instance to query.

        :param info_files: info file name or a list of file names
        :param fetcher: custom info fetcher,
                        implementation of distroinfo.fetch.InfoFetcher,
                        you can use *_info params instead for builtins
        :param local_info: a shortcut to use LocalInfoFetcher
        :param remote_info: a shortcut to use RemoteRawInfoFetcher
        :param remote_git_info: a shortcut use RemoteGitInfoFetcher
        """
        if fetcher:
            self.fetcher = fetcher
        else:
            # convenience shortcuts to builtin info fetchers
            if local_info:
                self.fetcher = fetch.LocalInfoFetcher(local_info)
            elif remote_info:
                self.fetcher = fetch.RemoteRawInfoFetcher(remote_info)
            elif remote_git_info:
                self.fetcher = fetch.RemoteGitInfoFetcher(remote_git_info)
            else:
                # TODO: proper exception: InfoFetcherRequired
                raise NotImplementedError()
        self.info_files = info_files

        if isinstance(self.info_files, six.string_types):
            # support both a single file and a list
            self.info_files = [self.info_files]

    def get_info(self, apply_tag=None):
        """
        Get data from distroinfo instance.

        :param apply_tag: apply supplied tag to info
        :return: parsed info metadata
        """
        raw_infos = self.fetcher.fetch(*self.info_files)
        raw_info = parse.merge_infos(*raw_infos)
        info = parse.parse_info(raw_info, apply_tag=apply_tag)
        return info
