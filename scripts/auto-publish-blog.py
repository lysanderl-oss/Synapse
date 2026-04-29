#!/usr/bin/env python3
"""
auto-publish-blog.py  v2.0
Reads inbox notes → generates full blog post → publishes to lysander.bond
Run: py -3 scripts/auto-publish-blog.py
Integrated into: session-to-worklog.py daily pipeline

v2.0 changes:
- SYSTEM_PROMPT + BLOG_PROMPT_V2: mandatory structure (TL;DR/code/callout/reasoning)
- structural_qa(): zero-API pre-publish gate
- QA_PROMPT_V2: upgraded to 100-point scale (threshold 75)
- Dual-language path: src/content/blog/zh/ + src/content/blog/en/
- generate_blog_post_en(): English abstract generator (350-500 words)
- build_md_file(): Markdown output for Content Collections
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Fix Windows console encoding for Chinese characters
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass

import logging
logging.basicConfig(
    filename=str(Path(__file__).parent / "auto-publish-blog.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    encoding="utf-8",
)

DUBAI_TZ = timezone(timedelta(hours=4))
SYNAPSE_ROOT = Path(__file__).parent.parent
INBOX_DIR = SYNAPSE_ROOT / "obs" / "04-content-pipeline" / "_inbox"
DRAFTS_DIR = SYNAPSE_ROOT / "obs" / "04-content-pipeline" / "_drafts"
PUBLISHED_DIR = SYNAPSE_ROOT / "obs" / "04-content-pipeline" / "_published"

# ── Bond Repo Path ────────────────────────────────────────────────────────────
# Priority: --bond-repo CLI > BOND_REPO_DIR env > Windows default.
# Cloud (GitHub Actions) sets BOND_REPO_DIR=$GITHUB_WORKSPACE/lysander-bond.
def _resolve_bond_root(cli_path: str | None = None) -> Path:
    if cli_path:
        return Path(cli_path)
    env_path = os.environ.get("BOND_REPO_DIR", "").strip()
    if env_path:
        return Path(env_path)
    return Path("C:/Users/lysanderl_janusd/lysander-bond")

LYSANDER_BOND_ROOT = _resolve_bond_root()

# v2: dual-language Content Collections paths
BLOG_ROOT_ZH = LYSANDER_BOND_ROOT / "src" / "content" / "blog" / "zh"
BLOG_ROOT_EN = LYSANDER_BOND_ROOT / "src" / "content" / "blog" / "en"

# Legacy: keep BLOG_ROOT and BLOG_INDEX for index.astro updates (pages/ dir)
BLOG_ROOT = LYSANDER_BOND_ROOT / "src" / "pages" / "blog"
BLOG_INDEX = LYSANDER_BOND_ROOT / "src" / "pages" / "blog" / "index.astro"
TRACKING_FILE = Path(__file__).parent / ".blog-published.json"

# Default model used when ANTHROPIC_API_KEY path is taken (cloud)
DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")

# When True (cloud mode), skip the in-script git add/commit/push on lysander-bond
# because the calling GitHub Actions workflow handles those steps (with proper
# bot identity + retry on conflict). Toggle via BLOG_SKIP_GIT=1.
SKIP_GIT_PUSH = os.environ.get("BLOG_SKIP_GIT", "").strip() in ("1", "true", "yes")


# ── Prompt Constants v2 ───────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are Lysander, the technical blogger of Synapse-PJ AI engineering team.
Your writing style: first-person, based on real experience, showing reasoning process not just conclusions.
Your readers: engineers and founders building AI Agent systems or n8n automation workflows.
Your credibility comes from: specific numbers, real filenames, showing mistakes made and thinking process.
Write in Chinese (Simplified) unless specified otherwise."""

