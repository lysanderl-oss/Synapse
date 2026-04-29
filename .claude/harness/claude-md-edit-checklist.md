---
id: claude-md-edit-checklist
type: harness-fragment
parent: CLAUDE.md
created_at: 2026-04-27
created_per: Lysander 自我反省（4-27 压缩遗漏 6 处事实错误）
---

# CLAUDE.md 修改前事实校验 Checklist（强制）

## 触发条件
任何对 `CLAUDE.md` 的修改（无论是压缩 / 重写 / 追加 / 删除）必须执行本 checklist。

## 校验维度（修改前 + 修改后各执行一次）

### A. 数字事实校验
- [ ] 所有 "X 人 Agent" / "X 位" / "X 个 团队" 数字与 `agent-CEO/config/organization.yaml` 实际计数一致
- [ ] 所有 "X 行" 数字与 `wc -l <实际文件>` 一致
- [ ] 所有 "X 天" / "X 小时" 时间约束是否仍然合理
- [ ] 所有 "X 分" 评分阈值与 `hr_base.py` / qa_auto_review 实现一致

### B. 路径引用校验
- [ ] 所有 `path/to/file.ext` 引用真实存在（用 `ls` 验证）
- [ ] 所有团队/Agent 路径反映最新结构（如 agent-butler → agent-CEO 重命名）
- [ ] 所有 `.claude/harness/` 碎片引用存在

### C. 函数 / 命令引用校验
- [ ] 所有 Python 函数调用（如 `audit_harness()`）实际有实现（用 grep 验证）
- [ ] 所有 Skill 引用（如 `/dispatch`）在 `.claude/commands/` 实际存在
- [ ] 所有 npm/python 命令在系统中可执行

### D. 规则一致性校验
- [ ] 修改后规则与其他规则不冲突 / 不重复
- [ ] P0 规则变更须总裁会话确认（不可 Lysander 自决）
- [ ] 行数 ≤ 350（Phase 2 收紧至 300）

### E. SSOT 校验
- [ ] 与 `synapse-stats.yaml` 数字一致（公开体系）
- [ ] 与 `organization.yaml` 团队列表一致（私有实例）
- [ ] 与 `VERSION` 文件版本号一致

## 失败处理

任一校验项 ✗ → **不得 commit**，回到修订表格，标"不通过"原因，下一轮修复。

## 历史失败案例

- **2026-04-27 压缩 CLAUDE.md（407→327）**：仅做行数压缩，未走本 checklist，遗漏 6 处事实错误（44 Agent / agent-butler 路径 / qa ≥3.5 / /dispatch Skill / audit_harness 函数 / 团队列举不全）。后由总裁警觉 + 4-27 22:00 修复。
- **教训**：压缩任务的 QA 必须含"事实校验"维度，仅做"行数 + 语义压缩"是不充分的。

## 与现有规则的关系
- 本 checklist 服务于 CLAUDE.md "Harness 治理规则"节（P0）
- 校验维度 A/E 复用 fact-SSOT 元规则
- 校验维度 B/C/D 是 CLAUDE.md 专属

## 实际执行机制（# [ADDED: 2026-04-27]）

⚠️ **本 checklist 不是仅靠自觉。** 通过 git pre-commit hook 强制执行：

### 安装（一次性）
```bash
bash scripts/install-git-hooks.sh
```
新 clone 或重置 `.git/hooks/` 后必须再次运行。脚本是幂等的。

### 拦截脚本
- `scripts/check_claude_md_edit.py` — 5 维度自动校验（A 数字 / B 路径 / C 函数命令 / D 行数 / E QA 阈值）
- `scripts/check_decision_log.py` — L3+ 决策必须有 D 编号归档
- `scripts/frontmatter_lint.py` — frontmatter 合规（warning 模式，不阻断）

### 拦截行为
- 修改 CLAUDE.md 并 stage → pre-commit 自动跑 `check_claude_md_edit.py`
- 任一 P0 失败 → commit 被拦截（exit 1）
- decision-smell commit 缺 D 编号或 decision-log/* 改动 → commit 被拦截
- 紧急绕过：`git commit --no-verify`（**仅紧急使用** + Lysander 必须 24h 内在 `obs/06-daily-reports/` 复盘原因）

### 验证测试（2026-04-27 通过）
| 故意破坏 | 期望 | 实际 |
|---------|------|------|
| 修改 CLAUDE.md 加 `agent-butler/` 路径 | exit 1 + B-FAIL | ✅ exit 1，命中 B |
| 修改 CLAUDE.md 加 `44 人 Agent` | exit 1 + 3 个 A-FAIL | ✅ exit 1，命中 A×3 |
| 干净状态运行 | exit 0 | ✅ exit 0 |

### 历史拦截记录
每次实际拦截事件追加到 `obs/06-daily-reports/pre-commit-blocks-{date}.md`（首次拦截时由 Lysander 创建）。

### 局限
- pre-commit hook 仅本地拦截，不影响推到远端后的状态（远端无对应 CI）
- `--no-verify` 可绕过（属"自律"层 + 周审日志会捕获）
- frontmatter 仍是 warning（计划下一轮升级到 block）
