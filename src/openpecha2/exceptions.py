class RepoDoesNotExist(Exception):
    """Raised when there is a problem with the repository."""

    def __init__(self, org_name, repo_name):
        self.org_name = org_name
        self.repo_name = repo_name
        self.message = f"Repo {repo_name} does not exist in {org_name}."
        super().__init__(self.message)


class RepoCloneError(Exception):
    """Raised when there is a problem with the repository."""

    def __init__(self, org_name, repo_name, error):
        self.org_name = org_name
        self.repo_name = repo_name
        self.message = f"Repo {repo_name} could not be cloned from {org_name}.\n{error}"
        super().__init__(self.message)


class CustomDataValidationError(Exception):
    """Raised when there is a problem with the data in repository(OpenPecha-Data)"""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