BLOG_PROMPT_V2 = """## 素材

核心问题/场景：{core_insight}
具体技术细节（全部使用，不得泛化）：{technical_details}
写作切入点：{angle}
文章类型：{content_type}

## 强制结构（必须按此顺序，缺一不可）

输出格式：纯 HTML。使用元素：
- 段落：<p>
- 标题：<h2>（主节）、<h3>（子节）
- 代码块：<pre><code class="language-python">（或 yaml/bash）</code></pre>
- 关键要点：<div class="callout callout-insight"><p>...</p></div>
- 无序列表：<ul><li>
- 有序列表：<ol><li>
- 表格：<table><thead><tr><th>...</th></tr></thead><tbody>...

必须包含的节（缺一退回重写）：

1. TL;DR（位于正文最顶部）
<div class="tl-dr"><ul>
  <li>3-5条bullet，每条≤20字，让扫读者获得完整价值</li>
</ul></div>

2. 问题背景（H2，1-2段）
- 第一段：一个具体场景 + 至少1个具体数字
- 不假设读者了解 Synapse

3. 为什么难排查/为什么这个决策难做（H2，1-2段）
- 必须包含"我们一开始以为…但实际上…"的推理结构
- 禁止：直接给结论，跳过分析过程

4. 根因/核心设计决策（H2，含代码块）
- 必须包含至少1个 <pre><code> 代码块
- 内容：真实配置片段/伪代码/命令（仅使用素材中提及的，不编造路径）

5. 可移植的原则（H2）
- 第一条原则放入 callout-insight
- 其余用 <ol> 编号
- 每条格式：「如果你在[场景]，[具体行动原则]」

6. 结尾（1段）
- 关联文章具体技术问题的CTA
- 禁止：固定宣传模板语

## 强制约束
- 禁用词：革命性、未来可期、AI很强大、无限可能、日新月异
- 禁止：结论复述正文
- 禁止：使用素材未提及的文件路径或API字段名
- 长度：1200-2000字（中文）
"""

ENGLISH_ABSTRACT_PROMPT = """Based on the following Chinese technical blog article, write an English abstract version.

Original article:
{zh_content}

Requirements:
- Length: 350-500 words
- Structure (mandatory):
  ## TL;DR
  3-5 bullets, each ≤15 words

  [1-2 paragraphs: what problem, why it matters, how solved]

  ## Key Takeaways
  3-5 actionable principles, format: "If you [scenario], [principle]"

  ## Read the Full Article (Chinese)
  [Link back note: "This is an abstract. The full technical walkthrough is in Chinese.]

- Tone: direct, technical, first-person
- Include: at least 1 specific number or filename from the original
- Forbidden: "revolutionary", "game-changing", "powerful AI"
"""

QA_PROMPT_V2 = """Rate this blog article (0-100):

{content}

Scoring:
- Completeness (25pts): TL;DR(5) + H2≥3(5) + code block(5) + callout(5) + specific number(5)
- Narrative quality (25pts): shows reasoning process(10) + has failure/tradeoff path(10) + portable principles(5)
- Technical accuracy (20pts): specific not vague(10) + no invented file paths(10)
- Reader value (20pts): actionable guidance(10) + no empty buzzwords(10)
- Compliance (10pts): no sensitive info(5) + contextual CTA not template(5)

Output ONLY valid JSON: {{"score": 82, "pass": true, "issues": ["issue1"], "reason": "one line summary"}}
pass=true when score >= 75
"""


# ── Claude API Call ───────────────────────────────────────────────────────────

def _call_claude_text(prompt: str, system: str | None = None, timeout: int = 180) -> str:
    """Send prompt to Claude, return text response.

    Cloud-friendly: prefers Anthropic SDK when ANTHROPIC_API_KEY is set
    (GitHub Actions has no `claude` CLI). Falls back to the local `claude`
    CLI subprocess for legacy local-machine runs.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if api_key:
        try:
            from anthropic import Anthropic
        except ImportError as e:
            raise RuntimeError(
                "anthropic SDK not installed but ANTHROPIC_API_KEY is set. "
                "Run: pip install 'anthropic>=0.40'"
            ) from e
        client = Anthropic(api_key=api_key)
        kwargs = dict(
            model=DEFAULT_MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        if system:
            kwargs["system"] = system
        response = client.messages.create(**kwargs)
        if not response.content:
            return ""
        first = response.content[0]
        return getattr(first, "text", str(first)).strip()

    # Fallback: local `claude` CLI (no system prompt support)
    result = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "text"],
        capture_output=True,
        text=True,
        timeout=timeout,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI error: {result.stderr}")
    return result.stdout.strip()


# ── Frontmatter Parser ────────────────────────────────────────────────────────

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown. Returns (meta_dict, body_text)."""
    meta = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm_block = parts[1]
            body = parts[2].strip()
            for line in fm_block.strip().splitlines():
                if ":" in line:
                    key, _, val = line.partition(":")
                    meta[key.strip()] = val.strip()
    return meta, body


