"""Global application constants and thresholds.

All magic numbers that carry domain meaning (thresholds, defaults, names,
versions) live here so they are not scattered across the codebase.
"""

APP_NAME_CN = "非线性动态模型参数辨识与校准软件"
APP_NAME_EN = "NDM-Calibrator"
APP_VERSION = "V1.0"
PROJECT_SCHEMA_VERSION = "1.0"
PROJECT_FILE_EXTENSION = ".ndmc"

# Default thresholds used by diagnostics. Centralised to avoid magic numbers.
CORRELATION_HIGH_THRESHOLD = 0.95
CORRELATION_WARNING_MESSAGE = "高度相关，参数可能难以独立辨识"
CONDITION_NUMBER_HIGH = 1e12
IDENTIFIABILITY_MAX_SINGULAR_VALUES = 12

# Residual diagnostics
RESIDUAL_ACF_MAX_LAG_DEFAULT = 20
RESIDUAL_ACF_MAX_LAG_LIMIT = 100
RESIDUAL_STRUCTURE_MESSAGE = "残差可能仍存在未建模动态结构"

# Uncertainty
BOOTSTRAP_DEFAULT_B = 100
BOOTSTRAP_MAX_B = 1000
BOOTSTRAP_CI_ALPHA = 0.05  # -> 95% interval
STABILITY_CV_HIGH_THRESHOLD = 0.5

# Identification defaults
DE_DEFAULT_POPULATION = 15
DE_DEFAULT_MUTATION = (0.5, 1.0)
DE_DEFAULT_RECOMBINATION = 0.7
DE_DEFAULT_MAX_ITERATIONS = 1000
MULTISTART_DEFAULT_STARTS = 10
NELDER_MEAD_MAX_ITERATIONS = 10000

# Solver defaults
ODE_DEFAULT_METHOD = "RK45"
ODE_DEFAULT_RTOL = 1e-6
ODE_DEFAULT_ATOL = 1e-9
ODE_MAX_STEP_DEFAULT = None

# Parameter bounds
PARAMETER_BOUND_DEFAULT_LOWER = 1e-6
PARAMETER_BOUND_DEFAULT_UPPER = 1e3
PARAMETER_INITIAL_DEFAULT = 1.0

# Status bar strings
STATUS_READY = "Ready"
STATUS_LOADING = "Loading..."
STATUS_RUNNING = "Running identification..."
STATUS_COMPLETED = "Completed"
STATUS_ERROR = "Error"
