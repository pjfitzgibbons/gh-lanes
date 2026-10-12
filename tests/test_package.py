"""The package installs and imports from the src layout.

This is the check CI needs before any module exists: a broken build backend or
module-name mapping fails here instead of as a confusing ImportError later.
"""

import ghplan


def test_package_reports_its_installed_version():
    assert ghplan.__version__ == "0.0.0"
