---
id: pmo-monday-auto-architecture-2026
type: living
status: draft
lang: zh
version: 1.0.0
created_at: 2026-04-27
author: harness_engineer
review_by: [Lysander]
audience: [ai_systems_dev, harness_engineer, integration_qa]
stale_after: 2026-10-27
---

# PMO Monday Auto 技术架构方案

> 本文档定义 PMO Auto 体系从 Asana + Notion 迁移至 Monday.com 的完整技术架构。
> 决策来源：Q1=B（Monday WBS）、Q2=A（WorkDocs 替代 Notion Hub）、Q3=B（Link Board 模式）。
> 所有 API 可行性已在 Janusd 账号（ID: 34769438）实测验证。

---

## 第 1 章：目标架构概述

**负责人：harness_engineer**

### 1.1 三层架构说明

PMO Monday Auto 采用三层解耦架构，职责清晰、可独立升级：

```
┌─────────────────────────────────────────────────────────┐
│          执行层（Monday.com）                            │
│  • Board / Group / Item / Subitem / WorkDoc              │
│  • Portfolio Dashboard（跨项目聚合）                     │
│  • Registry Board（替代 Notion Registry）                │
└──────────────────┬──────────────────────────────────────┘
                   │ Webhook（item 事件）/ GraphQL API
┌──────────────────▼──────────────────────────────────────┐
│          自定义逻辑层（pmo-api）                         │
│  • MondayClient（GraphQL 封装 + 限速 + 重试）            │
│  • wbs_to_monday.py（WBS → Monday 结构转换）             │
│  • MondayWebhookValidator（IP 白名单 + 时间戳验证）      │
│  • /run-wbs-monday / /webhooks/monday 端点               │
│  • notified_events 幂等去重表（key 格式更新）            │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTP 调用 / Webhook 回调
┌──────────────────▼──────────────────────────────────────┐
│          编排层（n8n.janusd.io）                         │
│  • WF-01~09（适配后版本）                                │
│  • Monday API 凭证管理                                   │
│  • Slack 通知出口                                        │
└─────────────────────────────────────────────────────────┘
```

### 1.2 与原体系对比表

| 原组件 | 新组件 | 迁移类型 | 备注 |
|--------|--------|----------|------|
| Asana 项目 | Monday Board（PMO WBS） | 1:1 替换 | 命名规范统一 |
| Asana Section（L1） | Monday Group | 1:1 替换 | — |
| Asana Task（L2/L3） | Monday Item / Subitem | 1:1 替换 | — |
| Asana Subtask（L4） | Monday Link Board | 结构调整 | Multi-Level API 403 硬限制 |
| Asana Webhook | Monday Webhook | 替换 | 安全模型不同（IP 白名单替代 HMAC） |
| Notion Registry DB | Monday Registry Board | 替换 | 统一入口，消除跨平台依赖 |
| Notion Hub 页面 | Monday WorkDoc | 替换 | 嵌入式 Board/Dashboard Widget |
| Notion WBS DB | Monday Board 数据 | 废弃 | 数据直接在 Monday 中管理 |
| pmo-api /run-wbs | pmo-api /run-wbs-monday | 重写 | GraphQL 替代 Asana REST |
| pmo-api /webhooks/asana | pmo-api /webhooks/monday | 重写 | 新安全验证逻辑 |
| pmo-api /create_project_hub | pmo-api /create_project_workdoc | 重写 | WorkDoc API 替代 Notion API |

### 1.3 数据流图

#### 初始化流（WBS 生成）

```
总裁 / 触发事件
    │
    ▼
n8n WF-01
  读取 Monday Registry Board
  （GraphQL: boards.items_page）
    │
    ▼
pmo-api /run-wbs-monday
  解析 WBS 数据
  MondayClient.create_board()
  MondayClient.create_group() × L1
  MondayClient.create_item() × L2
  MondayClient.create_subitem() × L3
  MondayClient.create_link_board() × L4（如有）
    │
    ▼
Monday.com Board
  结构创建完成
    │
    ▼
pmo-api /create_project_workdoc
  WorkDoc 生成（项目文档）
    │
    ▼
Monday Registry Board
  WorkDoc URL 回写
    │
    ▼
n8n → Slack 通知（项目初始化完成）
```

#### 状态变更流（任务完成通知）

```
Monday.com
  Item 状态列变更（Done / Stuck）
    │
    ▼（HTTP POST）
pmo-api /webhooks/monday
  MondayWebhookValidator.validate()
    ├─ IP 白名单检查
    └─ 时间戳窗口检查（300s）
  notified_events 幂等去重
  事件写入队列
    │
    ▼（HTTP 回调）
n8n WF-08
  解析 monday_item_id / event_type
  构造 Slack 通知消息
    │
    ▼
Slack #pmo-notifications
  通知总裁和相关人员
```

---

## 第 2 章：Monday Board 架构设计

**负责人：harness_engineer**

### 2.1 Workspace 规划

**建议方案：使用现有 Main Workspace + 创建 PMO 专属文件夹。**

理由：
- Main Workspace 已有 Asana Task Import 相关 Board，基础结构存在
- 不建议新建 Workspace（增加跨空间权限管理复杂度）
- 通过文件夹（Folder）隔离 PMO 相关 Board

**文件夹结构：**

```
Main Workspace
└── 📁 PMO（文件夹）
    ├── PMO_REGISTRY（Registry Board）
    ├── PMO_PORTFOLIO_DASHBOARD（Dashboard）
    ├── 📁 项目代码-A（子文件夹）
    │   ├── PMO_PRJA_WBS（主 WBS Board）
    │   └── PMO_PRJA_L4_Phase1（L4 Link Board）
    └── 📁 项目代码-B（子文件夹）
        └── PMO_PRJB_WBS
```

**Board 命名规范：**

| Board 类型 | 命名模板 | 示例 |
|------------|----------|------|
| WBS 主 Board | `PMO_<ProjectCode>_WBS` | `PMO_SYNAPSE_WBS` |
| L4 Link Board | `PMO_<ProjectCode>_L4_<Phase>` | `PMO_SYNAPSE_L4_Phase1` |
| Registry Board | `PMO_REGISTRY` | `PMO_REGISTRY` |
| Portfolio Dashboard | `PMO_PORTFOLIO_DASHBOARD` | — |

- `<ProjectCode>`：大写字母+数字，最长 8 字符（例：SYNAPSE、FINLEASE、HUB）
- `<Phase>`：Phase1 / Phase2 / Phase3（对应 L1 阶段）

### 2.2 WBS Board Column 结构

每个 WBS Board（`PMO_<Code>_WBS`）包含以下 Column：

| Column 名称 | Column ID（建议） | 类型 | 用途 | 对应 Asana 概念 |
|-------------|-----------------|------|------|----------------|
| Name | name（内置） | text | 任务/交付物名称 | Task Name |
| Status | status | status | 任务状态 | Custom Field: Status |
| Owner | person | people | 负责人 | Assignee |
| Priority | priority | color | 优先级（P0-P3） | Custom Field: Priority |
| Due Date | due_date | date | 截止日期 | Due Date |
| Dependency | dependency | dependency | 前置依赖关系 | Dependencies |
| WBS Level | wbs_level | text | L1/L2/L3 标识 | Custom Field |
| WBS Code | wbs_code | text | 例：1.2.3 | Custom Field |
| L4 Board Link | l4_link | board_relation | 关联 L4 Link Board | Subtask（改造） |
| WorkDoc | workdoc | doc | 项目文档入口 | — |
| Notes | notes | long_text | 备注 / 工作说明 | Notes |
| Created By | created_by | text | 记录创建来源（pmo-api / manual） | — |

**Status 列可选值（与原 Asana 状态对齐）：**

| 标签 | 颜色 | 对应 Asana 状态 |
|------|------|----------------|
| Not Started | 灰 | — |
| In Progress | 蓝 | In Progress |
| Stuck | 红 | Blocked |
| Done | 绿 | Completed |
| Cancelled | 深灰 | Cancelled |

**Priority 列可选值：**

| 标签 | 颜色 |
|------|------|
| P0 Critical | 红 |
| P1 High | 橙 |
| P2 Medium | 黄 |
| P3 Low | 灰 |

### 2.3 WBS 四层映射

```
WBS L0 项目
  └─▶ Monday Board（命名：PMO_<Code>_WBS）
      │  一个项目对应一个 Board
      │
WBS L1 阶段（Phase）
  └─▶ Monday Group
      │  例：Phase 1 - Initiation
      │      Phase 2 - Planning
      │      Phase 3 - Execution
      │      Phase 4 - Closure
      │
WBS L2 可交付成果（Deliverable）
  └─▶ Monday Item（位于对应 Group 下）
      │  含 Dependency Column（前置 Item 关联）
      │  含 WBS Code（例：1.2）
      │
WBS L3 工作包（Work Package）
  └─▶ Monday Subitem（绑定于对应 L2 Item）
      │  含 Owner / Due Date / Status
      │  含 WBS Code（例：1.2.3）
      │
WBS L4 子工作包（Task）
  └─▶ Link Board（命名：PMO_<Code>_L4_<Phase>）
         通过 board_relation Column 连接至 WBS Board
         Mirror Column 反映 L4 Board 的 Status / Owner
```

