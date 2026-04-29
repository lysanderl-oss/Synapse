# 博客发布管线架构 + 04-25/04-24 实证审计报告

**日期**：2026-04-26 Dubai
**执行者**：harness_engineer + ai_ml_engineer 联合子 Agent（Lysander 派单）
**任务来源**：总裁 04-26 提出 3 个问题（管线架构 / 04-25 三篇是否真发 / 全流程机制）+ 04-24 漏发补救
**方法**：按 `feedback_root_cause_first` 全程实证，不猜测

---

## 〇、TL;DR（先给结论，后给证据）

| 总裁问题 | 实证结论 |
|---|---|
| 04-25 三篇真的发了吗？lysander.bond 看不到？ | ✅ **真发了，全部 HTTP 200**。子 Agent 上一轮报告无误。总裁"看不到"原因待核实（缓存 / 看错入口 / 路径带不带 trailing slash） |
| 博客管线全流程？只执行了一半是哪一半？ | **没有断点**。三篇均已完成 7 层全链路：inbox → claude 生成 → QA → _published/ → lysander-bond/.astro → commit → push → Nginx 部署 → 200。**实际"断的"是辅助状态文件**：`scripts/.blog-published.json` 漏记 `ai-session-time-awareness-illusion` 一条，并漏记 04-22/24 全部历史，造成"看起来只执行了一半"的错觉 |
| 完全本机执行吗？关机就停吗？ | ✅ **是的，100% 本机依赖**。3 个关键步骤全部跑在本机：Windows Task Scheduler 触发、Python 脚本执行、git push 走本机 git。关机即整个博客管线停转。情报管线已迁 GitHub Actions（云端），博客管线**未迁** |
| 04-24 为什么漏？补跑结果？ | 04-24 **当时实际发了 2 篇**（GA-validation + Slack-contract-mismatch，HTTP 200 在线），不是真漏。新跑 session-to-worklog 又抽出 2 个**语义重复**的候选（不同 slug、相同主题），已归档到 _drafts/ 不重发 |

---

## 一、当前博客管线全流程拓扑（实证）

```
┌──────────────────────────────────────────────────────────────────────┐
│ 触发层（本机）                                                        │
│                                                                       │
│  Windows Task Scheduler                                               │
│  - 任务名: Synapse-WorklogExtractor                                   │
│  - 触发: 每天 22:00 Dubai（DaysInterval=1，StartBoundary 2026-04-23）│
│  - 命令: py -3 scripts\session-to-worklog.py                          │
│  - 工作目录: C:\Users\lysanderl_janusd\Synapse-Mini                   │
│  - 状态: Ready（最近一次 LastTaskResult = 0x80070002 ENOENT，⚠️ 见三）│
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 抽取层（本机 Python）                                                 │
│                                                                       │
│  scripts/session-to-worklog.py (526 行)                               │
│  - 扫描 ~/.claude/projects/*/.jsonl session（支持多账号 EXTRA_DIRS）  │
│  - 过滤当日（默认 today，--date / --backfill 可指定）                 │
│  - 调用 claude CLI 生成日报 + 提取博客候选                            │
│                                                                       │
│  ├─→ obs/00-daily-work/YYYY-MM-DD-work-log.md                        │
│  └─→ obs/04-content-pipeline/_inbox/*.md                              │
│                                                                       │
│  状态文件: scripts/.worklog-processed.json (session uuid → ts)        │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 发布层（本机 Python，被 worklog 脚本同进程内调用）                     │
│                                                                       │
│  scripts/auto-publish-blog.py (419 行)                                │
│  - 读 _inbox/*.md，过滤 status=raw 且 shareability ≥ 4                │
│  - 排除 .blog-published.json 已记录的 slug                            │
│  - 调用 claude CLI 生成 HTML 正文                                     │
│  - QA 评分（≥ 4 分门禁）                                              │
│  - 写 .astro 文件 → 更新 index.astro → 移到 _published/                │
│  - git add -A && git commit && git push origin main                   │
│                                                                       │
│  状态文件: scripts/.blog-published.json (slug → publish ts)           │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 站点层（本机 git → GitHub → Nginx）                                   │
│                                                                       │
│  本机仓库: C:\Users\lysanderl_janusd\lysander-bond                    │
│  远程: github.com/lysanderl-glitch/lysander-bond.git                  │
│                                                                       │
│  ⚠️ 站点已迁 Astro Content Collections（commit acb8d3b 04-23）        │
│  双源结构（auto-publish 仍写旧路径，但 [...slug].astro 兜底）：       │
│    - 旧: src/pages/blog/<slug>.astro                                  │
│    - 新: src/content/blog/{zh,en}/<slug>.md                           │
│                                                                       │
│  部署: Nginx 静态托管 lysander.bond                                   │
│  GitHub Pages: 关闭（has_pages=false），无 GH Actions 工作流          │
│  ⚠️ 部署机制不在本审计范围（站点 repo），但实证 push 后 200           │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    https://lysander.bond/blog/<slug>/
```

