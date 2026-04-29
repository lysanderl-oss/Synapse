#!/usr/bin/env python3
"""
session-to-worklog.py
Extracts Claude Code session content → Obsidian work log + blog inbox
Run: py -3 scripts/session-to-worklog.py
Scheduled: daily 22:00 Dubai via Windows Task Scheduler
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Config ─────────────────────────────────────────────────────────────────
DUBAI_TZ = timezone(timedelta(hours=4))

# Multi-source scan: default ~/.claude/projects/ plus any extras from env.
# Priority: --sessions-dir CLI > SESSIONS_DIR env > CLAUDE_PROJECTS_DIRS env >
#           default ~/.claude/projects/ ; CLAUDE_PROJECTS_EXTRA_DIRS appended.
# Why multiple: 1) future-proof against multi-account setups (lysanderl@janusd.io
# vs lysanderl@janusd.com); 2) allow secondary install paths;
# 3) cloud runs (GitHub Actions) point SESSIONS_DIR at the synapse-sessions
# checkout (lysanderl-glitch/synapse-sessions/projects/).
# Set CLAUDE_PROJECTS_EXTRA_DIRS=path1;path2 (Windows) or path1:path2 (POSIX).
def _split_paths(value: str) -> list[str]:
    """Split a path-list env var on `;` (Windows) or `:` (POSIX).

    Tricky case: a single Windows path like ``C:/foo`` contains `:` but is one
    path. Heuristic: if `;` is present, split on `;`; otherwise if the value
    looks like a single drive-letter path (`X:/...`), don't split. Else `:`.
    """
    value = value.strip()
    if not value:
        return []
    if ";" in value:
        return [p.strip() for p in value.split(";") if p.strip()]
    # Single drive-letter path heuristic: 1 char + ':' + (\\ or /)
    if len(value) >= 3 and value[1] == ":" and value[2] in ("/", "\\"):
        # Check if there's a second drive-letter pattern further in (multi-path)
        # e.g. "C:/a:D:/b" — rare, but split conservatively only if we see `:X:`.
        if not re.search(r":[A-Za-z]:[\\/]", value):
            return [value]
    return [p.strip() for p in value.split(":") if p.strip()]


def _resolve_projects_bases(cli_dir: str | None = None) -> list[Path]:
    bases: list[Path] = []

    # Priority 1: explicit CLI flag
    if cli_dir:
        bases.append(Path(cli_dir))
    else:
        # Priority 2: SESSIONS_DIR (cloud) or CLAUDE_PROJECTS_DIRS (legacy)
        env_dirs = (
            os.environ.get("SESSIONS_DIR", "").strip()
            or os.environ.get("CLAUDE_PROJECTS_DIRS", "").strip()
        )
        if env_dirs:
            for p in _split_paths(env_dirs):
                bases.append(Path(p))
        else:
            # Priority 3: default to local Claude Code projects
            bases.append(Path.home() / ".claude" / "projects")

    # Always append CLAUDE_PROJECTS_EXTRA_DIRS (multi-account support)
    extras = os.environ.get("CLAUDE_PROJECTS_EXTRA_DIRS", "").strip()
    if extras:
        for p in _split_paths(extras):
            bases.append(Path(p))

    # De-duplicate by resolved path while preserving order
    seen: set = set()
    uniq: list[Path] = []
    for b in bases:
        try:
            key = str(b.resolve())
        except Exception:
            key = str(b)
        if key not in seen:
            seen.add(key)
            uniq.append(b)
    return uniq

# Module-level default (no CLI override). Will be replaced after argparse
# in __main__ if --sessions-dir is provided.
PROJECTS_BASES: list[Path] = _resolve_projects_bases()
# Backward-compat alias (some downstream tooling may import this)
PROJECTS_BASE = PROJECTS_BASES[0] if PROJECTS_BASES else (Path.home() / ".claude" / "projects")

VAULT_ROOT = Path(__file__).parent.parent / "obs"
WORKLOG_DIR = VAULT_ROOT / "00-daily-work"
INBOX_DIR = VAULT_ROOT / "04-content-pipeline" / "_inbox"
TRACKING_FILE = Path(__file__).parent / ".worklog-processed.json"
MAX_TRANSCRIPT_CHARS = 8000  # per session, before sending to API


def get_all_project_dirs() -> list[Path]:
    """Return all project directories (across all configured bases) that have JSONL files."""
    out: list[Path] = []
    for base in PROJECTS_BASES:
        if not base.exists():
            continue
        for d in base.iterdir():
            if d.is_dir() and list(d.glob("*.jsonl")):
                out.append(d)
    return out


# ── Helpers ─────────────────────────────────────────────────────────────────

def load_tracking() -> dict:
    if TRACKING_FILE.exists():
        return json.loads(TRACKING_FILE.read_text(encoding="utf-8"))
    return {}

def save_tracking(data: dict):
    TRACKING_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def today_str() -> str:
    return datetime.now(DUBAI_TZ).strftime("%Y-%m-%d")

def now_str() -> str:
    return datetime.now(DUBAI_TZ).strftime("%H:%M")

def is_today(ts_str: str) -> bool:
    try:
        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        local = ts.astimezone(DUBAI_TZ)
        return local.strftime("%Y-%m-%d") == today_str()
    except Exception:
        return False

# ── JSONL Parser ─────────────────────────────────────────────────────────────

def _ts_to_dubai_date(ts_str: str) -> str | None:
    """Parse an ISO timestamp string and return Dubai-local YYYY-MM-DD, or None."""
    if not ts_str or not isinstance(ts_str, str):
        return None
    try:
        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        return ts.astimezone(DUBAI_TZ).strftime("%Y-%m-%d")
    except Exception:
        return None


def parse_session(filepath: Path, target_date: str | None = None) -> dict | None:
    """Parse a JSONL session file, return structured data or None if empty/skip.

    If target_date is provided (YYYY-MM-DD, Dubai), only records whose own
    `timestamp` field falls on that date are collected. This makes long-running
    sessions that span midnight correctly attributable to each day, instead of
    relying on file mtime (which only tracks last write).
    """
    session_id = None
    user_messages = []
    assistant_texts = []
    agent_dispatches = []
    message_count = 0
    last_prompt = ""
    date_match_count = 0  # how many records on target_date

    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Get session ID from first record
                if session_id is None:
                    session_id = rec.get("sessionId")

                # Date gating: skip records outside target_date
                if target_date is not None:
                    rec_date = _ts_to_dubai_date(rec.get("timestamp", ""))
                    # Records without timestamp (e.g. system meta) — keep,
                    # they don't carry user-visible content anyway.
                    if rec_date is not None and rec_date != target_date:
                        continue
                    if rec_date == target_date:
                        date_match_count += 1

                rec_type = rec.get("type", "")
                msg = rec.get("message", {})

                # User messages (human text only, not tool results)
                if rec_type == "user":
                    content = msg.get("content", "")
                    if isinstance(content, str) and content.strip():
                        # Skip system reminders and hook outputs
                        if not content.startswith("<system-reminder") and len(content) < 2000:
                            user_messages.append(content.strip())

                # Assistant text blocks
                elif rec_type == "assistant":
                    content = msg.get("content", [])
                    if isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict):
                                if block.get("type") == "text":
                                    text = block.get("text", "").strip()
                                    if text and len(text) > 20:
                                        # Truncate long responses
                                        assistant_texts.append(text[:500] + ("..." if len(text) > 500 else ""))
                                elif block.get("type") == "tool_use" and block.get("name") == "Agent":
                                    desc = block.get("input", {}).get("description", "")
                                    if desc:
                                        agent_dispatches.append(desc)

                # Session stats
                elif rec_type == "system":
                    message_count = rec.get("messageCount", message_count)

                # Last prompt (session title hint)
                elif rec_type == "last-prompt":
                    last_prompt = rec.get("lastPrompt", "")

    except Exception as e:
        print(f"  Warning: failed to parse {filepath.name}: {e}")
        return None

    if not session_id or (not user_messages and not assistant_texts):
        return None

    # When target_date filtering is on, require at least one record on that day
    if target_date is not None and date_match_count == 0:
        return None

    return {
        "session_id": session_id,
        "file": filepath.name,
        "user_messages": user_messages[:10],  # cap at 10
        "assistant_texts": assistant_texts[:8],  # cap at 8
        "agent_dispatches": agent_dispatches[:5],
        "message_count": message_count or date_match_count,
        "last_prompt": last_prompt,
    }


def build_transcript(session: dict) -> str:
    """Build a readable transcript string from parsed session."""
    parts = []
    if session["last_prompt"]:
        parts.append(f"[会话起点] {session['last_prompt']}")
    parts.append(f"[消息数] {session['message_count']}")

    if session["agent_dispatches"]:
        parts.append("[派单执行]")
        for d in session["agent_dispatches"]:
            parts.append(f"  • {d}")

    if session["user_messages"]:
        parts.append("[用户输入摘要]")
        for m in session["user_messages"][:5]:
            parts.append(f"  > {m[:200]}")

    return "\n".join(parts)[:MAX_TRANSCRIPT_CHARS]


# ── Claude SDK / CLI Summarization ────────────────────────────────────────

MAX_SESSIONS_PER_DAY = 30  # cap to avoid Windows CLI arg length limit
DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")


def _call_claude_text(prompt: str, timeout: int = 180) -> str:
    """Send prompt to Claude, return text response.

    Cloud-friendly: prefers Anthropic SDK when ANTHROPIC_API_KEY is set
    (GitHub Actions has no `claude` CLI). Falls back to the local `claude`
    CLI subprocess for legacy local-machine runs.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if api_key:
        try:
            from anthropic import Anthropic
        except ImportError as e:
            raise RuntimeError(
                "anthropic SDK not installed but ANTHROPIC_API_KEY is set. "
                "Run: pip install 'anthropic>=0.40'"
            ) from e
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        if not response.content:
            return ""
        first = response.content[0]
        return getattr(first, "text", str(first)).strip()

    # Fallback: local `claude` CLI
    result = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "text"],
        capture_output=True,
        text=True,
        timeout=timeout,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI error: {result.stderr}")
    return result.stdout.strip()


