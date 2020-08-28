class Error(Exception):
    pass


class DoesNotExistError(Error):
    pass


class UniqueConstraintError(Error):
    pass
