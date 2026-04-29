#!/usr/bin/env python3
"""One-time script: backfill historical milestones into Notion database.
Reads credentials from environment variables.
"""
import os, sys, io, requests, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
NOTION_DB_ID = os.environ.get("NOTION_DB_ID", "")

if not NOTION_TOKEN or not NOTION_DB_ID:
    print("ERROR: NOTION_TOKEN or NOTION_DB_ID not set")
    sys.exit(1)

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

milestones = [
    {
        "date": "2026-04-23",
        "source": "Claude Code",
        "title": "[Claude Code] 2026-04-23 PMO Auto V2.0 GA",
        "summary": "TC-A01~A06 all PASS, v2.0-ga tag pushed, PMO Auto officially GA",
        "key_outcomes": "- TC-A01~A06 all acceptance tests PASSED\n- v2.0-ga git tag created and pushed\n- PMO Auto V2.0 formally released to production",
        "key_decisions": "- PMO Auto V2.0 GA approved, no further blockers",
        "next_steps": "- Monitor production stability\n- Begin V2.1 sprint planning",
    },
    {
        "date": "2026-04-24",
        "source": "Claude Code",
        "title": "[Claude Code] 2026-04-24 Synapse V2.1 CEO Guard",
        "summary": "Worker Agents exempted from CEO Guard, REQ-INFRA-003 intelligence pipeline scaffolded",
        "key_outcomes": "- Worker Agents exempted from CEO Guard pre-tool-use hook\n- REQ-INFRA-003 Week 1 intelligence pipeline architecture skeleton created\n- CEO Guard audit log updated",
        "key_decisions": "- L3: Worker Agent exemption approved\n- L3: Intelligence pipeline Week 1 scope confirmed",
        "next_steps": "- Complete intelligence pipeline Week 2\n- Validate CEO Guard exemption logic",
    },
    {
        "date": "2026-04-25",
        "source": "Claude Code",
        "title": "[Claude Code] 2026-04-25 WF-09 Slack Full Chain Fix",
        "summary": "P0/P1/P2 three fixes, #ai-agents-noti channel routing, infra-1.0.3",
        "key_outcomes": "- P0 fix: WF-09 Slack notification routing corrected\n- P1 fix: #ai-agents-noti channel properly mapped\n- infra-1.0.3 tag released",
        "key_decisions": "",
        "next_steps": "- Verify all notification channels end-to-end",
    },
    {
        "date": "2026-04-25",
        "source": "Codex",
        "title": "[Codex] 2026-04-25 Company Agent Service Research Launch",
        "summary": "Started exploring next-gen Agent service architecture, Codex line joined Synapse",
        "key_outcomes": "- Company Agent Service research scope defined\n- Codex line formally integrated into Lysander-AI Hub\n- Initial architecture options documented",
        "key_decisions": "- L2: Codex line inclusion in Synapse approved",
        "next_steps": "- Complete initial research phase\n- Draft Company Agent Service proposal",
    },
    {
        "date": "2026-04-25",
        "source": "Trae",
        "title": "[Trae] 2026-04-25 Trae Promotion Line Established",
        "summary": "Domestic team Synapse rollout dedicated line launched",
        "key_outcomes": "- Trae promotion line formally established\n- Domestic team Synapse adoption program started\n- Trae line added to Lysander-AI Hub tracking",
        "key_decisions": "- L2: Trae as third AI product line approved",
        "next_steps": "- First domestic team onboarding session\n- Track adoption metrics",
    },
]

success = 0
for m in milestones:
    payload = {
        "parent": {"database_id": NOTION_DB_ID},
        "icon": {"type": "emoji", "emoji": "\U0001f3af"},
        "properties": {
            "Name": {"title": [{"text": {"content": m["title"]}}]},
            "Date": {"date": {"start": m["date"]}},
            "Source": {"select": {"name": m["source"]}},
            "Level": {"select": {"name": "里程碑"}},
            "Summary": {"rich_text": [{"text": {"content": m["summary"][:2000]}}]},
            "KeyOutcomes": {"rich_text": [{"text": {"content": m["key_outcomes"][:2000]}}]},
            "KeyDecisions": {"rich_text": [{"text": {"content": m["key_decisions"][:2000]}}]},
            "NextSteps": {"rich_text": [{"text": {"content": m["next_steps"][:2000]}}]},
            "CommitCount": {"number": 0},
            "SyncStatus": {"select": {"name": "manual"}},
        },
    }
    resp = requests.post(
        "https://api.notion.com/v1/pages",
        headers=NOTION_HEADERS,
        json=payload,
        timeout=15,
    )
    if resp.status_code == 200:
        print(f"OK: {m['title']}")
        success += 1
    else:
        data = resp.json()
        print(f"FAIL [{resp.status_code}]: {m['title']} | {data.get('message', '')[:150]}")

print(f"\nMilestones written: {success}/{len(milestones)}")
