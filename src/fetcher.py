"""
AI Daily Digest — Content Fetcher
Fetches articles from RSS feeds and APIs, normalizes to Article dicts.
"""

import logging
import re
import time
from datetime import datetime, timezone
from typing import Optional

import feedparser
import requests
from bs4 import BeautifulSoup

from .config import SOURCES, Article

logger = logging.getLogger(__name__)

# Shared HTTP session
_session = requests.Session()
_session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
})


# ── Fetch orchestration ───────────────────────────────────────────────


def fetch_all() -> list[Article]:
    """Fetch articles from all enabled sources."""
    articles: list[Article] = []

    for source in SOURCES:
        if not source.enabled:
            continue
        try:
            if source.feed_type == "hackernews":
                fetched = _fetch_hackernews(source)
            else:
                fetched = _fetch_rss(source)

            logger.info(f"  ✓ {source.name}: got {len(fetched)} articles")
            articles.extend(fetched)
        except Exception as e:
            logger.warning(f"  ✗ {source.name}: {e}")

    return articles


# ── RSS Feed Parser ────────────────────────────────────────────────────


def _fetch_rss(source) -> list[Article]:
    """Fetch and parse a standard RSS/Atom feed."""
    resp = _session.get(source.feed_url, timeout=30)
    resp.raise_for_status()

    # Detect encoding from headers or content
    raw = resp.content
    feed = feedparser.parse(raw)

    articles: list[Article] = []
    for entry in feed.entries[:15]:  # top 15 per source
        try:
            article = _rss_entry_to_article(entry, source)
            if article and article.title and article.url:
                articles.append(article)
        except Exception as e:
            logger.debug(f"    skip entry: {e}")
            continue

    return articles


def _rss_entry_to_article(entry, source) -> Optional[Article]:
    """Convert a feedparser entry to an Article."""
    title = entry.get("title", "").strip()
    if not title:
        return None

    # Get URL
    url = ""
    if entry.get("link"):
        url = entry["link"]
    elif entry.get("id") and entry["id"].startswith("http"):
        url = entry["id"]
    if not url:
        return None

    # Skip duplicate/marker entries
    if title.startswith("Advertisement") or title.startswith("Sponsored"):
        return None

    # Extract summary / description
    summary = ""
    if entry.get("summary"):
        summary = _clean_html(entry["summary"])
    elif entry.get("description"):
        summary = _clean_html(entry["description"])
    elif entry.get("subtitle"):
        summary = _clean_html(entry["subtitle"])

    # Truncate long summaries
    if len(summary) > 300:
        summary = summary[:297] + "..."

    # Extract content snippet (first ~200 chars of full content)
    content_snippet = ""
    if entry.get("content"):
        for c in entry["content"]:
            text = _clean_html(c.get("value", ""))
            if text and len(text) > 50:
                content_snippet = text[:200]
                break
    if not content_snippet and summary:
        content_snippet = summary[:200]

    # Parse published time
    published = ""
    if entry.get("published_parsed"):
        try:
            dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            published = dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            pass
    elif entry.get("updated_parsed"):
        try:
            dt = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
            published = dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            pass

    return Article(
        title=title,
        url=url,
        source=source.name,
        category=source.category,
        language=source.language,
        summary=summary,
        content_snippet=content_snippet,
        published=published,
    )


# ── Hacker News API ────────────────────────────────────────────────────


HN_BASE = "https://hacker-news.firebaseio.com/v0"


def _fetch_hackernews(source) -> list[Article]:
    """Fetch top stories from Hacker News Firebase API."""
    from .config import curation

    # Get top story IDs
    resp = _session.get(f"{HN_BASE}/topstories.json", timeout=30)
    resp.raise_for_status()
    story_ids = resp.json()[: curation.hn_top_n]

    articles: list[Article] = []
    for story_id in story_ids:
        try:
            story_resp = _session.get(
                f"{HN_BASE}/item/{story_id}.json", timeout=15
            )
            story_resp.raise_for_status()
            story = story_resp.json()
            if not story or story.get("type") != "story":
                continue

            title = (story.get("title") or "").strip()
            url = story.get("url") or ""
            # HN discussion link fallback
            if not url:
                url = f"https://news.ycombinator.com/item?id={story_id}"

            # Skip HN-native Ask/Show posts without external links
            if not url.startswith("http"):
                continue

            text = story.get("text") or ""
            summary = _clean_html(text)[:300] if text else ""
            score = story.get("score", 0)

            published_ts = story.get("time", 0)
            published = ""
            if published_ts:
                dt = datetime.fromtimestamp(published_ts, tz=timezone.utc)
                published = dt.strftime("%Y-%m-%d %H:%M")

            # Add score as suffix for curator signal
            if score > 0:
                summary = f"[HN ▲{score}] {summary}" if summary else f"[HN ▲{score}]"

            articles.append(Article(
                title=title,
                url=url,
                source="Hacker News",
                category=source.category,
                language=source.language,
                summary=summary,
                published=published,
            ))

            # Rate-limit politeness
            time.sleep(0.1)

        except Exception as e:
            logger.debug(f"    skip HN story {story_id}: {e}")
            continue

    return articles


# ── Helpers ────────────────────────────────────────────────────────────


def _clean_html(raw: str) -> str:
    """Strip HTML tags and normalize whitespace."""
    if not raw:
        return ""
    soup = BeautifulSoup(raw, "lxml")
    text = soup.get_text(separator=" ")
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text
