#!/usr/bin/env python3
"""
Synapse Skills Migration Script — Phase 2
Migrates skills from Multi-Agents System to Synapse-Mini
执行者：ai_systems_dev (via Python script)
"""

import os
import shutil

SRC = r"C:\Users\lysanderl_janusd\Multi-Agents System\.claude\skills"
DST = r"C:\Users\lysanderl_janusd\Synapse-Mini\skills"
MINI_BACKUP_SRC = r"C:\Users\lysanderl_janusd\Synapse-Mini\skills"

def mkdir(path):
    os.makedirs(path, exist_ok=True)
    print(f"  [CREATE] {path}")

def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [WRITE] {path} ({len(content)} bytes)")

def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def copytree(src_dir, dst_dir):
    """Copy all files from src_dir to dst_dir, preserving structure."""
    for item in os.listdir(src_dir):
        src_path = os.path.join(src_dir, item)
        dst_path = os.path.join(dst_dir, item)
        if os.path.isdir(src_path):
            mkdir(dst_path)
            for sub in os.listdir(src_path):
                sub_src = os.path.join(src_path, sub)
                sub_dst = os.path.join(dst_path, sub)
                shutil.copy2(sub_src, sub_dst)
                print(f"  [COPY] {sub_dst}")
        else:
            shutil.copy2(src_path, dst_path)
            print(f"  [COPY] {dst_path}")

# === Step 1: Create directory structure ===
print("\n=== Step 1: Creating directory structure ===")
subdirs = ["daily-blog", "dev-plan", "dev-qa", "dev-review", "dev-secure",
           "graphify", "hr-audit", "intel", "knowledge", "qa-gate", "retro", "synapse"]
for d in subdirs:
    mkdir(os.path.join(DST, d))

# === Step 2: Backup Mini existing files ===
print("\n=== Step 2: Backing up Mini existing files ===")
mini_files = ["dispatch.md", "weekly-review.md"]
for f in mini_files:
    src_path = os.path.join(MINI_BACKUP_SRC, f)
    backup_path = os.path.join(MINI_BACKUP_SRC, f + ".mini-backup")
    if os.path.exists(src_path):
        shutil.copy2(src_path, backup_path)
        print(f"  [BACKUP] {backup_path}")

# === Step 3: Process each skill ===
print("\n=== Step 3: Migrating skills ===")

skills_config = {
    # (skill_dir, extra_files)
    "dev-plan": [],
    "dev-qa": [],
    "dev-review": [],
    "dev-secure": [],
    "graphify": [],
    "hr-audit": [],
    "intel": [],
    "knowledge": [],
    "qa-gate": [],
    "retro": [],
    "synapse": [],
}

# Low-difficulty: direct copy (no path adaptation needed)
low_difficulty = ["dev-plan", "dev-qa", "dev-review", "dev-secure",
                  "graphify", "hr-audit", "intel", "knowledge", "qa-gate", "retro"]

for skill in low_difficulty:
    src_dir = os.path.join(SRC, skill)
    dst_dir = os.path.join(DST, skill)
    print(f"\n  Processing {skill}...")
    copytree(src_dir, dst_dir)

# === Step 4: Medium-difficulty with path adaptation ===
print("\n=== Step 4: Medium-difficulty skills with path adaptation ===")

# --- dispatch ---
print("  Processing dispatch...")
dispatch_src = os.path.join(SRC, "dispatch", "SKILL.md")
dispatch_dst = os.path.join(DST, "dispatch.md")
content = read(dispatch_src)
# Replace agent-butler/config → agent-CEO/config
content = content.replace("agent-butler/config/", "agent-CEO/config/")
# Replace ai-team-system hardcoded path
content = content.replace("/c/Users/lysanderl_janusd/Claude Code/ai-team-system",
                          "$SYNAPSE_ROOT")
write(dispatch_dst, content)

# --- synapse ---
print("  Processing synapse...")
synapse_src = os.path.join(SRC, "synapse", "SKILL.md")
synapse_dst = os.path.join(DST, "synapse")
mkdir(synapse_dst)
content = read(synapse_src)
content = content.replace("agent-butler/config/", "agent-CEO/config/")
write(os.path.join(synapse_dst, "SKILL.md"), content)

# --- weekly-review ---
print("  Processing weekly-review...")
wr_src = os.path.join(SRC, "weekly-review", "SKILL.md")
wr_dst = os.path.join(DST, "weekly-review.md")
content = read(wr_src)
content = content.replace("agent-butler/config/", "agent-CEO/config/")
content = content.replace("/c/Users/lysanderl_janusd/Claude Code/ai-team-system",
                          "$SYNAPSE_ROOT")
write(wr_dst, content)

# --- daily-blog (special: has blog-template.md) ---
print("  Processing daily-blog...")
db_src_dir = os.path.join(SRC, "daily-blog")
db_dst_dir = os.path.join(DST, "daily-blog")
mkdir(db_dst_dir)
copytree(db_src_dir, db_dst_dir)
# Also update the path reference inside blog-template.md if it exists
bt_src = os.path.join(db_src_dir, "blog-template.md")
bt_dst = os.path.join(db_dst_dir, "blog-template.md")
if os.path.exists(bt_src):
    content = read(bt_src)
    content = content.replace("Janus Digital", "Janus Digital")
    write(bt_dst, content)

# === Step 5: Verify ===
print("\n=== Step 5: Verification ===")
all_items = sorted(os.listdir(DST))
print(f"  Total items in skills/: {len(all_items)}")
for item in all_items:
    full = os.path.join(DST, item)
    if os.path.isdir(full):
        children = os.listdir(full)
        print(f"  {item}/ ({len(children)} files: {children})")
    else:
        size = os.path.getsize(full)
        print(f"  {item} ({size} bytes)")

print("\n=== Migration Complete ===")
