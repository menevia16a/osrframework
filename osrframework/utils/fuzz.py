import datetime as dt
import re

"""
Advanced username fuzzing utilities for OSRFramework.
Generates a rich set of permutations for given nicknames, including:
- Case variations (lower, upper, title)
- Separator insertions (".", "_", "-", none)
- Numeric suffixes (1-10, recent years)
- Common word suffixes (dev, test, admin)
- Basic leet substitutions (a->4, e->3, i->1, o->0, s->5, t->7)
- Custom patterns from a configuration file, if provided
"""

SEPARATOR_CHARS = ['', '.', '_', '-']
COMMON_WORDS = ['dev', 'test', 'admin']
LEET_MAP = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7'}


def load_custom_patterns(config_path):
    """
    Load custom patterns from a file. Each line should contain a pattern
    with '<USERNAME>' placeholder.
    """
    patterns = []
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and '<USERNAME>' in line:
                    patterns.append(line)
    except Exception:
        # Silently ignore load errors
        pass
    return patterns


def generate_leet_variations(nick):
    """
    Generate basic leet variations by substituting each letter once.
    """
    variations = set()
    for i, ch in enumerate(nick.lower()):
        if ch in LEET_MAP:
            variant = nick[:i] + LEET_MAP[ch] + nick[i+1:]
            variations.add(variant)
    return list(variations)


def generate_case_variations(base):
    """
    Return lower, upper, and title-case versions of the base string.
    """
    return {base.lower(), base.upper(), base.title()}


def fuzz_usernames(nicks, config_path=None):
    """
    Given an iterable of nicks, return a dict mapping each nick to a list of
    fuzzed username permutations.

    Args:
        nicks (list[str]): List of base usernames.
        config_path (str): Optional path to custom pattern file.

    Returns:
        dict[str, list[str]]: Mapping base nick -> fuzz variations.
    """
    results = {}
    now = dt.datetime.now().year
    years = [str(y) for y in range(now, now-6, -1)]  # this year and 5 prior

    # Load custom patterns if available
    custom_patterns = load_custom_patterns(config_path) if config_path else []

    for nick in nicks:
        seen = set()
        variations = []

        # Base case + case variations
        for case_nick in generate_case_variations(nick):
            seen.add(case_nick)
            variations.append(case_nick)

        # Separator + number and word suffixes
        for sep in SEPARATOR_CHARS:
            for num in range(1, 11):
                candidate = f"{nick}{sep}{num}"
                if candidate not in seen:
                    seen.add(candidate)
                    variations.append(candidate)
            for year in years:
                candidate = f"{nick}{sep}{year}"
                if candidate not in seen:
                    seen.add(candidate)
                    variations.append(candidate)
            for word in COMMON_WORDS:
                candidate = f"{nick}{sep}{word}"
                if candidate not in seen:
                    seen.add(candidate)
                    variations.append(candidate)

        # Leet substitutions
        for leet in generate_leet_variations(nick):
            if leet not in seen:
                seen.add(leet)
                variations.append(leet)

        # Apply custom patterns
        for pat in custom_patterns:
            candidate = pat.replace('<USERNAME>', nick)
            if candidate not in seen:
                seen.add(candidate)
                variations.append(candidate)

        results[nick] = variations
    return results


# For backward compatibility
fuzzUsufy = fuzz_usernames
