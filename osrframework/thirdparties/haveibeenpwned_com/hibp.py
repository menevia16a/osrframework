################################################################################
#
#    Copyright 2015-2020 Félix Brezo and Yaiza Rubio
#    Migrated to cloudscraper by Veilbreaker (2025)
#
################################################################################

import argparse
import json
import os
import time
import requests
import cloudscraper

import osrframework.utils.general as general
import osrframework.utils.configuration as configuration

def check_if_email_was_hacked(email=None, sleep_seconds=1, api_key=None):
    """Checks if `email` appears in any HIBP breach.
    Uses cloudscraper under the hood to bypass Cloudflare.
    """

    # rate-limit courtesy pause
    time.sleep(sleep_seconds)

    print("\t[*] Initializing Cloudflare bypass…")
    ua = f"osrframework/{configuration.get_configuration_values_for('version')}"

    if api_key is None:
        api_key = input("Insert the HIBP API KEY here:\t")

    headers = {
        'hibp-api-key': api_key,
        'User-Agent':   ua
    }

    # build a CloudScraper session
    scraper = cloudscraper.create_scraper(browser={'custom': ua})

    api_url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"

    # small pause before the API call
    time.sleep(sleep_seconds)

    try:
        resp = scraper.get(api_url, headers=headers, timeout=15)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"\t[*] Unauthorized or error: {e}")
        return []
    except Exception as e:
        print(f"\t[*] Request failed: {e}")
        return []

    # parse response
    try:
        jsonData = resp.json()
    except ValueError:
        return []

    leaks = []
    for breach in jsonData:
        entry = {
            "value":       f"(HIBP) {breach.get('Name')} - {email}",
            "type":        "com.i3visio.Profile",
            "attributes": [
                {"type":"com.i3visio.Platform.Leaked", "value": breach.get("Name"),      "attributes":[]},
                {"type":"@source",                 "value":"haveibeenpwned.com",         "attributes":[]},
                {"type":"@source_uri",             "value":api_url,                      "attributes":[]},
                {"type":"@pwn_count",              "value": breach.get("PwnCount"),      "attributes":[]},
                {"type":"com.i3visio.Date.Known",  "value": breach.get("AddedDate"),     "attributes":[]},
                {"type":"com.i3visio.Date.Breached","value": breach.get("BreachDate"),   "attributes":[]},
                {"type":"@description",            "value": breach.get("Description"),   "attributes":[]},
            ]
        }
        # merge in any expansions from email heuristics
        entry["attributes"] += general.expand_entities_from_email(email)
        leaks.append(entry)

    return leaks


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Check if an email has been breached on haveibeenpwned.com',
        prog='hibp.py'
    )
    parser.add_argument('-q','--query', metavar='<email>', required=True,
                        help='email address to check')
    parser.add_argument('--version', action='version',
                        version=f"%(prog)s {configuration.get_configuration_values_for('version')}")
    args = parser.parse_args()

    results = check_if_email_was_hacked(email=args.query)
    print(f"Results for {args.query}:\n{json.dumps(results, indent=2)}")
