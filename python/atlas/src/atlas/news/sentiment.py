"""Financial News Sentiment, Entity Relevance and Tone Classification Engine (Stage 102).

Provides institutional-grade, target-specific financial language analysis,
evidence-grounded sentiment classification, aspect tagging, and reproducible
evaluation metrics without fabricating sentiment or confusing journalistic tone
with investment recommendations.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from atlas.news.articles import NewsArticle
from atlas.news.enums import (
    NewsClassificationMethod,
    NewsEntityRelevanceClass,
    NewsEvidenceScope,
    NewsFinancialAspect,
    NewsSentimentLabel,
)
from atlas.news.origin import NewsDataOrigin


@dataclass(frozen=True)
class SentimentEvidenceReference:
    """Grounding citation linking a sentiment annotation to verified source text."""

    evidence_id: str
    article_revision_id: str
    evidence_scope: NewsEvidenceScope
    text_span: Optional[str] = None
    rationale_code: str = "DIRECT_FINANCIAL_STATEMENT"
    source_rights: str = "LICENSED_EXCERPT"


@dataclass
class NewsSentimentAnnotation:
    """Target-aware, evidence-grounded financial sentiment annotation."""

    annotation_id: str
    article_id: str
    article_revision_id: str
    target_entity_id: str
    target_entity_type: str
    target_canonical_name: Optional[str]
    target_ticker: Optional[str]
    sentiment_label: NewsSentimentLabel
    sentiment_aspect: NewsFinancialAspect
    sentiment_score: float
    confidence_score: Optional[float]
    classification_status: str
    classification_method: NewsClassificationMethod
    classifier_version: str
    taxonomy_version: str
    evidence: List[SentimentEvidenceReference] = field(default_factory=list)
    explanation: Optional[str] = None
    source_published_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    analysis_created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    retrospective_reprocessing: bool = False


@dataclass
class NewsEntityRelevance:
    """Direct journalistic relevance qualification of an article toward an entity."""

    relevance_id: str
    article_id: str
    article_revision_id: str
    entity_id: str
    entity_type: str
    canonical_name: str
    ticker: Optional[str]
    relevance_class: NewsEntityRelevanceClass
    relevance_score: float
    evidence_source: NewsEvidenceScope
    is_primary_subject: bool
    is_direct_participant: bool
    source_published_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class EntitySentimentAggregate:
    """Source-independent aggregated sentiment summary for a canonical entity."""

    target_entity_id: str
    target_canonical_name: Optional[str]
    target_ticker: Optional[str]
    evaluation_window_days: int
    eligible_count: int
    positive_count: int
    negative_count: int
    neutral_count: int
    mixed_count: int
    insufficient_evidence_count: int
    net_sentiment: float
    unique_story_count: int
    independent_publisher_count: int
    top_aspects: List[Dict[str, Any]] = field(default_factory=list)
    coverage_completeness: str = "MODERATE"
    methodology_version: str = "v1.0.0-institutional"
    evaluation_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SentimentTimelineBucket:
    """Chronologically bucketed sentiment observation cohort."""

    bucket_start: datetime
    bucket_end: datetime
    label: str
    eligible_count: int
    positive_count: int
    negative_count: int
    neutral_count: int
    mixed_count: int
    net_sentiment: float


@dataclass
class StorySentimentProfile:
    """Sentiment distribution aggregated across member articles in a Story Thread."""

    story_id: str
    target_entity_id: str
    distribution: Dict[str, int]
    net_sentiment: float
    eligible_article_count: int
    independent_source_count: int
    evaluation_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class EventSentimentProfile:
    """Sentiment evaluation aggregated across evidence supporting a Financial Event."""

    event_id: str
    target_entity_id: str
    distribution: Dict[str, int]
    net_sentiment: float
    eligible_evidence_count: int
    assertion_status: str
    evaluation_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# Curated financial tone dictionaries
POSITIVE_FINANCIAL_PATTERNS = [
    (r"\b(beats?|beating|topped|topping|exceeded|outperformed)\s+(?:[\w\s\-]{0,30}\s+)?(estimates?|expectations?|forecasts?|consensus)\b", NewsFinancialAspect.EARNINGS_PERFORMANCE),
    (r"\b(record|surged?|jumped?|soared?|rallied?|accelerat\w+)\s+(?:[\w\s\-]{0,30}\s+)?(revenue|profit|sales|earnings|growth|income)\b", NewsFinancialAspect.PROFITABILITY),
    (r"\b(raised?|raising|hiked?|boosted?|increased?)\s+(?:[\w\s\-]{0,30}\s+)?(dividend|payout|guidance|forecast|target|outlook)\b", NewsFinancialAspect.EARNINGS_GUIDANCE),
    (r"\b(authoriz\w+|announced?|expanded?)\s+(?:[\w\$\d\s\-]{0,30}\s+)?(buybacks?|share\s+repurchas\w+)\b", NewsFinancialAspect.CORPORATE_TRANSACTION),
    (r"\b(upgraded?|outperform|buy\s+rating|positive\s+outlook)\b", NewsFinancialAspect.OPERATIONAL_PERFORMANCE),
    (r"\b(secures?|wins?|awarded?)\s+(?:[\w\s\-]{0,30}\s+)?(contract|deal|order|license|partnership)\b", NewsFinancialAspect.REVENUE_GROWTH),
    (r"\b(regulatory\s+(approval|clearance)|regulators?\s+cleared?|fda\s+approved?)\b", NewsFinancialAspect.REGULATORY_EXPOSURE),
    (r"\b(debt\s+reduced?|deleverag\w+|cash\s+flow\s+positive)\b", NewsFinancialAspect.BALANCE_SHEET),
    (r"\b(successful|expanded)\s+(product\s+launch|facility|expansion)\b", NewsFinancialAspect.PRODUCT_DEVELOPMENT),
    (r"\b(narrowed?|reduced?|smaller\s+than\s+expected)\s+loss\b", NewsFinancialAspect.PROFITABILITY),
    (r"\b(higher-than-expected|better-than-expected)\s+(?:[\w\s\-]{0,30}\s+)?(revenue|profit|sales|earnings|growth|income)\b", NewsFinancialAspect.REVENUE_GROWTH),
]

NEGATIVE_FINANCIAL_PATTERNS = [
    (r"\b(missed?|missing|fell\s+short|trailed?)\s+(?:[\w\s\-]{0,30}\s+)?(estimates?|expectations?|forecasts?|consensus)?\b", NewsFinancialAspect.EARNINGS_PERFORMANCE),
    (r"\b(profit\s+warning|slashed?|slashes|cut|lowered?|reduced?)\s+(?:[\w\s\-]{0,30}\s+)?(guidance|forecast|outlook|dividend)\b", NewsFinancialAspect.EARNINGS_GUIDANCE),
    (r"\b(loss\s+widens?|plunged?|slumped?|tumbled?|dropped?|margins?\s+shrank)\s+(?:[\w\s\-]{0,30}\s+)?(revenue|profit|shares?|income|on\s+price)?\b", NewsFinancialAspect.PROFITABILITY),
    (r"\b(downgraded?|underperform|sell\s+rating|negative\s+outlook)\b", NewsFinancialAspect.OPERATIONAL_PERFORMANCE),
    (r"\b(investigation|subpoena|probe|lawsuit|litigation|sued?|allegations?)\b", NewsFinancialAspect.REGULATORY_EXPOSURE),
    (r"\b(regulatory\s+)?(fine|penalty|sanction|enforcement\s+action)\b", NewsFinancialAspect.REGULATORY_EXPOSURE),
    (r"\b(bankruptcy|insolvency|chapter\s+11|debt\s+default|restructuring)\b", NewsFinancialAspect.DEBT_FINANCING),
    (r"\b(executive\s+departure|resigned?|ousted?|stepping\s+down)\b", NewsFinancialAspect.MANAGEMENT),
    (r"\b(layoffs?|job\s+cuts?|workforce\s+reduction)\b", NewsFinancialAspect.OPERATIONAL_PERFORMANCE),
    (r"\b(debt\s+burden|liquidity\s+crunch|credit\s+downgrade)\b", NewsFinancialAspect.BALANCE_SHEET),
]

NEGATION_PATTERNS = r"\b(not|no|denies?|denied|avoided?|fails?\s+to|without)\b"


def _get_article_revision_id(article: NewsArticle) -> str:
    rev = getattr(article, "revision_id", None)
    if rev:
        return str(rev)
    rev_num = getattr(article, "revision", 1)
    return f"{article.article_id}-rev{rev_num}"


class FinancialSentimentClassifier:
    """Deterministic, rule-backed financial sentiment and relevance classifier.

    Extracts target-specific financial tone, detects multi-entity perspectives,
    tags financial aspects, and evaluates against golden benchmark suites.
    """

    CLASSIFIER_VERSION = "v1.0.0-institutional-rules"
    TAXONOMY_VERSION = "v1.0.0"

    @classmethod
    def classify_article_target(
        cls,
        article: NewsArticle,
        target_entity_id: str,
        target_name: Optional[str] = None,
        target_ticker: Optional[str] = None,
    ) -> NewsSentimentAnnotation:
        """Classify financial sentiment toward a specific canonical entity in an article."""
        text = f"{article.headline} {article.permitted_excerpt or ''}".strip()
        scope = NewsEvidenceScope.LICENSED_EXCERPT if article.permitted_excerpt else NewsEvidenceScope.HEADLINE

        if len(text.split()) < 3:
            return cls._create_abstention(article, target_entity_id, target_name, target_ticker, scope)

        # Check entity presence
        target_present = False
        target_keywords = []
        if target_ticker:
            target_keywords.append(target_ticker.lower())
            target_keywords.append(f"${target_ticker.lower()}")
        if target_name:
            target_keywords.append(target_name.lower())
            # Add short names (e.g. "Apple" for "Apple Inc.")
            clean_name = re.sub(r"\b(inc|corp|corporation|ltd|plc|co|group)\b", "", target_name, flags=re.IGNORECASE).strip().lower()
            if len(clean_name) >= 3:
                target_keywords.append(clean_name)

        text_lower = text.lower()
        for kw in target_keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", text_lower):
                target_present = True
                break

        # If entity not mentioned in text but linked in metadata, still allow evaluation with lower relevance
        pos_aspects: List[Tuple[str, NewsFinancialAspect]] = []
        neg_aspects: List[Tuple[str, NewsFinancialAspect]] = []
        neutralized_aspects: List[Tuple[str, NewsFinancialAspect]] = []

        # Find positive pattern matches
        for pattern, aspect in POSITIVE_FINANCIAL_PATTERNS:
            matches = list(re.finditer(pattern, text_lower))
            for m in matches:
                # Check preceding 5 words for negation
                preceding = text_lower[max(0, m.start() - 30) : m.start()]
                if re.search(NEGATION_PATTERNS, preceding):
                    neutralized_aspects.append((m.group(0), aspect))
                else:
                    pos_aspects.append((m.group(0), aspect))

        # Find negative pattern matches
        for pattern, aspect in NEGATIVE_FINANCIAL_PATTERNS:
            matches = list(re.finditer(pattern, text_lower))
            for m in matches:
                preceding = text_lower[max(0, m.start() - 30) : m.start()]
                if re.search(NEGATION_PATTERNS, preceding):
                    neutralized_aspects.append((m.group(0), aspect))
                else:
                    neg_aspects.append((m.group(0), aspect))

        # Determine label and aspect
        if pos_aspects and neg_aspects:
            label = NewsSentimentLabel.MIXED
            primary_aspect = pos_aspects[0][1]
            score = 0.0
            evidence_span = f"{pos_aspects[0][0]} / {neg_aspects[0][0]}"
            explanation = "Article exhibits both favorable and unfavorable financial developments."
        elif pos_aspects:
            label = NewsSentimentLabel.POSITIVE
            primary_aspect = pos_aspects[0][1]
            score = min(1.0, 0.5 + (0.15 * len(pos_aspects)))
            evidence_span = pos_aspects[0][0]
            explanation = f"Favorable reporting tone regarding {primary_aspect.value.lower().replace('_', ' ')}."
        elif neg_aspects:
            label = NewsSentimentLabel.NEGATIVE
            primary_aspect = neg_aspects[0][1]
            score = max(-1.0, -0.5 - (0.15 * len(neg_aspects)))
            evidence_span = neg_aspects[0][0]
            explanation = f"Unfavorable reporting tone regarding {primary_aspect.value.lower().replace('_', ' ')}."
        elif neutralized_aspects:
            label = NewsSentimentLabel.NEUTRAL
            primary_aspect = neutralized_aspects[0][1]
            score = 0.0
            evidence_span = f"Negated: {neutralized_aspects[0][0]}"
            explanation = "Adverse or favorable assertion is negated or denied by context."
        else:
            if not target_present and len(article.linked_entities) > 2:
                label = NewsSentimentLabel.NOT_APPLICABLE
                primary_aspect = NewsFinancialAspect.GENERAL
                score = 0.0
                evidence_span = None
                explanation = "Entity is mentioned only contextually without direct evaluative framing."
            else:
                label = NewsSentimentLabel.NEUTRAL
                primary_aspect = NewsFinancialAspect.GENERAL
                score = 0.0
                evidence_span = text[:80]
                explanation = "Descriptive reporting without significant positive or negative evaluative bias."

        annotation_id = f"sent-{hashlib.sha256(f'{article.article_id}:{target_entity_id}:{cls.CLASSIFIER_VERSION}'.encode()).hexdigest()[:16]}"
        rev_id = _get_article_revision_id(article)
        evidence_ref = SentimentEvidenceReference(
            evidence_id=f"sevd-{hashlib.sha256(f'{annotation_id}:0'.encode()).hexdigest()[:12]}",
            article_revision_id=rev_id,
            evidence_scope=scope,
            text_span=evidence_span,
            rationale_code=f"{label.value}_{primary_aspect.value}",
        )

        return NewsSentimentAnnotation(
            annotation_id=annotation_id,
            article_id=article.article_id,
            article_revision_id=rev_id,
            target_entity_id=target_entity_id,
            target_entity_type="COMPANY",
            target_canonical_name=target_name,
            target_ticker=target_ticker,
            sentiment_label=label,
            sentiment_aspect=primary_aspect,
            sentiment_score=score,
            confidence_score=0.92 if label in (NewsSentimentLabel.POSITIVE, NewsSentimentLabel.NEGATIVE) else 0.85,
            classification_status="CLASSIFIED",
            classification_method=NewsClassificationMethod.DETERMINISTIC_RULES,
            classifier_version=cls.CLASSIFIER_VERSION,
            taxonomy_version=cls.TAXONOMY_VERSION,
            evidence=[evidence_ref],
            explanation=explanation,
            source_published_at=article.published_at,
            analysis_created_at=datetime.now(timezone.utc),
        )

    @classmethod
    def _create_abstention(
        cls,
        article: NewsArticle,
        target_entity_id: str,
        target_name: Optional[str],
        target_ticker: Optional[str],
        scope: NewsEvidenceScope,
    ) -> NewsSentimentAnnotation:
        annotation_id = f"sent-{hashlib.sha256(f'{article.article_id}:{target_entity_id}:{cls.CLASSIFIER_VERSION}'.encode()).hexdigest()[:16]}"
        rev_id = _get_article_revision_id(article)
        return NewsSentimentAnnotation(
            annotation_id=annotation_id,
            article_id=article.article_id,
            article_revision_id=rev_id,
            target_entity_id=target_entity_id,
            target_entity_type="COMPANY",
            target_canonical_name=target_name,
            target_ticker=target_ticker,
            sentiment_label=NewsSentimentLabel.INSUFFICIENT_EVIDENCE,
            sentiment_aspect=NewsFinancialAspect.GENERAL,
            sentiment_score=0.0,
            confidence_score=None,
            classification_status="ABSTAINED",
            classification_method=NewsClassificationMethod.DETERMINISTIC_RULES,
            classifier_version=cls.CLASSIFIER_VERSION,
            taxonomy_version=cls.TAXONOMY_VERSION,
            evidence=[
                SentimentEvidenceReference(
                    evidence_id=f"sevd-{hashlib.sha256(f'{annotation_id}:abstain'.encode()).hexdigest()[:12]}",
                    article_revision_id=rev_id,
                    evidence_scope=scope,
                    text_span=None,
                    rationale_code="TEXT_TOO_SHORT",
                )
            ],
            explanation="Available licensed article text is insufficient for reliable financial tone classification.",
            source_published_at=article.published_at,
            analysis_created_at=datetime.now(timezone.utc),
        )

    @classmethod
    def classify_article_relevance(
        cls,
        article: NewsArticle,
        entity_id: str,
        canonical_name: str,
        ticker: Optional[str] = None,
    ) -> NewsEntityRelevance:
        """Classify the degree of journalistic relevance of an article to a canonical entity."""
        headline_lower = article.headline.lower()
        excerpt_lower = (article.permitted_excerpt or "").lower()

        keywords = [canonical_name.lower()]
        if ticker:
            keywords.append(ticker.lower())
            keywords.append(f"${ticker.lower()}")
        clean_name = re.sub(r"\b(inc|corp|corporation|ltd|plc|co|group)\b", "", canonical_name, flags=re.IGNORECASE).strip().lower()
        if len(clean_name) >= 3:
            keywords.append(clean_name)

        in_headline = any(re.search(r"\b" + re.escape(kw) + r"\b", headline_lower) for kw in keywords)
        in_excerpt = any(re.search(r"\b" + re.escape(kw) + r"\b", excerpt_lower) for kw in keywords)

        if in_headline:
            relevance_class = NewsEntityRelevanceClass.PRIMARY_SUBJECT
            score = 1.0
            is_primary = True
            is_direct = True
            scope = NewsEvidenceScope.HEADLINE
        elif in_excerpt:
            relevance_class = NewsEntityRelevanceClass.DIRECT_PARTICIPANT
            score = 0.75
            is_primary = False
            is_direct = True
            scope = NewsEvidenceScope.LICENSED_EXCERPT
        else:
            relevance_class = NewsEntityRelevanceClass.VERIFIED_MENTION
            score = 0.40
            is_primary = False
            is_direct = False
            scope = NewsEvidenceScope.SOURCE_STRUCTURED_LABEL

        relevance_id = f"rel-{hashlib.sha256(f'{article.article_id}:{entity_id}'.encode()).hexdigest()[:16]}"
        return NewsEntityRelevance(
            relevance_id=relevance_id,
            article_id=article.article_id,
            article_revision_id=_get_article_revision_id(article),
            entity_id=entity_id,
            entity_type="COMPANY",
            canonical_name=canonical_name,
            ticker=ticker,
            relevance_class=relevance_class,
            relevance_score=score,
            evidence_source=scope,
            is_primary_subject=is_primary,
            is_direct_participant=is_direct,
            source_published_at=article.published_at,
        )

    # -------------------------------------------------------------------------
    # Reproducible Golden Benchmark Evaluation
    # -------------------------------------------------------------------------
    @classmethod
    def get_golden_benchmark_corpus(cls) -> List[Dict[str, Any]]:
        """Golden benchmark evaluation corpus with validated ground truth labels."""
        return [
            {
                "headline": "Apple Beats Q4 Earnings Expectations on Record Services Revenue",
                "excerpt": "Cupertino tech giant reported earnings per share topping consensus estimates by 12%.",
                "target_id": "company-apple",
                "target_name": "Apple Inc.",
                "target_ticker": "AAPL",
                "ground_truth_label": NewsSentimentLabel.POSITIVE,
                "ground_truth_aspect": NewsFinancialAspect.EARNINGS_PERFORMANCE,
            },
            {
                "headline": "Intel Slashes Full-Year Profit Forecast as Data Center Sales Slump",
                "excerpt": "Chipmaker issued a severe profit warning following market share losses.",
                "target_id": "company-intel",
                "target_name": "Intel Corp.",
                "target_ticker": "INTC",
                "ground_truth_label": NewsSentimentLabel.NEGATIVE,
                "ground_truth_aspect": NewsFinancialAspect.EARNINGS_GUIDANCE,
            },
            {
                "headline": "Microsoft Declares Quarterly Dividend of $0.75 Per Share",
                "excerpt": "Board of directors approved regular dividend payable December 12.",
                "target_id": "company-microsoft",
                "target_name": "Microsoft Corp.",
                "target_ticker": "MSFT",
                "ground_truth_label": NewsSentimentLabel.NEUTRAL,
                "ground_truth_aspect": NewsFinancialAspect.GENERAL,
            },
            {
                "headline": "Tesla Revenue Surged to Record High but Margins Shrank on Price Cuts",
                "excerpt": "Automaker delivered record quarterly sales although net income fell short.",
                "target_id": "company-tesla",
                "target_name": "Tesla Inc.",
                "target_ticker": "TSLA",
                "ground_truth_label": NewsSentimentLabel.MIXED,
                "ground_truth_aspect": NewsFinancialAspect.PROFITABILITY,
            },
            {
                "headline": "Alphabet FTC Probe Into Advertising Tech Deepens",
                "excerpt": "Regulators expand antitrust investigation into digital ad auction mechanisms.",
                "target_id": "company-alphabet",
                "target_name": "Alphabet Inc.",
                "target_ticker": "GOOGL",
                "ground_truth_label": NewsSentimentLabel.NEGATIVE,
                "ground_truth_aspect": NewsFinancialAspect.REGULATORY_EXPOSURE,
            },
            {
                "headline": "Nvidia Authorizes Additional $25 Billion Share Buyback Program",
                "excerpt": "Semiconductor leader announces board authorization for substantial share repurchases.",
                "target_id": "company-nvidia",
                "target_name": "NVIDIA Corp.",
                "target_ticker": "NVDA",
                "ground_truth_label": NewsSentimentLabel.POSITIVE,
                "ground_truth_aspect": NewsFinancialAspect.CORPORATE_TRANSACTION,
            },
            {
                "headline": "Brief update",
                "excerpt": "",
                "target_id": "company-generic",
                "target_name": "Generic Corp",
                "target_ticker": "GEN",
                "ground_truth_label": NewsSentimentLabel.INSUFFICIENT_EVIDENCE,
                "ground_truth_aspect": NewsFinancialAspect.GENERAL,
            },
        ]

    @classmethod
    def evaluate_golden_benchmark(cls) -> Dict[str, Any]:
        """Execute evaluation across the golden corpus and compute precision, recall, and F1."""
        corpus = cls.get_golden_benchmark_corpus()
        labels = [
            NewsSentimentLabel.POSITIVE,
            NewsSentimentLabel.NEGATIVE,
            NewsSentimentLabel.NEUTRAL,
            NewsSentimentLabel.MIXED,
            NewsSentimentLabel.INSUFFICIENT_EVIDENCE,
        ]

        tp: Dict[str, int] = {lbl: 0 for lbl in labels}
        fp: Dict[str, int] = {lbl: 0 for lbl in labels}
        fn: Dict[str, int] = {lbl: 0 for lbl in labels}

        eval_origin = NewsDataOrigin(
            provider_id="licensed_wire",
            extracted_at=datetime.now(timezone.utc),
        )
        for item in corpus:
            art = NewsArticle(
                article_id=f"art-eval-{hashlib.sha256(item['headline'].encode()).hexdigest()[:8]}",
                source_provider_id="licensed_wire",
                publisher_id="reuters",
                publisher="Reuters",
                headline=item["headline"],
                permitted_excerpt=item["excerpt"],
                canonical_url="https://reuters.com/eval",
                published_at=datetime.now(timezone.utc),
                first_seen_at=datetime.now(timezone.utc),
                ingested_at=datetime.now(timezone.utc),
                origin=eval_origin,
            )
            # Evaluate
            ann = cls.classify_article_target(
                article=art,
                target_entity_id=item["target_id"],
                target_name=item["target_name"],
                target_ticker=item["target_ticker"],
            )

            pred = ann.sentiment_label
            actual = item["ground_truth_label"]

            for lbl in labels:
                if pred == lbl and actual == lbl:
                    tp[lbl] += 1
                elif pred == lbl and actual != lbl:
                    fp[lbl] += 1
                elif pred != lbl and actual == lbl:
                    fn[lbl] += 1

        per_class_metrics = {}
        f1_scores = []
        for lbl in labels:
            p = tp[lbl] / (tp[lbl] + fp[lbl]) if (tp[lbl] + fp[lbl]) > 0 else 1.0
            r = tp[lbl] / (tp[lbl] + fn[lbl]) if (tp[lbl] + fn[lbl]) > 0 else 1.0
            f1 = (2 * p * r) / (p + r) if (p + r) > 0 else 0.0
            per_class_metrics[lbl.value] = {
                "precision": round(p, 4),
                "recall": round(r, 4),
                "f1_score": round(f1, 4),
                "true_positives": tp[lbl],
                "false_positives": fp[lbl],
                "false_negatives": fn[lbl],
            }
            if (tp[lbl] + fn[lbl]) > 0:
                f1_scores.append(f1)

        macro_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 1.0

        return {
            "evaluation_corpus_size": len(corpus),
            "macro_f1": round(macro_f1, 4),
            "classifier_version": cls.CLASSIFIER_VERSION,
            "taxonomy_version": cls.TAXONOMY_VERSION,
            "per_class_metrics": per_class_metrics,
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat(),
        }


def evaluate_golden_benchmark() -> Dict[str, Any]:
    """Module-level helper to run the golden evaluation benchmark."""
    return FinancialSentimentClassifier.evaluate_golden_benchmark()

