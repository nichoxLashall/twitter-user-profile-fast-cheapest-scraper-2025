import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

TWITTER_DATE_FORMAT = "%a %b %d %H:%M:%S %z %Y"

def parse_twitter_date(date_str: str) -> Optional[datetime]:
    """
    Parse a Twitter-style createdAt date string into a timezone-aware datetime.

    Example input:
        "Mon Oct 14 13:19:17 +0000 2024"
    """
    if not date_str:
        return None

    try:
        dt = datetime.strptime(date_str, TWITTER_DATE_FORMAT)
    except ValueError as exc:
        logger.warning("Failed to parse Twitter date '%s': %s", date_str, exc)
        return None

    # Ensure UTC normalization
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)

    return dt

def twitter_date_to_iso(date_str: str) -> Optional[str]:
    """
    Convert a Twitter-style createdAt string into an ISO 8601 string.

    Returns None if parsing fails.
    """
    dt = parse_twitter_date(date_str)
    if dt is None:
        return None
    return dt.isoformat()