def extract_section(body: str, heading: str) -> str:
    """Extract content under a ## heading from markdown body."""
    pattern = rf"##\s+{re.escape(heading)}\s*\n(.*?)(?=\n##|\Z)"
    match = re.search(pattern, body, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


# ── Load Inbox Notes ──────────────────────────────────────────────────────────

def load_inbox_notes() -> list[dict]:
    """
    Glob INBOX_DIR/*.md, parse frontmatter, return notes where:
    - status is 'raw' (or not set)
    - shareability >= 4
    - not already in TRACKING_FILE
    """
    tracking = json.loads(TRACKING_FILE.read_text(encoding="utf-8")) if TRACKING_FILE.exists() else {}

    notes = []
    for md_file in sorted(INBOX_DIR.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(text)

        # Filter: status must be raw (or absent)
        status = meta.get("status", "raw").strip().lower()
        if status not in ("raw", ""):
            continue

        # Filter: shareability >= 4
        share_raw = meta.get("shareability", "0").split("/")[0].strip()
        try:
            shareability = int(share_raw)
        except ValueError:
            shareability = 0
        if shareability < 4:
            continue

        # Derive slug from filename: YYYY-MM-DD-slug.md → slug
        stem = md_file.stem  # e.g. 2026-04-23-ai-ceo-execution-chain-enforcement
        # Remove date prefix if present
        slug_match = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)$", stem)
        slug = slug_match.group(1) if slug_match else stem

        # Filter: not already published
        if slug in tracking:
            continue

        date_str = meta.get("date", stem[:10] if len(stem) >= 10 else "")

        # Extract sections from body
        core_insight = extract_section(body, "核心洞察") or stem
        angle = extract_section(body, "写作切入点") or ""
        why_interesting = extract_section(body, "为什么值得分享") or ""
        technical_details = extract_section(body, "技术细节") or extract_section(body, "具体细节") or ""
        content_type = meta.get("content_type", "B").strip()

        notes.append({
            "path": md_file,
            "slug": slug,
            "title": core_insight,
            "core_insight": core_insight,
            "angle": angle,
            "why_interesting": why_interesting,
            "technical_details": technical_details,
            "content_type": content_type,
            "date": date_str,
            "shareability": shareability,
        })

    return notes


# ── Route Conflict Check ──────────────────────────────────────────────────────

def check_route_conflict(slug: str) -> None:
    """Fail fast if a static .astro file would shadow the dynamic route."""
    static_zh = LYSANDER_BOND_ROOT / "src" / "pages" / "blog" / f"{slug}.astro"
    static_en = LYSANDER_BOND_ROOT / "src" / "pages" / "en" / "blog" / f"{slug}.astro"
    for static_file in [static_zh, static_en]:
        if static_file.exists():
            raise RuntimeError(
                f"ROUTE_CONFLICT: {static_file} shadows dynamic route. "
                f"Delete it before publishing."
            )


# ── Structural QA (zero API cost) ─────────────────────────────────────────────

def structural_qa(html_content: str) -> tuple[bool, list[str]]:
    """Pre-publish structural validation. Zero API cost, pure parsing."""
    issues = []

    # TL;DR
    if 'tl-dr' not in html_content and 'TL;DR' not in html_content:
        issues.append("MISSING: TL;DR section")

    # H2 count
    h2_count = len(re.findall(r'<h2[^>]*>', html_content, re.IGNORECASE))
    if h2_count < 3:
        issues.append(f"INSUFFICIENT: Only {h2_count} H2 headings (minimum 3)")

    # Code block
    if '<pre' not in html_content and '<code' not in html_content:
        issues.append("MISSING: No code block (<pre><code>)")

    # Callout
    if 'callout' not in html_content:
        issues.append("MISSING: No callout/key-insight box")

    # Word count (strip tags, count Chinese chars + words)
    clean = re.sub(r'<[^>]+>', '', html_content)
    clean = re.sub(r'\s+', ' ', clean).strip()
    char_count = len(clean)
    if char_count < 600:
        issues.append(f"TOO_SHORT: ~{char_count} chars (minimum 600)")
    if char_count > 3000:
        issues.append(f"TOO_LONG: ~{char_count} chars (maximum 3000)")

    # Forbidden phrases
    forbidden = ['革命性', '未来可期', '无限可能', '日新月异']
    for phrase in forbidden:
        if phrase in html_content:
            issues.append(f"FORBIDDEN_PHRASE: '{phrase}' found")

    passed = len(issues) == 0
    return passed, issues


# ── Generate Blog Post (ZH) ───────────────────────────────────────────────────

def generate_blog_post(note: dict) -> str:
    """Generate full HTML blog post content using Prompt v2 with system prompt."""
    # Fallback for technical_details if not in note
    technical_details = note.get('technical_details') or note.get('core_insight', '（见核心问题描述）')

    content_type_map = {
        "A": "A类（系统拆解）",
        "B": "B类（问题日志）",
        "C": "C类（方法论）",
        "D": "D类（进化记录）",
    }
    content_type_label = content_type_map.get(note['content_type'], note['content_type'])

    prompt = BLOG_PROMPT_V2.format(
        core_insight=note['core_insight'],
        technical_details=technical_details,
        angle=note.get('angle', ''),
        content_type=content_type_label,
    )

    return _call_claude_text(prompt, system=SYSTEM_PROMPT, timeout=180)


# ── Generate English Abstract ─────────────────────────────────────────────────

def generate_blog_post_en(zh_content: str, slug: str) -> str:
    """Generate English abstract version from Chinese article."""
    prompt = ENGLISH_ABSTRACT_PROMPT.format(zh_content=zh_content[:3000])
    en_system = "You are a technical writer creating English summaries of Chinese AI engineering blog posts."
    return _call_claude_text(prompt, system=en_system, timeout=120)


# ── QA Review (100-point scale) ───────────────────────────────────────────────

def qa_review(content: str, note: dict) -> tuple[bool, str]:
    """Quality review via Claude API. Returns (passed, reason). Threshold: 75/100."""
    prompt = QA_PROMPT_V2.format(content=content[:2500])

    raw = _call_claude_text(prompt, timeout=60)
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:-1])
    try:
        review = json.loads(raw.strip())
    except json.JSONDecodeError:
        # Try to extract JSON from the raw output
        json_match = re.search(r'\{[^{}]+\}', raw, re.DOTALL)
        if json_match:
            review = json.loads(json_match.group())
        else:
            return False, f"QA parse error: {raw[:100]}"
    score = review.get("score", 0)
    passed = review.get("pass", score >= 75)
    reason = review.get("reason", "")
    issues = review.get("issues", [])
    detail = f"score={score}/100 | {reason}"
    if issues:
        detail += f" | issues: {'; '.join(issues)}"
    return passed, detail