#### Link Board 模式工作原理

由于 Monday Multi-Level Board API 存在 403 硬限制（Subitem 的 Subitem 不可通过 API 编程），采用 Link Board 替代方案：

1. **创建独立 L4 Board**（`PMO_<Code>_L4_<Phase>`）：结构与 WBS Board 相同，但专门存放 L4 任务。
2. **在 WBS Board 添加 `board_relation` Column**：命名为 `L4 Board Link`，指向该 L4 Board。
3. **在 WBS Board 添加 Mirror Column**：镜像 L4 Board 的 Status / Owner 列，在主 Board 中可见 L4 进展。
4. **L3 Subitem 与 L4 Item 关联**：在 L4 Board 中，每个 Item 的自定义 Column 记录所属 L3 Subitem ID。
5. **可视化效果**：在 WBS Board 任意 Item 展开后，可通过 L4 Board Link Column 跳转查看完整 L4 任务列表。

**connect_boards GraphQL 示意：**

```graphql
mutation {
  create_column(
    board_id: "<WBS_BOARD_ID>",
    title: "L4 Board Link",
    column_type: board_relation,
    defaults: "{\"boardIds\": [\"<L4_BOARD_ID>\"]}"
  ) {
    id
    title
  }
}
```

### 2.4 Portfolio Dashboard 设计

**Dashboard 命名：** `PMO_PORTFOLIO_DASHBOARD`

该 Dashboard 聚合所有 `PMO_*_WBS` Board 的数据，提供跨项目视图。

**Widget 列表：**

| Widget 名称 | 类型 | 数据源 | 描述 |
|-------------|------|--------|------|
| 活跃项目总览 | Summary | 所有 WBS Board | 在建项目数 / 已完成项目数 |
| 逾期任务警报 | Battery / Table | Due Date < Today + Status ≠ Done | 按项目分组的逾期任务 |
| 团队负载分布 | Workload | Owner Column | 每人当前分配任务数 |
| WBS 进度甘特 | Gantt | Due Date + Dependency | 里程碑时间线 |
| 任务状态分布 | Pie Chart | Status Column | Done/In Progress/Stuck 比例 |
| 本周完成趋势 | Line Chart | Status + 时间戳 | 最近 14 天完成任务数 |
| 关键路径 P0 | Table | Priority = P0 Critical | 高优先级任务列表 |
| 阻塞任务 | Table | Status = Stuck | 需要关注的阻塞项 |

---

## 第 3 章：WF-01~09 适配方案

**负责人：harness_engineer + ai_systems_dev**

### 3.1 工作流改动总览

| WF | 原功能 | 改动内容 | 新触发源 | 新目标 API |
|----|--------|---------|---------|-----------|
| WF-01 | 读 Notion Registry → 创 Asana 项目 → 生 Notion Hub | 读 Monday Registry Board → 创 WBS Board → 生 WorkDoc | 手动触发 / Monday Automation | pmo-api /run-wbs-monday + /create_project_workdoc |
| WF-02 | 检查 Notion WBS DB → 调用 pmo-api /run-wbs | 读 Monday Registry 状态列 → 调用 pmo-api /run-wbs-monday | 定时 / Monday Column Change Webhook | pmo-api /run-wbs-monday |
| WF-03 | WBS L1/L2 Sections 创建（Asana） | 已合并进 WF-02 调用链（pmo-api 内部处理） | — | pmo-api 内部 |
| WF-04 | WBS L3 工序创建（Asana Tasks） | 已合并进 WF-02 调用链 | — | pmo-api 内部 |
| WF-05 | WBS L4 子任务创建 + Assignee 分配 + staticData 去重 | L4 改用 Link Board；幂等去重改为 notified_events 表 | — | pmo-api 内部 |
| WF-06 | 兜底轮询完成通知（60min） | 保留机制，改为轮询 Monday Board 状态 | 定时（60min） | pmo-api /check-monday-status（新端点） |
| WF-07 | 预留 | 保持预留 | — | — |
| WF-08 | Asana Webhook → pmo-api → Slack | Monday Webhook → pmo-api → Slack | Monday Webhook | pmo-api /webhooks/monday |
| WF-09 | Asana Webhook 注册覆盖率告警（每日 09:05） | Monday Board Webhook 覆盖率检查 | 定时（每日 09:05 Dubai） | pmo-api /webhooks/monday/coverage |

### 3.2 WF-01 详细规格（项目初始化）

**触发条件：**
- 手动触发（测试/首次上线）
- Monday Automation：Registry Board 中 Item 的 `Init Status` 列变为 `Pending`

**执行步骤：**

```
Step 1: 读取 Monday Registry Board（GraphQL boards.items_page）
        获取字段：project_code / project_name / wbs_template / charter_url

Step 2: 调用 pmo-api /run-wbs-monday
        Body: { project_code, project_name, wbs_template }
        pmo-api 完成：
          2a. create_board（PMO_<Code>_WBS）
          2b. create_group × L1 阶段数
          2c. create_item × L2 可交付成果
          2d. create_subitem × L3 工作包
          2e. create_link_board + connect（L4，如 wbs_template 含 L4）
        返回：{ board_id, group_ids, item_ids, link_board_ids }

Step 3: 调用 pmo-api /create_project_workdoc
        Body: { board_id, project_name, charter_url }
        pmo-api 完成：
          3a. 在 WBS Board 主 Item（L0）中创建 WorkDoc
          3b. 写入标准模板 Blocks（见第 5 章）
          3c. 返回 workdoc_url

Step 4: 回写 Monday Registry Board
        将 board_id / workdoc_url 写入 Registry Item 对应列
        将 Init Status 改为 Active

Step 5: n8n 发送 Slack 通知
        内容："项目 <project_name> 已初始化，WBS Board: <board_url>"
```

### 3.3 WF-02~05 详细规格（WBS 生成执行链）

原 WF-02~05 分别负责 L1/L2/L3/L4 的不同层级，迁移后统一由 pmo-api /run-wbs-monday 一次性完成，n8n 侧简化为单次调用。

**WF-02 新版（触发 + 调度）：**

```
触发条件：
  A. 定时触发（可配置：每天 08:00 Dubai）
  B. Monday Webhook（Registry Board Item 状态变更）

执行步骤：
  1. 读取 Monday Registry Board，筛选 Init Status = Pending 的项目
  2. 对每个 Pending 项目，调用 pmo-api /run-wbs-monday
  3. 收集执行结果，更新 Registry Board 状态
  4. 若任一项目失败，触发 Slack 告警
```

**WF-03/04/05 状态：** 降级为文档记录（历史工作流），在 n8n 中标记为 `Archived`，功能已内化至 pmo-api。

### 3.4 WF-08 详细规格（实时状态通知）

**替换原 Asana HMAC Webhook：**

```
Monday Webhook 触发（item 状态列变更）
    │
    ▼
n8n WF-08（Webhook 节点，监听 /webhooks/monday 路径）
    │
    ▼
转发至 pmo-api /webhooks/monday
    Body: { event: { type, pulseId, boardId, columnId, value } }
    │
    ▼
pmo-api 执行：
  1. MondayWebhookValidator.validate(request)
     - IP 白名单检查
     - 时间戳窗口检查（±300s）
  2. Challenge 握手处理（若 body.challenge 存在，原样返回）
  3. 幂等去重（notified_events 表，key: monday_<item_id>_<event_type>）
  4. 解析事件：item_id / board_id / new_status
  5. 构造通知消息
    │
    ▼
n8n 回调节点 → Slack #pmo-notifications
    消息格式："[<project_code>] <item_name> 状态变更为 <new_status>"
```

### 3.5 WF-09 详细规格（Webhook 覆盖率监控）

**原功能：** 检查 Asana 项目是否有注册 Webhook，未注册则告警。

**新功能：** 检查 Monday 活跃 Board 是否有注册 Webhook，覆盖率低于 100% 则 Slack 告警。

```
触发：定时（每日 09:05 Dubai）

执行步骤：
  1. 从 pmo-api /webhooks/monday/coverage 获取覆盖率报告
     返回：{ total_active_boards, boards_with_webhook, coverage_rate, uncovered_boards[] }
  2. 若 coverage_rate < 1.0：
     发送 Slack 告警：
     "⚠️ Monday Webhook 覆盖率 <rate>%，未覆盖 Board：<list>"
  3. 若 coverage_rate = 1.0：
     记录日志，无需通知
```

---

## 第 4 章：pmo-api 重写规格

**负责人：ai_systems_dev**

### 4.1 需要重写的文件列表

