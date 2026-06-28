"""
AI Daily Digest — Email Builder
Renders the HTML email from Jinja2 template with selected articles.
"""

import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .config import Article

logger = logging.getLogger(__name__)

# Jinja2 setup
_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
_env = Environment(loader=FileSystemLoader(str(_TEMPLATE_DIR)))


def build_email(articles: list[Article]) -> tuple[str, str]:
    """
    Build HTML email content from curated articles.

    Returns:
        (html_body: str, subject: str)
    """
    template = _env.get_template("email.html")

    # Date in Beijing time (UTC+8)
    beijing_tz = timezone(timedelta(hours=8))
    today = datetime.now(beijing_tz)

    # Weekday in Chinese
    weekday_map = {
        0: "星期一", 1: "星期二", 2: "星期三", 3: "星期四",
        4: "星期五", 5: "星期六", 6: "星期日",
    }
    weekday_cn = weekday_map.get(today.weekday(), "")
    date_display = today.strftime(f"%Y 年 %m 月 %d 日 · {weekday_cn}")

    # Render
    html = template.render(articles=articles, date=date_display)

    # Subject line with emoji
    subject = f"📰 AI Daily Digest | {today.strftime('%m/%d')} ({len(articles)} 篇)"

    return html, subject
