#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OSRFramework module for Google search engine queries.
"""

import argparse
import json
import os
import sys
import time

from http.cookiejar import LWPCookieJar
from urllib.request import Request, urlopen
from urllib.parse import quote_plus, urlparse, parse_qs

# Lazy import placeholder for BeautifulSoup
BeautifulSoup = None

# Google search URLs
url_home          = "http://www.google.%(tld)s/"
url_search        = "http://www.google.%(tld)s/search?hl=%(lang)s&q=%(query)s&btnG=Google+Search&inurl=https"
url_next_page     = "http://www.google.%(tld)s/search?hl=%(lang)s&q=%(query)s&start=%(start)d&inurl=https"
url_search_num    = "http://www.google.%(tld)s/search?hl=%(lang)s&q=%(query)s&num=%(num)d&btnG=Google+Search&inurl=https"
url_next_page_num = "http://www.google.%(tld)s/search?hl=%(lang)s&q=%(query)s&num=%(num)d&start=%(start)d&inurl=https"

# Cookie jar setup
home_folder = os.getenv('HOME') or os.getenv('USERHOME') or '.'
cookie_jar_path = os.path.join(home_folder, '.google-cookie')
cookie_jar = LWPCookieJar(cookie_jar_path)
try:
    cookie_jar.load()
except Exception:
    pass

def get_page(url):
    """Request a URL and return HTML response."""
    request = Request(url)
    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)')
    cookie_jar.add_cookie_header(request)
    response = urlopen(request)
    cookie_jar.extract_cookies(response, request)
    html = response.read()
    response.close()
    cookie_jar.save()
    return html

def filter_result(link):
    """Filter and clean a URL found in the search result."""
    try:
        o = urlparse(link, 'http')
        if o.netloc and 'google' not in o.netloc:
            return link

        if link.startswith('/url?'):
            link = parse_qs(o.query)['q'][0]
            o = urlparse(link, 'http')
            if o.netloc and 'google' not in o.netloc:
                return link
    except Exception:
        pass
    return None

def search(query, tld='com', lang='en', num=10, start=0, stop=None, pause=2.0, only_standard=False):
    """Search the given query on Google and yield found URLs."""
    global BeautifulSoup
    if BeautifulSoup is None:
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            from BeautifulSoup import BeautifulSoup  # fallback

    hashes = set()
    query = quote_plus(query)
    get_page(url_home % vars())

    if start:
        url = url_next_page_num % vars() if num != 10 else url_next_page % vars()
    else:
        url = url_search_num % vars() if num != 10 else url_search % vars()

    while not stop or start < stop:
        time.sleep(pause)
        html = get_page(url)
        soup = BeautifulSoup(html, "html.parser")

        anchors = soup.find(id='search').find_all('a')
        for a in anchors:
            if only_standard and (not a.parent or a.parent.name.lower() != "h3"):
                continue

            link = a.get('href')
            if not link:
                continue

            link = filter_result(link)
            if not link:
                continue

            h = hash(link)
            if h in hashes:
                continue
            hashes.add(h)
            yield link

        if not soup.find(id='nav'):
            break

        start += num
        url = url_next_page_num % vars() if num != 10 else url_next_page % vars()

def processSearch(query, tld='com', lang='en', num=10, start=0, stop=50, pause=2.0, only_standard=False):
    """Perform a search and return JSON-like result list."""
    uri_list = search(query, tld, lang, num, start, stop, pause, only_standard)
    results = []
    for uri in uri_list:
        results.append({
            "type": "i3visio.uri",
            "value": uri,
            "attributes": []
        })
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='A package that allows the execution of searches in Google.',
        prog='google.py',
        add_help=False
    )

    parser.add_argument("-q", "--query", metavar="<QUERY>", required=True, help="Query to be performed.")
    parser.add_argument("--tld", default="com", help="Top level domain to use [default: com]")
    parser.add_argument("--lang", default="en", help="Language to return results in [default: en]")
    parser.add_argument("--num", type=int, default=10, help="Results per page [default: 10]")
    parser.add_argument("--start", type=int, default=0, help="First result to retrieve [default: 0]")
    parser.add_argument("--stop", type=int, default=50, help="Last result to retrieve [default: 50]")
    parser.add_argument("--pause", type=float, default=2.0, help="Pause between requests [default: 2.0]")
    parser.add_argument("--all", dest="only_standard", action="store_false", default=True, help="Grab all links instead of only standard ones")

    group_about = parser.add_argument_group('About arguments', 'Additional info about the program.')
    group_about.add_argument('-h', '--help', action='help', help='Show help and exit.')
    group_about.add_argument('--version', action='version', version='%(prog)s 0.1.0', help='Show program version and exit.')

    args = parser.parse_args()

    print("Searching...")
    results = processSearch(
        args.query,
        tld=args.tld,
        lang=args.lang,
        num=args.num,
        start=args.start,
        stop=args.stop,
        pause=args.pause,
        only_standard=args.only_standard
    )
    print(json.dumps(results, indent=2))
