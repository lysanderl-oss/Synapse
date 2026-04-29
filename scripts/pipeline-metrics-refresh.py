#!/usr/bin/env python3
"""
Pipeline Metrics Refresh — Global Product Pipeline Daily Sync
Runs at 2:00 AM Dubai (UTC 22:00) via pipeline-daily-sync.yml
D-2026-04-29-001: Approved by President 刘子杨
"""

import os
import sys
import yaml
from pathlib import Path
from datetime import datetime, timezone, timedelta

DUBAI_TZ = timezone(timedelta(hours=4))
STALE_THRESHOLD_HOURS = 26

def count_files(directory: Path, ext: str = ".md") -> int:
    if not directory.exists():
        return 0
    return len([f for f in directory.iterdir() if f.suffix == ext and f.is_file()])

def check_stale(latest_yaml: Path) -> None:
    """M2 fix: exit(1) if last generated_at > STALE_THRESHOLD_HOURS (not just WARN)."""
    if not latest_yaml.exists():
        return
    with open(latest_yaml, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    last_ts = data.get("generated_at")
    if not last_ts:
        return
    if isinstance(last_ts, str):
        last_ts = datetime.fromisoformat(last_ts)
    if last_ts.tzinfo is None:
        last_ts = last_ts.replace(tzinfo=timezone.utc)
    age_hours = (datetime.now(timezone.utc) - last_ts).total_seconds() / 3600
    if age_hours > STALE_THRESHOLD_HOURS:
        print(f"[ERROR] pipeline-metrics/latest.yaml is {age_hours:.1f}h old (> {STALE_THRESHOLD_HOURS}h threshold). Previous sync may have failed.", flush=True)
        sys.exit(1)

def main():
    # M1 fix: bond_root is passed as CLI arg so GHA checks out lysander-bond first
    if len(sys.argv) < 2:
        print("[ERROR] Usage: pipeline-metrics-refresh.py <path-to-lysander-bond>", flush=True)
        sys.exit(1)

    bond_root = Path(sys.argv[1])
    synapse_root = Path(__file__).parent.parent
    metrics_dir = bond_root / "pipeline-metrics"
    latest_yaml = metrics_dir / "latest.yaml"

    print(f"[INFO] bond_root = {bond_root}", flush=True)
    print(f"[INFO] Checking stale threshold...", flush=True)
    check_stale(latest_yaml)

    # Count content collections
    content_root = bond_root / "src" / "content"
    counts = {
        "blog_zh":                  count_files(content_root / "blog" / "zh"),
        "blog_en":                  count_files(content_root / "blog" / "en"),
        "intelligence_daily":       count_files(content_root / "intelligence" / "daily"),
        "intelligence_decisions":   count_files(content_root / "intelligence" / "decisions"),
        "intelligence_results":     count_files(content_root / "intelligence" / "results"),
    }

    now_dubai = datetime.now(DUBAI_TZ)
    now_utc   = datetime.now(timezone.utc)

    metrics = {
        "generated_at":       now_utc.isoformat(),
        "generated_at_dubai": now_dubai.strftime("%Y-%m-%d %H:%M Dubai"),
        "generated_by":       "pipeline-metrics-refresh.py",
        "source":             "pipeline-daily-sync.yml (D-2026-04-29-001)",
        "content_collections": counts,
        "total_content_files": sum(counts.values()),
        "health": {
            "stale_threshold_hours": STALE_THRESHOLD_HOURS,
            "status": "fresh",
        },
    }

    metrics_dir.mkdir(parents=True, exist_ok=True)
    with open(latest_yaml, "w", encoding="utf-8") as f:
        yaml.dump(metrics, f, allow_unicode=True, sort_keys=False)

    print(f"[OK] pipeline-metrics/latest.yaml updated:", flush=True)
    for k, v in counts.items():
        print(f"     {k}: {v}", flush=True)
    print(f"     total: {sum(counts.values())}", flush=True)
    print(f"     generated_at: {now_dubai.strftime('%Y-%m-%d %H:%M Dubai')}", flush=True)

if __name__ == "__main__":
    main()
