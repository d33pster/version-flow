
## exception for checking updates in github
# case where private paramenter is True but api_token is not provided
class GitHubTokenErr(Exception):
    pass
# case where response status is not 200, i.e not success
class ServerResponseErr(Exception):
    pass
# case where tag name fetching fails for some error
class ReleaseTagErr(Exception):
    pass
# case where update is True but no files to download
class FilesNotSetErr(Exception):
    pass