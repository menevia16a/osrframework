################################################################################
#
#    Copyright 2015-2020 Félix Brezo and Yaiza Rubio
#    Migrated to cloudscraper by Veilbreaker (2025)
#
################################################################################

import argparse
import json
import os
import re
import time

import cloudscraper
import requests

import osrframework.utils.general as general


def check_reverse_whois(query=None, sleep_seconds=1):
    """Method that checks if the given string is linked to a domain.

    Args:
        query (str): query to verify.
        sleep_seconds (int): Number of seconds to wait between calls.

    Returns:
        A python structure for the json received. If nothing was found, it will
        return an empty list.
    """
    results = []

    # Sleeping just a little bit
    time.sleep(sleep_seconds)

    target_url = f"https://viewdns.info/reversewhois/?q={query}"

    # Use CloudScraper to bypass Cloudflare
    scraper = cloudscraper.create_scraper()
    try:
        resp = scraper.get(target_url, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(general.warning(f"ERROR: Could not reach {target_url}: {e}"))
        return []

    domains_found = re.findall(r"</td></tr><tr><td>([^<]+)</td>", resp.text)

    for domain in domains_found:
        new = {
            "value": f"(ViewDNS.info) {domain} - {query}",
            "type": "com.i3visio.Profile",
            "attributes": [
                {"type": "@source",      "value": "viewdns.info", "attributes": []},
                {"type": "@source_uri",  "value": target_url,     "attributes": []},
                {"type": "com.i3visio.Platform", "value": "ViewDNS.info", "attributes": []},
                {"type": "com.i3visio.Domain",   "value": domain,            "attributes": []},
                {"type": "com.i3visio.Email",    "value": query,             "attributes": []},
            ]
        }
        results.append(new)

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Reverse WHOIS via viewdns.info',
        prog='viewdns.py', epilog="", add_help=False
    )
    parser.add_argument('-q', '--query', metavar='<text>', required=True,
                        help='query to be performed to viewdns.info.')
    group_about = parser.add_argument_group('About arguments')
    group_about.add_argument('-h', '--help', action='help', help='show this help and exit')
    group_about.add_argument('--version', action='version', version='%(prog)s 0.1.0',
                             help='show the program version and exit')

    args = parser.parse_args()
    result = check_reverse_whois(query=args.query)
    print(f"Results found for {args.query}:\n")
    print(json.dumps(result, indent=2))
