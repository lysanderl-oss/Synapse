"""
Synapse Session Watcher — 本机 .claude/projects 增量同步到 synapse-sessions 私有 repo

OBJ-BLOG-PIPELINE-CLOUD Stage 1.2

设计：
- once 模式：跑一次同步立即退出（适合 Windows Task Scheduler 触发）
- daemon 模式：长驻轮询（适合 Service 化部署）
- dry-run 模式：仅打印将要 push 的文件，不实际 push

双账号支持：通过环境变量 CLAUDE_PROJECTS_EXTRA_DIRS 可加额外目录（: 或 ; 分隔）

Usage:
    python sessions_watcher.py --once              # 一次性同步
    python sessions_watcher.py --daemon            # 长驻（每 5 分钟轮询）
    python sessions_watcher.py --once --dry-run    # 测试

Environment:
    CLAUDE_PROJECTS_DIRS: 默认 ~/.claude/projects
    CLAUDE_PROJECTS_EXTRA_DIRS: 额外目录（: 或 ; 分隔）
    SESSIONS_REPO_PATH: synapse-sessions repo 本地路径（默认 ~/synapse-sessions）
    POLL_INTERVAL_SECONDS: daemon 模式轮询间隔（默认 300 秒 = 5 分钟）
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone

try:
    import requests  # type: ignore
except ImportError:
    requests = None  # type: ignore

DEFAULT_POLL_INTERVAL = 300  # 5 分钟
STATE_FILE = Path(__file__).parent / ".sessions_watcher_state.json"
FAILURE_ALERT_THRESHOLD = 3  # 连续失败 ≥3 次告警


def load_state() -> dict:
    """读取健康自检状态"""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"consecutive_failures": 0, "alerted": False}


def save_state(state: dict) -> None:
    """保存健康自检状态"""
    try:
        STATE_FILE.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        print(f"[Health] Failed to save state: {e}", flush=True)


def notify_wf09(title: str, body: str, priority: str = "warning") -> bool:
    """通过 WF-09 (Slack webhook) 告警总裁"""
    webhook = os.environ.get("SLACK_WEBHOOK_N8N")
    if not webhook:
        print("[Health] SLACK_WEBHOOK_N8N not set, skip notify", flush=True)
        return False
    if requests is None:
        print("[Health] requests module not available, skip notify", flush=True)
        return False
    try:
        r = requests.post(
            webhook,
            json={
                "recipient": "president",
                "title": title,
                "body": body[:3500],
                "source": "sessions-watcher",
                "priority": priority,
            },
            timeout=10,
        )
        ok = r.status_code < 300
        print(f"[Health] WF-09 notify status={r.status_code} ok={ok}", flush=True)
        return ok
    except Exception as e:
        print(f"[Health] WF-09 notify error: {e}", flush=True)
        return False


def run_once_with_health_check(dry_run: bool = False) -> bool:
    """跑一次同步并维护健康自检状态机"""
    state = load_state()
    try:
        success = run_once(dry_run=dry_run)
    except Exception as e:
        print(f"[Watcher] run_once raised: {e}", flush=True)
        success = False

    if success:
        if state.get("alerted"):
            failed_n = state.get("consecutive_failures", 0)
            notify_wf09(
                "✅ sessions_watcher 已恢复",
                f"sessions_watcher 在 {failed_n} 次连续失败后恢复正常同步。",
                "info",
            )
        state["consecutive_failures"] = 0
        state["alerted"] = False
    else:
        state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1
        if (
            state["consecutive_failures"] >= FAILURE_ALERT_THRESHOLD
            and not state.get("alerted")
        ):
            notify_wf09(
                "🚨 sessions_watcher 连续失败",
                (
                    f"已连续 {state['consecutive_failures']} 次同步失败，"
                    f"session 可能未上传到 synapse-sessions。"
                    f"\n阈值：{FAILURE_ALERT_THRESHOLD} 次（约 15 分钟）。"
                    f"\n请检查 SESSIONS_REPO_PATH / 网络 / git 凭证。"
                ),
                "warning",
            )
            state["alerted"] = True

    save_state(state)
    return success


def _resolve_source_dirs() -> list[Path]:
    """解析所有 .claude/projects 来源目录（支持双账号）"""
    bases = []

    # 主目录
    primary = os.environ.get(
        "CLAUDE_PROJECTS_DIRS",
        str(Path.home() / ".claude" / "projects")
    )
    if primary:
        for d in primary.replace(";", ":").split(":"):
            if d.strip():
                bases.append(Path(d.strip()))

    # 额外目录（双账号 / 多机）
    extra = os.environ.get("CLAUDE_PROJECTS_EXTRA_DIRS", "")
    if extra:
        for d in extra.replace(";", ":").split(":"):
            if d.strip():
                bases.append(Path(d.strip()))

    # 去重 + 仅保留实际存在的
    seen = set()
    valid = []
    for b in bases:
        b_resolved = b.resolve()
        if b_resolved not in seen and b_resolved.exists():
            seen.add(b_resolved)
            valid.append(b_resolved)

    return valid


def _resolve_sessions_repo() -> Path:
    """解析 synapse-sessions 本地路径"""
    p = os.environ.get(
        "SESSIONS_REPO_PATH",
        str(Path.home() / "synapse-sessions")
    )
    return Path(p)


def collect_session_files(source_dirs: list[Path]) -> list[tuple[Path, Path]]:
    """收集所有 .jsonl 文件，返回 (绝对路径, 相对源目录的相对路径) 列表"""
    pairs = []
    for src in source_dirs:
        for jsonl in src.rglob("*.jsonl"):
            rel = jsonl.relative_to(src)
            pairs.append((jsonl, rel))
    return pairs


def sync_files(
    source_files: list[tuple[Path, Path]],
    target_repo: Path,
    dry_run: bool = False,
) -> dict:
    """同步文件到 target_repo/projects/，返回统计 {copied, unchanged, total}"""
    target_projects = target_repo / "projects"
    target_projects.mkdir(parents=True, exist_ok=True)

    stats = {"copied": 0, "unchanged": 0, "total": len(source_files)}

    for src, rel in source_files:
        target_file = target_projects / rel
        target_file.parent.mkdir(parents=True, exist_ok=True)

        # 比较 mtime + size，决定是否需要 copy
        need_copy = True
        if target_file.exists():
            src_stat = src.stat()
            tgt_stat = target_file.stat()
            if (src_stat.st_size == tgt_stat.st_size
                and abs(src_stat.st_mtime - tgt_stat.st_mtime) < 1):
                need_copy = False

        if need_copy:
            if not dry_run:
                shutil.copy2(src, target_file)
            stats["copied"] += 1
            print(f"  [Sync] {rel}", flush=True)
        else:
            stats["unchanged"] += 1

    return stats


def update_last_sync(target_repo: Path, source_dirs: list[Path], stats: dict):
    """更新 last_sync.json"""
    data = {
        "last_sync": datetime.now(timezone.utc).isoformat(),
        "source_dirs": [str(d) for d in source_dirs],
        "stats": stats,
    }
    last_sync_file = target_repo / "last_sync.json"
    last_sync_file.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def git_commit_and_push(target_repo: Path, dry_run: bool = False) -> bool:
    """commit + push synapse-sessions"""
    if dry_run:
        print("[Git] dry-run skipped", flush=True)
        return True

    try:
        # 检查是否有变更
        result = subprocess.run(
            ["git", "-C", str(target_repo), "status", "--porcelain"],
            capture_output=True, text=True, encoding="utf-8", timeout=30,
        )
        if not result.stdout.strip():
            print("[Git] No changes, skip push", flush=True)
            return True

        # add + commit + push
        subprocess.run(["git", "-C", str(target_repo), "add", "-A"], check=True, timeout=60)

        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M Z")
        msg = f"chore(sync): {ts}"
        subprocess.run(
            ["git", "-C", str(target_repo), "commit", "-m", msg],
            check=True, timeout=30,
        )

        # push 重试 3 次
        for attempt in range(3):
            r = subprocess.run(
                ["git", "-C", str(target_repo), "push", "origin", "main"],
                capture_output=True, text=True, timeout=120,
            )
            if r.returncode == 0:
                print(f"[Git] Push OK (attempt {attempt+1})", flush=True)
                return True
            print(f"[Git] Push attempt {attempt+1} failed: {r.stderr[:200]}", flush=True)

            # rebase 后重试
            subprocess.run(
                ["git", "-C", str(target_repo), "pull", "--rebase", "origin", "main"],
                timeout=60,
            )

        print("[Git] All push attempts failed", flush=True)
        return False
    except subprocess.CalledProcessError as e:
        print(f"[Git] Error: {e}", flush=True)
        return False


def run_once(dry_run: bool = False) -> bool:
    """执行一次同步"""
    print(f"[Watcher] Starting one-shot sync at {datetime.now(timezone.utc).isoformat()}", flush=True)

    source_dirs = _resolve_source_dirs()
    if not source_dirs:
        print("[Watcher] No valid source directories found, skipping", flush=True)
        return False

    print(f"[Watcher] Source dirs: {[str(d) for d in source_dirs]}", flush=True)

    target_repo = _resolve_sessions_repo()
    if not target_repo.exists() or not (target_repo / ".git").exists():
        print(f"[Watcher] Target repo not found: {target_repo}", flush=True)
        return False

    print(f"[Watcher] Target repo: {target_repo}", flush=True)

    files = collect_session_files(source_dirs)
    print(f"[Watcher] Found {len(files)} jsonl files", flush=True)

    stats = sync_files(files, target_repo, dry_run=dry_run)
    print(f"[Watcher] Synced {stats['copied']} new/changed files ({stats['unchanged']} unchanged)", flush=True)

    update_last_sync(target_repo, source_dirs, stats)

    push_ok = git_commit_and_push(target_repo, dry_run=dry_run)

    return push_ok


def run_daemon(interval: int):
    """长驻轮询"""
    import time
    print(f"[Watcher] Daemon mode, polling every {interval}s", flush=True)
    while True:
        try:
            run_once_with_health_check(dry_run=False)
        except Exception as e:
            print(f"[Watcher] Sync error: {e}", flush=True)
        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--daemon", action="store_true", help="Long-running daemon")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--interval", type=int, default=DEFAULT_POLL_INTERVAL)
    args = parser.parse_args()

    if args.daemon:
        run_daemon(args.interval)
    elif args.once or not (args.once or args.daemon):
        # 默认 once 行为（带健康自检）
        ok = run_once_with_health_check(dry_run=args.dry_run)
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