def summarize_with_claude(transcripts: list[str]) -> dict:
    # Cap sessions to avoid oversized prompts
    if len(transcripts) > MAX_SESSIONS_PER_DAY:
        print(f"  [INFO] Capping {len(transcripts)} sessions to {MAX_SESSIONS_PER_DAY} most recent")
        transcripts = transcripts[-MAX_SESSIONS_PER_DAY:]

    combined = "\n\n---\n\n".join(f"[会话{i+1}]\n{t}" for i, t in enumerate(transcripts))

    prompt = f"""你是一个AI工作流分析师。分析以下Claude Code会话记录，提炼有价值的信息。

今日会话记录：
{combined}

请输出严格的JSON格式（不要有任何其他文字，只输出JSON），包含以下结构：
{{
  "work_summary": "今日主要工作的2-3句中文摘要",
  "problems_solved": [
    {{"problem": "问题描述", "solution": "解决方案"}}
  ],
  "key_decisions": ["关键决策或洞察1", "关键决策或洞察2"],
  "system_changes": ["系统变更描述"],
  "blog_candidates": [
    {{
      "title": "博客标题候选",
      "slug": "english-url-slug",
      "content_type": "B",
      "shareability": 4,
      "angle": "写作切入点一句话",
      "why_interesting": "为什么值得分享"
    }}
  ],
  "session_count": {len(transcripts)}
}}

规则：
- problems_solved 只包含真实遇到并解决的技术问题
- key_decisions 只包含真正有洞察价值的内容（不是普通操作步骤）
- blog_candidates：只包含 shareability >= 4 的内容（大多数日常操作不需要分享）
- system_changes 只包含对配置文件、脚本代码的实质性变更"""

    raw = _call_claude_text(prompt, timeout=180)
    # Clean up markdown code blocks if present
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
    raw = raw.strip()

    # Try strict parse first; on failure try extracting the largest balanced
    # JSON object (handles Claude's occasional preamble/postamble or smart-quote
    # escapes that break strict json.loads).
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        # Save raw response for debugging (visible in CI artifacts via cat)
        debug_path = TRACKING_FILE.parent / f".worklog-rawjson-{today_str()}.txt"
        try:
            debug_path.write_text(raw, encoding="utf-8")
            print(f"  [DEBUG] Raw Claude response saved: {debug_path}")
        except Exception:
            pass

        # Find first '{' and last '}' for naive balanced extraction
        first = raw.find("{")
        last = raw.rfind("}")
        candidates = []
        if first >= 0 and last > first:
            candidates.append(raw[first : last + 1])
        candidates.append(raw)

        for c in candidates:
            try:
                return json.loads(c)
            except json.JSONDecodeError:
                pass
            # Try replacing Chinese smart-quotes with plain space (they
            # commonly appear inside model-generated string values like
            # "记录"突触"传递" and break strict JSON parsing)
            sanitized = (c
                         .replace("“", " ")  # left double curly
                         .replace("”", " ")  # right double curly
                         .replace("‘", " ")  # left single curly
                         .replace("’", " ")) # right single curly
            try:
                return json.loads(sanitized)
            except json.JSONDecodeError:
                pass

        # Re-raise the original error with context
        raise json.JSONDecodeError(
            f"{e.msg} (raw response head: {raw[:200]!r})", e.doc, e.pos
        )


