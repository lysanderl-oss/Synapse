# Synapse 升级协议 — 参考模块
# [ADDED: 2026-04-12]
# 本文件由 CLAUDE.md 提取。按需读取，非会话启动时自动加载。
# 触发场景：用户说"升级 Synapse"/"更新体系"/"同步最新版本"/"/upgrade"

## 🔄 体系升级指令（Synapse Upgrade Protocol）

当用户说以下任意指令时，自动启动升级流程：
- `"升级 Synapse"` / `"更新体系"` / `"同步最新版本"` / `"/upgrade"`

**升级流程**（由 `harness_engineer` 执行，`Lysander` 审查）：

```
Step 1：读取本地版本
        cat VERSION → 获取当前版本号

Step 2：获取最新版本信息
        访问 https://lysander.bond/synapse/version.json
        → 返回 { version, release_date, changelog, download_url }

Step 3：版本对比 + Changelog 展示
        如 本地版本 == 最新版本 → 提示"已是最新版本"，结束
        如 本地版本 < 最新版本 → 向总裁展示 Changelog，请求确认

Step 4：总裁确认后执行升级
        → 下载最新 CLAUDE.md（Core Harness 区域）
        → 保留用户配置区的个人化设置（CEO名/总裁名/公司名）
        → 更新 VERSION 文件

Step 5：QA 验证
        integration_qa 验证新配置完整性（关键约束项是否存在）

Step 6：提示重启
        "升级完成，请关闭并重新打开 Claude Code 会话，新配置即刻生效。"
```

**注意**：升级只替换 Core Harness 区域，用户个人化配置区（CEO名/总裁名）不受影响。
