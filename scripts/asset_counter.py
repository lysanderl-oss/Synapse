#!/usr/bin/env python3
"""
Asset Counter — 每日资产快照生成器
统计 Synapse 系统资产数量，写入 logs/asset_snapshot.yaml
每日随 notion_daily_sync.py 一起触发
"""

import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SNAPSHOT_PATH = REPO_ROOT / "logs" / "asset_snapshot.yaml"
DUBAI_TZ = timezone(timedelta(hours=4))

EXCLUDE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}


def _walk_files(ext: str) -> list[Path]:
    """Return all files matching extension, excluding ignored dirs."""
    results = []
    for root, dirs, files in os.walk(REPO_ROOT):
        # Prune excluded directories in-place
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if f.endswith(ext):
                results.append(Path(root) / f)
    return results


def count_files() -> dict:
    yaml_files = _walk_files(".yaml") + _walk_files(".yml")
    py_files = _walk_files(".py")
    js_files = _walk_files(".js")

    yaml_count = len(yaml_files)
    py_count = len(py_files)
    js_count = len(js_files)
    total_scripts = py_count + js_count

    return {
        "yaml_count": yaml_count,
        "py_count": py_count,
        "js_count": js_count,
        "total_scripts": total_scripts,
    }


def count_org() -> dict:
    """Parse organization.yaml for teams and agents."""
    import yaml

    org_path = REPO_ROOT / "agent-CEO" / "config" / "organization.yaml"
    if not org_path.exists():
        print(f"[asset-counter] WARNING: {org_path} not found")
        return {"teams_count": 0, "agents_count": 0}

    with open(org_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    teams = data.get("teams", {})
    teams_count = len(teams)

    all_members: set[str] = set()
    for team_data in teams.values():
        members = team_data.get("members", [])
        if isinstance(members, list):
            all_members.update(members)

    agents_count = len(all_members)
    return {"teams_count": teams_count, "agents_count": agents_count}


def parse_version() -> dict:
    """Parse VERSION file for subsystem versions."""
    version_path = REPO_ROOT / "VERSION"
    if not version_path.exists():
        return {"synapse": None, "pmo_auto": None, "infra": None}

    content = version_path.read_text(encoding="utf-8")

    # First non-comment, non-blank line is the core version
    synapse_ver = None
    for line in content.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            synapse_ver = stripped
            break

    # Parse subsystem versions from comments like:  - pmo-auto: 2.0.3
    pmo_match = re.search(r"pmo-auto:\s*([\d.]+)", content)
    infra_matches = re.findall(r"infra:\s*([\d.]+)", content)

    pmo_ver = pmo_match.group(1) if pmo_match else None
    # Take the most recent (first listed) infra version
    infra_ver = infra_matches[0] if infra_matches else None

    return {
        "synapse": synapse_ver,
        "pmo_auto": pmo_ver,
        "infra": infra_ver,
    }


def read_yesterday_snapshot() -> dict:
    """Read yesterday's snapshot if it exists."""
    if not SNAPSHOT_PATH.exists():
        return {}
    try:
        import yaml
        with open(SNAPSHOT_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"[asset-counter] Could not read yesterday snapshot: {e}")
        return {}


def compute_delta(current: dict, previous: dict) -> dict:
    """Compute delta for tracked numeric fields."""
    if not previous:
        return {"yaml_count": None, "py_count": None, "agents_count": None}
    fields = ["yaml_count", "py_count", "agents_count"]
    delta = {}
    for f in fields:
        if f in previous and previous[f] is not None:
            delta[f] = current.get(f, 0) - previous[f]
        else:
            delta[f] = None
    return delta


def write_snapshot(snapshot: dict) -> None:
    """Write snapshot dict to logs/asset_snapshot.yaml."""
    import yaml

    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Custom representer for None -> null, int stays int
    lines = []
    lines.append(f'snapshot_date: "{snapshot["snapshot_date"]}"')
    for key in ["yaml_count", "py_count", "js_count", "total_scripts",
                "teams_count", "agents_count", "active_workflows", "sites_count"]:
        lines.append(f"{key}: {snapshot[key]}")

    lines.append("versions:")
    for k, v in snapshot["versions"].items():
        if v is None:
            lines.append(f'  {k}: null')
        else:
            lines.append(f'  {k}: "{v}"')

    lines.append("delta_from_yesterday:")
    delta = snapshot["delta_from_yesterday"]
    for k, v in delta.items():
        if v is None:
            lines.append(f"  {k}: null")
        elif v >= 0:
            lines.append(f"  {k}: +{v}")
        else:
            lines.append(f"  {k}: {v}")

    lines.append(f'generated_at: "{snapshot["generated_at"]}"')

    SNAPSHOT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    print("[asset-counter] Starting asset count...")

    # 1. Count files
    file_counts = count_files()
    print(f"  YAML files:    {file_counts['yaml_count']}")
    print(f"  Python files:  {file_counts['py_count']}")
    print(f"  JS files:      {file_counts['js_count']}")
    print(f"  Total scripts: {file_counts['total_scripts']}")

    # 2. Org stats
    org_counts = count_org()
    print(f"  Teams:         {org_counts['teams_count']}")
    print(f"  Agents:        {org_counts['agents_count']}")

    # 3. Versions
    versions = parse_version()
    print(f"  Versions:      {versions}")

    # 4. Read yesterday snapshot for delta
    yesterday = read_yesterday_snapshot()

    # 5. Build current snapshot
    now_dubai = datetime.now(DUBAI_TZ)
    current = {
        **file_counts,
        **org_counts,
        "active_workflows": 9,   # manually maintained
        "sites_count": 3,        # manually maintained
    }
    delta = compute_delta(current, yesterday)

    snapshot = {
        "snapshot_date": now_dubai.strftime("%Y-%m-%d"),
        **current,
        "versions": versions,
        "delta_from_yesterday": delta,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    # 6. Write snapshot
    write_snapshot(snapshot)
    print(f"\n[asset-counter] Snapshot written to {SNAPSHOT_PATH}")

    # 7. Print summary
    print("\n=== Asset Snapshot Summary ===")
    print(f"  Date:           {snapshot['snapshot_date']}")
    print(f"  YAML configs:   {snapshot['yaml_count']}")
    print(f"  Scripts (py+js):{snapshot['total_scripts']}")
    print(f"  Active Agents:  {snapshot['agents_count']}")
    print(f"  Teams:          {snapshot['teams_count']}")
    print(f"  Synapse ver:    {versions['synapse']}")
    print(f"  PMO Auto ver:   {versions['pmo_auto']}")
    print(f"  Infra ver:      {versions['infra']}")
    if any(v is not None for v in delta.values()):
        print(f"  Delta vs yesterday: {delta}")


if __name__ == "__main__":
    main()