| 文件 | 重写比例 | 主要变化 |
|------|---------|---------|
| `monday_client.py`（新增） | 100% 新文件 | Monday GraphQL 完整封装 |
| `wbs_to_monday.py`（新增） | 100% 新文件 | WBS → Monday 结构转换逻辑 |
| `monday_webhook_validator.py`（新增） | 100% 新文件 | IP 白名单 + 时间戳安全验证 |
| `wbs_to_asana.py` | 保留（只读归档） | 迁移期双轨并行，最终废弃 |
| `asana_webhook_handler.py` | 保留（只读归档） | 同上 |
| `routes/wbs_routes.py` | 60% 重写 | 新增 /run-wbs-monday 端点 |
| `routes/webhook_routes.py` | 80% 重写 | 新增 /webhooks/monday 系列端点 |
| `routes/hub_routes.py` | 80% 重写 | /create_project_workdoc 替代原 Notion 接口 |
| `models/notified_events.py` | 20% 修改 | event_key 格式更新 |
| `config.py` | 30% 修改 | 新增 Monday 相关环境变量 |

### 4.2 MondayClient 类设计

```python
# monday_client.py

import os
import time
import requests
from typing import Optional, Dict, Any, List

MONDAY_API_URL = "https://api.monday.com/v2"
MONDAY_RATE_LIMIT = 40        # 每秒最大请求数（Pro 方案）
MONDAY_RETRY_MAX = 5          # 最大重试次数
MONDAY_RETRY_BASE_DELAY = 1.0 # 初始重试延迟（秒）


class MondayRateLimitError(Exception):
    pass


class MondayAPIError(Exception):
    def __init__(self, message: str, status_code: int = None, errors: list = None):
        super().__init__(message)
        self.status_code = status_code
        self.errors = errors or []


class MondayClient:
    """
    Monday.com GraphQL API 客户端。
    封装限速控制、指数退避重试、错误处理。
    
    环境变量：
        MONDAY_API_TOKEN: Monday API 访问令牌（必填）
        MONDAY_WORKSPACE_ID: 默认 Workspace ID（可选，不传则使用 Main）
    """

    def __init__(
        self,
        api_token: Optional[str] = None,
        workspace_id: Optional[str] = None
    ):
        self.api_token = api_token or os.environ["MONDAY_API_TOKEN"]
        self.workspace_id = workspace_id or os.environ.get("MONDAY_WORKSPACE_ID")
        self._request_timestamps: List[float] = []  # 滑动窗口限速记录

    # ─────────────────────────── 内部工具 ────────────────────────────

    def _throttle(self):
        """滑动窗口限速：确保 1 秒内不超过 MONDAY_RATE_LIMIT 次请求。"""
        now = time.time()
        self._request_timestamps = [t for t in self._request_timestamps if now - t < 1.0]
        if len(self._request_timestamps) >= MONDAY_RATE_LIMIT:
            sleep_time = 1.0 - (now - self._request_timestamps[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        self._request_timestamps.append(time.time())

    def _execute(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """
        执行 GraphQL 请求，含指数退避重试。
        
        Args:
            query: GraphQL query / mutation 字符串
            variables: 变量字典（可选）
        
        Returns:
            data 字段内容（dict）
        
        Raises:
            MondayAPIError: API 返回错误或网络异常
            MondayRateLimitError: 超出重试次数仍限速
        """
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        headers = {
            "Authorization": self.api_token,
            "Content-Type": "application/json",
            "API-Version": "2024-01"
        }
        
        for attempt in range(MONDAY_RETRY_MAX):
            self._throttle()
            try:
                resp = requests.post(MONDAY_API_URL, json=payload, headers=headers, timeout=30)
            except requests.RequestException as e:
                if attempt == MONDAY_RETRY_MAX - 1:
                    raise MondayAPIError(f"网络请求失败: {e}")
                delay = MONDAY_RETRY_BASE_DELAY * (2 ** attempt)
                time.sleep(delay)
                continue

            if resp.status_code == 429:
                if attempt == MONDAY_RETRY_MAX - 1:
                    raise MondayRateLimitError("Monday API 限速，已达最大重试次数")
                delay = MONDAY_RETRY_BASE_DELAY * (2 ** attempt)
                time.sleep(delay)
                continue

            if resp.status_code != 200:
                raise MondayAPIError(f"HTTP {resp.status_code}", status_code=resp.status_code)

            body = resp.json()
            if "errors" in body and body["errors"]:
                raise MondayAPIError(
                    str(body["errors"]),
                    errors=body["errors"]
                )
            return body.get("data", {})
        
        raise MondayAPIError("已达最大重试次数")

    # ─────────────────────────── Board 操作 ──────────────────────────

    def create_board(
        self,
        project_code: str,
        board_suffix: str = "WBS",
        workspace_id: Optional[str] = None,
        folder_id: Optional[str] = None
    ) -> str:
        """
        创建 WBS Board。
        
        Returns:
            新建 Board 的 ID（字符串）
        """
        name = f"PMO_{project_code}_{board_suffix}"
        ws_id = workspace_id or self.workspace_id
        
        mutation = """
        mutation($name: String!, $workspace_id: ID, $folder_id: ID) {
          create_board(
            board_name: $name,
            board_kind: public,
            workspace_id: $workspace_id,
            folder_id: $folder_id
          ) {
            id
          }
        }
        """
        variables = {"name": name, "workspace_id": ws_id, "folder_id": folder_id}
        data = self._execute(mutation, variables)
        return data["create_board"]["id"]

    # ─────────────────────────── Group 操作 ──────────────────────────

    def create_group(self, board_id: str, phase_name: str) -> str:
        """
        在 Board 中创建 Group（对应 L1 阶段）。
        
        Returns:
            新建 Group 的 ID
        """
        mutation = """
        mutation($board_id: ID!, $group_name: String!) {
          create_group(board_id: $board_id, group_name: $group_name) {
            id
          }
        }
        """
        data = self._execute(mutation, {"board_id": board_id, "group_name": phase_name})
        return data["create_group"]["id"]

    # ─────────────────────────── Item 操作 ───────────────────────────

    def create_item(
        self,
        board_id: str,
        group_id: str,
        item_name: str,
        column_values: Optional[Dict] = None
    ) -> str:
        """
        在 Board+Group 下创建 Item（对应 L2 可交付成果）。
        
        Args:
            column_values: {column_id: value} 字典，例：
                {
                    "status": {"label": "Not Started"},
                    "person": {"personsAndTeams": [{"id": 12345, "kind": "person"}]},
                    "date4": {"date": "2026-06-30"},
                    "wbs_code": "1.2",
                    "priority": {"label": "P1 High"}
                }
        
        Returns:
            新建 Item 的 ID
        """
        import json
        cv_str = json.dumps(column_values or {})
        
        mutation = """
        mutation($board_id: ID!, $group_id: String!, $item_name: String!, $column_values: JSON) {
          create_item(
            board_id: $board_id,
            group_id: $group_id,
            item_name: $item_name,
            column_values: $column_values
          ) {
            id
          }
        }
        """
        variables = {
            "board_id": board_id,
            "group_id": group_id,
            "item_name": item_name,
            "column_values": cv_str
        }
        data = self._execute(mutation, variables)
        return data["create_item"]["id"]

    # ─────────────────────────── Subitem 操作 ────────────────────────

    def create_subitem(
        self,
        parent_item_id: str,
        name: str,
        column_values: Optional[Dict] = None
    ) -> str:
        """
        在父 Item 下创建 Subitem（对应 L3 工作包）。
        
        Returns:
            新建 Subitem 的 ID
        """
        import json
        cv_str = json.dumps(column_values or {})
        
        mutation = """
        mutation($parent_item_id: ID!, $item_name: String!, $column_values: JSON) {
          create_subitem(
            parent_item_id: $parent_item_id,
            item_name: $item_name,
            column_values: $column_values
          ) {
            id
            board {
              id
            }
          }
        }
        """
        variables = {
            "parent_item_id": parent_item_id,
            "item_name": name,
            "column_values": cv_str
        }
        data = self._execute(mutation, variables)
        return data["create_subitem"]["id"]

    # ─────────────────────────── Link Board 操作（L4）────────────────

    def create_link_board(self, project_code: str, phase: str) -> str:
        """
        创建 L4 Link Board（命名：PMO_<Code>_L4_<Phase>）。
        
        Returns:
            新建 Board 的 ID
        """
        return self.create_board(project_code, f"L4_{phase}")

    def connect_boards(
        self,
        main_board_id: str,
        link_board_id: str,
        column_title: str = "L4 Board Link"
    ) -> str:
        """
        在主 Board 上创建 board_relation Column 连接 Link Board。
        
        Returns:
            新建 Column 的 ID
        """
        import json
        defaults = json.dumps({"boardIds": [link_board_id]})
        
        mutation = """
        mutation($board_id: ID!, $title: String!, $defaults: String) {
          create_column(
            board_id: $board_id,
            title: $title,
            column_type: board_relation,
            defaults: $defaults
          ) {
            id
          }
        }
        """
        variables = {
            "board_id": main_board_id,
            "title": column_title,
            "defaults": defaults
        }
        data = self._execute(mutation, variables)
        return data["create_column"]["id"]

    # ─────────────────────────── WorkDoc 操作 ────────────────────────

    def create_workdoc(
        self,
        item_id: str,
        doc_column_id: str,
        content_blocks: Optional[List[Dict]] = None
    ) -> str:
        """
        在 Item 的 doc Column 下创建 WorkDoc。
        
        Args:
            item_id: 关联 Item ID
            doc_column_id: doc 类型 Column 的 ID
            content_blocks: WorkDoc 内容 Blocks（见第 5 章模板）
        
        Returns:
            WorkDoc 的 object_id（可构造 URL）
        """
        # Step 1: 创建空 doc
        create_doc_mutation = """
        mutation($item_id: ID!, $column_id: String!) {
          create_doc(
            location: {
              board: {
                item_id: $item_id,
                column_id: $column_id
              }
            }
          ) {
            id
            url
          }
        }
        """
        data = self._execute(create_doc_mutation, {
            "item_id": item_id,
            "column_id": doc_column_id
        })
        doc_id = data["create_doc"]["id"]
        doc_url = data["create_doc"]["url"]

        # Step 2: 写入内容 Blocks
        if content_blocks:
            import json
            blocks_json = json.dumps(content_blocks)
            blocks_mutation = """
            mutation($doc_id: ID!, $blocks: String!) {
              create_doc_blocks(
                doc_id: $doc_id,
                blocks: $blocks
              ) {
                id
                type
              }
            }
            """
            self._execute(blocks_mutation, {
                "doc_id": doc_id,
                "blocks": blocks_json
            })

        return doc_url
```

