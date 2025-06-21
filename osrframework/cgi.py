"""
Shim for the removed cgi module in Python 3.13+
Provides just enough of cgi.parse_header for httpx to import.
"""

def parse_header(header_value):
    """
    Minimal stub:
      - returns the full header_value
      - params dict always empty
    """
    return header_value, {}