# ── Write Outputs ─────────────────────────────────────────────────────────

def write_worklog(summary: dict, date: str):
    WORKLOG_DIR.mkdir(parents=True, exist_ok=True)
    path = WORKLOG_DIR / f"{date}-work-log.md"

    problems = "\n".join(
        f"- {p['problem']} → {p['solution']}"
        for p in summary.get("problems_solved", [])
    ) or "- 无"

    decisions = "\n".join(
        f"- {d}" for d in summary.get("key_decisions", [])
    ) or "- 无"

    changes = "\n".join(
        f"- {c}" for c in summary.get("system_changes", [])
    ) or "- 无"

    candidates = "\n".join(
        f"- [ ] [{c.get('content_type','B')}类] {c['title']} （{c['shareability']}/5）"
        for c in summary.get("blog_candidates", [])
        if c.get("shareability", 0) >= 3
    ) or "- 无"

    if path.exists():
        # Append update section
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"\n\n## [自动更新 {now_str()}]\n")
            f.write(f"{summary.get('work_summary', '')}\n")
    else:
        content = f"""---
date: {date}
type: work-log
session_count: {summary.get('session_count', 0)}
auto_generated: true
---

## 今日主要工作
{summary.get('work_summary', '')}

## 遇到的问题
{problems}

## 关键决策/洞察
{decisions}

## 系统变更
{changes}

## 潜在文章素材
{candidates}
"""
        path.write_text(content, encoding="utf-8")

    print(f"  [OK] Work log written: {path}")
    return path