### 4.3 wbs_to_monday.py 设计

```python
# wbs_to_monday.py

from typing import Dict, Any, List, Optional
from monday_client import MondayClient
import logging
import concurrent.futures

logger = logging.getLogger(__name__)


def run_wbs_to_monday(
    project_id: str,
    wbs_data: Dict[str, Any],
    monday_client: MondayClient,
    workspace_id: Optional[str] = None,
    folder_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    将 WBS 数据写入 Monday.com，创建完整的 L0-L4 层级结构。
    
    Args:
        project_id:     项目代码，例 "SYNAPSE"
        wbs_data:       WBS 数据字典（从 Monday Registry Board 读取），结构：
                        {
                          "project_name": "...",
                          "phases": [
                            {
                              "name": "Phase 1 - Initiation",
                              "deliverables": [
                                {
                                  "name": "...",
                                  "wbs_code": "1.1",
                                  "owner_id": 12345,
                                  "due_date": "2026-06-15",
                                  "priority": "P1 High",
                                  "depends_on_codes": ["1.0"],  # 前置依赖的 wbs_code
                                  "work_packages": [
                                    {
                                      "name": "...",
                                      "wbs_code": "1.1.1",
                                      "owner_id": 12345,
                                      "tasks": [...]  # L4，如有
                                    }
                                  ]
                                }
                              ]
                            }
                          ]
                        }
        monday_client:  已初始化的 MondayClient 实例
        workspace_id:   目标 Workspace ID（可选）
        folder_id:      目标文件夹 ID（可选）
    
    Returns:
        创建结果摘要：
        {
          "board_id": "...",
          "group_ids": {"Phase 1 - Initiation": "...", ...},
          "item_ids": {"1.1": "...", ...},       # wbs_code → item_id
          "subitem_ids": {"1.1.1": "...", ...},  # wbs_code → subitem_id
          "link_board_ids": {"Phase1": "...", ...},
          "errors": []
        }
    """
    result = {
        "board_id": None,
        "group_ids": {},
        "item_ids": {},
        "subitem_ids": {},
        "link_board_ids": {},
        "errors": []
    }

    # ─── 1. L0：创建 WBS Board ────────────────────────────────────────
    logger.info(f"[WBS] 创建 Board: PMO_{project_id}_WBS")
    board_id = monday_client.create_board(
        project_id, "WBS", workspace_id, folder_id
    )
    result["board_id"] = board_id

    # ─── 2. L1：创建 Group（阶段）────────────────────────────────────
    # 串行执行（Group 顺序影响 Board 显示顺序，不并发）
    for phase in wbs_data.get("phases", []):
        phase_name = phase["name"]
        logger.info(f"[WBS] 创建 Group: {phase_name}")
        group_id = monday_client.create_group(board_id, phase_name)
        result["group_ids"][phase_name] = group_id

    # ─── 3. L2：创建 Item（可交付成果）──────────────────────────────
    # 注意：依赖关系需要先全部创建 Item 后再建立，否则引用的 item_id 不存在
    dependency_map: List[tuple] = []  # [(item_id, depends_on_item_id), ...]

    for phase in wbs_data.get("phases", []):
        group_id = result["group_ids"][phase["name"]]
        for deliverable in phase.get("deliverables", []):
            column_values = _build_item_column_values(deliverable)
            logger.info(f"[WBS] 创建 Item: {deliverable['name']}")
            item_id = monday_client.create_item(
                board_id, group_id,
                deliverable["name"], column_values
            )
            result["item_ids"][deliverable["wbs_code"]] = item_id
            
            # 记录依赖关系，待所有 Item 创建完后统一处理
            for dep_code in deliverable.get("depends_on_codes", []):
                dependency_map.append((deliverable["wbs_code"], dep_code))

    # ─── 3b. 建立依赖关系 ────────────────────────────────────────────
    for (code, dep_code) in dependency_map:
        if dep_code in result["item_ids"]:
            item_id = result["item_ids"][code]
            dep_item_id = result["item_ids"][dep_code]
            try:
                _set_dependency(monday_client, board_id, item_id, dep_item_id)
            except Exception as e:
                result["errors"].append(f"依赖关系设置失败 {code}->{dep_code}: {e}")

    # ─── 4. L3：创建 Subitem（工作包）───────────────────────────────
    # 可并发执行（Subitem 之间无依赖顺序要求）
    subitem_tasks = []
    for phase in wbs_data.get("phases", []):
        for deliverable in phase.get("deliverables", []):
            parent_item_id = result["item_ids"].get(deliverable["wbs_code"])
            for wp in deliverable.get("work_packages", []):
                subitem_tasks.append((parent_item_id, wp))

    # 并发创建 Subitem（线程池，受 MondayClient._throttle 限速控制）
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(
                monday_client.create_subitem,
                parent_id,
                wp["name"],
                _build_subitem_column_values(wp)
            ): wp
            for parent_id, wp in subitem_tasks
            if parent_id is not None
        }
        for future, wp in futures.items():
            try:
                subitem_id = future.result()
                result["subitem_ids"][wp["wbs_code"]] = subitem_id
            except Exception as e:
                result["errors"].append(f"Subitem 创建失败 {wp['wbs_code']}: {e}")

    # ─── 5. L4：创建 Link Board 并连接（如有）───────────────────────
    for phase in wbs_data.get("phases", []):
        has_l4 = any(
            wp.get("tasks")
            for d in phase.get("deliverables", [])
            for wp in d.get("work_packages", [])
        )
        if not has_l4:
            continue

        phase_key = phase["name"].replace(" ", "").replace("-", "")
        logger.info(f"[WBS] 创建 L4 Link Board: {phase_key}")
        l4_board_id = monday_client.create_link_board(project_id, phase_key)
        result["link_board_ids"][phase_key] = l4_board_id

        # 在主 Board 上创建 board_relation Column
        monday_client.connect_boards(board_id, l4_board_id)

        # 在 L4 Board 中创建 Group 和 Item（L4 任务）
        _populate_l4_board(monday_client, l4_board_id, phase, result)

    logger.info(f"[WBS] 完成，board_id={board_id}，错误数={len(result['errors'])}")
    return result


def _build_item_column_values(deliverable: Dict) -> Dict:
    """将 WBS 数据字段映射为 Monday column_values 格式。"""
    cv = {}
    if deliverable.get("owner_id"):
        cv["person"] = {"personsAndTeams": [{"id": deliverable["owner_id"], "kind": "person"}]}
    if deliverable.get("due_date"):
        cv["date4"] = {"date": deliverable["due_date"]}
    if deliverable.get("priority"):
        cv["priority"] = {"label": deliverable["priority"]}
    cv["status"] = {"label": "Not Started"}
    if deliverable.get("wbs_code"):
        cv["wbs_code"] = deliverable["wbs_code"]
    cv["created_by"] = "pmo-api"
    return cv


def _build_subitem_column_values(wp: Dict) -> Dict:
    """为 Subitem 构造 column_values。"""
    cv = {}
    if wp.get("owner_id"):
        cv["person"] = {"personsAndTeams": [{"id": wp["owner_id"], "kind": "person"}]}
    if wp.get("due_date"):
        cv["date4"] = {"date": wp["due_date"]}
    cv["status"] = {"label": "Not Started"}
    if wp.get("wbs_code"):
        cv["wbs_code"] = wp["wbs_code"]
    cv["created_by"] = "pmo-api"
    return cv


def _set_dependency(client: MondayClient, board_id: str, item_id: str, dep_item_id: str):
    """
    设置 Item 的 Dependency Column 值。
    dependency column_values 格式：{"dependencyOf": ["<dep_item_id>"]}
    """
    import json
    mutation = """
    mutation($board_id: ID!, $item_id: ID!, $column_id: String!, $value: JSON!) {
      change_column_value(
        board_id: $board_id,
        item_id: $item_id,
        column_id: $column_id,
        value: $value
      ) {
        id
      }
    }
    """
    value = json.dumps({"item_ids": [int(dep_item_id)]})
    client._execute(mutation, {
        "board_id": board_id,
        "item_id": item_id,
        "column_id": "dependency",
        "value": value
    })


def _populate_l4_board(client, l4_board_id, phase, result):
    """在 L4 Board 中填充任务（L4 Item）。"""
    for deliverable in phase.get("deliverables", []):
        for wp in deliverable.get("work_packages", []):
            for task in wp.get("tasks", []):
                parent_subitem_id = result["subitem_ids"].get(wp["wbs_code"])
                cv = _build_item_column_values(task)
                cv["l3_subitem_ref"] = wp.get("wbs_code", "")  # 记录所属 L3
                group_id = result["group_ids"].get(phase["name"], "")
                # L4 Board 中用同名 Group 组织
                try:
                    client.create_item(l4_board_id, group_id, task["name"], cv)
                except Exception as e:
                    result["errors"].append(f"L4 任务创建失败 {task.get('name')}: {e}")
```

