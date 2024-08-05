
import requests
import warnings
from typing import Tuple, Callable, Any
from os import getcwd
from .exceptions import *
from .warnings import *

class VersionFlow:
    """`VersionFlow class is responsible for keeping your packages up to date!`

    ### :Importing

    >>> from version_flow.vf import VersionFlow

    ### :Basic usage structure

    >>> with VersionFlow() as vf: # this particular line is responsible for checking the internet.
    ...     # your code goes here
    """
    def __init__(self):
        """`VersionFlow class is responsible for keeping your packages up to date!`"""
        # internet status
        self.internet_status = False
        # update status
        self.update_available = False

    def check_internet_connection(self, timeout: int = 3, server: str = "https://www.google.com") -> 'VersionFlow':
        """`Check internet status`

        ### :params
        - `timeout (int)`: set timeout time. Defaults to 3.
        - `server (str)`: set server to connect and check. Defaults to Google.com

        ### :usage options

        - `option A`

        >>> vf = VersionFlow() # create instance of VersionFlow class
        >>> if vf.check_internet_connection().internet_status:
        ...     # your code goes here.
        ...     # This part runs only if internet connection is present.

        - `option B`

        >>> with VersionFlow() as vf:
        ...     if vf.internet_status:
        ...         # your code goes here
        ...         # Note that check_internet_connection() is called by default with the `with` statement
        """
        try:
            response = requests.get(url=server, timeout=timeout)
            # check if the request was successful (status code 200)
            self.internet_status = response.status_code == 200
        except (requests.ConnectionError, requests.ConnectTimeout):
            pass
        
        return self
    
    def check_for_updates_in_github(
        self,
        current_version: str,
        username: str,
        repository: str,
        release: str = 'latest',
        private: bool = False,
        if_private_then_api_token: str | None = None,
        update: bool = False,
        files_to_download: list[str] | None = None,
        download_directory: str | None = None,
        update_method: Callable[..., Any] | None = None,
        *update_method_args: Any
    ) -> (str | None):
        """`Checks if there are any updates in accordance with the current version in GitHub`
        """
        # define api_url for github
        api_url = "https://api.github.com/repos/{}/{}/releases/{}".format(username, repository, release)

        # define headers if the repository is private
        headers = None
        if private and if_private_then_api_token != None:
            headers = {
                'Authorization': 'token {}'.format(if_private_then_api_token),
                'Accept': 'application/vnd.github.v3+json'
            }
        elif private and if_private_then_api_token == None:
            # if private value is set to True but api token is not given
            raise GitHubTokenErr('The private parameter is set to True, however, no API Token was provided.')
        elif if_private_then_api_token != None and not private:
            # if api_token is provided but private value is not set to True
            warnings.warn(
                'The private parameter is set to False, however, an API_TOKEN has been provided. This practice is discouraged.',
                category=PrivateRepositoryWarning,
                stacklevel=2
            )
            # define the headers
            headers = {
                'Authorization': 'token {}'.format(if_private_then_api_token),
                'Accept': 'application/vnd.github.v3+json'
            }
        
        # get response
        if headers != None:
            response = requests.get(url=api_url, headers=headers)
        else:
            response = requests.get(url=api_url)
        
        
        # raise connection error if any
        try:
            response.raise_for_status()
        except Exception as e:
            raise ServerResponseErr('Failed to connect: {}'.format(e))
        
        # get release json
        release_ = response.json()
        # try to get tag
        try:
            release_tag = release_['tag_name']
        except Exception as e:
            raise ReleaseTagErr('Failed to get tag from release: {}'.format(e))
        
        # check if release_tag is greater than current version
        if Version(release_tag).is_greater_than(current_version):
            # if the latest release tag is greater than the current version
            self.update_available = True # update is available
            if not update:
                # if update is set to False, just return tag
                return release_tag
            else:
                ## update code goes here
                # check parameters
                if files_to_download == None:
                    raise FilesNotSetErr('Update parameter is set to True but no Files are provided.')
                
                if download_directory == None:
                    warnings.warn('No Download Directory was provided. Defaulting to current.', category=DownloadDirectoryWarning, stacklevel=2)
                    download_directory = getcwd()

                self.update_from_github(
                    username,
                    repository,
                    files_to_download,
                    download_directory,
                    private=private,
                    if_private_then_api_token=if_private_then_api_token,
                    update_method=update_method,
                    *update_method_args
                )
        else:
            return None
    
    def update_from_github(
            self,
            username: str,
            repository: str,
            files_to_download: list[str],
            download_directory: str | None = None,
            target_version: str = 'latest',
            private: bool = False,
            if_private_then_api_token: str | None = None,
            update_method: Callable[..., Any] | None = None,
            *update_method_args: Any
    ):
        """`update/downlaod from github.`
        """
        # check params
        if download_directory == None:
            warnings.warn('No Download Directory was provided. Defaulting to current.', category=DownloadDirectoryWarning, stacklevel=2)
            download_directory = getcwd()

        # set api_url
        api_url = "https://api.github.com/repos/{}/{}/releases/{}".format(username, repository, target_version)

        # define headers if the repository is private
        headers = None
        if private and if_private_then_api_token != None:
            headers = {
                'Authorization': 'token {}'.format(if_private_then_api_token),
                'Accept': 'application/vnd.github.v3+json'
            }
        elif private and if_private_then_api_token == None:
            # if private value is set to True but api token is not given
            raise GitHubTokenErr('The private parameter is set to True, however, no API Token was provided.')
        elif if_private_then_api_token != None and not private:
            # if api_token is provided but private value is not set to True
            warnings.warn(
                'The private parameter is set to False, however, an API_TOKEN has been provided. This practice is discouraged.',
                category=PrivateRepositoryWarning,
                stacklevel=2
            )
            # define the headers
            headers = {
                'Authorization': 'token {}'.format(if_private_then_api_token),
                'Accept': 'application/vnd.github.v3+json'
            }
        
        # get response
        if headers != None:
            response = requests.get(url=api_url, headers=headers)
        else:
            response = requests.get(url=api_url)
        
        # raise connection error if any
        try:
            response.raise_for_status()
        except Exception as e:
            raise ServerResponseErr('Failed to connect: {}'.format(e))

        # 
    
    def __enter__(self):
        """Enter context:

        : perform internet check
        : move on
        """
        self.check_internet_connection()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass

class Version:
    def __init__(self, version: str):
        parsed = self.parse(version)
        self.version = 'v{}.{}.{}'.format(parsed[0], parsed[1], parsed[2])
    
    def parse(self, version: str) -> Tuple[int, int, int]:
        """`returns version in the form (int, int, int)`
        
        ### :params
        - version (str): version to parse

        ### :returns
        `(major, minor, patch) for the type (int, int, int)`
        """
        if version.startswith('v'):
            version = version[1:]
        
        parts = version.split('.')
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0

        return (major, minor, patch)

    def is_greater_than(self, version_to_check: str) -> bool:
        """checks if the `Version` type object is greater than the provided version
        
        ### :params
        - version_to_check (str): The version to check against

        ### :returns
        `True | False`
        """
        parsed = [self.parse(self.version), self.parse(version_to_check)]
        latest = max(parsed)

        latest_in_string = 'v{}.{}.{}'.format(latest[0], latest[1], latest[2])

        return latest_in_string == self.version