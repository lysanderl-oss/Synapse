#!/usr/bin/env python3
"""
build-distribution.py — Synapse 分发包构建脚本

从原始系统（只读）生成干净的可分发 Synapse 包，输出到 dist/ 目录。

用法：
  python scripts/build-distribution.py               # 正式构建（写入 dist/）
  python scripts/build-distribution.py --preview     # 预览模式（不写文件，仅输出计划）
  python scripts/build-distribution.py --version 1.2.0  # 指定版本号

de-tooling 规则（7类）：
  1. n8n 集成文件：完全排除
  2. 域名/账号特定信息：替换为占位符
  3. 时区硬编码：Dubai/Asia/Dubai → UTC+0
  4. Janus/Stock 特有团队：移至可选扩展
  5. 博客/微信自动化：移至可选扩展
  6. Notion OAuth / 特定 API：清除（active_tasks 用模板替换）
  7. CLAUDE.md 中的自动化编排具体内容：替换为通用说明

作者：Harness Ops 团队
"""

import os
import sys
import re
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# 配置
# ─────────────────────────────────────────────────────────────────────────────

# 目录（以脚本的父目录为基准）
SCRIPT_DIR = Path(__file__).parent
SRC_DIR = SCRIPT_DIR.parent          # 原始系统根目录（只读）
DIST_DIR = SRC_DIR / "dist"          # 输出目录

# 读取当前版本
VERSION_FILE = SRC_DIR / "VERSION"
try:
    CURRENT_VERSION = open(VERSION_FILE).readline().strip()
except Exception:
    CURRENT_VERSION = "1.1.0"

# ─────────────────────────────────────────────────────────────────────────────
# 黑名单：这些文件/目录完全不纳入 dist/
# ─────────────────────────────────────────────────────────────────────────────

BLACKLIST_FILES = {
    "agent-CEO/config/n8n_integration.yaml",           # n8n 集成（环境绑定）
    "agent-CEO/config/janus_experts.yaml",             # Janus 特有项目团队
    "agent-CEO/config/stock_experts.yaml",            # Stock 交易团队
    # active_tasks.yaml: 不在此处排除，由下方特殊处理器用模板替换（保留条目供注释说明）
    # "agent-CEO/config/active_tasks.yaml",            # ← 由特殊处理器替换为空白模板
    "scripts/n8n_wf_pmo_notion_oauth.json",               # Notion OAuth 工作流
    "scripts/_migration",                                 # Notion/PMO 数据迁移脚本（Janus 专属）
    "scripts/asana_notion_sync.py",                       # Asana-Notion 同步（项目专属）
    "scripts/project_space_init.py",                      # 项目空间初始化（Janus 专属）
    "scripts/wbs_data_source.py",                         # WBS 数据源（Janus 专属）
    "scripts/generate-illustrations.py",                  # 含 API Key 的私有插画生成脚本
    "scripts/gemini-illustrations.py",                    # 私有 Gemini API 脚本（含凭证）
    "obs/personal",                                        # 个人文件（目录）
    "obs/00-daily-work",                                   # 个人工作记录（目录）
    "obs/06-daily-reports",                               # 每日报告（目录，私有输出）
    "obs/generated-articles",                             # 生成文章（目录，私有输出）
    "obs/daily-intelligence",                             # 情报输出（目录，私有输出）
    "obs/credentials.md",                                 # 凭证文件
    "obs/credentials.mdenc",                              # 加密凭证
    # logs/ 目录：.gitkeep 会被复制（创建目录结构），.log 文件通过 BLACKLIST_EXTENSIONS 排除
    "dist",                                               # 输出目录自身
    ".git",                                               # Git 历史（不分发）
    "node_modules",                                       # 依赖
    "__pycache__",                                        # Python 缓存
    ".claude/projects",                                   # 项目记忆（私有）
    ".claude/plans",                                      # 计划文件（私有）
    ".claude/scheduled_tasks.lock",                       # 定时任务锁文件（环境绑定）
    "scripts/build-distribution.py",                      # 构建脚本自身不进 dist（不需要）
    "lysander-bond-rebuild",                              # 官网重建项目（私有开发资产）
    "obs/.obsidian/plugins/obsidian-git/data.json",       # Obsidian Git 个人配置
}

# 黑名单扩展名（不分发的文件类型）
BLACKLIST_EXTENSIONS = {
    ".mdenc",    # 加密文件
    ".env",      # 环境变量
    ".log",      # 运行日志（本地记录，不分发）
}

