"""
fixQuotes.py - Replace smart/curly quotes and en dashes in set files with ASCII equivalents.

LackeyCCG renders cp1252 and UTF-8 smart quote characters as invisible. This script
normalises them to straight quotes and hyphens across all set files.

Usage:
    python fixQuotes.py           # fix all set files in ../starwars/sets/
    python fixQuotes.py --dry-run # report changes without writing
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SETS_FOLDER = os.path.join(SCRIPT_DIR, '..', 'starwars', 'sets')

# Applied in order; longer sequences must come before their constituent bytes.
REPLACEMENTS = [
    # UTF-8 smart quotes (must precede cp1252 single-byte replacements)
    (b'\xe2\x80\x9c', b'"'),   # left double quote
    (b'\xe2\x80\x9d', b'"'),   # right double quote
    (b'\xe2\x80\x98', b"'"),   # left single quote
    (b'\xe2\x80\x99', b"'"),   # right single quote / apostrophe
    (b'\xe2\x80\x93', b'-'),   # UTF-8 en dash
    (b'\xe2\x80\x94', b'-'),   # UTF-8 em dash
    # cp1252 smart quotes
    (b'\x93', b'"'),            # left double quote
    (b'\x94', b'"'),            # right double quote
    (b'\x91', b"'"),            # left single quote
    (b'\x92', b"'"),            # right single quote / apostrophe
    # cp1252 dashes
    (b'\x96', b'-'),            # en dash
    (b'\x97', b'-'),            # em dash
]

def fix_file(path, dry_run):
    with open(path, 'rb') as f:
        original = f.read()

    data = original
    for old, new in REPLACEMENTS:
        data = data.replace(old, new)

    if data == original:
        return 0

    count = sum(original.count(old) for old, _ in REPLACEMENTS)
    fname = os.path.basename(path)
    print(f'  {fname}: {count} replacement(s)')

    if not dry_run:
        with open(path, 'wb') as f:
            f.write(data)

    return count

def main():
    dry_run = '--dry-run' in sys.argv
    if dry_run:
        print('Dry run - no files will be changed.\n')

    total_files = 0
    total_replacements = 0

    for fname in sorted(os.listdir(SETS_FOLDER)):
        if not fname.endswith('.txt'):
            continue
        path = os.path.join(SETS_FOLDER, fname)
        n = fix_file(path, dry_run)
        if n:
            total_files += 1
            total_replacements += n

    action = 'Would fix' if dry_run else 'Fixed'
    print(f'\n{action} {total_replacements} character(s) in {total_files} file(s).')

if __name__ == '__main__':
    main()
