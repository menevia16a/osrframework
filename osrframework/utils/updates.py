"""
Utility functions for OSRFramework updates, using importlib.metadata.
"""

import xmlrpc.client

# Python ≥3.8 has importlib.metadata in stdlib
try:
    from importlib.metadata import distributions, Distribution
except ImportError:
    # fallback for older Pythons via the backport package
    from importlib_metadata import distributions, Distribution  # type: ignore

class UpgradablePackage:
    """
    Wraps a Distribution for update checking.
    """
    def __init__(self, dist: Distribution):
        self.name = dist.metadata.get("Name", dist.metadata.get("name", ""))
        self.current_version = dist.version
        self.latest_version = None

    def fetch_latest(self) -> str:
        """
        Fetch the latest version from PyPI.
        """
        import requests
        resp = requests.get(f"https://pypi.org/pypi/{self.name}/json", timeout=10)
        resp.raise_for_status()
        info = resp.json().get("info", {})
        self.latest_version = info.get("version", "")
        return self.latest_version

    def is_upgradable(self) -> bool:
        """
        Return True if a newer version exists on PyPI.
        """
        if self.latest_version is None:
            self.fetch_latest()
        from packaging.version import Version
        return Version(self.latest_version) > Version(self.current_version)

def check_for_updates() -> list[UpgradablePackage]:
    """
    Return a list of UpgradablePackage for all installed dists.
    """
    return [UpgradablePackage(dist) for dist in distributions()]
