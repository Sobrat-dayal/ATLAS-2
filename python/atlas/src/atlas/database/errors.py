class DatabaseError(Exception):
    """Base class for all database exceptions."""
    pass

class DatabaseConfigurationError(DatabaseError):
    """Raised when database configuration is invalid."""
    pass

class DatabaseUnavailableError(DatabaseError):
    """Raised when the database is unreachable."""
    pass
