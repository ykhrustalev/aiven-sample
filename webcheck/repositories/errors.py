class Error(Exception):
    pass


class UniqueConstraintError(Error):
    pass


class DoesNotExistError(Error):
    pass