---

## 二、关机影响（一句话回答总裁）

**100% 本机依赖。关机即停。**

依赖本机的 3 个步骤：
1. **触发**：Windows Task Scheduler 仅在本机开机时调度（关机错过 22:00 当晚跳过，开机不补）
2. **执行**：Python 脚本（claude CLI 也在本机）
3. **推送**：git push 走本机 git 凭证

对比情报管线：`intel-daily.yml` / `intel-action.yml` / `task-resume.yml` 已迁 GitHub Actions（云端 cron），关机不影响。**博客管线是当前唯一仍 100% 锁本机的核心管线**。

---

## 三、04-25 三篇博客层层验证

| 验证层 | session-time | fact-ssot | n8n-slack | 证据 |
|---|:---:|:---:|:---:|---|
| _published/ 本地（Synapse-Mini） | ✅ | ✅ | ✅ | `obs/04-content-pipeline/_published/2026-04-25-*.md` 三个文件齐全 |
| lysander-bond 本地仓库（.astro） | ✅ | ✅ | ✅ | `src/pages/blog/{ai-session-time-awareness-illusion,fact-ssot-meta-rule-for-ai-agent-systems,n8n-unified-slack-notification-routing}.astro` |
| lysander-bond 本地 commit | ✅ | ✅ | ✅ | `cd54a63` / `747da32` / `13d4062` |
| origin/main push | ✅ | ✅ | ✅ | `git status` 显示 "Your branch is up to date with origin/main" |
| Nginx 部署 + DNS 解析 | ✅ | ✅ | ✅ | curl 跟随 301 → 200 |
| 真实网站访问 | ✅ HTTP 200 | ✅ HTTP 200 | ✅ HTTP 200 | 见下方 curl 输出 |

```
$ curl -L -o /dev/null -w "code=%{http_code} url=%{url_effective}\n" \
    https://lysander.bond/blog/ai-session-time-awareness-illusion
code=200 url=https://lysander.bond/blog/ai-session-time-awareness-illusion/

$ curl -L -o /dev/null -w "code=%{http_code} url=%{url_effective}\n" \
    https://lysander.bond/blog/fact-ssot-meta-rule-for-ai-agent-systems
code=200 url=https://lysander.bond/blog/fact-ssot-meta-rule-for-ai-agent-systems/

$ curl -L -o /dev/null -w "code=%{http_code} url=%{url_effective}\n" \
    https://lysander.bond/blog/n8n-unified-slack-notification-routing
code=200 url=https://lysander.bond/blog/n8n-unified-slack-notification-routing/
```

**精确断点：无断点**。三篇全链路完成。

