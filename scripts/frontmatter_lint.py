#!/usr/bin/env python3
"""frontmatter_lint.py - Validate docs/public/*.md frontmatter against 12-field spec.

Ref: docs/public/methodology/content-frontmatter-spec.md
Mode: warning (default) until 2026-07-23; then --strict required for CI.
"""
import argparse
import sys
import re
import json
import subprocess
from pathlib import Path
from datetime import date

REQUIRED_ALWAYS = {
    'id', 'type', 'status', 'lang', 'version',
    'published_at', 'updated_at', 'author', 'review_by', 'audience'
}
TYPE_ENUM = {'core', 'living', 'reference', 'narrative', 'private'}
STATUS_ENUM = {'draft', 'review', 'published', 'deprecated'}
LANG_ENUM = {'en', 'zh'}
AUDIENCE_ENUM = {
    'team_partner', 'technical_builder', 'enterprise_decider',
    'content_strategist', 'knowledge_engineer', 'all'
}

ERROR_MODE_CUTOVER = date(2026, 7, 23)

SEMVER_RE = re.compile(r'^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$')
ISO_DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:?\d{2})?)?$')
GIT_HASH_RE = re.compile(r'^[0-9a-f]{7,40}$')


def parse_frontmatter(text):
    """Extract YAML frontmatter block from markdown text."""
    pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
    m = pattern.match(text)
    if not m:
        return None
    block = m.group(1)
    try:
        import yaml
        data = yaml.safe_load(block)
        return data if isinstance(data, dict) else {}
    except ImportError:
        return _simple_parse(block)
    except Exception:
        return _simple_parse(block)


def _simple_parse(block):
    """Fallback key-value parser (limited YAML support)."""
    data = {}
    current_list_key = None
    for line in block.splitlines():
        stripped = line.rstrip()
        if not stripped or stripped.lstrip().startswith('#'):
            continue
        # list continuation: "  - value"
        lead = len(line) - len(line.lstrip())
        if current_list_key and stripped.lstrip().startswith('- '):
            val = stripped.lstrip()[2:].strip().strip("'\"")
            data[current_list_key].append(val)
            continue
        else:
            current_list_key = None

        if ':' not in stripped:
            continue
        key, _, val = stripped.partition(':')
        key = key.strip()
        val = val.strip()
        if val == '':
            # Possibly start of a block list
            data[key] = []
            current_list_key = key
            continue
        if val.startswith('[') and val.endswith(']'):
            inner = val[1:-1]
            parts = [v.strip().strip("'\"") for v in inner.split(',') if v.strip()]
            data[key] = parts
        else:
            data[key] = val.strip("'\"")
    return data


def _is_list_of_str(v):
    return isinstance(v, list) and all(isinstance(x, str) for x in v)


def validate(fm, filepath):
    """Return list of (severity, message) tuples."""
    issues = []
    if fm is None:
        issues.append(('error', 'no frontmatter block found'))
        return issues
    if not isinstance(fm, dict):
        issues.append(('error', f'frontmatter is not a mapping (got {type(fm).__name__})'))
        return issues

    # Required-always fields
    for field in REQUIRED_ALWAYS:
        if field not in fm or fm[field] in (None, '', []):
            issues.append(('error', f'missing required field: {field}'))

    # Type
    t = fm.get('type')
    if t is not None and t not in TYPE_ENUM:
        issues.append(('error', f'invalid type: {t!r} (allowed: {sorted(TYPE_ENUM)})'))

    # Status
    s = fm.get('status')
    if s is not None and s not in STATUS_ENUM:
        issues.append(('error', f'invalid status: {s!r} (allowed: {sorted(STATUS_ENUM)})'))

    # Lang
    lang = fm.get('lang')
    if lang is not None and lang not in LANG_ENUM:
        issues.append(('error', f'invalid lang: {lang!r} (allowed: {sorted(LANG_ENUM)})'))

    # Version (SemVer)
    v = fm.get('version')
    if isinstance(v, str) and not SEMVER_RE.match(v):
        issues.append(('warning', f'version {v!r} is not SemVer (X.Y.Z)'))

    # synapse_version (optional but if present check SemVer)
    sv = fm.get('synapse_version')
    if sv is not None and isinstance(sv, str) and not SEMVER_RE.match(sv):
        issues.append(('warning', f'synapse_version {sv!r} is not SemVer'))

    # source_commit (optional unless syncing; validate if present)
    sc = fm.get('source_commit')
    if sc is not None and isinstance(sc, str) and not GIT_HASH_RE.match(sc):
        issues.append(('warning', f'source_commit {sc!r} does not look like a git hash'))

    # Dates
    for df in ('published_at', 'updated_at', 'stale_after'):
        dv = fm.get(df)
        if dv is None:
            continue
        dv_str = str(dv)
        if not ISO_DATE_RE.match(dv_str):
            issues.append(('warning', f'{df} {dv_str!r} is not ISO date (YYYY-MM-DD[THH:MM...])'))

    # translation_of (optional string)
    to = fm.get('translation_of')
    if to is not None and not isinstance(to, str):
        issues.append(('warning', f'translation_of should be string, got {type(to).__name__}'))

    # Author: string or list of strings
    au = fm.get('author')
    if au is not None and not (isinstance(au, str) or _is_list_of_str(au)):
        issues.append(('warning', 'author should be string or list of strings'))

    # review_by: array
    rb = fm.get('review_by')
    if rb is not None and not _is_list_of_str(rb):
        issues.append(('warning', 'review_by should be list of strings'))

    # Audience: subset of AUDIENCE_ENUM
    aud = fm.get('audience')
    if aud is not None:
        if isinstance(aud, str):
            aud_list = [aud]
            issues.append(('warning', 'audience should be a list, got string'))
        elif isinstance(aud, list):
            aud_list = aud
        else:
            aud_list = []
            issues.append(('warning', f'audience has unexpected type {type(aud).__name__}'))
        unknown = set(aud_list) - AUDIENCE_ENUM
        if unknown:
            issues.append(('warning', f'unknown audience values: {sorted(unknown)}'))

    # Conditional stale_after for core/reference
    if fm.get('type') in {'core', 'reference'} and not fm.get('stale_after'):
        issues.append(('error', f'type={fm.get("type")!r} requires stale_after'))

    # id must be kebab-case string
    id_v = fm.get('id')
    if isinstance(id_v, str) and id_v and not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', id_v):
        issues.append(('warning', f'id {id_v!r} is not kebab-case'))

    return issues