# ─────────────────────────────────────────────────────────────────────────────
# 内容替换规则
# 格式：(pattern, replacement, flags)
# ─────────────────────────────────────────────────────────────────────────────

CONTENT_REPLACEMENTS = [
    # 类型2：个人名字（中文无 \b 边界，直接匹配）
    (r"刘子杨", "{{PRESIDENT_NAME}}", 0),

    # 类型2：公司名
    (r"Synapse-PJ", "{{COMPANY_NAME}}", 0),

    # 类型2：个人 n8n 实例域名（保留 lysander.bond 主域，这是产品品牌域名）
    (r"https?://n8n\.lysander\.bond/[^\s\"')\]]*", "http://localhost:5678/webhook/...", 0),

    # 类型2：旧域名（janusd.com 是旧公司域名，非产品域名）
    (r"https?://www\.janusd\.com/?", "https://{{YOUR_WEBSITE}}/", 0),
    (r"\bjanusd\.com\b", "{{YOUR_DOMAIN}}", 0),

    # 类型2：邮箱
    (r"lysanderl@janusd\.io", "{{YOUR_EMAIL}}", 0),

    # 类型3：时区（Dubai 特定时区）
    (r"Asia/Dubai", "UTC", 0),
    (r"\b(\d+):(\d+)am\s+Dubai\b", r"\1:\2 UTC", re.IGNORECASE),
    (r"\b(\d+):(\d+)pm\s+Dubai\b", r"\1:\2 UTC", re.IGNORECASE),
    (r"8am Dubai", "your local time", re.IGNORECASE),
    (r"6am Dubai", "your local time", re.IGNORECASE),
    (r"10am Dubai", "your local time", re.IGNORECASE),

    # 类型2：系统路径中的用户名
    (r"/Users/lysanderl_janusd/", "/Users/{{YOUR_USERNAME}}/", 0),
    (r"C:\\\\Users\\\\lysanderl_janusd\\\\", "C:\\\\Users\\\\{{YOUR_USERNAME}}\\\\", 0),
    (r"C:/Users/lysanderl_janusd/", "C:/Users/{{YOUR_USERNAME}}/", 0),

    # 类型1：n8n trigger IDs（具体的触发器 ID）
    (r"trig_[A-Za-z0-9]+", "{{YOUR_N8N_TRIGGER_ID}}", 0),

    # 类型1：n8n webhook URLs（残留的）
    (r"https?://[^\s\"']*n8n[^\s\"']*", "http://localhost:5678/webhook/...", re.IGNORECASE),
    (r"http://localhost:5678/webhook/[^\s\"')\]]*", "http://localhost:5678/webhook/...", 0),

    # CEO Guard hooks：绝对路径 → 相对路径（适配任意项目目录）
    # settings.json 读入后字符序列为：node \"/c/Users/...\"（即 backslash + quote + path）
    # re pattern: \\\" 匹配字面 \" (1个反斜杠+引号)，[^\"]+ 匹配任意路径
    (r'node \\\"/[^\"]+ceo-guard-pre\.js\\\"', 'node scripts/ceo-guard-pre.js', 0),
    (r'node \\\"/[^\"]+ceo-guard-post\.js\\\"', 'node scripts/ceo-guard-post.js', 0),
]

# ─────────────────────────────────────────────────────────────────────────────
# 特殊文件处理器
# ─────────────────────────────────────────────────────────────────────────────

def handle_organization_yaml(content: str) -> str:
    """
    移除 janus 和 stock 团队的完整配置块。
    保留所有其他团队。
    """
    import yaml

    try:
        data = yaml.safe_load(content)
    except Exception as e:
        print(f"  ⚠️  organization.yaml YAML 解析失败：{e}")
        return content

    teams = data.get("teams", {})
    removed = []

    for team_key in ["janus", "stock"]:
        if team_key in teams:
            teams.pop(team_key)
            removed.append(team_key)

    if removed:
        print(f"  ✂️  移除团队：{', '.join(removed)}")

    # 同时更新 organization.name
    if "organization" in data and "name" in data["organization"]:
        data["organization"]["name"] = "{{COMPANY_NAME}}"

    # 重新序列化
    try:
        import yaml as yaml_mod
        result = yaml_mod.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)
        # 添加文件头注释
        header = (
            "# organization.yaml — Synapse 团队配置\n"
            "# 个性化：将 {{COMPANY_NAME}} 替换为你的公司名\n"
            "# 详见 CUSTOMIZATION_GUIDE.md\n\n"
        )
        return header + result
    except Exception:
        return content


