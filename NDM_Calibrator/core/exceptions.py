"""Domain-specific exception types for NDM-Calibrator.

UI layer catches these and shows friendly messages instead of tracebacks.
"""


class NDMCError(Exception):
    """Base class for all domain errors in this application."""


class ProjectError(NDMCError):
    """Raised when a project cannot be created/saved/opened."""


class CorruptedProjectError(ProjectError):
    """Raised when a project file is damaged or unreadable."""


class DataError(NDMCError):
    """Raised when imported data is invalid or cannot be parsed."""


class DataValidationError(DataError):
    """Raised when a data frame fails a validation rule."""


class ModelError(NDMCError):
    """Raised for invalid model definitions or expressions."""


class ModelParseError(ModelError):
    """Raised when a user expression cannot be parsed safely."""


class ParameterError(NDMCError):
    """Raised for invalid parameter configurations."""


class SimulationError(NDMCError):
    """Raised when numerical integration or simulation fails."""


class OptimizationError(NDMCError):
    """Raised when an identification run fails."""