def write_inbox_notes(summary: dict, date: str):
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    created = []
    for c in summary.get("blog_candidates", []):
        if c.get("shareability", 0) < 4:
            continue
        slug = c.get("slug", "untitled").replace(" ", "-").lower()
        path = INBOX_DIR / f"{date}-{slug}.md"
        if path.exists():
            continue
        content = f"""---
date: {date}
type: insight
status: raw
content_type: {c.get('content_type', 'B')}
shareability: {c.get('shareability', 4)}/5
---

## 核心洞察
{c.get('title', '')}

## 写作切入点
{c.get('angle', '')}

## 为什么值得分享
{c.get('why_interesting', '')}

## 正文草稿
（待展开）
"""
        path.write_text(content, encoding="utf-8")
        created.append(path.name)

    if created:
        print(f"  [OK] Inbox notes created: {', '.join(created)}")
    return created


# ── Main ─────────────────────────────────────────────────────────────────────

def _run_auto_publish() -> None:
    """Invoke auto-publish-blog.py as a subprocess.

    Uses sys.executable so it works on Linux GHA (no `py` launcher) and
    Windows (without the py launcher dependency). Surfaces non-zero exits
    via sys.exit so the caller (GHA workflow) sees the failure.
    """
    print("\nRunning auto-publish pipeline...")
    publish_script = Path(__file__).parent / "auto-publish-blog.py"
    if not publish_script.exists():
        print(f"  [WARN] {publish_script} not found, skipping")
        return
    result = subprocess.run(
        [sys.executable, str(publish_script)],
        cwd=str(Path(__file__).parent.parent),
    )
    if result.returncode != 0:
        print(f"  [WARN] auto-publish-blog.py exited {result.returncode}")
        sys.exit(result.returncode)


