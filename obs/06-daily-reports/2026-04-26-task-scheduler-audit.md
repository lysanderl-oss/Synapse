# Windows Task Scheduler + 博客发布审计（2026-04-26）

**审计人**：harness_engineer（子 Agent）
**审计时间**：2026-04-26
**触发原因**：总裁报告"昨天博客没有发布"
**红线**：仅调研告知，未修改任何 Task Scheduler 设置，未触发博客脚本

---

## 一、博客发布事实

### 1.1 04-25 是否有发布

**结论：04-25 没有任何新博客文章发布。**

证据：

| 来源 | 最新记录 |
|------|----------|
| `scripts/.blog-published.json` | 最后一条 = `notion-mcp-over-local-api-scripts` @ 2026-04-23 21:17 |
| `obs/04-content-pipeline/_published/` | 最新两篇 = `2026-04-24-ai-product-ga-validation-version-lock.md`、`2026-04-24-ai-workflow-slack-payload-contract-mismatch.md` |
| `lysander-bond` git log（远端 = lysanderl-glitch/lysander-bond，但 gh api 返回 404，使用本地 clone） | 最新 publish 类 commit = `cd65afa 2026-04-24 21:46 feat: publish blog post '管道没坏，契约断了'` |
| `obs/04-content-pipeline/_inbox/` | 仅 `.gitkeep`，无任何待发文章 |
| `obs/04-content-pipeline/_drafts/` | 空 |

**04-25 lysander-bond 的 commits 是站点 i18n / 双语化工作（9 个 commit），无任何 `feat: publish blog post` 类型 commit。**

### 1.2 04-26 截至诊断时间

无博客发布，pipeline inbox 仍空。

---

## 二、Synapse-WorklogExtractor 状态

| 字段 | 值 |
|------|---|
| State | Ready |
| LastRunTime | **2026/4/26 01:36:04**（不是 04-25 22:00） |
| LastTaskResult | **2147942402 = 0x80070002（FILE_NOT_FOUND / The system cannot find the file specified）** |
| NextRunTime | 2026/4/26 22:00:00 |
| NumberOfMissedRuns | 0 |

**04-24 修复（去电池限制 + 重试 3 次）状态：**

XML 验证（`schtasks /query /tn 'Synapse-WorklogExtractor' /xml`）：
- `<DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>` ✅ 已去除电池限制
- `<StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>` ✅
- `<RestartOnFailure><Count>3</Count><Interval>PT10M</Interval></RestartOnFailure>` ✅ 已配置 3 次重试
- `<StartWhenAvailable>true</StartWhenAvailable>` ✅ 唤醒后追跑

**修复部分生效**：04-25 22:00 电脑大概率休眠/关机错过触发，但 04-26 01:36 系统唤醒后通过 `StartWhenAvailable` 触发了追跑——**追跑发生了，但脚本以 0x80070002 失败**。问题不在调度，转移到了脚本/环境层。

---

## 三、所有 Synapse 相关 task 清单