**并发控制策略说明：**

- L1 Group、L2 Item：**串行**创建，保证 Board 显示顺序和依赖关系的正确性。
- L3 Subitem：**并发**创建（ThreadPoolExecutor，max_workers=5），受 MondayClient._throttle() 控制，实际每秒不超过 40 次请求（Pro 方案限制）。
- L4 Task：**串行**创建（L4 Board 中 Group 顺序需要保证）。
- 指数退避重试：由 MondayClient._execute() 统一处理，最多 5 次，延迟 1→2→4→8→16 秒。

### 4.4 Monday Webhook 安全层设计

```python
# monday_webhook_validator.py

import ipaddress
import time
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Monday.com 官方出口 IP 段
# 来源：https://support.monday.com/hc/en-us/articles/360002494235
# 注意：官方 IP 列表可能更新，建议订阅 Monday 状态页变更通知
MONDAY_IP_WHITELIST = [
    "52.214.0.0/16",    # EU-West (Ireland)
    "52.48.0.0/14",     # EU-West (Ireland) extended
    "34.252.0.0/15",    # EU-West (Ireland)
    "54.93.0.0/16",     # EU-Central (Frankfurt)
    "18.185.0.0/16",    # EU-Central (Frankfurt)
    "3.64.0.0/13",      # EU-Central (Frankfurt) extended
    "52.1.0.0/16",      # US-East (Virginia)
    "52.2.0.0/15",      # US-East
    "54.156.0.0/14",    # US-East extended
    "52.52.0.0/15",     # US-West (Oregon)
    "54.176.0.0/14",    # US-West extended
    "18.144.0.0/15",    # US-West (N. California)
]

TIMESTAMP_WINDOW_SECONDS = 300  # 5 分钟时间窗口


class MondayWebhookValidator:
    """
    Monday.com Webhook 安全验证器。
    
    验证策略：
    1. IP 白名单（基于 Monday 官方出口 IP 段）
    2. 时间戳窗口（防重放攻击，±300 秒）
    3. Challenge 握手（Monday 首次注册 Webhook 时发送 challenge）
    
    注意：Monday 不提供 HMAC 签名（不同于 Asana），
    安全性主要依赖 IP 白名单 + HTTPS + 时间戳验证。
    """

    def __init__(
        self,
        ip_whitelist: Optional[list] = None,
        timestamp_window: int = TIMESTAMP_WINDOW_SECONDS
    ):
        self._parsed_networks = [
            ipaddress.ip_network(cidr, strict=False)
            for cidr in (ip_whitelist or MONDAY_IP_WHITELIST)
        ]
        self.timestamp_window = timestamp_window

    def validate_ip(self, client_ip: str) -> bool:
        """
        验证请求来源 IP 是否在 Monday 官方 IP 段内。
        
        Args:
            client_ip: 客户端 IP（字符串，支持 IPv4 / IPv6）
        
        Returns:
            True 表示来源合法
        """
        try:
            addr = ipaddress.ip_address(client_ip)
            result = any(addr in network for network in self._parsed_networks)
            if not result:
                logger.warning(f"[MondayWebhook] IP 不在白名单: {client_ip}")
            return result
        except ValueError:
            logger.error(f"[MondayWebhook] 无法解析 IP: {client_ip}")
            return False

    def validate_timestamp(self, event_timestamp: int) -> bool:
        """
        验证事件时间戳是否在合法窗口内（防重放攻击）。
        
        Args:
            event_timestamp: Unix 时间戳（秒级）
        
        Returns:
            True 表示时间戳合法
        """
        now = int(time.time())
        diff = abs(now - event_timestamp)
        if diff > self.timestamp_window:
            logger.warning(f"[MondayWebhook] 时间戳超出窗口: diff={diff}s > {self.timestamp_window}s")
            return False
        return True

    def validate(self, client_ip: str, event_timestamp: Optional[int] = None) -> bool:
        """
        综合验证（IP + 时间戳）。
        
        Args:
            client_ip:       请求来源 IP
            event_timestamp: 事件时间戳（秒级，可选）
        
        Returns:
            True 表示验证通过
        """
        if not self.validate_ip(client_ip):
            return False
        if event_timestamp is not None:
            if not self.validate_timestamp(event_timestamp):
                return False
        return True


def handle_challenge(body: dict) -> Optional[dict]:
    """
    处理 Monday Webhook Challenge 握手。
    
    Monday 在首次注册 Webhook 时会发送包含 'challenge' 字段的请求，
    服务器必须原样返回该 challenge 值，Monday 才会确认 Webhook 注册成功。
    
    Args:
        body: 请求 body（dict）
    
    Returns:
        若为 challenge 请求，返回 {"challenge": "<value>"}；
        否则返回 None（继续正常处理流程）。
    """
    if "challenge" in body:
        challenge_value = body["challenge"]
        logger.info(f"[MondayWebhook] 收到 Challenge 握手，原样返回: {challenge_value}")
        return {"challenge": challenge_value}
    return None
```

### 4.5 新增 API 端点规格

| 端点 | 方法 | 功能 | 替代原端点 |
|------|------|------|-----------|
| `/run-wbs-monday` | POST | WBS 生成，结果写入 Monday Board | `/run-wbs`（写 Asana） |
| `/webhooks/monday` | POST | 接收 Monday Webhook 事件，验证并转发 | `/webhooks/asana` |
| `/webhooks/monday/register` | POST | 向 Monday 注册指定 Board 的 Webhook | `/webhooks/asana/register` |
| `/webhooks/monday/coverage` | GET | 检查活跃 Board 的 Webhook 覆盖率 | — |
| `/create_project_workdoc` | POST | 在 Board Item 下创建 WorkDoc（标准模板） | `/create_project_hub` |
| `/check-monday-status` | GET | 查询 Board 完成状态（WF-06 兜底轮询） | Asana 任务查询 |

**`/run-wbs-monday` 请求/响应规格：**

```
POST /run-wbs-monday
Content-Type: application/json

Request Body:
{
  "project_id": "SYNAPSE",          // 必填，项目代码
  "project_name": "Synapse Hub",    // 必填
  "wbs_source": "registry",         // "registry"（从 Monday Registry 读）或 "inline"
  "wbs_data": { ... },              // 当 wbs_source=inline 时提供
  "workspace_id": "...",            // 可选，默认使用环境变量
  "folder_id": "..."                // 可选
}

Response 200:
{
  "status": "success",
  "board_id": "...",
  "board_url": "https://janusd.monday.com/boards/...",
  "group_count": 4,
  "item_count": 12,
  "subitem_count": 28,
  "link_board_ids": { "Phase1Initiation": "..." },
  "errors": []
}

Response 422:
{
  "status": "partial_success",
  "board_id": "...",
  "errors": ["Subitem 创建失败 1.1.1: ..."]
}
```

**`/webhooks/monday` 请求处理流程：**

