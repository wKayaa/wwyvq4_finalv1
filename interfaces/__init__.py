"""
WWYVQ v2.1 Interfaces Package
Multiple interface implementations (CLI, Web, API)
"""

# Import only available interfaces
try:
    from .cli.main_cli import WWYVQCLIInterface
    __all__ = ['WWYVQCLIInterface']
except ImportError:
    __all__ = []

try:
    from .api.rest_api import WWYVQAPIInterface
    __all__.append('WWYVQAPIInterface')
except ImportError:
    pass