#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
#
#    Copyright 2015-2021 Félix Brezo and Yaiza Rubio
#
#    This program is part of OSRFramework. You can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

import argparse
import datetime as dt
import json
import os
import sys

import osrframework
import osrframework.utils.banner as banner
import osrframework.utils.platform_selection as platform_selection
import osrframework.utils.configuration as configuration
import osrframework.utils.general as general


def perform_search(platformNames=[], queries=[], exclude_platform_names=[]):
    platforms = platform_selection.get_platforms_by_name(platformNames, mode="searchfy", exclude_platform_names=exclude_platform_names)
    results = []
    for q in queries:
        for pla in platforms:
            entities = pla.get_info(query=q, mode="searchfy")
            if entities != "[]":
                results += json.loads(entities)
    return results


def get_parser():
    DEFAULT_VALUES = configuration.get_configuration_values_for("searchfy")
    try:
        exclude_list = [DEFAULT_VALUES["exclude_platforms"]]
    except Exception:
        exclude_list = []

    parser = argparse.ArgumentParser(
        description='searchfy - Performs queries on configured OSRFramework platforms.',
        prog='searchfy',
        epilog='See README.md or https://github.com/i3visio/osrframework for more info.',
        add_help=False,
        conflict_handler='resolve'
    )
    parser._optionals.title = "Input options (one required)"

    group_main = parser.add_mutually_exclusive_group(required=True)
    group_main.add_argument('--license', action='store_true', help='Shows the AGPLv3+ license and exits.')
    group_main.add_argument('-q', '--queries', metavar='<searches>', nargs='+', help='List of queries to search.')

    listAll = platform_selection.get_all_platform_names("searchfy")

    group_processing = parser.add_argument_group('Processing arguments', 'Search processing options.')
    group_processing.add_argument('-e', '--extension', nargs='+', choices=['csv', 'gml', 'json', 'ods', 'png', 'txt', 'xls', 'xlsx'],
                                  default=DEFAULT_VALUES.get("extension", ["csv"]),
                                  help='Output file format(s). Default: csv')
    group_processing.add_argument('-F', '--file_header', default=DEFAULT_VALUES.get("file_header", "profiles"),
                                  help='Prefix for generated filenames.')
    group_processing.add_argument('-o', '--output_folder', default=DEFAULT_VALUES.get("output_folder", "."),
                                  help='Output directory for results.')
    group_processing.add_argument('-p', '--platforms', nargs='+', choices=listAll,
                                  default=DEFAULT_VALUES.get("platforms", []),
                                  help='Platforms to search. Defaults to all.')
    group_processing.add_argument('-x', '--exclude', nargs='+', choices=listAll,
                                  default=exclude_list,
                                  help='Platforms to exclude from search.')
    group_processing.add_argument('-w', '--web_browser', action='store_true',
                                  help='Open results in default web browser.')

    group_about = parser.add_argument_group('About arguments', 'Metadata about this tool.')
    group_about.add_argument('-h', '--help', action='help', help='Show this help message and exit.')
    group_about.add_argument('--version', action='version',
                             version='[%(prog)s] OSRFramework ' + osrframework.__version__,
                             help='Show the program version and exit.')
    return parser


def main(params=None):
    parser = get_parser()
    args = parser.parse_args(params) if isinstance(params, list) else params

    print(general.title(banner.text))

    print(general.info(f"""
     Searchfy | Copyright (C) Yaiza Rubio & Félix Brezo (i3visio) 2014-2021

This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
are welcome to redistribute it under certain conditions. For additional info,
visit <{general.LICENSE_URL}>.
"""))

    if args.license:
        general.showLicense()
        return

    start_time = dt.datetime.now()
    print(f"{start_time}\tStarting search in different platform(s)... Relax!\n")
    print(general.emphasis("\tPress <Ctrl + C> to stop...\n"))

    try:
        results = perform_search(platformNames=args.platforms, queries=args.queries, exclude_platform_names=args.exclude)
    except KeyboardInterrupt:
        print(general.error("\n[!] Process manually stopped by the user. Workers terminated without providing any result.\n"))
        results = []

    if args.extension:
        if not os.path.exists(args.output_folder):
            os.makedirs(args.output_folder)

        file_header = os.path.join(args.output_folder, args.file_header)
        for ext in args.extension:
            general.export_usufy(results, ext, file_header)

    now = dt.datetime.now()
    print(f"\n{now}\tResults obtained:\n")
    print(general.success(general.osrf_to_text_export(results)))

    if args.web_browser:
        general.open_results_in_browser(results)

    print(f"\n{now}\tYou can find all the information collected in the following files:")
    for ext in args.extension:
        print("\t" + general.emphasis(file_header + "." + ext))

    end_time = dt.datetime.now()
    print(f"\n{end_time}\tFinishing execution...\n")
    print("Total time used:\t" + general.emphasis(str(end_time - start_time)))
    try:
        avg_time = (end_time - start_time).total_seconds() / len(args.platforms)
        print("Average seconds/query:\t" + general.emphasis(f"{avg_time:.2f} seconds\n"))
    except Exception:
        pass

    print(banner.footer)

    if params:
        return results


if __name__ == "__main__":
    main(sys.argv[1:])
