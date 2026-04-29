# -*- coding: utf-8 -*-
"""
Synapse v3.0 — Intelligence Forecaster
情报趋势预测：预测未来热点、识别周期性模式

Phase 3 T1-4: 情报预测模型
用法:
    from agent_butler.intelligence_forecaster import IntelligenceForecaster
    fc = IntelligenceForecaster()
    topics = fc.predict_trending_topics(days_ahead=7)
    velocity = fc.get_intelligence_velocity()
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional

DEFAULT_DATA_DIR = Path(__file__).parent / "data"
DEFAULT_INTEL_DIR = Path(__file__).parent.parent / "obs" / "06-daily-reports"


class IntelligenceForecaster:
    """情报趋势预测

    核心功能:
        predict_trending_topics: 预测未来7天可能的情报热点
        get_intelligence_velocity: 情报生成速度分析
        get_topic_momentum: 主题动量分析（上升/平稳/下降）
    """

    def __init__(
        self,
        intel_dir: Optional[str] = None,
        storage_path: Optional[str] = None
    ):
        self.intel_dir = Path(intel_dir) if intel_dir else DEFAULT_INTEL_DIR
        self.storage_path = Path(storage_path) if storage_path else DEFAULT_DATA_DIR
        self._intel_cache: Optional[list] = None

    # ─── 情报加载 ──────────────────────────────────────────────

    @property
    def intelligence_history(self) -> list:
        if self._intel_cache is None:
            self._intel_cache = self._load_intel()
        return self._intel_cache

    def _load_intel(self) -> list:
        """从 obs/06-daily-reports 加载历史日报"""
        items = []
        if not self.intel_dir.exists():
            return items
        for f in sorted(self.intel_dir.glob("*-intelligence-daily.html"), reverse=True):
            try:
                # 从文件名提取日期: 2026-04-17-intelligence-daily.html
                date_str = f.name.split("-")[0:3]
                if len(date_str) >= 3:
                    date = "-".join(date_str)
                else:
                    date = f.name[:10]
                content = f.read_text(encoding="utf-8", errors="ignore")
                # 提取标题（H1标签内容）
                titles = re.findall(r"<h[12][^>]*>([^<]+)</h[12]>", content)
                title = titles[0].strip() if titles else ""
                # 提取关键词（从标题或 meta 标签）
                keywords = self._extract_keywords(content)
                items.append({
                    "date": date,
                    "title": title,
                    "keywords": keywords,
                    "path": str(f)
                })
            except Exception:
                continue
        return items

    @staticmethod
    def _extract_keywords(content: str) -> list:
        """从 HTML 内容提取关键词"""
        text = re.sub(r"<[^>]+>", " ", content)
        text = re.sub(r"\s+", " ", text)
        # 高频词过滤（冠词/介词/停用词）
        stop = {"the", "a", "an", "of", "in", "on", "for", "and", "or", "to", "is",
                "with", "as", "by", "at", "from", "that", "this", "are", "be",
                "的", "在", "和", "与", "为", "了", "是", "对", "等", "及"}
        words = [w.lower().strip() for w in re.findall(r"[A-Za-z]{4,}", text)]
        freq = defaultdict(int)
        for w in words:
            if w not in stop:
                freq[w] += 1
        return [w for w, _ in sorted(freq.items(), key=lambda x: -x[1])[:20]]

    # ─── 核心预测 ──────────────────────────────────────────────

    def predict_trending_topics(self, days_ahead: int = 7) -> list[dict]:
        """预测未来 N 天可能的情报热点

        Returns:
            [{
                "topic": str,
                "confidence": float,      # 0.0-1.0 置信度
                "reason": str,            # 预测依据
                "keywords": list[str],
                "urgency": str,           # "high" | "medium" | "low"
            }, ...]
        """
        history = self.intelligence_history
        if len(history) < 2:
            return [{
                "topic": "insufficient_data",
                "confidence": 0.0,
                "reason": "历史情报数据不足（<2条）",
                "keywords": [],
                "urgency": "low"
            }]

        predictions = []

        # 1. 周期性热点检测（月初/月末技术发布季等）
        periodic = self._detect_periodic_topics(history)
        predictions.extend(periodic)

        # 2. 关键词趋势外推
        trending = self._extrapolate_keywords(history, days_ahead)
        predictions.extend(trending)

        # 3. 近期高频主题（惯性延续）
        recent = self._recent_hot_topics(history, lookback=5)
        for topic, score in recent:
            predictions.append({
                "topic": topic,
                "confidence": min(score * 0.5, 0.85),
                "reason": f"惯性延续：近{len(history[:5])}期持续出现",
                "keywords": [topic],
                "urgency": "medium"
            })

        # 去重 + 排序
        seen = set()
        unique = []
        for p in sorted(predictions, key=lambda x: -x["confidence"]):
            key = p["topic"].lower()
            if key not in seen and p["confidence"] > 0.1:
                seen.add(key)
                unique.append(p)

        return unique[:10]

    def _detect_periodic_topics(self, history: list) -> list[dict]:
        """检测周期性热点（如月初 AI 发布、月中报告等）"""
        periodic = []
        today = datetime.now()
        day_of_month = today.day

        # 月初（1-5日）：新月份计划/目标设定
        if 1 <= day_of_month <= 5:
            periodic.append({
                "topic": "monthly_planning",
                "confidence": 0.65,
                "reason": "月初周期性：适合复盘上月OKR、制定当月计划",
                "keywords": ["planning", "okr", "review", "strategy"],
                "urgency": "high"
            })

        # 月末（25-31日）：月度总结/下月预测
        if 25 <= day_of_month <= 31:
            periodic.append({
                "topic": "monthly_review",
                "confidence": 0.70,
                "reason": "月末周期性：月度总结、趋势预测、季度规划",
                "keywords": ["monthly", "review", "forecast", "summary"],
                "urgency": "high"
            })

        # 周中（周二/周三）：技术深度分析
        weekday = today.weekday()
        if weekday in (1, 2):
            periodic.append({
                "topic": "deep_dive_analysis",
                "confidence": 0.55,
                "reason": "周中：适合发布深度技术分析报告",
                "keywords": ["analysis", "technical", "deep", "research"],
                "urgency": "medium"
            })

        return periodic

    def _extrapolate_keywords(self, history: list, days_ahead: int) -> list[dict]:
        """基于历史关键词频率趋势外推"""
        # 分别统计近7天和8-30天的高频词
        recent_cutoff = datetime.now() - timedelta(days=7)
        older_cutoff = datetime.now() - timedelta(days=30)

        recent_freq = defaultdict(int)
        older_freq = defaultdict(int)

        for item in history:
            try:
                date = datetime.fromisoformat(item["date"])
            except Exception:
                continue
            for kw in item.get("keywords", []):
                if date >= recent_cutoff:
                    recent_freq[kw] += 1
                elif date >= older_cutoff:
                    older_freq[kw] += 1

        # 找出近期加速出现的词
        extrapolated = []
        for kw, recent_count in recent_freq.items():
            older_count = older_freq.get(kw, 0)
            if older_count == 0:
                # 新出现的主题
                if recent_count >= 2:
                    extrapolated.append({
                        "topic": kw,
                        "confidence": min(0.5 + recent_count * 0.05, 0.80),
                        "reason": f"新兴主题：近7天出现{recent_count}次",
                        "keywords": [kw],
                        "urgency": "high" if recent_count >= 3 else "medium"
                    })
            else:
                ratio = recent_count / older_count
                if ratio > 1.5:
                    extrapolated.append({
                        "topic": kw,
                        "confidence": min(0.4 + ratio * 0.1, 0.75),
                        "reason": f"加速增长：近期出现{recent_count}x，历史{older_count}x",
                        "keywords": [kw],
                        "urgency": "medium"
                    })

        return extrapolated

    def _recent_hot_topics(self, history: list, lookback: int = 5) -> list[tuple]:
        """近期高频主题"""
        freq = defaultdict(int)
        for item in history[:lookback]:
            for kw in item.get("keywords", [])[:5]:
                freq[kw] += 1
        return sorted(freq.items(), key=lambda x: -x[1])

    # ─── 情报速度 ──────────────────────────────────────────────

    def get_intelligence_velocity(self) -> dict:
        """情报生成速度分析

        Returns:
            {
                "total_reports": int,
                "period_days": int,
                "reports_per_day": float,
                "daily_breakdown": {date: count},
                "top_keywords": [(keyword, count), ...],
            }
        """
        history = self.intelligence_history
        if not history:
            return {
                "total_reports": 0,
                "period_days": 0,
                "reports_per_day": 0.0,
                "daily_breakdown": {},
                "top_keywords": []
            }

        try:
            first_date = datetime.fromisoformat(history[-1]["date"])
            last_date = datetime.fromisoformat(history[0]["date"])
            period_days = max((last_date - first_date).days, 1)
        except Exception:
            period_days = 1

        # 日报分布
        daily = defaultdict(int)
        kw_freq = defaultdict(int)
        for item in history:
            daily[item["date"][:10]] += 1
            for kw in item.get("keywords", [])[:10]:
                kw_freq[kw] += 1

        return {
            "total_reports": len(history),
            "period_days": period_days,
            "reports_per_day": round(len(history) / period_days, 2),
            "daily_breakdown": dict(sorted(daily.items())),
            "top_keywords": sorted(kw_freq.items(), key=lambda x: -x[1])[:15]
        }

    def get_topic_momentum(self, topic: str, days: int = 30) -> dict:
        """特定主题的动量分析（上升/平稳/下降）"""
        history = self.intelligence_history
        cutoff = datetime.now() - timedelta(days=days)

        hits = []
        for item in history:
            try:
                date = datetime.fromisoformat(item["date"])
            except Exception:
                continue
            if date < cutoff:
                continue
            keywords = [k.lower() for k in item.get("keywords", [])]
            if topic.lower() in keywords:
                hits.append({"date": item["date"], "position": keywords.index(topic.lower())})

        if not hits:
            return {"topic": topic, "momentum": "no_recent_data", "hit_count": 0}

        # 动量 = 最近出现位置越靠前（即index越小）越强
        recent_positions = [h["position"] for h in hits[:3]] if len(hits) >= 3 else [h["position"] for h in hits]
        avg_position = sum(recent_positions) / len(recent_positions)

        if len(hits) >= 3:
            momentum = "rising" if avg_position < 5 else "stable"
        elif len(hits) >= 1:
            momentum = "stable"
        else:
            momentum = "declining"

        return {
            "topic": topic,
            "momentum": momentum,
            "hit_count": len(hits),
            "recent_positions": recent_positions,
            "avg_position": round(avg_position, 1)
        }


# ─── 使用示例 & 验证 ─────────────────────────────────────────────────────────

def demo():
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print("=" * 60)
    print("Intelligence Forecaster Demo -- Synapse v3.0 Phase 3 T1-4")
    print("=" * 60)

    fc = IntelligenceForecaster()

    # 情报速度
    velocity = fc.get_intelligence_velocity()
    print(f"\n[Intelligence Velocity]")
    print(f"  Total reports: {velocity['total_reports']} over {velocity['period_days']} days")
    print(f"  Avg per day: {velocity['reports_per_day']}")
    if velocity['top_keywords']:
        top_kw = ", ".join(f"{k}({c})" for k, c in velocity['top_keywords'][:8])
        print(f"  Top keywords: {top_kw}")

    # 预测热点
    predictions = fc.predict_trending_topics(days_ahead=7)
    print(f"\n[Trending Predictions] ({len(predictions)} topics)")
    for p in predictions[:5]:
        print(f"  [{p['urgency']:8s}] {p['topic']:25s} "
              f"conf={p['confidence']:.2f}  {p['reason'][:50]}")

    # 主题动量
    for topic in ["claude", "ai", "agent", "automation"]:
        mom = fc.get_topic_momentum(topic, days=30)
        if mom["hit_count"] > 0:
            print(f"\n  Momentum[{topic}]: {mom['momentum']} "
                  f"(hits={mom['hit_count']}, avg_pos={mom['avg_position']})")

    return fc


if __name__ == "__main__":
    demo()
