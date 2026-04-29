"""
Synapse Phase 2 — Fan-out Intelligence Parallel Review Pipeline
Fan-out 并行评审管线：多专家并行评估情报输入，汇总评分+决策建议

Phase 2 T1-3 交付物
Pipeline: intelligence_fanout.py
对应配置: agent-CEO/config/fanout_config.yaml
"""

import concurrent.futures
import threading
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
import yaml
import os

# === Data Models ===

@dataclass
class IntelligenceItem:
    """情报输入项"""
    source: str
    content: str
    timestamp: str
    raw_data: dict = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)


@dataclass
class ReviewResult:
    """单一维度评审结果"""
    dimension: str
    score: float          # 0-5
    findings: list[str]
    recommendation: str   # 决策标签
    confidence: float     # 0-1
    processing_time_ms: float = 0.0


@dataclass
class AggregatedResult:
    """汇总评审结果"""
    radar_score: float        # 0-100 (质量雷达图总分)
    avg_score: float          # 0-5 (各维度平均)
    decision: str             # APPROVE / CONDITIONAL_APPROVE / REJECT
    priority: str             # P1 / P2 / P3
    overall_confidence: float # 0-1
    dimension_scores: dict     # {dimension: score}
    dimension_confidences: dict
    all_findings: list[str]
    bottleneck_dimensions: list[str]  # 得分最低的维度
    approval_score: float     # T1-2 风格 0-100
    recommendations: list[str]
    timestamp: str


# === Fan-out Pipeline ===

