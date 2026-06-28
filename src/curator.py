"""
AI Daily Digest — Content Curator
Selects the best 2-3 articles from the fetched pool using smart rules.
Supports optional LLM enhancement for better summaries.
"""

import logging
import random
from collections import defaultdict
from typing import Optional

from .config import Article, curation, llm as llm_cfg

logger = logging.getLogger(__name__)


def curate(articles: list[Article]) -> list[Article]:
    """
    Select the best 2-3 articles for today's digest.

    Strategy:
    1. Score & rank each article by freshness + source quality
    2. Ensure diversity: at least 1 Chinese article, max 2 per category
    3. Pick top candidates balancing the above constraints
    """
    if not articles:
        logger.warning("No articles to curate!")
        return []

    # ── Score each article ──
    scored = [_score_article(a) for a in articles]
    scored.sort(key=lambda x: x[1], reverse=True)

    logger.info(f"Scored {len(scored)} articles, top-5:")
    for a, s in scored[:5]:
        logger.info(f"  [{s:.1f}] {a.source} → {a.title[:60]}")

    # ── Greedy selection with diversity constraints ──
    selected: list[Article] = []
    seen_urls: set[str] = set()
    cat_count: dict[str, int] = defaultdict(int)
    lang_count: dict[str, int] = defaultdict(int)

    for article, score in scored:
        if len(selected) >= curation.target_count:
            break

        # Dedup
        if article.url in seen_urls:
            continue

        # Category diversity
        if cat_count[article.category] >= curation.max_per_category:
            continue

        selected.append(article)
        seen_urls.add(article.url)
        cat_count[article.category] += 1
        lang_count[article.language] = lang_count.get(article.language, 0) + 1

    # ── Fallback: if no Chinese article, swap the lowest-ranked non-Chinese ──
    if lang_count.get("zh", 0) < curation.min_zh_count:
        zh_candidates = [
            a for a, s in scored
            if a.language == "zh" and a.url not in seen_urls
        ]
        if zh_candidates:
            # Remove the lowest-ranked selected article
            removed = selected.pop()
            cat_count[removed.category] -= 1
            lang_count[removed.language] -= 1
            seen_urls.discard(removed.url)

            # Pick best Chinese article that fits category constraint
            for zh_a in zh_candidates:
                if cat_count[zh_a.category] < curation.max_per_category:
                    selected.append(zh_a)
                    cat_count[zh_a.category] += 1
                    lang_count[zh_a.language] += 1
                    seen_urls.add(zh_a.url)
                    logger.info(f"  ↻ Swapped in Chinese article: {zh_a.title[:60]}")
                    break

    # ── Sort by category for consistent email layout ──
    category_order = {"ai_models": 0, "ai_apps": 1, "business": 2}
    selected.sort(key=lambda a: category_order.get(a.category, 99))

    # ── Optional: LLM-enhanced summaries ──
    if llm_cfg.enabled:
        try:
            selected = _llm_enhance(selected)
        except Exception as e:
            logger.warning(f"LLM enhancement failed: {e}")

    logger.info(f"Final digest: {len(selected)} articles")
    return selected


# ── Scoring Logic ──────────────────────────────────────────────────────


def _score_article(article: Article) -> tuple[Article, float]:
    """
    Score an article on freshness, source authority, and content quality.

    Returns (article, score) tuple.
    """
    score = 50.0  # base

    # Authority bonus by source
    authority_bonus = {
        "TechCrunch AI": 20,
        "TechCrunch Startups": 20,
        "机器之心": 18,
        "量子位": 18,
        "Product Hunt": 15,
        "The Verge": 15,
        "36氪": 15,
        "少数派": 12,
        "ArsTechnica": 18,
        "MIT Technology Review": 20,
        "VentureBeat": 16,
    }
    score += authority_bonus.get(article.source, 5)

    # Content quality signals
    if len(article.title) > 15:
        score += 5  # substantial title
    if article.summary and len(article.summary) > 50:
        score += 5  # has a real summary

    # Freshness — prefer newer articles (slight random to avoid staleness)
    score += random.uniform(0, 3)

    return (article, score)


# ── Optional LLM Enhancement ──────────────────────────────────────────


def _llm_enhance(articles: list[Article]) -> list[Article]:
    """
    Use an LLM API to rewrite summaries for selected articles.
    Requires LLM_API_KEY to be set.
    """
    provider = llm_cfg.provider.lower()

    if provider == "openai":
        return _enhance_with_openai(articles)
    elif provider == "claude":
        return _enhance_with_claude(articles)
    else:
        logger.warning(f"Unknown LLM provider: {provider}")
        return articles


def _enhance_with_openai(articles: list[Article]) -> list[Article]:
    """Use OpenAI to generate concise summaries."""
    import openai

    openai.api_key = llm_cfg.api_key

    for article in articles:
        if not article.summary:
            continue
        prompt = (
            f"Summarize this article in 1-2 sentences in {article.language}:\n\n"
            f"Title: {article.title}\n{article.summary[:500]}"
        )
        try:
            resp = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3,
            )
            new_summary = resp.choices[0].message.content.strip()
            if new_summary:
                article.summary = new_summary
        except Exception as e:
            logger.debug(f"OpenAI enhancement failed for {article.title}: {e}")

    return articles


def _enhance_with_claude(articles: list[Article]) -> list[Article]:
    """Use Claude API to generate concise summaries."""
    import anthropic

    client = anthropic.Anthropic(api_key=llm_cfg.api_key)

    for article in articles:
        if not article.summary:
            continue
        prompt = (
            f"Summarize this article in 1-2 sentences in {article.language}:\n\n"
            f"Title: {article.title}\n{article.summary[:500]}"
        )
        try:
            resp = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=150,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}],
            )
            new_summary = resp.content[0].text.strip()
            if new_summary:
                article.summary = new_summary
        except Exception as e:
            logger.debug(f"Claude enhancement failed for {article.title}: {e}")

    return articles