| TaskName | TaskPath | State | LastRun | LastResult | NextRun |
|----------|----------|-------|---------|------------|---------|
| Synapse-NotionDailySync | `\` | Ready | 2026/4/26 01:46:07 | **0x80070002** | 2026/4/26 18:00 |
| Synapse-WorklogExtractor | `\` | Ready | 2026/4/26 01:36:04 | **0x80070002** | 2026/4/26 22:00 |
| CalendarSync | `\Synapse\` | Ready | 2026/4/26 09:18:22 | 0x800700C1 | 2026/4/27 06:15 |
| DailyIntelligence | `\Synapse\` | Ready | 2026/4/26 09:18:22 | 0x800700C1 | 2026/4/27 08:00 |
| DailyReview | `\Synapse\` | Ready | 2026/4/26 01:36:04 | 0x800700C1 | 2026/4/26 20:00 |
| IntelligenceAction | `\Synapse\` | Ready | 2026/4/26 10:00:01 | 0x800700C1 | 2026/4/27 10:00 |
| TaskAutoResume | `\Synapse\` | Ready | 2026/4/26 09:18:22 | 0x800700C1 | 2026/4/27 06:00 |

**5 个 0x800700C1 task 现状：自 P2-B 报告以来无变化**，仍处于"Ready 但每次执行返回 0xC1（应用不是有效 Win32 应用）"的废弃状态。`State=Ready`，每天按时被调度，每次按时失败，没人处理。

**新增发现**：`Synapse-WorklogExtractor` 和 `Synapse-NotionDailySync` 两个根目录 task 也开始返回 `0x80070002`（FILE_NOT_FOUND）。这是过去 P2-B 没有标记的新故障。

**Task Scheduler 操作日志状态**：`Microsoft-Windows-TaskScheduler/Operational` 日志当前 **IsEnabled=False**，无法回查事件细节（推荐手动开启以便后续诊断）。

---

## 四、根因判定

总裁说"昨天博客没发布"——拆成两个独立故障：

**故障 A：04-25 22:00 调度未触发**
- 大概率电脑当时休眠/关机/网络断开
- 04-24 修复让它能在 04-26 01:36 系统唤醒后追跑（修复有效）

**故障 B：追跑也失败了（0x80070002）**
- 0x80070002 = 系统找不到文件，但 `py -3` 在交互式 shell 下可正常运行（已验证 Python 3.12.10）
- 候选根因（无 Operational 日志，无法精确定位）：
  1. Windows Unified Scheduler 在登录前/锁屏阶段，`py.exe` 不在系统级 PATH，找不到 launcher
  2. 工作目录 `C:\Users\lysanderl_janusd\Synapse-Mini` 在执行时不可达（OneDrive / 加密分区延迟挂载）
  3. 脚本内部某条 subprocess.run 找不到 `git`/`gh`/`claude` 等子命令（写入 stderr 后以 0x80070002 退出）
- `Synapse-NotionDailySync` 同时间窗口、同错误码 → 强烈支持环境/PATH 问题，不是脚本逻辑问题
- **博客本来就不依赖那 5 个 0x800700C1 task**，它们是独立无关故障

**结论**：04-25 博客没发，根因是 WorklogExtractor pipeline 在追跑时遇到环境/PATH 类故障（0x80070002）。04-24 的"去电池 + 重试 3 次"修复仅解决了"调度不触发"的部分，没解决"触发后脚本失败"的部分。

---

## 五、关键发现

1. **04-24 修复部分生效**：调度成功触发追跑（说明 `DisallowStartIfOnBatteries=false` + `StartWhenAvailable=true` 起作用），但脚本本身失败。
2. **新故障浮现**：`Synapse-WorklogExtractor` + `Synapse-NotionDailySync` 两个根目录 task 同时间出现 0x80070002，过去 P2-B 报告中未列出，是新增故障。
3. **5 个 0x800700C1 task 仍未处理**：CalendarSync / DailyIntelligence / DailyReview / IntelligenceAction / TaskAutoResume 自 P2-B 以来零变化，每天按时失败 5 次。
4. **博客 pipeline 与那 5 个 task 解耦**：博客发不出来与它们无关，不要混为一谈。
5. **诊断盲区**：`Microsoft-Windows-TaskScheduler/Operational` 日志被禁用，无法回查 04-26 01:36 失败时具体在哪一行返回 0x80070002。

---

## 六、调整建议（仅建议，未执行）

**候选 1：开启 Task Scheduler Operational 日志**
- 命令：`wevtutil sl Microsoft-Windows-TaskScheduler/Operational /e:true`（需要管理员）
- 收益：下次失败可精确定位是哪一步找不到文件
- 成本：日志体积增长（可控）
- 风险：低

**候选 2：让 WorklogExtractor 失败时把 stderr 落盘**
- 修改 task XML 把 Action 改成 `cmd /c py -3 ... > logs\worklog.log 2>&1`
- 收益：根因从"猜"变成"看"
- 成本：1 次 task 重建
- 风险：低，但需总裁授权改 Task Scheduler

**候选 3：删除 5 个 0x800700C1 废弃 task**
- 已确认无依赖、每天 5 次假阳性失败、噪音污染审计
- 收益：清理调度器，降低误判概率
- 风险：极低（已确认废弃）；需总裁授权
- 备注：本任务红线禁止执行，仅列入候选

**候选 4：博客管线迁云端（GitHub Actions）**
- 长期方案，彻底脱离本地电脑开机/PATH/休眠依赖
- 已有现成 workflow 模板（`scripts/intelligence/` 提示曾有云端迁移工作）
- 成本：1-2 个会话搬迁
- 风险：需要把 `~/.claude/projects` 会话源改成可远程访问的镜像，不简单

**候选 5：手动补发 04-25 博客（短期止血）**
- 04-25 session-archive 已存在 145 行，可手动跑 `py -3 scripts/session-to-worklog.py` 走完一次完整流程
- 收益：补回 04-25 内容
- 风险：本任务红线禁止"重新启动博客脚本"，仅列候选

---

## 七、给 Lysander 的一行

WorklogExtractor 04-24 修复让 04-26 01:36 追跑生效了（调度层修好了），但脚本以 0x80070002 失败 → 04-25 博客没发是新增的环境/PATH 类故障，与 5 个 0x800700C1 废弃 task 无关；建议优先执行候选 1+2（开日志 + 落盘 stderr）拿到根因，候选 3+4 可作下阶段规划。
