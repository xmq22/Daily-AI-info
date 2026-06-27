"""
AI Daily Digest — Main entry point

Pipeline:
  fetch_all() → curate() → build_email() → send_email()

Run locally:
    python src/main.py

Run with LLM enhancement:
    LLM_API_KEY=sk-xxx LLM_PROVIDER=openai python src/main.py
"""

import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.fetcher import fetch_all
from src.curator import curate
from src.email_builder import build_email
from src.sender import send_email


def main():
    # ── Logging ──
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    logger = logging.getLogger(__name__)

    logger.info("=" * 40)
    logger.info("AI Daily Digest — Starting pipeline")
    logger.info("=" * 40)

    # Step 1: Fetch
    logger.info("\n📡 Fetching articles…")
    all_articles = fetch_all()
    logger.info(f"  Total fetched: {len(all_articles)}")

    if not all_articles:
        logger.warning("  ⚠ No articles fetched from any source!")
        logger.info("\n📧 Sending empty digest email…")
        html, subject = build_email([])
        send_email(html, subject)
        return

    # Step 2: Curate
    logger.info("\n🎯 Curating top picks…")
    selected = curate(all_articles)
    logger.info(f"  Selected: {len(selected)} articles")

    if not selected:
        logger.warning("  ⚠ Curation returned no articles!")
        html, subject = build_email([])
        send_email(html, subject)
        return

    # Brief preview
    for i, art in enumerate(selected, 1):
        logger.info(f"  {i}. [{art.category}] {art.source}: {art.title}")

    # Step 3: Build email
    logger.info("\n📝 Building email…")
    html, subject = build_email(selected)

    # Step 4: Send
    logger.info("\n📧 Sending email…")
    success = send_email(html, subject)

    if success:
        logger.info("\n✅ Digest sent successfully!")
    else:
        logger.error("\n❌ Failed to send digest!")
        sys.exit(1)


if __name__ == "__main__":
    main()
