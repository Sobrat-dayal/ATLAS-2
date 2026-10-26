"""Canonical Article Deduplication, Fingerprinting, and Revision Management (Stage 99)."""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from atlas.news.articles import NewsArticle, NewsArticleRevision
from atlas.news.enums import (
    NewsAvailabilityStatus,
    NewsChangeType,
)
from atlas.news.normalization import normalize_canonical_url, sanitize_plain_text


def generate_canonical_article_id(
    source_provider_id: str,
    canonical_url: str,
    publisher_article_id: Optional[str] = None,
) -> str:
    """
    Computes a deterministic, stable canonical article identifier.
    Prioritizes provider + publisher_article_id if provided, falling back to canonical_url hash.
    """
    if publisher_article_id and publisher_article_id.strip():
        seed = f"{source_provider_id.strip().lower()}:{publisher_article_id.strip()}"
    elif canonical_url and canonical_url.strip():
        norm_url = normalize_canonical_url(canonical_url)
        seed = f"url:{norm_url}"
    else:
        seed = f"random:{datetime.now(timezone.utc).isoformat()}"

    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:24]
    return f"art-{digest}"


def generate_content_fingerprint(headline: str, publisher: str) -> str:
    """
    Creates a normalized alphanumeric token fingerprint for fuzzy and syndicated duplicate detection.
    """
    clean_hl = re.sub(r"[^a-zA-Z0-9\s]", "", headline.lower())
    tokens = [t for t in clean_hl.split() if t]
    tokens.sort()
    token_str = " ".join(tokens)
    seed = f"{publisher.strip().lower()}:{token_str}"
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:20]


class DeduplicationResult:
    """Outcome of running an incoming article through deduplication."""

    def __init__(
        self,
        article: NewsArticle,
        is_new: bool,
        is_revision: bool,
        is_exact_duplicate: bool,
        is_syndicated: bool,
        revision_record: Optional[NewsArticleRevision] = None,
    ):
        self.article = article
        self.is_new = is_new
        self.is_revision = is_revision
        self.is_exact_duplicate = is_exact_duplicate
        self.is_syndicated = is_syndicated
        self.revision_record = revision_record