def handle_claude_md(content: str) -> str:
    """
    CLAUDE.md 特殊处理：
    - 移除 n8n_integration.yaml 引用描述
    - 将自动化编排章节中的具体触发信息替换为通用说明
    """
    # 替换自动化编排章节中的具体内容
    automation_pattern = r"(### 自动化编排 — Harness Automation Layer.*?)(---|\Z)"
    automation_replacement = """### 自动化编排 — Harness Automation Layer（可选扩展）

执行链不仅在对话中运行，还可以通过自动化工具持续运转（无需你在线）。

**标准自动化场景**：
- 每日情报日报：定时触发 → 搜索 → 分析 → 生成报告
- 任务自动恢复：检查 active_tasks.yaml → 续接未完成工作
- 情报行动管线：情报→评估→执行→通知

**如何启用**：
参考 `docs/OPTIONAL_EXTENSIONS/` 目录中的扩展指南，选择适合你的自动化工具（n8n、定时任务、CI/CD 等）。

**不启用时**：直接对 AI CEO 说"开始今日情报日报"即可手动触发所有功能。

"""
    content = re.sub(automation_pattern, automation_replacement + "\n---", content, flags=re.DOTALL)

    # 移除对 n8n_integration.yaml 的引用行
    content = re.sub(r".*n8n_integration\.yaml.*\n", "", content)

    return content


def handle_active_tasks_yaml(src_dir: Path, dist_dir: Path) -> None:
    """
    不复制原 active_tasks.yaml，而是用模板替换。
    """
    template_src = src_dir / "scripts" / "templates" / "active_tasks.template.yaml"
    dest = dist_dir / "agent-CEO" / "config" / "active_tasks.yaml"

    if template_src.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(template_src, dest)
        print(f"  📋  active_tasks.yaml ← 使用模板（清空个人任务）")
    else:
        print(f"  ⚠️  模板文件不存在：{template_src}")


# ─────────────────────────────────────────────────────────────────────────────
# 残留个人信息扫描（验证步骤）
# ─────────────────────────────────────────────────────────────────────────────

RESIDUAL_PATTERNS = [
    (r"刘子杨", "个人名字「刘子杨」"),
    (r"Synapse-PJ", "公司名「Synapse-PJ」"),
    (r"lysanderl@janusd\.io", "邮箱地址"),
    # 注意：lysander.bond 是产品品牌域名，不扫描（在 SYNAPSE_SETUP.md、upgrade URL 中保留是正确的）
    (r"https?://n8n\.lysander\.bond", "n8n 个人实例域名"),
    (r"trig_[A-Za-z0-9]{10,}", "n8n trigger ID"),
    # 注意：n8n_integration.yaml 在决策文档中的引用是可接受的架构说明
    (r"Notion OAuth", "Notion OAuth 配置"),
    (r"lysanderl_janusd", "系统路径中的用户名"),
    (r"\bjanusd\.com\b", "旧公司域名（janusd.com）"),
    (r"sk-ant-api\d{2}-[A-Za-z0-9_-]{10,}", "Anthropic API Key（安全风险！）"),
    (r"AIzaSy[A-Za-z0-9_-]{33,}", "Google/Gemini API Key（安全风险！）"),
]


def scan_residuals(dist_dir: Path) -> list[tuple[str, str, str]]:
    """扫描 dist/ 目录中的残留个人信息。返回 [(文件路径, 模式描述, 匹配内容)]"""
    violations = []
    text_extensions = {".md", ".yaml", ".yml", ".py", ".json", ".txt", ".html", ".js", ".ts"}

    for file_path in dist_dir.rglob("*"):
        if file_path.is_dir():
            continue
        if file_path.suffix.lower() not in text_extensions:
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for pattern, description in RESIDUAL_PATTERNS:
            matches = re.findall(pattern, content)
            if matches:
                rel_path = str(file_path.relative_to(dist_dir))
                violations.append((rel_path, description, matches[0]))

    return violations


# ─────────────────────────────────────────────────────────────────────────────
# 核心构建逻辑
# ─────────────────────────────────────────────────────────────────────────────