# ── Build Markdown File ───────────────────────────────────────────────────────

def build_md_file(slug: str, title: str, description: str, date: str,
                   html_content: str, tags: list, lang: str = 'zh') -> str:
    """Build markdown file content for Content Collections."""
    tags_yaml = '\n'.join([f'  - {t}' for t in tags])
    # Escape double quotes in title/description for YAML safety
    title_safe = title.replace('"', '\\"')
    desc_safe = description.replace('"', '\\"')
    # publishDate needs ISO 8601 format
    publish_date = date if 'T' in str(date) else f"{date}T00:00:00.000Z"
    return f"""---
title: "{title_safe}"
description: "{desc_safe}"
date: {date}
publishDate: {publish_date}
slug: {slug}
lang: {lang}
keywords:
{tags_yaml}
author: lysander
---

{html_content}
"""


# ── Build Astro File (legacy, for pages/ dir) ─────────────────────────────────

def build_astro_file(note: dict, content: str) -> str:
    """
    Generate .astro file content matching the exact structure of existing blog posts.
    Based on: harness-engineering-guide.astro structure.
    """
    date_formatted = note['date']  # YYYY-MM-DD
    title = note['title']
    # Build a short description from the angle/why_interesting
    description = (note.get('angle') or note.get('why_interesting') or title)[:120]

    # Determine tag color classes based on content_type
    type_label_map = {
        "A": ("系统拆解", "sky"),
        "B": ("问题日志", "purple"),
        "C": ("方法论", "green"),
        "D": ("进化记录", "cyan"),
    }
    type_label, type_color = type_label_map.get(note['content_type'], ("AI工程", "sky"))

    astro = f"""---
import Layout from '../../layouts/Layout.astro';
---

<Layout darkContent={{true}} title="{title} - Lysander" description="{description}">
  <article class="max-w-4xl mx-auto px-6 py-16">
    <header class="mb-12">
      <div class="flex items-center gap-3 mb-4">
        <time class="text-white/40 text-sm">{date_formatted}</time>
        <div class="flex gap-2">
          <span class="px-2 py-0.5 bg-{type_color}-500/20 text-{type_color}-400 rounded text-xs">{type_label}</span>
          <span class="px-2 py-0.5 bg-purple-500/20 text-purple-400 rounded text-xs">AI工程</span>
          <span class="px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded text-xs">Synapse</span>
        </div>
      </div>
      <h1 class="text-4xl font-bold text-white">{title}</h1>
    </header>

    <div class="prose prose-invert max-w-none space-y-8 text-white/80 leading-relaxed">

{content}

    </div>

    <footer class="mt-16 pt-8 border-t border-white/10">
      <p class="text-white/40 text-sm mb-4">
        如果你在构建 AI 工程团队，欢迎参考我们开源的
        <a href="https://github.com/lysanderl-glitch/synapse" class="text-sky-400 hover:text-sky-300" target="_blank" rel="noopener noreferrer">Synapse 框架</a>
      </p>
      <a href="/blog" class="text-sky-400 hover:text-sky-300">&larr; 返回博客</a>
    </footer>
  </article>
</Layout>
"""
    return astro


