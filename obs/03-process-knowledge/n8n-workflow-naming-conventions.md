# n8n Workflow 命名规范（Synapse-PJ）

> 版本：v1.0
> 生效日期：2026-04-23
> 维护者：harness_engineer + n8n_ops
> 来源：`OBJ-N8N-WORKFLOW-AUDIT` P3-A 阶段产出

## 1. 设计目标

- **编号唯一**：每个生产 workflow 一个独立编号，不允许重号
- **语义清晰**：从名字一眼看出归属（PMO Auto / Synapse 治理 / 业务集成）
- **演进可控**：编号空间预先规划，新增 workflow 不会再撞主路
- **审计可追**：所有重命名走 PR + 备份，n8n snapshot 同步入仓

## 2. 命名格式

```
WF-XX [中英文功能名]
```

- **WF-XX**：两位数字编号（01–99，按编号空间规划分配）
- **功能名**：中文或英文，能描述 workflow 的核心动作
- 例：`WF-04 PMO周报自动化`、`WF-13 Asana进度同步`

**例外**：`Synapse-*` / `Harness-*` 等语义命名 workflow 保留原名，不强制 WF 编号（属于体系基础设施层，不参与业务编号空间）。

## 3. 编号空间规划

| 编号区间 | 用途 | 现状（2026-04-23） |
|----------|------|-------------------|
| **WF-01 ~ WF-09** | PMO Auto 生产主路（不可动） | 全部占用，详见下表 |
| **WF-10 ~ WF-29** | 业务集成 / 副路 workflow | 已分配 WF-10 ~ WF-14 |
| **WF-30 ~ WF-49** | 情报管线 / 数据管道 | 预留 |
| **WF-50 ~ WF-69** | 内容生产 / 发布 | 预留 |
| **WF-70 ~ WF-89** | 实验性 / 试运行 | 预留 |
| **WF-90 ~ WF-99** | 紧急修复 / 临时 | 预留 |
| `Synapse-*` | Synapse 治理框架 workflow | 不参与编号空间 |
| `Harness-*` | Harness 系统级 workflow | 不参与编号空间 |
| `[archived] *` | 已归档 workflow | 保留原名加前缀，不再使用 |

### 3.1 PMO Auto 主路（WF-01 ~ WF-09，绝不动）

| 编号 | 功能 | 备注 |
|------|------|------|
| WF-01 | 项目初始化 | PMO Auto 入口 |
| WF-02 | 任务变更通知 | Asana 任务事件 |
| WF-03 | 里程碑提醒 | 时间触发 |
| WF-04 | PMO 周报自动化 | 每周固定推送 |
| WF-05 | 逾期任务预警 | 时间触发 |
| WF-06 | 任务依赖链通知 | 依赖关系变更 |
| WF-07 | 会议纪要 → Asana 任务 | 文档事件 |
| WF-08 | Webhook 任务完成通知 | Slack 集成 |
| WF-09 | Unified Notification | 统一通知中枢 |

## 4. 重命名 / 新建变更管理

**强制流程**（违反视为执行链断裂）：

1. **提案** — harness_engineer 在 PR 描述中说明：旧名、新名、变更原因
2. **备份** — 重命名前 GET 全量 JSON 至 `harness/n8n-snapshots/_pre-XXX-backup/`
3. **执行** — 通过 n8n REST API `PUT /workflows/{id}` 修改 name 字段
4. **同步** — 运行 `scripts/n8n/export_workflows.py` 把最新 snapshot 写回 git
5. **审计** — git commit 含完整 mapping 表，hash 记入 OBJ 跟踪文档

**禁止**：
- 在 n8n 控制台直接改名而不走 PR
- 跳过备份直接 PUT
- 与 PMO Auto 主路（WF-01 ~ WF-09）撞编号
- 在生产 workflow 名字中使用临时标记（如 `test`、`copy`、`new` 后缀）

## 5. 命名反例（不要这样做）

| 反例 | 问题 | 正确做法 |
|------|------|----------|
| `WF-02 WBS导入触发` + `WF-02 任务变更通知` | 编号重复 | 副路改 WF-11 |
| `My workflow 12` | n8n 默认名 | 重命名为 WF-XX [功能名] |
| `WF-99 test` | 临时标记入主线 | 移到 archived 或删除 |
| `WF-4 周报` | 编号位数不一致 | 统一两位 `WF-04` |
| `WF-02: 项目注册表Done → 自动建项` | 冒号 + 长描述 | `WF-10 项目注册表Done → 自动建项` |

## 6. 审计

- **3 天定期**：n8n_ops 运行 `python scripts/n8n/audit_naming.py`（待建）扫描重号 / 默认名
- **新增 workflow**：harness_engineer 审核命名是否符合本规范
- **变更记录**：本规范 v 号 + 生效日期；每次大改写入 CHANGELOG

## 7. 关联文档

- `harness/n8n-snapshots/` — 全量 workflow snapshot
- `agent-butler/config/n8n_integration.yaml` — n8n 编排配置
- `scripts/n8n/export_workflows.py` — snapshot 同步脚本
- `OBJ-N8N-WORKFLOW-AUDIT` — 本规范的来源 Objective

---

**维护**：本文档由 harness_engineer 在每次 P3 系列变更后更新。
