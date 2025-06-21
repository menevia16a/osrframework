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
import osrframework.utils.configuration as configuration
import osrframework.utils.general as general
import osrframework.utils.platform_selection as platform_selection
import osrframework.utils.benchmark as benchmark
import osrframework.utils.fuzz as fuzz

def get_parser():
    DEFAULT_VALUES = configuration.get_configuration_values_for("usufy")
    list_all = platform_selection.get_all_platform_names("usufy")

    parser = argparse.ArgumentParser(
        description="usufy - Checks for registered accounts with given nicknames.",
        prog="usufy",
        epilog="See README.md for usage details.",
        add_help=False,
        conflict_handler='resolve'
    )
    parser._optionals.title = "Input options (one required)"

    group_main = parser.add_mutually_exclusive_group(required=True)
    group_main.add_argument('--license', action='store_true', help='Show AGPLv3+ license and exit.')
    group_main.add_argument('-n', '--nicks', metavar='<nick>', nargs='+', help='Nicknames to be checked.')
    group_main.add_argument('-l', '--list', metavar='<file>', type=argparse.FileType('r'), help='File containing nicknames.')

    group_processing = parser.add_argument_group('Processing arguments', 'Configuration options.')
    group_processing.add_argument('-p', '--platforms', choices=list_all, nargs='+', default=DEFAULT_VALUES.get("platforms", []), help='Select platforms to check.')
    group_processing.add_argument('-t', '--tags', metavar='<tag>', nargs='+', default=DEFAULT_VALUES.get("tags", []), help='Select platform groups using tags.')
    group_processing.add_argument('-x', '--exclude', choices=list_all, nargs='+', default=DEFAULT_VALUES.get("exclude_platforms", []), help='Exclude these platforms.')
    group_processing.add_argument('-e', '--extension', choices=['csv', 'gml', 'json', 'ods', 'png', 'txt', 'xls', 'xlsx'], nargs='+', default=DEFAULT_VALUES.get("extension", ["csv"]), help='Output file formats.')
    group_processing.add_argument('-F', '--file_header', default=DEFAULT_VALUES.get("file_header", "profiles"), help='Prefix for output files.')
    group_processing.add_argument('-o', '--output_folder', default=DEFAULT_VALUES.get("output_folder", "./"), help='Directory to write results to.')
    group_processing.add_argument('-w', '--web_browser', action='store_true', help='Open results in web browser.')
    group_processing.add_argument('--fuzz', nargs='+', help='Fuzz nicknames using given strategy.')
    group_processing.add_argument('--fuzz-config', help='Configuration for fuzzing.')
    group_processing.add_argument('--avoid-processing', action='store_true', help='Skip post-processing.')
    group_processing.add_argument('--avoid-download', action='store_true', help='Skip content downloads.')
    group_processing.add_argument('--threads', type=int, default=5, help='Number of threads (default: 5).')
    group_processing.add_argument('--verbose', action='store_true', help='Verbose output.')
    group_processing.add_argument('--logfolder', default="./log", help='Folder to save platform-specific logs.')

    group_debug = parser.add_argument_group("Debug/Info arguments")
    group_debug.add_argument('--info', choices=['list_platforms', 'list_tags'], help='Show platform or tag info.')
    group_debug.add_argument('--benchmark', action='store_true', help='Run benchmark tests.')
    group_debug.add_argument('--show-tags', action='store_true', help='Show platforms grouped by tag.')

    group_about = parser.add_argument_group("About")
    group_about.add_argument('-h', '--help', action='help', help='Show help and exit.')
    group_about.add_argument('--version', action='version', version=f"%(prog)s {osrframework.__version__}", help='Show version and exit.')

    return parser

def process_nick_list(nicks, platforms, output_folder, avoidProcessing=False, avoidDownload=False, nThreads=5, verbosity=False, logFolder="./log"):
    # Dummy implementation placeholder
    from osrframework.utils.processor import process_nicks
    return process_nicks(nicks, platforms, output_folder, avoidProcessing, avoidDownload, nThreads, verbosity, logFolder)

def main(params=None):
    parser = get_parser()

    if params is None:
        args = parser.parse_args()
    elif isinstance(params, list):
        args = parser.parse_args(params)
    else:
        args = params

    print(general.title(banner.text))

    print(general.info(f"""
      Usufy | Copyright (C) Yaiza Rubio & Félix Brezo (i3visio)

This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions. See <{general.LICENSE_URL}> for details.
"""))

    if args.fuzz:
        return fuzz.fuzzUsufy(args.fuzz, args.fuzz_config)

    if args.license:
        general.showLicense()
        return

    list_platforms = platform_selection.get_platforms_by_name(
        platform_names=args.platforms,
        tags=args.tags,
        mode="usufy",
        exclude_platform_names=args.exclude
    )

    if args.info == 'list_platforms':
        for p in list_platforms:
            print(f"{p}: {p.tags}")
        return
    elif args.info == 'list_tags':
        tags = {}
        for p in list_platforms:
            for t in p.tags:
                tags[t] = tags.get(t, 0) + 1
        for tag, count in tags.items():
            print(f"{tag}: {count}")
        return
    elif args.benchmark:
        bench = benchmark.do_benchmark(platform_selection.get_all_platform_names("usufy"))
        print(json.dumps(bench, indent=2))
        return
    elif args.show_tags:
        tags = platform_selection.get_all_platform_names_by_tag("usufy")
        print(json.dumps(tags, indent=2))
        return

    start_time = dt.datetime.now()
    print(f"{start_time}\tStarting search across {len(list_platforms)} platform(s)...\n")
    print(general.emphasis("\tPress <Ctrl + C> to stop...\n"))

    try:
        nicks = args.nicks if args.nicks else args.list.read().splitlines()
        res = process_nick_list(nicks, list_platforms, args.output_folder,
                                avoidProcessing=args.avoid_processing,
                                avoidDownload=args.avoid_download,
                                nThreads=args.threads,
                                verbosity=args.verbose,
                                logFolder=args.logfolder)
    except KeyboardInterrupt:
        print(general.error("Process interrupted by user."))
        res = []

    if not os.path.exists(args.output_folder):
        os.makedirs(args.output_folder)
    file_header = os.path.join(args.output_folder, args.file_header)

    for ext in args.extension:
        general.export_usufy(res, ext, file_header)

    now = dt.datetime.now()
    print(f"\n{now}\tResults obtained:\n")
    print(general.success(general.osrf_to_text_export(res)))

    if args.web_browser:
        general.open_results_in_browser(res)

    print(f"\n{now}\tFiles generated:")
    for ext in args.extension:
        print("\t" + general.emphasis(f"{file_header}.{ext}"))

    end_time = dt.datetime.now()
    print(f"\n{end_time}\tExecution finished.\n")
    print("Total time:\t" + general.emphasis(str(end_time - start_time)))
    try:
        print("Avg seconds/platform:\t" + general.emphasis(
            str((end_time - start_time).total_seconds() / len(list_platforms))) + " sec\n")
    except ZeroDivisionError:
        pass

    print(banner.footer)

    if params:
        return res


if __name__ == "__main__":
    main(sys.argv[1:])