```python
# routes/webhook_routes.py（核心逻辑）

@app.post("/webhooks/monday")
async def monday_webhook(request: Request):
    body = await request.json()
    
    # 1. Challenge 握手处理（优先级最高）
    challenge_response = handle_challenge(body)
    if challenge_response:
        return JSONResponse(challenge_response)
    
    # 2. 安全验证
    client_ip = request.client.host
    event_ts = body.get("event", {}).get("createdAt")  # Unix ms → 转秒
    if event_ts:
        event_ts = event_ts // 1000
    
    validator = MondayWebhookValidator()
    if not validator.validate(client_ip, event_ts):
        logger.warning(f"[Webhook] 验证失败，IP={client_ip}")
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # 3. 幂等去重
    event = body.get("event", {})
    item_id = event.get("pulseId")
    event_type = event.get("type")
    event_key = f"monday_{item_id}_{event_type}"
    
    if notified_events.exists(event_key):
        return JSONResponse({"status": "duplicate_ignored"})
    notified_events.record(event_key)
    
    # 4. 异步派发处理
    background_tasks.add_task(process_monday_event, event)
    return JSONResponse({"status": "accepted"})
```

### 4.6 notified_events 表适配

**event_key 格式变更：**

| 字段 | 原格式（Asana） | 新格式（Monday） |
|------|----------------|----------------|
| event_key | `asana_<task_gid>_<event_type>` | `monday_<item_id>_<event_type>` |
| event_type 示例 | `task_completed` | `change_column_value` |
| item_id 示例 | Asana Task GID（字符串） | Monday Item ID（数字字符串） |

**其他字段无需变更：**

```sql
-- notified_events 表结构（无需迁移）
CREATE TABLE notified_events (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  event_key   TEXT NOT NULL UNIQUE,   -- 仅此字段格式变更
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  metadata    TEXT                    -- JSON，可选
);
```

**数据迁移注意事项：**
- 双轨期间旧 `asana_*` 记录保留，新 `monday_*` 记录新增
- 切换完成后，可定期清理 90 天前的 `asana_*` 记录

---

## 第 5 章：Notion Hub → Monday WorkDocs 迁移方案

**负责人：ai_systems_dev + harness_engineer**

### 5.1 WorkDoc 模板设计

每个项目初始化时，`/create_project_workdoc` 自动创建以下结构的 WorkDoc：

```
WorkDoc 结构（Block 层级）
│
├─ [heading_1] 项目名称（动态填入 project_name）
│
├─ [text] 项目基本信息
│   内容：Charter 摘要（project_code / owner / start_date / end_date）
│
├─ [divider] ──────────────────────────
│
├─ [heading_2] 实时 WBS 进度
├─ [board_widget] 嵌入 WBS Board（实时数据）
│   参数：board_id（WBS Board ID）
│         view：甘特图 / 看板（默认甘特）
│
├─ [divider] ──────────────────────────
│
├─ [heading_2] 项目 KPI 概览
├─ [dashboard_widget] 嵌入 Portfolio Dashboard（过滤当前项目）
│
├─ [divider] ──────────────────────────
│
├─ [heading_2] 当前状态（pmo-api 自动写入）
├─ [text] 状态摘要（最后更新时间 / 整体进度 % / 当前阻塞）
│
├─ [divider] ──────────────────────────
│
├─ [heading_2] 里程碑进度
└─ [table] 里程碑表格
     列：里程碑名称 / 目标日期 / 当前状态 / 负责人
```

**Block 类型对应 Monday API `block_type` 值：**

| 显示内容 | block_type | 说明 |
|---------|-----------|------|
| 标题 H1 | `normal_text`（size: large） | Monday WorkDoc 标题 Block |
| 标题 H2 | `normal_text`（size: medium） | 二级标题 |
| 正文文字 | `normal_text` | 普通文本 |
| 分隔线 | `divider` | — |
| Board 嵌入 | `board_item` | 需要 board_id 参数 |
| 表格 | `table` | 里程碑表格 |

### 5.2 `/create_project_workdoc` 接口规格

```
POST /create_project_workdoc
Content-Type: application/json

Request Body:
{
  "board_id": "...",              // WBS Board ID（必填）
  "project_name": "Synapse Hub",  // 必填
  "project_code": "SYNAPSE",      // 必填
  "charter_summary": {            // 可选，Charter 摘要
    "owner": "刘子杨",
    "start_date": "2026-05-01",
    "end_date": "2026-08-31",
    "objective": "..."
  },
  "doc_column_id": "workdoc",     // WBS Board 上 doc Column 的 ID
  "anchor_item_id": "..."         // 关联的 Item ID（通常是项目根 Item）
}

Response 200:
{
  "status": "success",
  "doc_id": "...",
  "doc_url": "https://janusd.monday.com/docs/...",
  "blocks_created": 12
}
```

**实现流程：**

```python
def create_project_workdoc(body: dict, monday_client: MondayClient) -> dict:
    content_blocks = _build_standard_template(
        project_name=body["project_name"],
        project_code=body["project_code"],
        board_id=body["board_id"],
        charter_summary=body.get("charter_summary", {})
    )
    
    doc_url = monday_client.create_workdoc(
        item_id=body["anchor_item_id"],
        doc_column_id=body["doc_column_id"],
        content_blocks=content_blocks
    )
    
    # 将 WorkDoc URL 回写至 Monday Registry Board
    _update_registry_workdoc_url(
        monday_client,
        project_code=body["project_code"],
        doc_url=doc_url
    )
    
    return {"status": "success", "doc_url": doc_url}
```

---

## 第 6 章：Monday Registry Board 设计

**负责人：harness_engineer**

### 6.1 Registry Board 完整 Column 结构

Board 命名：`PMO_REGISTRY`，放置于 Main Workspace / PMO 文件夹。

| Column Name | Column ID | Type | Purpose | Replaces Notion Field |
|-------------|----------|------|---------|----------------------|
| Project Name | `name` | text | Full project name | Name |
| Project Code | `text_mm2vy6jg` | text | Unique identifier (uppercase, ≤8 chars) | project_code |
| Project Status | `color_mm2v52nt` | status | Active / On Hold / Completed / Archived | status |
| Init Status | `color_mm2vmmgs` | status | Pending / In Progress / Done / Failed | — |
| WBS Board ID | `text_mm2vbp4r` | text | Linked Monday WBS Board ID | asana_project_id |
| WBS Board URL | `link_mm2vjjmy` | link | Direct WBS Board link | asana_project_url |
| WorkDoc URL | `link_mm2vr8bx` | link | WorkDoc direct link | notion_hub_url |
| Project Owner | `multiple_person_mm2veqfd` | people | Project owner | owner |
| Start Date | `date_mm2vzx79` | date | Project start date | start_date |
| End Date | `date_mm2v6k5e` | date | Target end date | end_date |
| WBS Template | `dropdown_mm2v21n9` | dropdown | WBS template type | wbs_template |
| Charter URL | `link_mm2vx0bn` | link | Project charter document link | charter_url |
| Slack Channel | `text_mm2v3kwm` | text | Notification Slack channel ID | slack_channel |
| Notes | `long_text_mm2vjasa` | long_text | Operational notes | notes |

> **已创建（2026-04-28）** — Board ID `5095424024` · URL: https://janusd-company.monday.com/boards/5095424024

### 6.2 WF-01 触发逻辑（从 Registry Board 读取）

```python
# n8n WF-01 中的 Monday GraphQL 查询节点

query = """
query {
  boards(ids: [PMO_REGISTRY_BOARD_ID]) {
    items_page(
      limit: 100,
      query_params: {
        rules: [
          { column_id: "init_status", compare_value: ["Pending"] }
        ]
      }
    ) {
      items {
        id
        name
        column_values {
          id
          text
        }
      }
    }
  }
}
"""
# 筛选 init_status = Pending 的项目
# 对每个项目触发 WF-01 初始化流程
```

**Notion Registry 字段映射对照：**

| Notion Registry 字段 | Monday Registry Column | 迁移注意事项 |
|---------------------|----------------------|------------|
| Name | name（内置） | 直接迁移 |
| project_code | project_code | 直接迁移 |
| asana_project_id | wbs_board_id | 值从 Asana GID → Monday Board ID |
| notion_hub_url | workdoc_url | 值从 Notion URL → Monday WorkDoc URL |
| status | project_status | 状态值需对齐（Notion Enum → Monday Status） |
| wbs_template | wbs_template | 直接迁移 |

---

## 第 6.5 章：英文数据源（Notion）— EN Notion Source Databases

**负责人：notion_architect + ai_systems_dev**

> 为实现 PMO Monday Auto 全英文运行，在 Notion PMO Monday Auto 页面创建两个英文版数据库作为 `wbs_to_monday.py` 的读取数据源。中文原始数据库（项目注册表 / WBS工序数据库）完全不变，Asana 流程不受影响。

### 6.5.1 英文数据库清单

| 数据库 | Notion ID | 用途 | 对应原库 |
|--------|-----------|------|---------|
| 📁 EN Project Registry | `61e17074-706d-4e17-855d-f34b15d6a75c` | wbs_to_monday.py 读取项目注册信息 | 项目注册表 (29aba1e3) |
| 🗂️ EN WBS Task Database | `922aa4bd-73e5-48d4-aca8-4d7504ce6652` | wbs_to_monday.py 读取 WBS 工序数据 | WBS工序数据库 (079e04b9) |