def get_staged_md_files():
    """Return list of obs/*.md files that are staged (Added or Modified).

    Existing OBS docs (236, 1.3% compliance baseline) are exempt — strict-staged
    only checks newly-added or modified files in the current commit.
    """
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=AM'],
            capture_output=True, text=True, check=False
        )
        if result.returncode != 0:
            return []
        files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
        # Only obs/*.md files (use forward-slash since git always uses /)
        return [f for f in files if f.endswith('.md') and f.startswith('obs/')]
    except Exception:
        return []


def run_strict_staged():
    """Strict mode against staged obs/*.md files only.

    Returns exit code 0 if all staged files pass, 1 otherwise.
    """
    staged = get_staged_md_files()

    if not staged:
        print('[frontmatter_lint] no staged obs/*.md files - skip')
        return 0

    print(f'[frontmatter_lint] strict-staged check on {len(staged)} file(s):')
    for f in staged:
        print(f'  - {f}')

    error_count = 0
    findings = []
    for fp in staged:
        path = Path(fp)
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding='utf-8', errors='replace')
        except Exception as e:
            error_count += 1
            findings.append((fp, 'error', f'cannot read: {e}'))
            continue
        fm = parse_frontmatter(text)
        issues = validate(fm, fp)
        for sev, msg in issues:
            if sev == 'error':
                error_count += 1
            findings.append((fp, sev, msg))

    print('-' * 60)
    for fp, sev, msg in findings:
        print(f'[{sev.upper()}] {fp}: {msg}')
    if error_count > 0:
        print('-' * 60)
        print(f'[frontmatter_lint] STRICT-STAGED FAILED: {error_count} error(s)')
        print('[frontmatter_lint] Fix: add 12-field frontmatter per')
        print('                   docs/public/methodology/content-frontmatter-spec.md')
        print('                   or unstage the file (git reset HEAD <file>).')
        return 1
    print('[frontmatter_lint] strict-staged OK')
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--path', default='docs/public', help='Directory to scan (default: docs/public)')
    ap.add_argument('--strict', action='store_true', help='Treat errors as exit 1')
    ap.add_argument('--strict-staged', action='store_true',
                    help='Strict mode but only against git-staged obs/*.md files (for pre-commit hook)')
    ap.add_argument('--json', action='store_true', help='JSON output')
    args = ap.parse_args()

    if args.strict_staged:
        sys.exit(run_strict_staged())

    strict = args.strict or date.today() >= ERROR_MODE_CUTOVER
    root = Path(args.path)
    if not root.exists():
        print(f'ERROR: path not found: {root}', file=sys.stderr)
        sys.exit(2)

    report = {
        'mode': 'strict' if strict else 'warning',
        'cutover': ERROR_MODE_CUTOVER.isoformat(),
        'scanned': 0, 'passed': 0, 'warnings': 0, 'errors': 0,
        'findings': []
    }

    cwd = Path.cwd()
    for md in sorted(root.rglob('*.md')):
        report['scanned'] += 1
        try:
            text = md.read_text(encoding='utf-8', errors='replace')
        except Exception as e:
            report['errors'] += 1
            report['findings'].append({
                'file': str(md), 'severity': 'error',
                'message': f'cannot read file: {e}'
            })
            continue
        fm = parse_frontmatter(text)
        issues = validate(fm, str(md))
        if not issues:
            report['passed'] += 1
            continue
        has_error = any(sev == 'error' for sev, _ in issues)
        if has_error:
            report['errors'] += 1
        else:
            report['warnings'] += 1
        try:
            rel = md.relative_to(cwd)
            fpath = str(rel)
        except ValueError:
            fpath = str(md)
        for sev, msg in issues:
            report['findings'].append({
                'file': fpath, 'severity': sev, 'message': msg
            })

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Scanned: {report['scanned']} | Passed: {report['passed']} | "
              f"Warnings: {report['warnings']} | Errors: {report['errors']}")
        print(f"Mode: {'STRICT' if strict else f'WARNING (until {ERROR_MODE_CUTOVER.isoformat()})'}")
        print('-' * 70)
        for f in report['findings']:
            print(f"[{f['severity'].upper()}] {f['file']}: {f['message']}")

    if strict and report['errors'] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