class DeduplicationEngine:
    """
    Manages deterministic identity, duplicate suppression, syndicated wire mapping,
    and revision lifecycle.
    """

    def __init__(self) -> None:
        # article_id -> NewsArticle
        self._articles_by_id: Dict[str, NewsArticle] = {}
        # canonical_url -> article_id
        self._url_to_id: Dict[str, str] = {}
        # (provider_id, publisher_article_id) -> article_id
        self._provider_id_to_id: Dict[Tuple[str, str], str] = {}
        # content_fingerprint -> article_id
        self._fingerprint_to_id: Dict[str, str] = {}
        # article_id -> List[NewsArticleRevision]
        self._revisions_by_id: Dict[str, List[NewsArticleRevision]] = {}

    def process_incoming_article(self, incoming: NewsArticle) -> DeduplicationResult:
        """
        Processes an incoming candidate article:
        1. Checks for exact ID / provider native ID matches.
        2. Checks for normalized canonical URL matches.
        3. Identifies revisions / corrections vs exact identical re-ingestions.
        4. Detects syndicated copies across distributors.
        """
        canonical_url = normalize_canonical_url(incoming.canonical_url or incoming.original_url)
        provider_key = (
            incoming.source_provider_id.lower(),
            (incoming.publisher_article_id or "").strip(),
        )

        existing_id: Optional[str] = None

        # 1. Check direct ID match
        if incoming.article_id and incoming.article_id in self._articles_by_id:
            existing_id = incoming.article_id

        # 2. Check provider native ID
        if not existing_id and provider_key[1]:
            existing_id = self._provider_id_to_id.get(provider_key)

        # 3. Check canonical URL
        if not existing_id and canonical_url:
            existing_id = self._url_to_id.get(canonical_url)

        # Content fingerprint
        fp = generate_content_fingerprint(incoming.headline or incoming.title, incoming.publisher)

        # If existing article identified:
        if existing_id and existing_id in self._articles_by_id:
            existing = self._articles_by_id[existing_id]

            # Check if metadata or content actually changed
            sanitized_incoming_hl = sanitize_plain_text(incoming.headline or incoming.title)
            sanitized_existing_hl = sanitize_plain_text(existing.headline or existing.title)
            sanitized_incoming_ex = sanitize_plain_text(incoming.permitted_excerpt or incoming.summary)
            sanitized_existing_ex = sanitize_plain_text(existing.permitted_excerpt or existing.summary)

            is_content_changed = (
                sanitized_incoming_hl != sanitized_existing_hl
                or (sanitized_incoming_ex and sanitized_incoming_ex != sanitized_existing_ex)
            )

            # Check if withdrawal was flagged
            is_withdrawn = incoming.availability_status == NewsAvailabilityStatus.WITHDRAWN

            if is_content_changed or is_withdrawn:
                # This is a valid Revision / Correction
                new_rev_number = existing.revision + 1
                change_type = (
                    NewsChangeType.WITHDRAWAL
                    if is_withdrawn
                    else NewsChangeType.HEADLINE_CORRECTION
                )
                rev_id = f"rev-{existing_id}-{new_rev_number}"
                now_utc = datetime.now(timezone.utc)

                rev = NewsArticleRevision(
                    revision_id=rev_id,
                    article_id=existing_id,
                    revision_number=new_rev_number,
                    observed_at=now_utc,
                    source_updated_at=incoming.source_updated_at or now_utc,
                    change_type=change_type,
                    headline=sanitized_incoming_hl,
                    permitted_excerpt=None if is_withdrawn else sanitized_incoming_ex,
                    change_summary="Published correction or metadata update",
                )

                updated_dict = existing.model_dump()
                updated_dict["headline"] = sanitized_incoming_hl
                updated_dict["title"] = sanitized_incoming_hl
                updated_dict["permitted_excerpt"] = None if is_withdrawn else sanitized_incoming_ex
                updated_dict["summary"] = None if is_withdrawn else sanitized_incoming_ex
                updated_dict["revision"] = new_rev_number
                updated_dict["source_updated_at"] = incoming.source_updated_at or now_utc
                updated_dict["is_corrected"] = True
                updated_dict["correction_details"] = "Source updated article content"
                if is_withdrawn:
                    updated_dict["availability_status"] = NewsAvailabilityStatus.WITHDRAWN

                updated_article = NewsArticle.model_validate(updated_dict)
                self._articles_by_id[existing_id] = updated_article

                if existing_id not in self._revisions_by_id:
                    self._revisions_by_id[existing_id] = []
                self._revisions_by_id[existing_id].append(rev)

                return DeduplicationResult(
                    article=updated_article,
                    is_new=False,
                    is_revision=True,
                    is_exact_duplicate=False,
                    is_syndicated=False,
                    revision_record=rev,
                )
            else:
                # Exact identical duplicate - idempotent no-op
                return DeduplicationResult(
                    article=existing,
                    is_new=False,
                    is_revision=False,
                    is_exact_duplicate=True,
                    is_syndicated=False,
                )

        # 4. Check for syndication from wire service
        is_syndicated = False
        syndicated_parent_id: Optional[str] = None
        if fp in self._fingerprint_to_id:
            parent_id = self._fingerprint_to_id[fp]
            parent_article = self._articles_by_id.get(parent_id)
            if parent_article and parent_article.publisher != incoming.publisher:
                # Distinct publisher with identical content fingerprint -> Syndicated copy
                is_syndicated = True
                syndicated_parent_id = parent_id

        # 5. Brand New Article
        art_id = incoming.article_id or generate_canonical_article_id(
            source_provider_id=incoming.source_provider_id,
            canonical_url=canonical_url,
            publisher_article_id=incoming.publisher_article_id,
        )

        now_utc = datetime.now(timezone.utc)
        sanitized_hl = sanitize_plain_text(incoming.headline or incoming.title)
        sanitized_ex = sanitize_plain_text(incoming.permitted_excerpt or incoming.summary)

        new_dict = incoming.model_dump()
        new_dict["article_id"] = art_id
        new_dict["canonical_url"] = canonical_url
        new_dict["headline"] = sanitized_hl
        new_dict["title"] = sanitized_hl
        new_dict["permitted_excerpt"] = sanitized_ex
        new_dict["summary"] = sanitized_ex
        new_dict["first_seen_at"] = incoming.first_seen_at or now_utc
        new_dict["ingested_at"] = incoming.ingested_at or now_utc
        if is_syndicated:
            new_dict["syndicated_from_id"] = syndicated_parent_id

        persisted = NewsArticle.model_validate(new_dict)

        # Index new article
        self._articles_by_id[art_id] = persisted
        if canonical_url:
            self._url_to_id[canonical_url] = art_id
        if provider_key[1]:
            self._provider_id_to_id[provider_key] = art_id
        self._fingerprint_to_id[fp] = art_id

        # Initial revision
        initial_rev = NewsArticleRevision(
            revision_id=f"rev-{art_id}-1",
            article_id=art_id,
            revision_number=1,
            observed_at=now_utc,
            source_updated_at=persisted.source_updated_at,
            change_type=NewsChangeType.INITIAL_INGESTION,
            headline=sanitized_hl,
            permitted_excerpt=sanitized_ex,
            change_summary="Initial article ingestion",
        )
        self._revisions_by_id[art_id] = [initial_rev]

        return DeduplicationResult(
            article=persisted,
            is_new=True,
            is_revision=False,
            is_exact_duplicate=False,
            is_syndicated=is_syndicated,
            revision_record=initial_rev,
        )

    def get_article(self, article_id: str) -> Optional[NewsArticle]:
        return self._articles_by_id.get(article_id)

    def get_revisions(self, article_id: str) -> List[NewsArticleRevision]:
        return self._revisions_by_id.get(article_id, [])

    def clear(self) -> None:
        self._articles_by_id.clear()
        self._url_to_id.clear()
        self._provider_id_to_id.clear()
        self._fingerprint_to_id.clear()
        self._revisions_by_id.clear()
