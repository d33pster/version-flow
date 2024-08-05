
# warning for checking updates in github
# case where api token is provided but private is set to False
class PrivateRepositoryWarning(Warning):
    pass
# case where download directory is None
class DownloadDirectoryWarning(Warning):
    pass