class FanoutPipeline:
    """
    情报并行评审管线

    设计架构：
    ┌─────────────────────────────────────────────┐
    │           情报输入 (IntelligenceItem)         │
    └─────────────────┬───────────────────────────┘
                      │
    ┌─────────────────┼───────────────────────────┐
    │  并行执行 (ThreadPoolExecutor, max_workers=5) │
    │  ┌──────────┐ ┌──────────┐ ┌──────────┐     │
    │  │accuracy  │ │action-   │ │ recency  │     │
    │  │_reviewer │ │ability   │ │ _reviewer│     │
    │  │          │ │          │ │          │     │
    │  └────┬─────┘ └────┬─────┘ └────┬─────┘     │
    │  ┌────┴─────┐ ┌────┴─────┐      │           │
    │  │relevance │ │completeness    │           │
    │  │_reviewer │ │_reviewer       │           │
    │  └────┬─────┘ └────┬─────┘      │           │
    └───────┼────────────┼────────────┼───────────┘
            │            │            │
            └────────────┼────────────┘
                         ▼
              ┌──────────────────┐
              │  汇总评分 + 决策  │
              │  (aggregate)     │
              └──────────────────┘

    评审维度（参考 T1-2 质量雷达图）：
    - accuracy       准确性：信息是否正确，有无事实错误
    - actionability  实用性：是否有明确可执行建议
    - recency        时效性：信息是否足够新
    - relevance      相关性：与 Synapse/Janus Digital 的关联度
    - completeness   完整性：是否包含背景/影响/建议

    决策规则（参考 T1-2 APPROVE/CONDITIONAL_APPROVE/REJECT）：
    - avg_score >= 4.0  → APPROVE (P1)
    - avg_score >= 3.0  → CONDITIONAL_APPROVE (P2)
    - avg_score < 3.0   → REJECT (P3)
    """

    DIMENSIONS = ["accuracy", "actionability", "recency", "relevance", "completeness"]
    DECISION_THRESHOLD_APPROVE = 4.0
    DECISION_THRESHOLD_CONDITIONAL = 3.0

    def __init__(self, config_path: Optional[str] = None):
        """初始化管线，可选加载外部配置"""
        self.lock = threading.Lock()
        self.config = self._load_config(config_path)
        self.reviewers = self._init_reviewers()

    def _load_config(self, config_path: Optional[str] = None) -> dict:
        """加载评审维度权重配置"""
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__),
                "config", "fanout_config.yaml"
            )
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}

    # ─── Dimension Reviewers ────────────────────────────────────────────────

    def _review_accuracy(self, item: IntelligenceItem, cfg: dict) -> ReviewResult:
        """准确性评审：信息是否正确，有无事实错误"""
        findings = []
        base_score = cfg.get("base_score", 4.0)
        score = base_score

        # 规则1：内容长度（过短难以验证）
        if len(item.content) < 50:
            findings.append("⚠️ 内容过短（<50字符），难以验证准确性")
            score -= 0.5
        elif len(item.content) < 100:
            findings.append("内容偏短，建议补充更多细节")

        # 规则2：量化数据（有数据准确性更高）
        has_numbers = any(c.isdigit() for c in item.content)
        has_percent = "%" in item.content or "percent" in item.content.lower()
        has_dates = any(c.isdigit() for c in item.timestamp)

        if has_numbers:
            score += 0.2
            findings.append("✓ 包含量化数据")
        if has_percent:
            score += 0.1
            findings.append("✓ 包含百分比数据")

        # 规则3：来源可靠性
        source_weight = cfg.get("source_weights", {}).get(item.source, 1.0)
        if source_weight >= 1.2:
            score += 0.3
            findings.append(f"✓ 高可信来源: {item.source}")
        elif source_weight <= 0.8:
            score -= 0.2
            findings.append(f"⚠️ 低可信来源: {item.source}")

        # 规则4：重复内容检测
        if len(set(item.content.split())) / max(len(item.content.split()), 1) < 0.5:
            findings.append("⚠️ 内容重复度高，可能存在信息噪声")
            score -= 0.3

        return ReviewResult(
            dimension="accuracy",
            score=round(min(5.0, max(1.0, score)), 2),
            findings=findings,
            recommendation="verified" if score >= 4.0 else "needs_factcheck",
            confidence=cfg.get("confidence", 0.85)
        )

    def _review_actionability(self, item: IntelligenceItem, cfg: dict) -> ReviewResult:
        """实用性评审：是否有明确可执行建议"""
        findings = []
        score = cfg.get("base_score", 3.5)

        action_words = ["应该", "建议", "可以", "需要", "必须",
                        "recommend", "should", "need", "consider",
                        "建议是", "推荐", "推荐使用", "actionable"]

        content_lower = item.content.lower()
        found_actions = [w for w in action_words if w in content_lower]

        if found_actions:
            bonus = 0.5 * min(len(found_actions), 4)
            score += bonus
            findings.append(f"✓ 发现行动建议词: {', '.join(found_actions[:3])}")
        else:
            findings.append("⚠️ 无明显行动建议词")

        # 检查是否有具体步骤/数字（高实用性标志）
        has_steps = any(w in content_lower for w in ["第一步", "1.", "step", "首先", "然后"])
        has_numbers = any(c.isdigit() for c in item.content)

        if has_steps:
            score += 0.4
            findings.append("✓ 包含具体执行步骤")
        if has_numbers and found_actions:
            score += 0.2
            findings.append("✓ 有量化行动指标")

        return ReviewResult(
            dimension="actionability",
            score=round(min(5.0, max(1.0, score)), 2),
            findings=findings,
            recommendation="high_priority" if score >= 4.0 else "low_priority",
            confidence=cfg.get("confidence", 0.80)
        )

    def _review_recency(self, item: IntelligenceItem, cfg: dict) -> ReviewResult:
        """时效性评审：信息是否足够新"""
        findings = []
        score = cfg.get("base_score", 4.5)

        # 解析时间戳
        try:
            ts_clean = item.timestamp.replace("Z", "+00:00")
            item_time = datetime.fromisoformat(ts_clean)
            now = datetime.now()

            age_hours = (now - item_time.replace(tzinfo=None)).total_seconds() / 3600

            if age_hours > 72:
                score -= 2.0
                findings.append(f"🔴 信息已超过72小时（{age_hours:.0f}h），时效性较差")
            elif age_hours > 48:
                score -= 1.5
                findings.append(f"🟡 信息超过48小时（{age_hours:.1f}h），建议核实")
            elif age_hours > 24:
                score -= 0.5
                findings.append(f"🟡 信息超过24小时（{age_hours:.1f}h）")
            else:
                findings.append(f"✓ 信息新鲜（{age_hours:.1f}h内），时效性良好")

        except ValueError:
            score -= 1.0
            findings.append("⚠️ 无法解析时间戳，时效性无法评估")

        return ReviewResult(
            dimension="recency",
            score=round(min(5.0, max(1.0, score)), 2),
            findings=findings,
            recommendation="use_now" if score >= 4.0 else "verify_date",
            confidence=cfg.get("confidence", 0.90)
        )

    def _review_relevance(self, item: IntelligenceItem, cfg: dict) -> ReviewResult:
        """相关性评审：与 Synapse/Janus Digital 的关联度"""
        findings = []
        score = cfg.get("base_score", 3.5)

        # 相关关键词
        relevant = cfg.get("keywords", [
            "agent", "ai", "automation", "synapse", "janus", "workflow",
            "claude", "llm", "n8n", "multi-agent", "harness",
            "intelligence", "pipeline", "multi-agent", "rag"
        ])

        content_lower = item.content.lower()
        tags_lower = [t.lower() for t in item.tags]

        # 匹配内容中的关键词
        matches = [w for w in relevant if w in content_lower]
        # 匹配标签
        tag_matches = [t for t in tags_lower if t in relevant]

        if matches:
            bonus = 0.5 * min(len(matches), 5)
            score += bonus
            findings.append(f"✓ 相关关键词命中: {', '.join(matches[:4])}")
        else:
            findings.append("⚠️ 无直接相关关键词命中")

        if tag_matches:
            score += 0.3
            findings.append(f"✓ 相关标签: {', '.join(tag_matches)}")

        # 来源相关性调整
        high_relevance_sources = cfg.get("high_relevance_sources", [
            "techcrunch", "anthropic", "arxiv", "github", "huggingface"
        ])
        if any(src in item.source.lower() for src in high_relevance_sources):
            score += 0.2
            findings.append(f"✓ 高相关来源: {item.source}")

        return ReviewResult(
            dimension="relevance",
            score=round(min(5.0, max(1.0, score)), 2),
            findings=findings,
            recommendation="highly_relevant" if score >= 4.0 else "peripheral",
            confidence=cfg.get("confidence", 0.75)
        )

    def _review_completeness(self, item: IntelligenceItem, cfg: dict) -> ReviewResult:
        """完整性评审：是否包含背景/影响/建议"""
        findings = []
        score = cfg.get("base_score", 3.0)

        completeness_map = {
            "background": ["因为", "背景", "由于", "背景是", "背景信息",
                           "背景介绍", "context", "background", "recently"],
            "impact":     ["影响", "将会", "导致", "结果是", "impact",
                         "效应", "结果", "consequence", "implication"],
            "recommendation": ["建议", "应该", "推荐", "recommend", "suggest",
                             "行动", "做法", "action", "proposal"]
        }

        content_lower = item.content.lower()
        present_elements = []

        for element, keywords in completeness_map.items():
            if any(kw in content_lower for kw in keywords):
                score += 0.6
                present_elements.append(element)

        if present_elements:
            findings.append(f"✓ 包含完整性要素: {', '.join(present_elements)}")
        else:
            findings.append("⚠️ 缺少背景/影响/建议等完整性要素")

        # 内容长度（长内容完整性通常更高）
        if len(item.content) > 300:
            score += 0.3
            findings.append("✓ 内容较为详尽")
        elif len(item.content) < 100:
            score -= 0.3
            findings.append("⚠️ 内容过短，完整性受限")

        # raw_data 有额外元数据
        if item.raw_data:
            score += 0.2
            findings.append("✓ 包含原始元数据")

        return ReviewResult(
            dimension="completeness",
            score=round(min(5.0, max(1.0, score)), 2),
            findings=findings,
            recommendation="comprehensive" if score >= 4.0 else "incomplete",
            confidence=cfg.get("confidence", 0.80)
        )

    def _init_reviewers(self) -> dict:
        """初始化评审专家（根据配置调整权重）"""
        cfg = self.config
        dim_cfg = cfg.get("dimensions", {})

        def get_cfg(dim):
            return dim_cfg.get(dim, {})

        return {
            "accuracy":      lambda item: self._review_accuracy(item, get_cfg("accuracy")),
            "actionability": lambda item: self._review_actionability(item, get_cfg("actionability")),
            "recency":       lambda item: self._review_recency(item, get_cfg("recency")),
            "relevance":     lambda item: self._review_relevance(item, get_cfg("relevance")),
            "completeness":  lambda item: self._review_completeness(item, get_cfg("completeness")),
        }

    # ─── Pipeline Core ────────────────────────────────────────────────────────

    def review_parallel(self, item: IntelligenceItem) -> list[ReviewResult]:
        """
        并行执行所有维度评审
        使用 ThreadPoolExecutor 实现真正的并发
        """
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(reviewer, item): dim
                for dim, reviewer in self.reviewers.items()
            }
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    dim = futures[future]
                    results.append(ReviewResult(
                        dimension=dim,
                        score=1.0,
                        findings=[f"评审异常: {str(e)}"],
                        recommendation="error",
                        confidence=0.0
                    ))
        return results

    def aggregate(self, results: list[ReviewResult]) -> AggregatedResult:
        """
        汇总评审结果 → 决策建议

        决策规则（Phase 1 参考 T1-2 决策标准）：
        - avg_score >= 4.0  → APPROVE → P1
        - avg_score >= 3.0  → CONDITIONAL_APPROVE → P2
        - avg_score < 3.0   → REJECT → P3
        """
        if not results:
            return AggregatedResult(
                radar_score=0, avg_score=0, decision="REJECT",
                priority="P3", overall_confidence=0,
                dimension_scores={}, dimension_confidences={},
                all_findings=[], bottleneck_dimensions=[],
                approval_score=0, recommendations=["无评审结果"],
                timestamp=datetime.now().isoformat()
            )

        # 基本统计
        dimension_scores = {r.dimension: r.score for r in results}
        dimension_confidences = {r.dimension: r.confidence for r in results}
        all_findings = [f for r in results for f in r.findings]

        total_score = sum(r.score for r in results)
        avg_score = total_score / len(results)

        # 质量雷达图（归一化到 0-100）
        radar_score = (avg_score / 5.0) * 100

        # 决策
        if avg_score >= self.DECISION_THRESHOLD_APPROVE:
            decision = "APPROVE"
            priority = "P1"
        elif avg_score >= self.DECISION_THRESHOLD_CONDITIONAL:
            decision = "CONDITIONAL_APPROVE"
            priority = "P2"
        else:
            decision = "REJECT"
            priority = "P3"

        # 置信度
        overall_confidence = sum(r.confidence for r in results) / len(results)

        # 瓶颈维度（得分最低的维度，权重>0.5 时触发改进建议）
        sorted_dims = sorted(dimension_scores.items(), key=lambda x: x[1])
        bottleneck_dimensions = [
            dim for dim, score in sorted_dims
            if score < 3.5
        ]

        # 改进建议
        recommendations = []
        if bottleneck_dimensions:
            recommendations.append(
                f"需改进维度: {', '.join(bottleneck_dimensions)}"
            )
        for dim, score in sorted_dims[:2]:
            if score < 3.5:
                recommendations.append(
                    f"  → {dim}: {score}/5（建议补充相关要素）"
                )

        # 行动建议（基于决策）
        if decision == "APPROVE":
            recommendations.insert(0, "✅ 可直接进入情报日报/行动管线")
        elif decision == "CONDITIONAL_APPROVE":
            recommendations.insert(0, "⚠️ 有条件通过，建议补充缺失信息后进入管线")
        else:
            recommendations.insert(0, "❌ 不符合发布标准，建议搁置或重构")

        # T1-2 风格 APPROVE SCORE（0-100 百分制）
        approval_score = radar_score

        return AggregatedResult(
            radar_score=round(radar_score, 1),
            avg_score=round(avg_score, 2),
            decision=decision,
            priority=priority,
            overall_confidence=round(overall_confidence, 2),
            dimension_scores=dimension_scores,
            dimension_confidences=dimension_confidences,
            all_findings=all_findings,
            bottleneck_dimensions=bottleneck_dimensions,
            approval_score=round(approval_score, 1),
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )

    def review(self, item: IntelligenceItem) -> AggregatedResult:
        """
        主入口：并行评审 + 汇总
        替代原有的串行评审 (daily_report → action_report)
        """
        results = self.review_parallel(item)
        return self.aggregate(results)

    # ─── 批量评审（支持多情报并行处理）──────────────

    def review_batch(self, items: list[IntelligenceItem]) -> list[AggregatedResult]:
        """批量评审多条情报"""
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=min(len(items), 10)
        ) as executor:
            futures = [
                executor.submit(self.review, item) for item in items
            ]
            return [f.result() for f in concurrent.futures.as_completed(futures)]

    # ─── 输出格式化 ─────────────────────────────────────────────────────────

    def format_summary(self, result: AggregatedResult) -> str:
        """生成可读评审摘要"""
        lines = [
            f"📊 质量雷达图评分: {result.radar_score}/100",
            f"   平均维度分: {result.avg_score}/5.0",
            f"   决策结果: {result.decision} ({result.priority})",
            f"   置信度: {result.overall_confidence:.0%}",
            f"",
            f"   各维度评分:",
        ]
        for dim, score in result.dimension_scores.items():
            conf = result.dimension_confidences.get(dim, 0)
            bar = "█" * int(score) + "░" * (5 - int(score))
            lines.append(f"   {dim:15s} {bar} {score:.2f}/5  (置信度 {conf:.0%})")

        if result.bottleneck_dimensions:
            lines.append(f"")
            lines.append(f"   ⚠️ 瓶颈维度: {', '.join(result.bottleneck_dimensions)}")

        lines.append(f"")
        lines.append(f"   建议行动:")
        for rec in result.recommendations:
            lines.append(f"   {rec}")

        return "\n".join(lines)