Notion 链接：
- EN Project Registry: https://www.notion.so/61e17074706d4e17855df34b15d6a75c
- EN WBS Task Database: https://www.notion.so/922aa4bd73e548d4aca84d7504ce6652

### 6.5.2 wbs_to_monday.py 配置变更

`wbs_to_monday.py` 中所有 Notion DB 读取需从中文库切换至英文库：

```python
# config.py — 新增 Monday 数据源配置
NOTION_EN_PROJECT_REGISTRY_DB_ID = os.getenv(
    "NOTION_EN_PROJECT_REGISTRY_DB_ID",
    "61e17074-706d-4e17-855d-f34b15d6a75c"
)
NOTION_EN_WBS_TASK_DB_ID = os.getenv(
    "NOTION_EN_WBS_TASK_DB_ID",
    "922aa4bd-73e5-48d4-aca8-4d7504ce6652"
)
```

字段名映射（中文原库 → 英文新库）：

| 原字段（中文库） | 新字段（英文库） | 说明 |
|----------------|----------------|------|
| WBS编码 | WBS Code | title 字段 |
| 任务名称 | Task Name | rich_text |
| 层级 | Level | select: L0/L1/L2/L3/L4 |
| 工期(天) | Duration Days | number |
| 标准工期(天) | Standard Duration Days | number |
| 所属阶段 | Phase | select (English options) |
| 阶段门 | Gate | select: G0-Charter…G5-Handover |
| 执行流 | Execution Flow | select (English options) |
| 负责角色 | Role | select: PM/DE/SA/CDE/QA/Sales |
| 并行组 | Parallel Group | rich_text |
| 前置依赖编码 | Predecessor Code | rich_text |
| 关键交付物 | Deliverable | rich_text |
| 跨流依赖 | Cross Flow Dependency | rich_text |
| 工序状态 | Task Status | select: Not Started/In Progress/Done/Blocked/Cancelled |
| (新增) | Critical Path | checkbox |

### 6.5.3 并行策略

```
中文库（项目注册表 / WBS工序数据库）
  → wbs_to_asana.py → Asana → n8n.lysander.bond（完全不变）

英文库（EN Project Registry / EN WBS Task Database）
  → wbs_to_monday.py → Monday.com → n8n.janusd.io（新路径）
```

两套系统完全解耦，数据录入需双轨维护（每个新项目需同时在中文库和英文库录入），
直至 Asana 流程正式退役。

---

## 第 7 章：迁移执行方案（Phase 2 详细步骤）

**负责人：ai_systems_dev + integration_qa + harness_engineer**

### 7.1 Phase 2 前置条件

在开始任何迁移工作前，必须满足以下全部条件：

| # | 条件 | 验证方式 |
|---|------|---------|
| 1 | Monday Pro 方案已激活（Automation Actions ≥25,000次/月） | Monday 账单页截图 |
| 2 | n8n.janusd.io 稳定运行满 5 个工作日（Phase 1 稳定期） | n8n 健康监控日志 |
| 3 | pmo-api 部署环境可更新（CI/CD 管线正常） | 测试部署一次验证 |
| 4 | Monday API Token 获取并安全存储（不得明文写入代码） | Credential Store 验证 |
| 5 | Monday Webhook 出口 IP 列表已从官方文档获取 | 对比 MONDAY_IP_WHITELIST 常量 |

### 7.2 Step 0：环境准备

- **0.1** Monday Pro 激活确认 + API Token 写入 Credential Store
  - 路径：n8n Credentials → 新建 Monday API 凭证
  - 同时写入 pmo-api 部署环境变量 `MONDAY_API_TOKEN`
- **0.2** 在 Main Workspace 创建 PMO 文件夹（通过 Monday UI 或 create_folder API）
  - 获取 folder_id，写入 pmo-api 环境变量 `MONDAY_PMO_FOLDER_ID`
- **0.3** 创建 `PMO_REGISTRY` Board ✅ COMPLETED 2026-04-28
  - Board ID: `5095424024`
  - Board URL: https://janusd-company.monday.com/boards/5095424024
  - Workspace ID: `6203977`
  - 所有 14 个 Column 已创建，Column ID 映射见第 6 章
  - 环境变量：`MONDAY_REGISTRY_BOARD_ID=5095424024`，`MONDAY_WORKSPACE_ID=6203977`
- **0.4** 获取 Monday Webhook 出口 IP 最新列表
  - 来源：https://support.monday.com/hc/en-us/articles/360002494235
  - 更新 `monday_webhook_validator.py` 中 `MONDAY_IP_WHITELIST` 常量
  - 提交 Git，更新 pmo-api 部署

### 7.3 Step 1：pmo-api 重写

- **1.1** MondayClient 类开发（`monday_client.py`）
  - 单元测试：覆盖所有 public 方法，mock HTTP 层
  - 集成测试：使用 Monday 测试账号真实 API 调用（测试 Board 中执行）
- **1.2** wbs_to_monday.py 开发
  - 单元测试：输入标准 WBS 数据，验证输出 `result` 结构
  - 集成测试：在测试 Board 创建完整 L0-L4 结构，人工验证显示效果
- **1.3** MondayWebhookValidator 开发
  - 安全测试：
    - 合法 IP + 有效时间戳 → 通过
    - 非白名单 IP → 403
    - 超时时间戳（±301s）→ 403
    - Challenge 握手 → 正确返回 challenge 值
- **1.4** 新 API 端点开发（`/run-wbs-monday`、`/webhooks/monday` 系列）
  - 集成测试：端到端调用，验证数据链路
- **1.5** `/create_project_workdoc` 接口开发
  - 集成测试：调用后验证 Monday WorkDoc 中 Blocks 内容正确

### 7.4 Step 2：n8n 工作流适配

- **2.1** 在 n8n.janusd.io 添加 Monday API Token 凭证（`MONDAY_API` 凭证名称）
- **2.2** WF-01 改造：
  - 触发节点：Monday Webhook（或定时轮询 Registry Board）
  - 删除 Notion API 节点，替换为 Monday GraphQL 节点
  - 替换 Asana 项目创建节点，改为调用 pmo-api /run-wbs-monday
  - 添加 WorkDoc 创建节点（调用 pmo-api /create_project_workdoc）
  - 单独端到端测试（用真实测试项目验证全链路）
- **2.3** WF-02~05 改造：
  - 删除 Notion WBS DB 读取节点
  - 替换触发逻辑（Monday Registry Board 状态变更）
  - 合并为单个 pmo-api 调用节点（/run-wbs-monday）
  - WF-03/04/05 标记为 Archived（保留 90 天后删除）
- **2.4** WF-08 改造：
  - Webhook 触发 URL 切换至 `/webhooks/monday`
  - 删除 Asana HMAC 验证节点
  - 验证 Challenge 握手流程正常
- **2.5** WF-09 改造：
  - 替换查询逻辑（Monday Board Webhook 覆盖率）
  - 调用 pmo-api /webhooks/monday/coverage
- **2.6** 每个 WF 单独端到端测试，结果记录至 integration_qa 验收报告

### 7.5 Step 3：Webhook 注册与安全验证

- **3.1** 向 Monday 注册 PMO WBS Board 的 Webhook
  - 事件类型：`change_column_value`（Status 列变更）
  - 目标 URL：`https://pmo-api.janusd.io/webhooks/monday`
  - 通过 `/webhooks/monday/register` 端点自动化注册
- **3.2** IP 白名单测试（由 integration_qa 执行）：
  - 模拟 Monday IP 发送请求 → 期望 200
  - 使用非白名单 IP 发送请求 → 期望 403
- **3.3** 时间戳验证测试：
  - 有效时间戳（now - 60s）→ 期望 200
  - 超时时间戳（now - 400s）→ 期望 403
- **3.4** 输出安全验证报告（存入 `obs/04-decision-knowledge/`，格式参考 M2-D 验收标准）

### 7.6 Step 4：双轨期（72 小时）

- **4.1** 进行中 Asana 任务手动迁移至 Monday
  - 使用 pmo-api 专用迁移脚本（`migrate_asana_to_monday.py`，新增工具）
  - 对每个活跃 Asana 项目：创建对应 Monday Board，迁移任务数据
- **4.2** 72 小时内，Asana 和 Monday 同时写入
  - pmo-api 双写开关：`DUAL_WRITE_MODE=true`
  - 每小时监控双向一致性（item 数量 / 状态分布对比）
- **4.3** 人工监控阶段
  - integration_qa 每 4 小时检查一次数据一致性
  - 发现不一致项立即上报，修复后继续计时
  - 72 小时无严重不一致 → 进入 Step 5

### 7.7 Step 5：切换与验收