def is_blacklisted(rel_path: str) -> bool:
    """检查文件是否在黑名单中"""
    p = Path(rel_path)

    # 检查扩展名黑名单
    if p.suffix.lower() in BLACKLIST_EXTENSIONS:
        return True

    # 检查文件/目录黑名单
    for item in BLACKLIST_FILES:
        item_path = Path(item)
        # 精确匹配或前缀匹配（目录）
        if p == item_path or str(p).startswith(str(item_path) + os.sep) or str(p).startswith(str(item_path) + "/"):
            return True
        # 检查路径中是否包含黑名单目录名
        if item in {"__pycache__", "node_modules", ".git", "dist"}:
            if item in p.parts:
                return True

    return False


def apply_content_replacements(content: str) -> tuple[str, int]:
    """应用内容替换规则，返回 (处理后内容, 替换次数)"""
    total_replacements = 0
    for pattern, replacement, flags in CONTENT_REPLACEMENTS:
        new_content, count = re.subn(pattern, replacement, content, flags=flags)
        total_replacements += count
        content = new_content
    return content, total_replacements


def build_distribution(preview: bool = False, version_override: str = None) -> bool:
    """
    执行构建。
    preview=True 时只输出计划，不写文件。
    返回 True 表示成功，False 表示有严重问题。
    """
    version = version_override or CURRENT_VERSION
    build_date = datetime.now().strftime("%Y-%m-%d")

    print(f"\n{'='*60}")
    print(f"Synapse 分发包构建")
    print(f"版本：{version}  日期：{build_date}")
    print(f"源目录：{SRC_DIR}")
    print(f"输出目录：{DIST_DIR}")
    print(f"模式：{'[预览] 不写文件' if preview else '[正式构建]'}")
    print(f"{'='*60}\n")

    if not preview:
        # 清空 dist/ 目录（Windows 需要特殊处理只读文件/目录）
        if DIST_DIR.exists():
            def handle_readonly(func, path, exc):
                """处理 Windows 只读文件删除问题（.git objects）"""
                import stat
                os.chmod(path, stat.S_IWRITE)
                func(path)
            shutil.rmtree(DIST_DIR, onerror=handle_readonly)
        DIST_DIR.mkdir(parents=True)

    # 统计
    stats = {"copied": 0, "skipped": 0, "modified": 0, "template_used": 0}
    skipped_items = []

    # ── 遍历所有文件 ──────────────────────────────────────────────────────────
    for src_path in sorted(SRC_DIR.rglob("*")):
        if src_path.is_dir():
            continue

        rel_path = src_path.relative_to(SRC_DIR)
        rel_str = str(rel_path).replace("\\", "/")

        # 检查黑名单
        if is_blacklisted(rel_str):
            stats["skipped"] += 1
            skipped_items.append(f"  ❌  跳过：{rel_str}")
            continue

        # 特殊处理：active_tasks.yaml（用模板替换）
        if rel_str == "agent-CEO/config/active_tasks.yaml":
            stats["template_used"] += 1
            if not preview:
                handle_active_tasks_yaml(SRC_DIR, DIST_DIR)
            else:
                print(f"  📋  [预览] active_tasks.yaml → 使用空白模板")
            continue

        # 读取文件内容
        try:
            is_text = src_path.suffix.lower() in {
                ".md", ".yaml", ".yml", ".py", ".json", ".txt", ".html",
                ".js", ".ts", ".css", ".sh", ".bat", ".ps1", ".toml", ".cfg", ".ini"
            }

            if is_text:
                content = src_path.read_text(encoding="utf-8", errors="ignore")
            else:
                content = None  # 二进制文件直接复制
        except Exception as e:
            print(f"  ⚠️  读取失败：{rel_str}：{e}")
            continue

        # 特殊文件处理器
        modified = False
        if is_text and content:
            original_content = content

            if rel_str == "agent-CEO/config/organization.yaml":
                content = handle_organization_yaml(content)
                modified = content != original_content

            elif rel_str == "CLAUDE.md":
                content = handle_claude_md(content)
                modified = content != original_content

            # 通用内容替换
            if is_text:
                content, replacement_count = apply_content_replacements(content)
                if replacement_count > 0:
                    modified = True

        # 写入 dist/
        dest_path = DIST_DIR / rel_path
        if not preview:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            if is_text and content is not None:
                dest_path.write_text(content, encoding="utf-8")
            else:
                shutil.copy2(src_path, dest_path)

        if modified:
            stats["modified"] += 1
            print(f"  ✏️  修改：{rel_str}")
        else:
            stats["copied"] += 1

    # ── 添加分发包专用文件 ───────────────────────────────────────────────────

    # 复制模板文件到 dist/templates/
    templates_src = SRC_DIR / "scripts" / "templates"
    if templates_src.exists():
        for tmpl_file in templates_src.iterdir():
            if tmpl_file.is_file():
                dest = DIST_DIR / "templates" / tmpl_file.name
                if not preview:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(tmpl_file, dest)
                print(f"  📦  模板：templates/{tmpl_file.name}")

    # 添加 synapse.config.yaml（空白配置文件）
    config_template = SRC_DIR / "scripts" / "templates" / "synapse.config.template.yaml"
    if config_template.exists():
        config_content = config_template.read_text(encoding="utf-8")
        config_content = config_content.replace("{{VERSION}}", version)
        config_dest = DIST_DIR / "synapse.config.yaml"
        if not preview:
            config_dest.write_text(config_content, encoding="utf-8")
            print(f"  ✅  synapse.config.yaml 已生成")

    # ── 使用 README 模板覆盖 dist/README.md ────────────────────────────────
    readme_template = SRC_DIR / "scripts" / "templates" / "README.template.md"
    if readme_template.exists():
        readme_content = readme_template.read_text(encoding="utf-8")
        readme_content = readme_content.replace("{{VERSION}}", version)
        readme_content = readme_content.replace("{{BUILD_DATE}}", build_date)
        if not preview:
            readme_dest = DIST_DIR / "README.md"
            readme_dest.write_text(readme_content, encoding="utf-8")
            print(f"  📄  README.md ← 使用模板覆盖（面向 GitHub 访客的通用说明）")
        else:
            print(f"  📄  [预览] README.md → 使用 README.template.md 覆盖")
    else:
        print(f"  ⚠️  README.template.md 不存在，跳过覆盖")

    # ── 更新 dist/VERSION ──────────────────────────────────────────────────
    if not preview:
        version_dest = DIST_DIR / "VERSION"
        version_dest.write_text(
            f"{version}\n"
            f"# Synapse Version\n"
            f"# Build date: {build_date}\n"
        )

    # ── 输出跳过列表 ────────────────────────────────────────────────────────
    print(f"\n── 跳过的文件/目录 ──")
    for item in skipped_items[:30]:  # 最多显示30条
        print(item)
    if len(skipped_items) > 30:
        print(f"  ... 还有 {len(skipped_items) - 30} 项")

    # ── 统计报告 ─────────────────────────────────────────────────────────────
    print(f"\n── 构建统计 ──")
    print(f"  复制：{stats['copied']} 个文件")
    print(f"  修改：{stats['modified']} 个文件（内容替换）")
    print(f"  模板：{stats['template_used']} 个文件（使用空白模板）")
    print(f"  跳过：{stats['skipped']} 个文件（黑名单）")

    # ── 残留扫描 ─────────────────────────────────────────────────────────────
    if not preview and DIST_DIR.exists():
        print(f"\n── 残留个人信息扫描 ──")
        violations = scan_residuals(DIST_DIR)

        if violations:
            print(f"  ⚠️  发现 {len(violations)} 处潜在残留：")
            for file_path, description, sample in violations:
                print(f"     {file_path}：{description}（样本：{sample[:50]}）")
            print(f"\n  请检查以上文件，确认是否需要手动处理。")
        else:
            print(f"  ✅  未发现残留个人信息")

    if not preview:
        print(f"\n✅  构建完成！输出目录：{DIST_DIR}")
        print(f"   下一步：将 dist/ 内容推送到 GitHub 仓库 lysanderl-glitch/synapse")
    else:
        print(f"\n✅  预览完成。运行时去掉 --preview 参数执行正式构建。")

    return True


# ─────────────────────────────────────────────────────────────────────────────
# 入口
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Synapse 分发包构建脚本 — 从原始系统生成干净的可分发包"
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="预览模式：输出构建计划但不写入文件"
    )
    parser.add_argument(
        "--version",
        type=str,
        default=None,
        help=f"指定版本号（默认：{CURRENT_VERSION}）"
    )
    args = parser.parse_args()

    success = build_distribution(preview=args.preview, version_override=args.version)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
