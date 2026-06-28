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
    category: str          # "ai_models" | "ai_apps" | "interesting"
    language: str          # "zh" | "en"
    feed_type: str = "rss"
    enabled: bool = True
    keyword_filter: bool = False  # enable AI keyword filtering for broad feeds


# Curated sources — precisely assigned by category
SOURCES: list[Source] = [
    # ── AI Models / Foundation Models ──
    Source(
        name="TechCrunch AI",
        feed_url="https://techcrunch.com/tag/ai/feed/",
        category="ai_models",
        language="en",
    ),
    Source(
        name="The Verge",
        feed_url="https://www.theverge.com/rss/index.xml",
        category="ai_models",
        language="en",
        keyword_filter=True,  # broad feed → filter for AI keywords
    ),
    Source(
        name="ArsTechnica",
        feed_url="https://feeds.arstechnica.com/arstechnica/index",
        category="ai_models",
        language="en",
        keyword_filter=True,  # broad feed → filter for AI keywords
    ),
    Source(
        name="机器之心",
        feed_url="https://www.jiqizhixin.com/rss",
        category="ai_models",
        language="zh",
    ),
    # ── AI Applications / Tools / Agents ──
    Source(
        name="Product Hunt",
        feed_url="https://www.producthunt.com/feed",
        category="ai_apps",
        language="en",
    ),
    Source(
        name="VentureBeat",
        feed_url="https://venturebeat.com/feed/",
        category="ai_apps",
        language="en",
    ),
    Source(
        name="量子位",
        feed_url="https://www.qbitai.com/feed",
        category="ai_apps",
        language="zh",
    ),
    Source(
        name="少数派",
        feed_url="https://sspai.com/feed",
        category="ai_apps",
        language="zh",
    ),
    # ── Interesting News (any topic) ──
    Source(
        name="MIT Technology Review",
        feed_url="https://www.technologyreview.com/feed/",
        category="interesting",
        language="en",
    ),
]


# ── Article Data Structure ─────────────────────────────────────────────


@dataclass
class Article:
    title: str
    url: str
    source: str            # source display name
    category: str          # "ai_models" | "ai_apps" | "interesting"
    language: str          # "zh" | "en"
    summary: str = ""      # article excerpt or description
    content_snippet: str = ""  # first ~200 chars of body
    published: str = ""    # human-readable date


# ── Curation Settings ──────────────────────────────────────────────────


@dataclass
class CurationConfig:
    """How many articles to pick for each category."""
    target_count: int = 4         # total articles in final digest (3-4)
    max_per_category: int = 2     # max from same category
    min_zh_count: int = 1         # at least 1 Chinese article


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
