"""
Version information for Task API
This file is automatically updated by the CI/CD pipeline
"""

__version__ = "1.0.0"

def get_version_info():
    """Return detailed version information"""
    return {
        "version": __version__,
        "api_version": "v1",
        "min_cli_version": "1.0.0"
    }