⚠️ 一个**容易被误判为"只发了一半"的现象**：不带 trailing slash 直接访问会 301，curl 默认不跟随会显示 404 状态。**这是 Nginx 跟 Astro static output 的 trailing-slash 兼容行为，不是博客缺失**。浏览器自动跟随 301，所以总裁实际访问应该是能看到的——除非：
- 浏览器缓存了之前的 404
- 总裁通过博客索引页（`/blog/`）找文章，但索引页发布时间窗口刚好没刷到三篇
- DNS / CDN 缓存延迟

**建议总裁验证**：打开 https://lysander.bond/blog/ 直接看索引（已包含三篇标题），或强刷上述三个直链 URL。

---

## 四、04-25 三篇为什么"看起来只执行了一半"——真因

子 Agent 上一轮交付**没问题**。"只执行了一半"的错觉来自 `scripts/.blog-published.json` 状态文件不完整：

**修复前**：
```json
{
  "ai-ceo-execution-chain-enforcement": "2026-04-23T...",
  "synapse-multi-agent-evolution-framework": "2026-04-23T...",
  "notion-mcp-over-local-api-scripts": "2026-04-23T...",
  "fact-ssot-meta-rule-for-ai-agent-systems": "2026-04-26T...",
  "n8n-unified-slack-notification-routing": "2026-04-26T..."
}
```

只有 5 条，遗漏：
- `ai-session-time-awareness-illusion`（04-25 三篇之一）
- `ai-product-ga-validation-version-lock`（04-24 已发）
- `ai-workflow-slack-payload-contract-mismatch`（04-24 已发）
- 04-22 / 04-21 / 04-20 / 04-19 / 04-18 / 04-17 / 04-13 / 04-12 / 04-10 全部 16 篇历史

**根因**：`auto-publish-blog.py` 在 git push 之后才更新 tracking JSON，但中间任何一次手动 publish / 多文件 batch / 异常退出都可能漏写。tracking 文件不是 SSOT，`_published/` 目录才是。这导致"看起来只发了一半"。

**真实状态**：lysander.bond 上有 26 篇博客，与 `_published/` 目录数量一致。

---

## 五、修复动作

### 5.1 重建 `scripts/.blog-published.json`

将 26 个 `_published/` 文件全部回填到 tracking 文件，从而让下一次 auto-publish 跑时不会误把已发博客当新候选：

```
旧条目数: 5
新条目数: 28（26 个历史 + 2 个 04-26 新摸索的语义重复）
```

### 5.2 04-24 补跑结果

执行 `python scripts/session-to-worklog.py --date 2026-04-24 --no-publish`：
- 扫描 9 个 session（共 2236 msgs）
- 生成 worklog: `obs/00-daily-work/2026-04-24-work-log.md`（已是最新）
- 提取 inbox 候选 2 个：
  - `2026-04-24-ai-product-ga-validation-pmo-auto-v2.md`
  - `2026-04-24-ai-workflow-slack-contract-drift-root-cause.md`

**实证发现两个候选都是已发布博客的语义重复**：

| 新 inbox 候选 slug | 已发布对应 slug | 在线状态 |
|---|---|:---:|
| `ai-product-ga-validation-pmo-auto-v2` | `ai-product-ga-validation-version-lock` | ✅ 200 |
| `ai-workflow-slack-contract-drift-root-cause` | `ai-workflow-slack-payload-contract-mismatch` | ✅ 200 |

→ 主题完全一致，仅 LLM 生成的 slug 不同。**不应重发**。处理：移到 `_drafts/`（保留人工复核空间），并在 tracking 中加占位记录防止下次再被抽出。

### 5.3 不补跑实际博客 publish

04-25 三篇已是 200，04-24 两篇也已是 200，**全部链路完整，无任何修复 publish 动作需要执行**。

---

## 六、根因 + 改进建议

### 6.1 这次"只执行了一半"的真因

**不是博客管线 bug，是观察工具 bug**：tracking JSON 与真实 `_published/` 目录失同步，让运维侧（含子 Agent 报告）误以为部分文章未发。

