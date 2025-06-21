#!/usr/bin/env python3
"""
OSRFramework upgrade script, using importlib.metadata for local version.
"""

import argparse
import datetime as dt
import json
import os
import sys
from subprocess import call

import osrframework
import osrframework.utils.general as general
import osrframework.utils.banner as banner
from osrframework.utils.updates import UpgradablePackage

# Python ≥3.8: importlib.metadata
try:
    from importlib.metadata import distribution, PackageNotFoundError
except ImportError:
    from importlib_metadata import distribution, PackageNotFoundError  # type: ignore


def get_parser(include_help=True) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="OSRFramework upgrade tool",
        prog="upgrade",
        epilog="See README.md for details.",
        add_help=include_help
    )
    grp = parser.add_argument_group("Options")
    grp.add_argument(
        "--only-check", action="store_true", default=False,
        help="Only check for updates, do not install"
    )
    grp.add_argument(
        "--use-development", action="store_true", default=False,
        help="Allow prerelease versions"
    )
    if include_help:
        grp.add_argument(
            "-h", "--help", action="help",
            help="Show this help message and exit"
        )
        grp.add_argument(
            "--version", action="version",
            version=f"%(prog)s {osrframework.__version__}",
            help="Show program version and exit"
        )
    return parser


def main(args=None):
    args = get_parser().parse_args(args)
    print(general.title(banner.text))

    print(general.info(f"""
  OSRFramework Upgrade Tool | © Yaiza Rubio & Félix Brezo (i3visio) 2014-2025

  This is free software with ABSOLUTELY NO WARRANTY.
"""))

    now = dt.datetime.now()
    print(f"{now}\tChecking local vs PyPI version…\n")

    try:
        dist = distribution("osrframework")
    except PackageNotFoundError:
        print(general.error("OSRFramework not installed!"))
        sys.exit(1)

    pkg = UpgradablePackage(dist)
    details = {
        "local_version":  pkg.current_version,
        "latest_version": pkg.fetch_latest()
    }
    print(general.emphasis(json.dumps(details, indent=2)) + "\n")

    now = dt.datetime.now()
    if pkg.is_upgradable():
        print(f"{now}\tAn update is available: {pkg.current_version} → {pkg.latest_version}\n")
        if not args.only_check:
            cmd = ["pip3", "install", "osrframework", "--upgrade"]
            if args.use_development:
                cmd.append("--pre")
            if os.geteuid() != 0 and sys.platform != "win32":
                cmd.append("--user")

            print(f"{now}\tRunning: {' '.join(cmd)}")
            status = call(cmd)
            if status != 0:
                print(general.error("Upgrade failed"))
                sys.exit(1)
            else:
                print(general.success(f"Successfully upgraded to {pkg.latest_version}"))
    else:
        print(f"{now}\tAlready up to date: {pkg.current_version}")


if __name__ == "__main__":
    main(sys.argv[1:])
