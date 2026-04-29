---
id: synapsehd-com-activation-runbook
type: reference
status: published
lang: zh
version: 1.0
published_at: 2026-04-26
updated_at: 2026-04-26
author: knowledge_engineer
review_by: [Lysander, ai_systems_dev]
audience: [team_partner, technical_builder]
stale_after: 2026-10-30
---

# synapsehd.com 备案完成后激活 Runbook

## 触发条件
火山引擎 ICP 备案审核通过 → 立即执行本 runbook

## 前置完成情况（截至 2026-04-26）
- 服务器（118.196.41.252）SSH alias 配置完成
- Nginx 安装 + 80 端口配置 + listen synapsehd.com / www.synapsehd.com
- lysander-bond 代码 clone + build + 部署到 /home/synapsehd-website/dist
- www.synapsehd.com HTTP 可访问（200 OK，完整内容）
- astro.config.mjs SITE_URL 环境变量化（兼容 lysander.bond 主站）
- GitHub Actions deploy-volcano job 准备（待手动触发或备案后启用）
- 裸根域名 synapsehd.com 仍被 Volcano WAF 302 拦截（待备案）

## 步骤 1：验证备案状态

### 1.1 控制台验证
登录火山引擎控制台 → 备案管理 → 查看 synapsehd.com 状态：
- 期望：**已通过 / 备案号 [备案号]**

### 1.2 网络验证
```bash
curl -sIL --max-time 15 http://synapsehd.com/
# 期望：HTTP 200（不再 302 → webblock.volcengine.com）

curl -sIL --max-time 15 http://www.synapsehd.com/
# 期望：HTTP 200（保持）
```

如 1.1 完成但 1.2 仍 302：等待 Volcano WAF 同步（通常几分钟到 1 小时）

## 步骤 2：启用 HTTPS

### 2.1 检查证书申请条件
```bash
ssh synapsehd-server "
which certbot || apt install -y certbot python3-certbot-nginx
nginx -t
"
```

### 2.2 申请 Let's Encrypt 证书
```bash
ssh synapsehd-server "
certbot --nginx \
  -d synapsehd.com \
  -d www.synapsehd.com \
  --non-interactive \
  --agree-tos \
  --email lysanderl@janusd.io \
  --redirect 2>&1 | tail -10
"
```

certbot --nginx 会自动：
- 申请双域名（裸根 + www）证书
- 修改 /etc/nginx/sites-available/synapsehd 加 listen 443
- 配置 HTTP→HTTPS 强制 redirect
- 重载 nginx

### 2.3 验证 HTTPS
```bash
curl -sIL --max-time 15 https://synapsehd.com/ | head -3
curl -sIL --max-time 15 https://www.synapsehd.com/ | head -3
# 期望：HTTP 200 + valid SSL
```

## 步骤 3：触发 GitHub Actions deploy-volcano

```bash
gh workflow run deploy-volcano.yml --ref main 2>&1 || \
echo "Manual trigger via GitHub UI: Actions → deploy-volcano → Run workflow"

# 等待运行
sleep 60
gh run list --workflow=deploy-volcano.yml --limit 3
```

期望：success（约 60-90 秒）

## 步骤 4：canonical/hreflang/sitemap 验证

由于 SITE_URL 已在 deploy-volcano 中设置为 `https://synapsehd.com`，构建产物的 SEO meta 应该指向 synapsehd.com：

```bash
curl -sL https://synapsehd.com/about | grep -oE 'canonical[^>]*'
# 期望：rel="canonical" href="https://synapsehd.com/about/"

curl -sL https://synapsehd.com/about | grep -oE 'hreflang[^>]*' | head -3
# 期望：3 条，全部含 synapsehd.com

curl -sL https://synapsehd.com/sitemap-0.xml | grep -oE 'https://[^<]+' | head -5
# 期望：全部 synapsehd.com
```

## 步骤 5：全站 UAT 回归（25+ URL）

派 integration_qa agent 执行：
- HTTP 200 全站抽样（25+ URL）
- hreflang 三联完整性
- 301 redirects 兼容
- 双语切换功能
- LangToggle 行为
- LICENSE / USAGE_TERMS GitHub raw 200

## 步骤 6：Pipeline Product 锁版

### 6.1 更新 VERSION
```bash
echo "1.1.1-multi-deploy" > VERSION
```

### 6.2 更新 CHANGELOG
追加 v1.1.1 条目（multi-deploy 变更摘要）

### 6.3 创建 metric baseline
`pipeline-metrics/v1.1.1-multi-deploy.yaml`：
- lysander.bond 当前 metric
- synapsehd.com 当前 metric

### 6.4 git tag
```bash
git tag -a v1.1.1-multi-deploy -m "PATCH: synapsehd.com fully activated after ICP approval"
git push origin v1.1.1-multi-deploy
```

## 步骤 7：总裁简报

简报内容（不超过 200 字）：
- ICP 备案完成时间
- HTTPS 启用时间
- canonical/SEO 状态
- 全站 UAT 通过率
- v1.1.1 已锁版

## 失败回滚

### 备案未通过 / SSL 申请失败
- 保留 www.synapsehd.com HTTP（无需 SSL）作为临时入口
- 不启用 https://synapsehd.com 裸根
- active_tasks 状态改为 blocked，原因记录

### canonical 仍指向 lysander.bond
- 验证 GitHub Actions 是否成功传 SITE_URL 环境变量
- 检查 astro.config.mjs 是否正确读取 process.env.SITE_URL
- 必要时手动 build：`SITE_URL=https://synapsehd.com npm run build` + scp dist/

## 历史背景

- 2026-04-26：发现 Volcano WAF 拦截裸根域名（用户判断需修正）
- 2026-04-26：完成所有备案前可做的改造（代码 + GHA + 文档）
- 2026-04-27：总裁提交 ICP 备案
- 2026-04-30（预计）：备案完成 → 执行本 runbook

## 关联文档
- `obs/04-decision-knowledge/2026-04-26-strategic-overhaul-approval-package.md`
- `lysander-bond/PIPELINE.md`（治理框架）
- 火山引擎备案流程：https://console.volcengine.com/beian