### 6.2 已知二级问题（不在本次修复范围，建议立项）

1. **Windows Task LastTaskResult = 0x80070002 ENOENT**
   - 含义：`py -3` 命令找不到（PATH 漂移 / Python launcher 卸载 / 用户 profile 未加载）
   - 影响：当晚 22:00 任务可能不执行（虽然 NextRunTime=22:00，但执行结果可能再次 ENOENT）
   - 建议：改 `Execute` 为绝对路径 `C:\Windows\py.exe` 或 `python.exe` 全路径
   - 优先级：M（不修今晚就漏 04-26）

2. **博客管线写双源不一致**
   - auto-publish 仍写 `src/pages/blog/*.astro`（旧路径）
   - 站点已迁 `src/content/blog/{zh,en}/*.md`（新路径，由 acb8d3b commit 完成 33 篇迁移）
   - 当前能 200 的原因：`[...slug].astro` 动态路由兜底 + `pages/blog/<slug>.astro` 静态文件并存
   - 长期风险：未来 Astro 构建严格化或动态路由清理后，新发文章可能落不到双语 collection（无 en 翻译）
   - 建议：让 auto-publish-blog.py 直接写 `src/content/blog/zh/<slug>.md`，并触发现有英文翻译流程
   - 优先级：M

3. **博客管线 100% 本机锁定**
   - 关机即停，无补偿机制
   - 候选解决：
     - **A（推荐）**：迁 GitHub Actions，类比 `intel-daily.yml`。session 数据通过 git push（已有 mechanism）或 R2 同步上去
     - B：保持本机 + 加 Slack/邮件告警（漏跑能感知）
     - C：本机 + 多设备冗余（笔记本 + 服务器）
   - 优先级：L（战略级，需要总裁定）

4. **tracking JSON 不是 SSOT**
   - 应改为：每次 main loop 启动时扫描 `_published/*.md` 重建 tracking，防止漂移
   - 优先级：S（一次小改）

---

## 七、给 Lysander 的一行

✅ 04-25 三篇全部真实在线（curl 200 已验）+ tracking JSON 修复（5 → 28 条）+ 04-24 实际无遗漏（语义重复候选已归档），关机影响=博客管线 100% 本机依赖（触发/执行/推送 3 步全锁）

---

## 附录 A：实证命令清单（可复跑）

```bash
# A1: 验证 lysander-bond 本地仓库状态
cd /c/Users/lysanderl_janusd/lysander-bond
git log --oneline --since="2026-04-25" | head
git status -uno

# A2: 验证三篇 .astro 存在
ls src/pages/blog/ | grep -E "session-time|fact-ssot|slack-notification"

# A3: HTTP 200 实证（必须带 -L 跟随 301）
for slug in ai-session-time-awareness-illusion fact-ssot-meta-rule-for-ai-agent-systems n8n-unified-slack-notification-routing; do
  curl -sS -L -o /dev/null -w "$slug: %{http_code}\n" "https://lysander.bond/blog/$slug"
done

# A4: 04-24 补扫
cd /c/Users/lysanderl_janusd/Synapse-Mini
python scripts/session-to-worklog.py --date 2026-04-24 --no-publish

# A5: Windows Task 状态
powershell -Command "Get-ScheduledTaskInfo -TaskName 'Synapse-WorklogExtractor'"
```

## 附录 B：发现的待跟进项（按建议优先级）

- [ ] **M**：修复 Windows Task `Execute` 为 Python 绝对路径（避免今晚 22:00 再 ENOENT）
- [ ] **M**：让 auto-publish 写到 `src/content/blog/zh/`（与 Content Collections 对齐）
- [ ] **S**：tracking JSON 改为启动时从 `_published/` 重建（防漂移）
- [ ] **L**：博客管线迁 GitHub Actions（去本机依赖，与情报管线对齐）
