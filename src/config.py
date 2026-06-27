"""
AI Daily Digest — Configuration
Defines curated sources, categories, and runtime settings.
"""

from dataclasses import dataclass, field
from typing import Optional
import os

# ── Source Definition ──────────────────────────────────────────────────


@dataclass
class Source:
    name: str              # display name
    feed_url: str          # RSS feed URL or API endpoint
    category: str          # "ai" | "startups" | "apps"
    language: str          # "zh" | "en"
    feed_type: str = "rss"  # "rss" | "hackernews"
    enabled: bool = True


# Curated sources — 9 high-quality feeds covering AI, Startups & Apps
SOURCES: list[Source] = [
    # ── International / English ──
    Source(
        name="TechCrunch AI",
        feed_url="https://techcrunch.com/tag/ai/feed/",
        category="ai",
        language="en",
    ),
    Source(
        name="TechCrunch Startups",
        feed_url="https://techcrunch.com/tag/startups/feed/",
        category="startups",
        language="en",
    ),
    Source(
        name="Hacker News",
        feed_url="https://hacker-news.firebaseio.com/v0/",
        category="startups",
        language="en",
        feed_type="hackernews",
    ),
    Source(
        name="Product Hunt",
        feed_url="https://www.producthunt.com/feed",
        category="apps",
        language="en",
    ),
    Source(
        name="The Verge",
        feed_url="https://www.theverge.com/rss/index.xml",
        category="ai",
        language="en",
    ),
    # ── Chinese / 中文 ──
    Source(
        name="机器之心",
        feed_url="https://www.jiqizhixin.com/rss",
        category="ai",
        language="zh",
    ),
    Source(
        name="量子位",
        feed_url="https://www.qbitai.com/feed",
        category="ai",
        language="zh",
    ),
    Source(
        name="36氪",
        feed_url="https://rsshub.app/36kr/news/latest",
        category="startups",
        language="zh",
    ),
    Source(
        name="少数派",
        feed_url="https://sspai.com/feed",
        category="apps",
        language="zh",
    ),
]


# ── Article Data Structure ─────────────────────────────────────────────


@dataclass
class Article:
    title: str
    url: str
    source: str            # source display name
    category: str          # "ai" | "startups" | "apps"
    language: str          # "zh" | "en"
    summary: str = ""      # article excerpt or description
    content_snippet: str = ""  # first ~200 chars of body
    published: str = ""    # human-readable date


# ── Curation Settings ──────────────────────────────────────────────────


@dataclass
class CurationConfig:
    """How many articles to pick for each category."""
    target_count: int = 3         # total articles in final digest (2-3)
    max_per_category: int = 2     # max from same category
    min_zh_count: int = 1         # at least 1 Chinese article
    hn_top_n: int = 20            # how many top HN stories to evaluate


# ── Email Settings (from env vars) ─────────────────────────────────────


@dataclass
class EmailConfig:
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.qq.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "465"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_pass: str = os.getenv("SMTP_PASS", "")
    email_to: str = os.getenv("EMAIL_TO", "")
    email_from_name: str = os.getenv("EMAIL_FROM_NAME", "AI Daily Digest")


# ── Optional LLM Enhancement ──────────────────────────────────────────


@dataclass
class LLMConfig:
    """Set LLM_API_KEY env var to enable AI-powered summarization."""
    api_key: Optional[str] = os.getenv("LLM_API_KEY")
    provider: str = os.getenv("LLM_PROVIDER", "openai")  # or "claude"
    enabled: bool = field(default=False)

    def __post_init__(self):
        self.enabled = bool(self.api_key)


# ── Global Config ──────────────────────────────────────────────────────


curation = CurationConfig()
email = EmailConfig()
llm = LLMConfig()