# === Demo & Validation ===

def demo():
    """Phase 2 T1-3 验证演示"""
    print("=" * 60)
    print("Phase 2 T1-3 | Fan-out Pipeline 演示")
    print("=" * 60)

    pipeline = FanoutPipeline()

    # 测试用例1：高质量情报（预期 APPROVE）
    item1 = IntelligenceItem(
        source="techcrunch",
        content=(
            "Anthropic 发布 Claude 4.7，性能大幅提升。基准测试显示 "
            "推理能力增强35%。建议企业评估升级 AI 基础设施，第一步是 "
            "对接入点进行压力测试，然后更新 prompt 模板。发布于2026年4月。"
        ),
        timestamp=datetime.now().isoformat(),
        raw_data={"author": "TC Editorial", "verified": True},
        tags=["ai", "claude", "anthropic"]
    )

    print("\n[Test 1] 高质量情报（预期 APPROVE/P1）")
    print("-" * 40)
    results1 = pipeline.review_parallel(item1)
    summary1 = pipeline.aggregate(results1)
    print(pipeline.format_summary(summary1))

    # 测试用例2：低质量情报（预期 REJECT）
    item2 = IntelligenceItem(
        source="unknown-blog",
        content="AI is changing things.",
        timestamp="2026-01-01T00:00:00",  # 非常旧
        raw_data={},
        tags=[]
    )

    print("\n[Test 2] 低质量情报（预期 REJECT/P3）")
    print("-" * 40)
    results2 = pipeline.review_parallel(item2)
    summary2 = pipeline.aggregate(results2)
    print(pipeline.format_summary(summary2))

    # 测试用例3：中等质量（预期 CONDITIONAL_APPROVE）
    item3 = IntelligenceItem(
        source="arxiv",
        content="New multi-agent orchestration paper published. The approach shows promise for workflow automation.",
        timestamp="2026-04-20T10:00:00",
        raw_data={"category": "cs.AI"},
        tags=["multi-agent", "research"]
    )

    print("\n[Test 3] 中等质量（预期 CONDITIONAL_APPROVE/P2）")
    print("-" * 40)
    results3 = pipeline.review_parallel(item3)
    summary3 = pipeline.aggregate(results3)
    print(pipeline.format_summary(summary3))

    # 批量评审演示
    print("\n[Batch Review] 3条情报并行处理")
    print("-" * 40)
    batch_results = pipeline.review_batch([item1, item2, item3])
    for i, r in enumerate(batch_results, 1):
        print(f"  情报{i}: {r.decision} ({r.priority}) | Radar: {r.radar_score}/100")

    return {
        "item1": summary1,
        "item2": summary2,
        "item3": summary3
    }


if __name__ == "__main__":
    results = demo()