- **5.1** 停止 Asana 写入（`DUAL_WRITE_MODE=false`，`ASANA_WRITE=false`）
- **5.2** Asana 账号降级为只读（保留 90 天，用于历史数据查阅）
- **5.3** 全量回归测试（按第 8 章验收标准 M2-A 到 M2-H 逐项验证）
- **5.4** Notion Hub 页面迁移：
  - 在每个旧 Notion Hub 页面顶部添加 Banner："✅ 本项目已迁移至 Monday WorkDocs"
  - 附 WorkDoc 直链
  - 原 Notion 页面保留 90 天后归档

---

## 第 8 章：验收标准

**负责人：integration_qa**

| 编号 | 标准描述 | 验证方式 | 优先级 |
|------|---------|---------|-------|
| M2-A | WBS 生成端到端成功：`/run-wbs-monday` 调用 → Monday Board 中 L1/L2/L3 结构正确创建，L4 Link Board 已连接 | 使用真实 WBS 数据测试，API 验证 item 数量 + 结构 | P0 |
| M2-B | 任务状态变更通知链路：Monday Item 状态改为 Done → Webhook 触发 → pmo-api 处理 → n8n → Slack 收到通知 | 端到端操作测试，记录完整链路时延（目标 <30s） | P0 |
| M2-C | L4 Link Board 结构可视：连接关系在主 WBS Board 中可见，Mirror Column 正确反映 L4 状态 | UI 截图 + GraphQL 查询验证 mirror_value | P1 |
| M2-D | 安全验证通过：IP 白名单、时间戳验证均通过 integration_qa 安全测试报告（见 Step 3） | 提交安全验证报告文档 | P0 |
| M2-E | WorkDoc 自动生成：项目初始化后 WorkDoc URL 自动写入 Registry Board 对应 Item | UI 截图 + Registry Board 数据验证 | P1 |
| M2-F | Registry Board 数据完整：所有活跃项目已录入 Monday Registry Board，Notion Registry 已标注"已迁移" | 数据行数对比 + 字段完整性检查 | P1 |
| M2-G | Asana 只读验证：Asana 账号已降级，通过 pmo-api 尝试写入 Asana 返回权限错误 | API 调用验证 + 截图 | P2 |
| M2-H | n8n 工作流状态：n8n.janusd.io 中所有新 WF active，旧 WF（Asana 版）已 paused | n8n UI 状态截图 | P1 |

**验收判定规则：**
- P0 全部通过 → 可正式切换
- P1 全部通过 → 可归档旧系统
- P2 全部通过 → Phase 2 完整交付

---

## 第 9 章：风险矩阵

**负责人：harness_engineer + integration_qa**

| # | 风险描述 | 概率 | 影响 | 风险等级 | 控制措施 |
|---|---------|------|------|---------|---------|
| R01 | Monday Webhook 无 HMAC 签名，存在伪造风险 | 中 | 高 | 🔴 高 | IP 白名单 + 时间戳验证 + HTTPS（TLS 1.3）；定期更新 IP 白名单；非 Monday IP 一律 403 |
| R02 | Monday GraphQL 并发限速（Pro: 40 req/s）导致大型 WBS 生成超时 | 中 | 中 | 🟡 中 | 滑动窗口限速 + 指数退避重试；L3 Subitem 并发上限 5 线程；大型项目分批次提交 |
| R03 | WorkDoc API 参数变化（Monday 未通知 API changelog） | 低 | 高 | 🟡 中 | 订阅 Monday Developer changelog；pmo-api 中 WorkDoc 调用封装为独立模块，便于快速更新；集成测试覆盖 WorkDoc 创建路径 |
| R04 | Notion Registry 迁移期数据不一致（双轨期内 Notion 有新写入） | 中 | 中 | 🟡 中 | 双轨期冻结 Notion Registry 写入（只读模式）；迁移前备份 Notion Registry 完整数据导出 |
| R05 | L4 Link Board 数量增长，Board 管理混乱（每个项目×阶段 = N boards） | 高 | 低 | 🟡 中 | 严格命名规范（`PMO_<Code>_L4_<Phase>`）；文件夹隔离（每项目一子文件夹）；定期清理已归档项目 Board |
| R06 | Monday Pro 方案 Automation Actions 耗尽（25,000次/月） | 低 | 高 | 🟡 中 | pmo-api 直接调用 GraphQL API（不依赖 Monday 内置 Automation）；监控 Action 消耗量，接近 80% 时告警 |
| R07 | n8n.janusd.io 不稳定导致 Webhook 事件丢失 | 低 | 高 | 🟡 中 | WF-06 兜底轮询（60 分钟）补偿丢失事件；pmo-api notified_events 幂等保证重试安全；n8n 内置重试机制（3 次） |
| R08 | Monday API Token 泄露 | 低 | 极高 | 🔴 高 | Token 仅存储于 Credential Store（n8n）和 pmo-api 环境变量，不入代码仓库；.env 加入 .gitignore；每 90 天轮换一次 Token |

---

## 附录 A：Monday GraphQL 关键 Mutation 速查

**负责人：ai_systems_dev**

> 以下 Mutation 均经过 API 版本 `2024-01` 验证，可直接复制使用。
> 替换 `<BOARD_ID>`、`<GROUP_ID>`、`<ITEM_ID>` 等占位符为实际值。

### A.1 create_board

```graphql
mutation {
  create_board(
    board_name: "PMO_SYNAPSE_WBS",
    board_kind: public,
    workspace_id: <WORKSPACE_ID>,
    folder_id: <FOLDER_ID>
  ) {
    id
    name
    url
  }
}
```

### A.2 create_group

```graphql
mutation {
  create_group(
    board_id: "<BOARD_ID>",
    group_name: "Phase 1 - Initiation"
  ) {
    id
    title
  }
}
```

### A.3 create_item（含 column_values 示例）

```graphql
mutation {
  create_item(
    board_id: "<BOARD_ID>",
    group_id: "<GROUP_ID>",
    item_name: "1.1 项目章程",
    column_values: "{
      \"status\": {\"label\": \"Not Started\"},
      \"person\": {\"personsAndTeams\": [{\"id\": 34769438, \"kind\": \"person\"}]},
      \"date4\": {\"date\": \"2026-06-15\"},
      \"priority\": {\"label\": \"P1 High\"},
      \"wbs_code\": \"1.1\",
      \"created_by\": \"pmo-api\"
    }"
  ) {
    id
    name
  }
}
```

**注意：** `column_values` 为 JSON 字符串（需转义引号）。实际代码中使用 `json.dumps()` 处理。

### A.4 create_subitem

```graphql
mutation {
  create_subitem(
    parent_item_id: "<PARENT_ITEM_ID>",
    item_name: "1.1.1 撰写项目范围说明书",
    column_values: "{
      \"status\": {\"label\": \"Not Started\"},
      \"person\": {\"personsAndTeams\": [{\"id\": 34769438, \"kind\": \"person\"}]},
      \"date4\": {\"date\": \"2026-06-10\"},
      \"wbs_code\": \"1.1.1\"
    }"
  ) {
    id
    name
    board {
      id
    }
  }
}
```

### A.5 create_doc（创建空 WorkDoc）

```graphql
mutation {
  create_doc(
    location: {
      board: {
        item_id: "<ITEM_ID>",
        column_id: "workdoc"
      }
    }
  ) {
    id
    url
    object_id
  }
}
```

### A.6 create_doc_blocks（写入 WorkDoc 内容）

```graphql
mutation {
  create_doc_blocks(
    doc_id: "<DOC_ID>",
    blocks: "[
      {
        \"type\": \"normal_text\",
        \"content\": {
          \"deltaFormat\": [
            {\"insert\": \"项目名称\", \"attributes\": {\"bold\": true, \"font-size\": \"large\"}}
          ]
        }
      },
      {
        \"type\": \"normal_text\",
        \"content\": {
          \"deltaFormat\": [
            {\"insert\": \"项目代码：SYNAPSE\\n负责人：刘子杨\\n开始日期：2026-05-01\"}
          ]
        }
      },
      {
        \"type\": \"divider\"
      }
    ]"
  ) {
    id
    type
    content
  }
}
```

### A.7 change_column_value（设置依赖关系）

```graphql
mutation {
  change_column_value(
    board_id: "<BOARD_ID>",
    item_id: "<ITEM_ID>",
    column_id: "dependency",
    value: "{\"item_ids\": [<DEP_ITEM_ID>]}"
  ) {
    id
  }
}
```

### A.8 boards.items_page（查询 Registry Board）

```graphql
query {
  boards(ids: [<REGISTRY_BOARD_ID>]) {
    items_page(
      limit: 100,
      query_params: {
        rules: [
          {
            column_id: "init_status",
            compare_value: ["Pending"],
            operator: any_of
          }
        ]
      }
    ) {
      cursor
      items {
        id
        name
        column_values {
          id
          text
          value
        }
      }
    }
  }
}
```

---

*文档版本：1.0.0 | 创建于：2026-04-27 | 下次审查：2026-10-27*
*作者：harness_engineer | 审阅：Lysander CEO*