def main(target_date: str = None, skip_publish: bool = False):
    date = target_date or today_str()
    print(f"Synapse WorkLog Extractor — {date}")

    existing_bases = [b for b in PROJECTS_BASES if b.exists()]
    if not existing_bases:
        print(f"ERROR: No Claude projects directories found. Searched: {PROJECTS_BASES}")
        sys.exit(1)

    all_project_dirs = get_all_project_dirs()
    print(f"Scanning {len(existing_bases)} base(s): "
          + ", ".join(str(b) for b in existing_bases)
          + f"  ({len(all_project_dirs)} projects)")

    tracking = load_tracking()
    sessions_data = []

    all_jsonl_files = []
    for proj_dir in all_project_dirs:
        all_jsonl_files.extend(proj_dir.glob("*.jsonl"))
    all_jsonl_files = sorted(all_jsonl_files)

    # Pre-filter by mtime as a cheap optimization: a file whose mtime is
    # strictly *before* target_date cannot contain records on target_date.
    # We do NOT reject files with mtime *after* target_date — those may be
    # long-running sessions that started on target_date and continued past
    # midnight. parse_session(target_date=...) does the precise filtering.
    target_dt = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=DUBAI_TZ)
    next_day_start_ts = (target_dt + timedelta(days=1)).timestamp()
    target_day_start_ts = target_dt.timestamp()

    for jsonl_file in all_jsonl_files:
        try:
            mtime_ts = jsonl_file.stat().st_mtime
        except OSError:
            continue
        # Skip files modified entirely before target_date — they can't have target-day records
        if mtime_ts < target_day_start_ts:
            continue

        session = parse_session(jsonl_file, target_date=date)
        if session is None:
            continue

        sid = session["session_id"]
        # Tracking is keyed by (session_id, date) so a long session that
        # spans days can be processed once per day it touched.
        track_key = f"{sid}::{date}" if sid else None
        if track_key and track_key in tracking:
            print(f"  Skip (already processed): {jsonl_file.name[:20]}... ({date})")
            continue

        print(f"  Parsing: {jsonl_file.name[:40]}... ({session.get('message_count', 0)} msgs on {date})")
        sessions_data.append(session)

    if not sessions_data:
        print("No new sessions found for today.")
        # Write minimal log if none exists
        log_path = WORKLOG_DIR / f"{date}-work-log.md"
        if not log_path.exists():
            WORKLOG_DIR.mkdir(parents=True, exist_ok=True)
            log_path.write_text(
                f"---\ndate: {date}\ntype: work-log\nauto_generated: true\n---\n\n今日无新会话记录\n",
                encoding="utf-8"
            )
            print(f"  [OK] Minimal log written: {log_path}")

        # Even with no fresh sessions, the inbox may carry over candidates
        # from previous runs that haven't been published yet (e.g. cloud
        # run created notes but publish step couldn't run). Drain the inbox.
        if not skip_publish:
            inbox_dir = INBOX_DIR
            pending = list(inbox_dir.glob("*.md")) if inbox_dir.exists() else []
            if pending:
                print(f"\nInbox has {len(pending)} pending note(s) — running auto-publish...")
                _run_auto_publish()
        return

    print(f"Processing {len(sessions_data)} session(s)...")
    transcripts = [build_transcript(s) for s in sessions_data]

    print("Calling claude CLI for summarization...")
    try:
        summary = summarize_with_claude(transcripts)
    except Exception as e:
        print(f"ERROR: API call failed: {e}")
        fallback = TRACKING_FILE.parent / f".worklog-fallback-{date}.txt"
        fallback.write_text("\n---\n".join(transcripts), encoding="utf-8")
        print(f"  Raw transcript saved to: {fallback}")
        sys.exit(1)

    write_worklog(summary, date)
    write_inbox_notes(summary, date)

    # Update tracking. Key = "session_id::date" so long-running sessions can be
    # processed once per day they touched (was previously keyed by session_id
    # only, which caused day-2 of a multi-day session to be silently skipped).
    for s in sessions_data:
        if s["session_id"]:
            tracking[f"{s['session_id']}::{date}"] = datetime.now(DUBAI_TZ).isoformat()
    save_tracking(tracking)

    # Auto-publish blog posts from inbox
    if sessions_data and not skip_publish:
        _run_auto_publish()

    print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Process sessions for this date (YYYY-MM-DD). Default: today.")
    parser.add_argument("--backfill", type=int, help="Process last N days (e.g. --backfill 7)")
    parser.add_argument("--no-publish", action="store_true", help="Skip blog publishing step")
    parser.add_argument(
        "--sessions-dir",
        help="Override the Claude projects base dir (default: $SESSIONS_DIR or ~/.claude/projects/). "
             "Used by GitHub Actions to point at the synapse-sessions checkout.",
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Diagnostic: print resolved paths and exit without calling Claude.")
    args = parser.parse_args()

    # Allow --sessions-dir to override the module-level PROJECTS_BASES
    if args.sessions_dir:
        PROJECTS_BASES = _resolve_projects_bases(cli_dir=args.sessions_dir)
        PROJECTS_BASE = PROJECTS_BASES[0] if PROJECTS_BASES else PROJECTS_BASE

    if args.dry_run:
        print(f"[dry-run] PROJECTS_BASES = {PROJECTS_BASES}")
        print(f"[dry-run] WORKLOG_DIR    = {WORKLOG_DIR}")
        print(f"[dry-run] INBOX_DIR      = {INBOX_DIR}")
        print(f"[dry-run] target date    = {args.date or today_str()}")
        sys.exit(0)

    if args.backfill:
        from datetime import date as date_cls, timedelta as td
        today = date_cls.today()
        for i in range(args.backfill, 0, -1):
            d = (today - td(days=i)).strftime("%Y-%m-%d")
            print(f"\n{'='*50}")
            print(f"Backfilling: {d}")
            print('='*50)
            main(target_date=d, skip_publish=args.no_publish)
    elif args.date:
        main(target_date=args.date, skip_publish=args.no_publish)
    else:
        main(skip_publish=args.no_publish)
