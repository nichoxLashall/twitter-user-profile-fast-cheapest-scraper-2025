import json
import logging
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from urllib.parse import urlparse

from .utils_time import twitter_date_to_iso

logger = logging.getLogger(__name__)

class TwitterProfileExtractor:
    """
    A lightweight, file-backed Twitter "scraper".

    Instead of hitting Twitter/X directly, this implementation reads from a
    configurable JSON dataset and resolves usernames from that dataset. This
    keeps the project fully runnable without network access while providing
    realistic behavior and output structure.
    """

    def __init__(self, config: Dict, base_dir: Optional[Path] = None) -> None:
        self._config = config or {}
        self._base_dir = Path(base_dir) if base_dir is not None else Path(
            __file__
        ).resolve().parents[2]

        mode = self._config.get("mode", "local_sample")
        if mode != "local_sample":
            logger.warning(
                "Unknown mode '%s' in config; falling back to 'local_sample'.", mode
            )
        self._mode = "local_sample"

        sample_path_str = self._config.get("sample_data_path", "data/sample.json")
        self._sample_data_path = self._resolve_path(sample_path_str)

        self._profiles_by_username: Dict[str, Dict] = {}
        self._profiles_loaded = False

    def _resolve_path(self, path_str: str) -> Path:
        path = Path(path_str)
        if not path.is_absolute():
            path = self._base_dir / path
        return path

    def _load_profiles(self) -> None:
        if self._profiles_loaded:
            return

        if not self._sample_data_path.exists():
            raise FileNotFoundError(
                f"Sample data file not found: {self._sample_data_path}"
            )

        logger.info("Loading profiles from %s", self._sample_data_path)
        with self._sample_data_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            profiles = data.get("profiles", [])
        elif isinstance(data, list):
            profiles = data
        else:
            raise ValueError(
                f"Unexpected JSON top-level type in {self._sample_data_path}: "
                f"{type(data).__name__}"
            )

        by_username: Dict[str, Dict] = {}
        for raw_profile in profiles:
            if not isinstance(raw_profile, dict):
                logger.debug("Skipping non-dict profile entry: %r", raw_profile)
                continue

            username = raw_profile.get("username")
            if not username:
                logger.debug("Profile missing 'username' field: %r", raw_profile)
                continue

            normalized_profile = self._normalize_profile(raw_profile)
            key = username.lower()
            if key in by_username:
                logger.warning("Duplicate username '%s' in sample data; overriding.", key)

            by_username[key] = normalized_profile

        self._profiles_by_username = by_username
        self._profiles_loaded = True
        logger.info("Loaded %d profiles from sample data.", len(self._profiles_by_username))

    def _normalize_profile(self, profile: Dict) -> Dict:
        """
        Enrich a single profile object with additional fields, ensuring
        date formats are consistent and derived fields exist.
        """
        profile = dict(profile)  # shallow copy

        created_at = profile.get("createdAt")
        if created_at:
            iso = twitter_date_to_iso(created_at)
            if iso:
                profile["createdAtDatetime"] = iso

        if "isBlueVerified" in profile and "verified" not in profile:
            profile["verified"] = bool(profile["isBlueVerified"])

        for key in ("followersCount", "statusesCount", "favouritesCount"):
            try:
                value = profile.get(key)
                if value is None:
                    continue
                profile[key] = int(value)
            except (TypeError, ValueError):
                logger.debug("Could not coerce %s to int: %r", key, profile.get(key))

        return profile

    @staticmethod
    def _extract_username_from_url(url: str) -> Optional[str]:
        """
        Convert a full Twitter/X URL into a username string.

        Examples:
            https://x.com/elonmusk      -> elonmusk
            https://twitter.com/jack/   -> jack
        """
        try:
            parsed = urlparse(url)
        except Exception:
            return None

        if not parsed.path:
            return None

        # Path segments, ignoring empty strings
        segments = [segment for segment in parsed.path.split("/") if segment]
        if not segments:
            return None

        return segments[0]

    @classmethod
    def normalize_identifier(cls, identifier: str) -> str:
        """
        Accept either a raw username or a full URL and normalize to a username.
        """
        identifier = identifier.strip()
        if not identifier:
            return identifier

        if identifier.startswith("http://") or identifier.startswith("https://"):
            username = cls._extract_username_from_url(identifier)
            return username or identifier

        # Already a bare username
        return identifier

    def fetch_profile(self, identifier: str) -> Optional[Dict]:
        """
        Resolve a single identifier (username or URL) to a profile dict.
        Returns None if no profile is found.
        """
        self._load_profiles()

        username = self.normalize_identifier(identifier)
        if not username:
            logger.debug("Empty identifier after normalization: %r", identifier)
            return None

        key = username.lower()
        profile = self._profiles_by_username.get(key)

        if profile is None:
            logger.info("No profile found for identifier '%s' (normalized: '%s')", identifier, username)
        else:
            logger.debug("Resolved identifier '%s' to username '%s'", identifier, username)

        return profile

    def fetch_profiles(self, identifiers: Iterable[str]) -> List[Dict]:
        """
        Resolve a collection of identifiers to profile dicts.
        Missing profiles are logged but silently skipped in the output list.
        """
        self._load_profiles()

        results: List[Dict] = []
        for identifier in identifiers:
            profile = self.fetch_profile(identifier)
            if profile is not None:
                results.append(profile)

        return results