"""releaseManager.py - SWTCG-LACKEY Plugin Release Manager

Automates:
  1. Version date bumping across 4 manifest files
  2. updatelist.txt URL switching (playtest/release) and checksum regeneration

Usage:
  python releaseManager.py [--mode playtest|release] [--branch BRANCH]
                           [--date YYYY-MM-DD] [--skip-validate]
"""

import argparse
import io
import os
import re
import subprocess
import sys
from datetime import date, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGIN_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..', 'starwars'))
REPO_DIR   = os.path.normpath(os.path.join(SCRIPT_DIR, '..'))

RELEASE_BASE = 'https://lackey.swtcg.com/'
PLAYTEST_BASE_TEMPLATE = 'https://raw.githubusercontent.com/SWTCG/SWTCG-LACKEY/refs/heads/{branch}/'

ENCODING = 'cp1252'

# Patterns to detect and strip known URL bases
_RELEASE_PATTERN  = re.compile(r'^https://lackey\.swtcg\.com/')
_PLAYTEST_PATTERN = re.compile(r'^https://raw\.githubusercontent\.com/SWTCG/SWTCG-LACKEY/refs/heads/[^/]+/')


# ---------------------------------------------------------------------------
# LackeyCCG checksum
# ---------------------------------------------------------------------------

def _c_mod(x: int, m: int) -> int:
    """Truncated modulo matching C int % int behavior (result has sign of x)."""
    r = x % m
    if x < 0 and r != 0:
        r -= m
    return r


def lackey_checksum(filepath: str) -> int:
    """Compute LackeyCCG's file checksum (port of C/C# implementations)."""
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        cs = 0
        for byte in data:
            if byte != 10 and byte != 13:  # skip \n and \r
                signed_byte = byte - 256 if byte > 127 else byte
                cs += signed_byte
                cs = _c_mod(cs, 100_000_000)
        cs -= 1
        cs = _c_mod(cs, 100_000_000)
        return cs
    except Exception:
        return 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_current_branch() -> str:
    try:
        result = subprocess.check_output(
            ['git', 'branch', '--show-current'],
            cwd=REPO_DIR,
            stderr=subprocess.DEVNULL,
        )
        branch = result.decode().strip()
        return branch or 'master'
    except Exception:
        return 'master'


def local_path_to_repo_path(local_path: str) -> str:
    """Map LackeyCCG install-relative path to repo-relative path.

    LackeyCCG installs plugins at <lackey_root>/plugins/<plugin>/,
    but in the repo the plugin lives at <repo_root>/starwars/.
    Images/avatars/backgrounds live at <lackey_root>/images/, which
    mirrors <repo_root>/images/ directly.
    """
    if local_path.startswith('plugins/'):
        return local_path[len('plugins/'):]  # plugins/starwars/X → starwars/X
    return local_path  # images/..., sounds/... etc. — same relative path


def replace_url_base(url: str, new_base: str) -> str:
    """Strip the current URL base and replace with new_base."""
    for pattern in (_RELEASE_PATTERN, _PLAYTEST_PATTERN):
        m = pattern.match(url)
        if m:
            return new_base + url[m.end():]
    return url  # unrecognized base — leave unchanged


# ---------------------------------------------------------------------------
# Version bumping
# ---------------------------------------------------------------------------

def _replace_tag(content: str, tag: str, value: str) -> str:
    return re.sub(
        rf'<{tag}>[^<]*</{tag}>',
        f'<{tag}>{value}</{tag}>',
        content,
    )


def bump_versions(date_str: str, url_base: str, message: str | None = None) -> None:
    d = date.fromisoformat(date_str)
    fmt_yymmdd     = d.strftime('%y%m%d')              # 260314
    fmt_yymmdd_pre = (d - timedelta(days=1)).strftime('%y%m%d')  # 260313
    fmt_yyyy_mm_dd = d.strftime('%Y.%m.%d')            # 2026.03.14

    files = {
        'plugininfo.txt': ('pluginversion', fmt_yyyy_mm_dd),
        'version.txt':    ('lastupdateYYMMDD', fmt_yymmdd),
        'uninstall.txt':  ('dateYYMMDD', fmt_yymmdd_pre),
    }
    for filename, (tag, value) in files.items():
        path = os.path.join(PLUGIN_DIR, filename)
        with io.open(path, 'r', encoding=ENCODING) as f:
            content = f.read()
        content = _replace_tag(content, tag, value)
        if filename == 'version.txt':
            for url_tag in ('versionurl', 'updateurl'):
                m = re.search(rf'<{url_tag}>([^<]*)</{url_tag}>', content)
                if m:
                    content = _replace_tag(content, url_tag, replace_url_base(m.group(1), url_base))
            if message is not None:
                content = _replace_tag(content, 'message', message)
                print(f'  {filename:<20} {tag} -> {value}, message -> {message}')
            else:
                print(f'  {filename:<20} {tag} -> {value}')
        else:
            print(f'  {filename:<20} {tag} -> {value}')
        with io.open(path, 'w', encoding=ENCODING, newline='\n') as f:
            f.write(content)


# ---------------------------------------------------------------------------
# updatelist.txt rewrite
# ---------------------------------------------------------------------------