# ── Update Blog Index ─────────────────────────────────────────────────────────

def format_chinese_date(date_str: str) -> str:
    """Convert YYYY-MM-DD to Chinese date string like '2026年4月23日'."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return f"{dt.year}年{dt.month}月{dt.day}日"
    except ValueError:
        return date_str


def update_blog_index(note: dict, description: str):
    """
    Read index.astro, insert new post entry at top of the posts array (newest first).
    Matches the exact existing entry format from index.astro.
    """
    if not BLOG_INDEX.exists():
        print(f"  [SKIP] index.astro not found at {BLOG_INDEX}")
        return

    index_text = BLOG_INDEX.read_text(encoding="utf-8")

    # Build new entry — match existing indentation (2-space inside array)
    chinese_date = format_chinese_date(note['date'])
    raw_desc = (description or note.get('angle') or note['title'])
    desc_short = re.sub(r"\s+", " ", raw_desc).strip()[:80]
    # Escape backslashes / single-quotes for embedding into Astro JS string literal.
    bs = "\\"
    desc_short = desc_short.replace(bs, bs + bs).replace("'", bs + "'")
    title_escaped = note['title'].replace(bs, bs + bs).replace("'", bs + "'")

    new_entry = f"""  {{
    slug: '{note['slug']}',
    title: '{title_escaped}',
    date: '{note['date']}',
    description: '{desc_short}',
    tags: ['AI工程', 'Synapse', '{note['content_type']}类']
  }},"""

    # Insert after `const posts = [`
    insert_marker = "const posts = ["
    idx = index_text.find(insert_marker)
    if idx == -1:
        print("  [WARN] Could not find 'const posts = [' in index.astro — skipping index update")
        return

    insert_pos = idx + len(insert_marker) + 1  # after the newline following [
    new_text = index_text[:insert_pos] + new_entry + "\n" + index_text[insert_pos:]

    BLOG_INDEX.write_text(new_text, encoding="utf-8")
    print(f"  [OK] index.astro updated with: {note['slug']}")


# ── Archive Inbox Note ────────────────────────────────────────────────────────

def archive_inbox_note(note: dict):
    """Move inbox note to _published/, update frontmatter status to published."""
    PUBLISHED_DIR.mkdir(parents=True, exist_ok=True)

    src_path = note['path']
    dest_path = PUBLISHED_DIR / src_path.name

    text = src_path.read_text(encoding="utf-8")
    # Update status in frontmatter
    text = re.sub(r'^status:\s*raw', 'status: published', text, flags=re.MULTILINE)
    # Add published_at if not present
    if 'published_at:' not in text:
        text = re.sub(
            r'^(status: published)',
            f'\\1\npublished_at: {datetime.now(DUBAI_TZ).strftime("%Y-%m-%d")}',
            text,
            flags=re.MULTILINE
        )

    dest_path.write_text(text, encoding="utf-8")
    src_path.unlink()
    print(f"  [OK] Archived: {src_path.name} → _published/")


# ── Publish ───────────────────────────────────────────────────────────────────

def publish(note: dict, html_content: str) -> bool:
    """
    Full publish pipeline v2:
    1. structural_qa() gate (zero API)
    2. Write ZH markdown file to src/content/blog/zh/
    3. Generate + write EN abstract to src/content/blog/en/
    4. Remove any legacy .astro file in src/pages/blog/ that shadows the dynamic route
    5. Update index.astro
    6. Archive inbox note to _published/
    7. Git commit + push
    Returns True if published, False if blocked.
    """
    slug = note['slug']

    # 1. Structural QA gate
    sq_passed, sq_issues = structural_qa(html_content)
    if not sq_passed:
        print(f"  [STRUCTURAL QA FAIL] {slug}: {sq_issues}")
        logging.warning(f"Structural QA failed for {slug}: {sq_issues}")
        return False

    print(f"  [STRUCTURAL QA PASS] {slug}")

    # Prepare metadata
    title = note['title']
    description = re.sub(r"\s+", " ",
        (note.get('angle') or note.get('why_interesting') or title)
    ).strip()[:120]
    date = note['date']
    tags_zh = ['AI工程', 'Synapse', f"{note['content_type']}类"]

    # Ensure dirs exist
    BLOG_ROOT_ZH.mkdir(parents=True, exist_ok=True)
    BLOG_ROOT_EN.mkdir(parents=True, exist_ok=True)

    # 2. Write ZH Markdown
    zh_md = build_md_file(slug, title, description, date, html_content, tags_zh, lang='zh')
    zh_path = BLOG_ROOT_ZH / f"{slug}.md"
    zh_path.write_text(zh_md, encoding='utf-8')
    print(f"  [OK] ZH written: {zh_path.name}")

    # 3. EN 生成（原子性：EN 失败则回滚 ZH）
    try:
        en_content = generate_blog_post_en(html_content, slug)
        en_sq_pass, en_sq_issues = structural_qa(en_content)  # EN 也过结构检查
        if not en_sq_pass:
            logging.warning(f"EN structural QA issues for {slug}: {en_sq_issues}")
        en_md = build_md_file(slug, f"[EN] {title}", description, date, en_content, tags_zh, lang='en')
        en_path = BLOG_ROOT_EN / f"{slug}.md"
        en_path.write_text(en_md, encoding='utf-8')
        print(f"  [EN] Written: {en_path.name}")
        # EN 写入成功后，更新 ZH 文件的 hasEnglish 字段
        zh_content_txt = zh_path.read_text(encoding='utf-8')
        if 'hasEnglish:' not in zh_content_txt:
            zh_content_txt = zh_content_txt.replace(
                'lang: zh',
                'lang: zh\nhasEnglish: true'
            )
            zh_path.write_text(zh_content_txt, encoding='utf-8')
    except Exception as e:
        # 原子性回滚：EN 失败则撤销已写入的 ZH 文件
        if zh_path.exists():
            zh_path.unlink()
            print(f"  [ROLLBACK] ZH file removed due to EN failure: {e}")
        raise RuntimeError(f"Bilingual publish failed for {slug}: {e}")

    # 4. Remove any legacy .astro file in src/pages/blog/ that shadows the dynamic route.
    #    Content Collections (.md in src/content/blog/) is the sole source of truth.
    #    A static .astro at src/pages/blog/{slug}.astro would override [....slug].astro,
    #    causing esbuild failures and 404s on the live site.
    astro_path = BLOG_ROOT / f"{slug}.astro"
    if astro_path.exists():
        astro_path.unlink()
        print(f"  [CLEANUP] Removed legacy .astro file: {astro_path.name}")

    # 5. Update blog index
    clean_desc = re.sub(r'<[^>]+>', '', html_content)
    clean_desc = clean_desc.strip()[:80]
    update_blog_index(note, clean_desc)

    # 6. Archive inbox note
    archive_inbox_note(note)

    # 7. Git operations
    if SKIP_GIT_PUSH:
        print("  [OK] Git: skipped (BLOG_SKIP_GIT=1, workflow handles push)")
        return True

    repo = str(LYSANDER_BOND_ROOT)
    subprocess.run(["git", "-C", repo, "add", "-A"], check=True)
    subprocess.run(
        ["git", "-C", repo, "commit", "-m", f"feat: publish blog post '{note['title']}'"],
        check=True
    )
    subprocess.run(["git", "-C", repo, "push", "origin", "main"], check=True)
    print(f"  [OK] Git: committed and pushed")

    print(f"  [PUBLISHED] zh: {zh_path.name} | en: {(BLOG_ROOT_EN / (slug + '.md')).name}")
    return True


# ── Backfill EN for existing .astro articles ──────────────────────────────────

def backfill_en_from_astro():
    """
    For each .astro file in src/pages/blog/ (excluding index.astro, [...slug].astro),
    generate an EN abstract and write to src/content/blog/en/<slug>.md.
    Skips if EN file already exists.
    """
    BLOG_ROOT_EN.mkdir(parents=True, exist_ok=True)

    astro_files = [
        f for f in sorted(BLOG_ROOT.glob("*.astro"))
        if f.stem not in ("index", "[...slug]")
    ]

    print(f"\n[BACKFILL] Found {len(astro_files)} .astro files to check for EN backfill")

    skipped = 0
    generated = 0
    failed = 0

    for i, astro_path in enumerate(astro_files, 1):
        slug = astro_path.stem
        en_path = BLOG_ROOT_EN / f"{slug}.md"

        if en_path.exists():
            print(f"  [{i}/{len(astro_files)}] SKIP (exists): {slug}")
            skipped += 1
            continue

        print(f"  [{i}/{len(astro_files)}] Generating EN for: {slug}...")

        # Read .astro and extract content
        astro_text = astro_path.read_text(encoding="utf-8")

        # Extract title from Layout title= attribute or h1
        title = slug  # fallback
        title_match = re.search(r'title="([^"]+?)\s*-\s*Lysander"', astro_text)
        if title_match:
            title = title_match.group(1).strip()
        else:
            h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', astro_text)
            if h1_match:
                title = h1_match.group(1).strip()

        # Extract description
        description = ""
        desc_match = re.search(r'description="([^"]*)"', astro_text)
        if desc_match:
            description = desc_match.group(1).strip()

        # Extract date
        date = "2026-04-01"  # fallback
        date_match = re.search(r'<time[^>]*>(\d{4}-\d{2}-\d{2})</time>', astro_text)
        if date_match:
            date = date_match.group(1)

        # Extract main HTML body (between prose div and footer)
        body_match = re.search(
            r'<div class="prose[^"]*"[^>]*>(.*?)</div>\s*<footer',
            astro_text, re.DOTALL
        )
        zh_content = body_match.group(1).strip() if body_match else astro_text

        # Generate EN abstract
        try:
            en_content = generate_blog_post_en(zh_content, slug)
            tags = ['AI Engineering', 'Synapse', 'Automation']
            en_md = build_md_file(slug, f"[EN] {title}", description, date, en_content, tags, lang='en')
            en_path.write_text(en_md, encoding='utf-8')
            print(f"    → Written: {en_path.name}")
            generated += 1
        except Exception as e:
            print(f"    [ERROR] {slug}: {e}")
            logging.error(f"Backfill EN failed for {slug}: {e}")
            failed += 1

    print(f"\n[BACKFILL DONE] generated={generated} | skipped={skipped} | failed={failed}")
    return generated, skipped, failed


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"Auto-Publish Blog Pipeline v2 — {datetime.now(DUBAI_TZ).strftime('%Y-%m-%d %H:%M')} Dubai")

    # Ensure directories exist
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    PUBLISHED_DIR.mkdir(parents=True, exist_ok=True)
    BLOG_ROOT_ZH.mkdir(parents=True, exist_ok=True)
    BLOG_ROOT_EN.mkdir(parents=True, exist_ok=True)

    notes = load_inbox_notes()
    if not notes:
        print("No new inbox notes to publish.")
        return

    print(f"Found {len(notes)} publishable note(s).")

    tracking = json.loads(TRACKING_FILE.read_text(encoding="utf-8")) if TRACKING_FILE.exists() else {}
    published = []

    for note in notes:
        print(f"\nProcessing: {note['title'][:60]}...")

        try:
            content = generate_blog_post(note)
        except Exception as e:
            print(f"  [ERROR] Content generation failed: {e}")
            logging.error(f"Content generation failed for {note['slug']}: {e}")
            continue

        passed, reason = qa_review(content, note)

        if not passed:
            print(f"  [QA FAIL] {reason} — skipping")
            logging.warning(f"QA failed for {note['slug']}: {reason}")
            continue

        print(f"  [QA PASS] {reason}")

        try:
            ok = publish(note, content)
        except Exception as e:
            print(f"  [ERROR] Publish failed: {e}")
            logging.error(f"Publish failed for {note['slug']}: {e}")
            continue

        if ok:
            tracking[note['slug']] = datetime.now(DUBAI_TZ).isoformat()
            published.append(note['title'])

    TRACKING_FILE.write_text(json.dumps(tracking, ensure_ascii=False, indent=2), encoding="utf-8")

    if published:
        print(f"\nPublished {len(published)} post(s):")
        for t in published:
            print(f"  - {t}")
    else:
        print("\nNo posts were published this run.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bond-repo",
        help="Override lysander-bond repo path (default: $BOND_REPO_DIR or "
             "C:/Users/lysanderl_janusd/lysander-bond). Used by cloud workflow.",
    )
    parser.add_argument("--skip-git", action="store_true",
                        help="Skip in-script git add/commit/push (workflow handles it).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Diagnostic: print resolved paths and exit.")
    parser.add_argument("--backfill-en", action="store_true",
                        help="Backfill EN abstracts for existing .astro blog articles.")
    args = parser.parse_args()

    if args.bond_repo:
        LYSANDER_BOND_ROOT = _resolve_bond_root(args.bond_repo)
        BLOG_ROOT = LYSANDER_BOND_ROOT / "src" / "pages" / "blog"
        BLOG_INDEX = LYSANDER_BOND_ROOT / "src" / "pages" / "blog" / "index.astro"
        BLOG_ROOT_ZH = LYSANDER_BOND_ROOT / "src" / "content" / "blog" / "zh"
        BLOG_ROOT_EN = LYSANDER_BOND_ROOT / "src" / "content" / "blog" / "en"
    if args.skip_git:
        SKIP_GIT_PUSH = True

    if args.dry_run:
        print(f"[dry-run] LYSANDER_BOND_ROOT = {LYSANDER_BOND_ROOT}")
        print(f"[dry-run] BLOG_ROOT_ZH       = {BLOG_ROOT_ZH}")
        print(f"[dry-run] BLOG_ROOT_EN       = {BLOG_ROOT_EN}")
        print(f"[dry-run] BLOG_ROOT (legacy) = {BLOG_ROOT}")
        print(f"[dry-run] BLOG_INDEX         = {BLOG_INDEX}")
        print(f"[dry-run] INBOX_DIR          = {INBOX_DIR}")
        print(f"[dry-run] SKIP_GIT_PUSH      = {SKIP_GIT_PUSH}")
        sys.exit(0)

    if args.backfill_en:
        backfill_en_from_astro()
        sys.exit(0)

    main()
