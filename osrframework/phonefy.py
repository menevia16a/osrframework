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

def process_phone_list(platformNames=[], numbers=[], exclude_platform_names=[]):
    platforms = platform_selection.get_platforms_by_name(
        platformNames,
        mode="phonefy",
        exclude_platform_names=exclude_platform_names
    )
    results = []
    for num in numbers:
        for pla in platforms:
            entities = pla.get_info(query=num, mode="phonefy")
            if entities != {}:
                results += json.loads(entities)
    return results

def get_parser():
    DEFAULT_VALUES = configuration.get_configuration_values_for("phonefy")
    exclude_list = DEFAULT_VALUES.get("exclude_domains", [])

    parser = argparse.ArgumentParser(
        description='phonefy - Checks a series of phone numbers against known spam/malicious lists.',
        prog='phonefy',
        epilog='Check the README.md or <http://twitter.com/i3visio> for more info.',
        add_help=False,
        conflict_handler='resolve'
    )
    parser._optionals.title = "Input options (one required)"

    group_main_options = parser.add_mutually_exclusive_group(required=True)
    group_main_options.add_argument('--license', action='store_true', help='Shows the AGPLv3+ license and exits.')
    group_main_options.add_argument('-n', '--numbers', metavar='<phones>', nargs='+', help='Phone numbers to check.')

    list_all = platform_selection.get_all_platform_names("phonefy")

    group_processing = parser.add_argument_group('Processing arguments')
    group_processing.add_argument('-e', '--extension', metavar='<ext>', nargs='+', choices=['csv', 'gml', 'json', 'ods', 'png', 'txt', 'xls', 'xlsx'], default=DEFAULT_VALUES.get("extension", ["csv"]), help='Output file formats. Default: csv.')
    group_processing.add_argument('-o', '--output_folder', metavar='<path>', default=DEFAULT_VALUES.get("output_folder", "./"), help='Where output files will be stored.')
    group_processing.add_argument('-p', '--platforms', metavar='<platform>', choices=list_all, nargs='+', default=DEFAULT_VALUES.get("platforms", ["all"]), help='Specify platforms to search.')
    group_processing.add_argument('-F', '--file_header', metavar='<filename_prefix>', default=DEFAULT_VALUES.get("file_header", "profiles"), help='Prefix for output filenames.')
    group_processing.add_argument('--quiet', action='store_true', help='Suppress output to terminal.')
    group_processing.add_argument('-w', '--web_browser', action='store_true', help='Open result links in web browser.')
    group_processing.add_argument('-x', '--exclude', metavar='<platform>', choices=list_all, nargs='+', default=exclude_list, help='Platforms to exclude from processing.')

    group_about = parser.add_argument_group('About arguments')
    group_about.add_argument('-h', '--help', action='help', help='Show this help message and exit.')
    group_about.add_argument('--version', action='version', version='[%(prog)s] OSRFramework ' + osrframework.__version__, help='Show program version and exit.')

    return parser

def main(params=None):
    parser = get_parser()
    args = parser.parse_args(params) if isinstance(params, list) or params is None else params

    results = []

    if not args.quiet:
        print(general.title(banner.text))

    print(general.info(f"""
     Phonefy | Copyright (C) Yaiza Rubio & Félix Brezo (i3visio) 2014-2021

This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
are welcome to redistribute it under certain conditions. For additional info,
visit <{general.LICENSE_URL}>.
"""))

    if args.license:
        general.showLicense()
        return

    start_time = dt.datetime.now()
    print(f"\n{start_time}\tStarting search in different platform(s)... Relax!\n")
    print(general.emphasis("\tPress <Ctrl + C> to stop...\n"))

    try:
        results = process_phone_list(
            platformNames=args.platforms,
            numbers=args.numbers,
            exclude_platform_names=args.exclude
        )
    except KeyboardInterrupt:
        print(general.error("\n[!] Process manually stopped by the user. Workers terminated without providing any result.\n"))

    file_header = os.path.join(args.output_folder, args.file_header)

    if args.output_folder:
        os.makedirs(args.output_folder, exist_ok=True)
        for ext in args.extension:
            general.export_usufy(results, ext, file_header)

    if not args.quiet:
        now = dt.datetime.now()
        print(f"\n{now}\tResults obtained:\n")
        print(general.success(general.osrf_to_text_export(results)))

        if args.web_browser:
            general.open_results_in_browser(results)

        print(f"\n{now}\tYou can find all the information collected in the following files:")
        for ext in args.extension:
            print("\t" + general.emphasis(f"{file_header}.{ext}"))

        end_time = dt.datetime.now()
        print(f"\n{end_time}\tFinishing execution...\n")
        print("Total time consumed:\t" + general.emphasis(str(end_time - start_time)) + "\n")
        print(banner.footer)

    return results

if __name__ == "__main__":
    main(sys.argv[1:])