def rewrite_updatelist(date_str: str, url_base: str, out_path: str) -> None:
    d = date.fromisoformat(date_str)
    fmt_mm_dd_yy = d.strftime('%m-%d-%y')  # 03-14-26

    src_path = os.path.join(PLUGIN_DIR, 'updatelist.txt')
    with io.open(src_path, 'r', encoding=ENCODING) as f:
        lines = f.readlines()

    output = []
    in_card_images = False
    checksums_updated = 0
    checksums_skipped = 0

    for i, line in enumerate(lines):
        raw = line.rstrip('\n')

        # Line 1: "starwars\t<date>"
        if i == 0:
            parts = raw.split('\t')
            if len(parts) >= 2:
                parts[1] = fmt_mm_dd_yy
            output.append('\t'.join(parts) + '\n')
            continue

        # CardImageURLs: marker
        if raw.startswith('CardImageURLs:'):
            in_card_images = True
            output.append(line)
            continue

        parts = raw.split('\t')

        if in_card_images:
            # Card image entry: local_path\tURL\t (empty checksum)
            if len(parts) >= 2 and parts[1]:
                parts[1] = replace_url_base(parts[1], url_base)
            output.append('\t'.join(parts) + '\n')

        else:
            # Header entry: local_path\tURL\tchecksum
            if len(parts) >= 2 and parts[1]:
                parts[1] = replace_url_base(parts[1], url_base)

                # Recompute checksum from local file
                repo_path = local_path_to_repo_path(parts[0])
                abs_path  = os.path.normpath(os.path.join(REPO_DIR, repo_path))
                if os.path.isfile(abs_path):
                    cs = lackey_checksum(abs_path)
                    if len(parts) >= 3:
                        parts[2] = str(cs)
                    else:
                        parts.append(str(cs))
                    checksums_updated += 1
                else:
                    checksums_skipped += 1

            output.append('\t'.join(parts) + '\n')

    with io.open(out_path, 'w', encoding=ENCODING, newline='\n') as f:
        f.writelines(output)

    out_name = os.path.basename(out_path)
    print(f'  {out_name}: {checksums_updated} checksums updated, '
          f'{checksums_skipped} files missing locally')
    print(f'  {out_name} date -> {fmt_mm_dd_yy}')
    print(f'  Written to: {out_path}')


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def check_date_spacing(date_str: str) -> None:
    """Warn if new uninstall date is not strictly later than the current updatelist date."""
    new_uninstall = date.fromisoformat(date_str) - timedelta(days=1)
    src_path = os.path.join(PLUGIN_DIR, 'updatelist.txt')
    try:
        with io.open(src_path, 'r', encoding=ENCODING) as f:
            first_line = f.readline()
        parts = first_line.rstrip('\n').split('\t')
        if len(parts) >= 2 and parts[1]:
            current_date = date(
                2000 + int(parts[1][6:8]),
                int(parts[1][0:2]),
                int(parts[1][3:5]),
            )
            if new_uninstall <= current_date:
                print(f'WARNING: new uninstall date ({new_uninstall.strftime("%y%m%d")}) '
                      f'is not later than current updatelist date '
                      f'({current_date.strftime("%y%m%d")}). '
                      f'Clients may not re-download updated files.')
    except Exception:
        pass


def run_validation() -> None:
    print('\nRunning missingCardFinder.py...')
    subprocess.run([sys.executable, 'missingCardFinder.py'], cwd=SCRIPT_DIR)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description='SWTCG-LACKEY Plugin Release Manager',
    )
    parser.add_argument(
        '-t', '--type', choices=['playtest', 'release'], default='playtest',
        help='URL target type (default: playtest)',
    )
    parser.add_argument(
        '-b', '--branch', default=None,
        help='Git branch for playtest URLs (default: current branch)',
    )
    parser.add_argument(
        '-d', '--date', default=None,
        help='Release date YYYY-MM-DD (default: today)',
    )
    parser.add_argument(
        '-m', '--message', default=None,
        help='Update message written to version.txt (default: leave unchanged)',
    )
    parser.add_argument(
        '-o', '--output', default=None,
        help='Output path for the generated updatelist (default: starwars/updatelistNEW.txt)',
    )
    parser.add_argument(
        '-s', '--skip-validate', action='store_true',
        help='Skip running missingCardFinder.py',
    )
    args = parser.parse_args()

    date_str = args.date or date.today().isoformat()

    if args.type == 'playtest':
        branch   = args.branch or get_current_branch()
        url_base = PLAYTEST_BASE_TEMPLATE.format(branch=branch)
        print(f'Type:   playtest  (branch: {branch})')
    else:
        url_base = RELEASE_BASE
        print(f'Type:   release')

    out_path = args.output or os.path.join(PLUGIN_DIR, 'updatelist.txt')

    print(f'Date:   {date_str}')
    print()

    check_date_spacing(date_str)

    print('Bumping version dates...')
    bump_versions(date_str, url_base, args.message)

    print('\nGenerating updatelist...')
    rewrite_updatelist(date_str, url_base, out_path)

    if not args.skip_validate:
        run_validation()

    print('\nDone.')


if __name__ == '__main__':
    main()
