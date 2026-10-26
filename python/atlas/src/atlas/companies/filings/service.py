"""Service orchestration layer for Regulatory Company Filings Intelligence (Stage 86)."""

from typing import List, Optional

from .comparator import compare_regulatory_filings
from .enums import FilingCategory, Regulator
from .errors import (
    FilingDocumentNotFoundError,
    FilingNotFoundError,
)
from .models import RegulatoryFiling
from .repository import CompanyFilingsRepository
from .schemas import (
    FilingCatalogResponseDTO,
    FilingComparisonResponseDTO,
    FilingContentDTO,
    FilingCoverageDTO,
    FilingDetailDTO,
    FilingDocumentDTO,
    FilingSearchHitDTO,
    FilingSearchResponseDTO,
    FilingSectionDTO,
    FilingSourceReferenceDTO,
    FilingSummaryDTO,
    SectionDiffDTO,
    XBRLFactDiffDTO,
    XBRLFactDTO,
    XBRLFactsResponseDTO,
)


class CompanyFilingsService:
    """Orchestrates regulatory filing retrieval, search, comparison, and XBRL analysis."""

    def __init__(self, repository: Optional[CompanyFilingsRepository] = None):
        self.repository = repository or CompanyFilingsRepository()

    def _map_to_summary_dto(self, filing: RegulatoryFiling) -> FilingSummaryDTO:
        """Converts domain filing into catalog summary DTO."""
        return FilingSummaryDTO(
            filing_id=filing.filing_id,
            company_id=filing.company_id,
            filer_cik=filing.filer_cik,
            filer_name=filing.filer_name,
            regulator=filing.regulator,
            accession_number=filing.accession_number,
            form_type=filing.form_type,
            category=filing.category,
            reporting_period=filing.reporting_period,
            filing_date=filing.filing_date,
            acceptance_timestamp=filing.acceptance_timestamp,
            publication_timestamp=filing.publication_timestamp,
            is_amendment=filing.is_amendment,
            amendment_status=filing.amendment_status,
            amends_accession_number=filing.amends_accession_number,
            primary_document_name=filing.primary_document_name,
            title=filing.title,
            document_count=len(filing.documents),
            fact_count=len(filing.xbrl_facts),
        )

    def get_filings_catalog(
        self,
        company_id: str,
        category: Optional[FilingCategory] = None,
        form_type: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        limit: int = 25,
        offset: int = 0,
    ) -> FilingCatalogResponseDTO:
        """Retrieves paginated and filtered catalog of company filings."""
        filings = self.repository.get_filings_by_company(
            company_id=company_id,
            category=category,
            form_type=form_type,
            from_date=from_date,
            to_date=to_date,
        )

        total_count = len(filings)
        paged_filings = filings[offset : offset + limit]

        return FilingCatalogResponseDTO(
            company_id=company_id,
            total_count=total_count,
            limit=limit,
            offset=offset,
            items=[self._map_to_summary_dto(f) for f in paged_filings],
        )

    def get_filing_detail(self, filing_id: str) -> FilingDetailDTO:
        """Retrieves detailed filing record with document catalog and sections."""
        filing = self.repository.get_filing_by_id(filing_id)
        if not filing:
            raise FilingNotFoundError(f"Filing with ID '{filing_id}' does not exist.")

        docs_dto = [
            FilingDocumentDTO(
                document_id=d.document_id,
                filename=d.filename,
                document_type=d.document_type,
                description=d.description,
                media_type=d.media_type,
                byte_size=d.byte_size,
                content_hash=d.content_hash,
                source_url=d.source_url,
                is_primary=d.is_primary,
            )
            for d in filing.documents
        ]

        secs_dto = [
            FilingSectionDTO(
                item_id=s.item_id,
                title=s.title,
                anchor=s.anchor,
                char_offset=s.char_offset,
                char_length=s.char_length,
                summary_excerpt=s.summary_excerpt,
            )
            for s in filing.sections
        ]

        return FilingDetailDTO(
            filing_id=filing.filing_id,
            company_id=filing.company_id,
            filer_cik=filing.filer_cik,
            filer_name=filing.filer_name,
            regulator=filing.regulator,
            accession_number=filing.accession_number,
            form_type=filing.form_type,
            category=filing.category,
            reporting_period=filing.reporting_period,
            filing_date=filing.filing_date,
            acceptance_timestamp=filing.acceptance_timestamp,
            publication_timestamp=filing.publication_timestamp,
            is_amendment=filing.is_amendment,
            amendment_status=filing.amendment_status,
            amends_accession_number=filing.amends_accession_number,
            primary_document_name=filing.primary_document_name,
            primary_document_url=filing.primary_document_url,
            title=filing.title,
            documents=docs_dto,
            sections=secs_dto,
            fact_count=len(filing.xbrl_facts),
            full_text_indexed=filing.full_text_indexed,
        )

    def get_filing_documents(self, filing_id: str) -> List[FilingDocumentDTO]:
        """Lists all files and exhibit attachments for a filing."""
        filing = self.repository.get_filing_by_id(filing_id)
        if not filing:
            raise FilingNotFoundError(f"Filing with ID '{filing_id}' does not exist.")

        return [
            FilingDocumentDTO(
                document_id=d.document_id,
                filename=d.filename,
                document_type=d.document_type,
                description=d.description,
                media_type=d.media_type,
                byte_size=d.byte_size,
                content_hash=d.content_hash,
                source_url=d.source_url,
                is_primary=d.is_primary,
            )
            for d in filing.documents
        ]

    def get_filing_content(
        self, filing_id: str, document_id: Optional[str] = None
    ) -> FilingContentDTO:
        """Retrieves safely sanitized document HTML and plain text."""
        filing = self.repository.get_filing_by_id(filing_id)
        if not filing:
            raise FilingNotFoundError(f"Filing with ID '{filing_id}' does not exist.")

        target_doc = None
        if document_id:
            for doc in filing.documents:
                if doc.document_id == document_id:
                    target_doc = doc
                    break
            if not target_doc:
                raise FilingDocumentNotFoundError(
                    f"Document with ID '{document_id}' not found in filing."
                )
        else:
            # Use primary document
            for doc in filing.documents:
                if doc.is_primary:
                    target_doc = doc
                    break
            if not target_doc and filing.documents:
                target_doc = filing.documents[0]

        if not target_doc:
            raise FilingDocumentNotFoundError("No documents associated with this filing.")

        return FilingContentDTO(
            filing_id=filing.filing_id,
            document_id=target_doc.document_id,
            accession_number=filing.accession_number,
            filename=target_doc.filename,
            media_type=target_doc.media_type,
            content_html=target_doc.content_raw or filing.content_html,
            content_text=filing.content_text,
        )

    def get_filing_facts(
        self, filing_id: str, concept_filter: Optional[str] = None
    ) -> XBRLFactsResponseDTO:
        """Retrieves extracted XBRL financial facts for a filing."""
        filing = self.repository.get_filing_by_id(filing_id)
        if not filing:
            raise FilingNotFoundError(f"Filing with ID '{filing_id}' does not exist.")

        facts = filing.xbrl_facts
        if concept_filter:
            facts = [f for f in facts if concept_filter.lower() in f.concept_name.lower()]

        dtos = [
            XBRLFactDTO(
                fact_id=f.fact_id,
                concept_name=f.concept_name,
                label=f.label,
                period_type=f.period_type,
                period_end=f.period_end,
                period_start=f.period_start,
                unit=f.unit,
                exact_value=float(f.exact_value),
                formatted_value=f.formatted_value,
                decimals=f.decimals,
                dimensions=f.dimensions,
            )
            for f in facts
        ]

        return XBRLFactsResponseDTO(
            filing_id=filing.filing_id,
            accession_number=filing.accession_number,
            total_count=len(dtos),
            items=dtos,
        )

    def search_filings(
        self, company_id: str, query: str, limit: int = 25
    ) -> FilingSearchResponseDTO:
        """Searches indexed filing text and extracts matching contextual snippets."""
        hits = self.repository.search_filings_content(company_id, query, limit=limit)

        dtos = [
            FilingSearchHitDTO(
                filing_id=h.filing_id,
                document_id=h.document_id,
                accession_number=h.accession_number,
                form_type=h.form_type,
                reporting_period=h.reporting_period,
                filing_date=h.filing_date,
                section_name=h.section_name,
                matched_snippet=h.matched_snippet,
                char_offset=h.char_offset,
                score=h.score,
            )
            for h in hits
        ]

        return FilingSearchResponseDTO(
            company_id=company_id,
            query=query,
            total_hits=len(dtos),
            hits=dtos,
        )

    def compare_filings(
        self, left_filing_id: str, right_filing_id: str
    ) -> FilingComparisonResponseDTO:
        """Performs comparative diff analysis between two filings."""
        left = self.repository.get_filing_by_id(left_filing_id)
        right = self.repository.get_filing_by_id(right_filing_id)

        if not left:
            raise FilingNotFoundError(f"Prior filing '{left_filing_id}' not found.")
        if not right:
            raise FilingNotFoundError(f"Comparison filing '{right_filing_id}' not found.")

        result = compare_regulatory_filings(left, right)

        sec_diffs = [
            SectionDiffDTO(
                section_name=d.section_name,
                added_lines_count=d.added_lines_count,
                removed_lines_count=d.removed_lines_count,
                diff_text=d.diff_text,
            )
            for d in result.text_diff_sections
        ]

        fact_diffs = [
            XBRLFactDiffDTO(
                concept_name=f.concept_name,
                label=f.label,
                period_label=f.period_label,
                unit=f.unit,
                prior_value=float(f.prior_value),
                current_value=float(f.current_value),
                absolute_difference=float(f.absolute_difference),
                percentage_difference=float(f.percentage_difference)
                if f.percentage_difference is not None
                else None,
                is_restatement=f.is_restatement,
            )
            for f in result.xbrl_fact_diffs
        ]

        return FilingComparisonResponseDTO(
            left_filing_id=result.left_filing_id,
            right_filing_id=result.right_filing_id,
            left_accession=result.left_accession,
            right_accession=result.right_accession,
            comparison_type=result.comparison_type,
            left_filing_date=result.left_filing_date,
            right_filing_date=result.right_filing_date,
            text_diff_sections=sec_diffs,
            xbrl_fact_diffs=fact_diffs,
            total_text_changes=result.total_text_changes,
            total_fact_adjustments=result.total_fact_adjustments,
        )

    def get_filing_coverage(self, company_id: str) -> FilingCoverageDTO:
        """Returns regulator coverage, available forms, and source policy."""
        filings = self.repository.get_filings_by_company(company_id)
        forms = sorted(list(set(f.form_type for f in filings)))

        latest_date = filings[0].filing_date if filings else None
        oldest_date = filings[-1].filing_date if filings else None

        return FilingCoverageDTO(
            company_id=company_id,
            company_name=self.repository.apple_name
            if company_id == self.repository.apple_company_id
            else "Company",
            regulator=Regulator.SEC_EDGAR,
            filer_cik=self.repository.apple_cik,
            total_filings=len(filings),
            forms_available=forms,
            latest_filing_date=latest_date,
            oldest_filing_date=oldest_date,
            source_policy="US SEC EDGAR Fair Access Policy (10 requests/sec limit, identified User-Agent required)",
            user_agent_configured="ATLAS/2.0 (research@atlas.internal; contact: security@atlas.internal)",
        )

    def get_filing_source(self, filing_id: str) -> FilingSourceReferenceDTO:
        """Returns official provenance, content hashes, and official links."""
        filing = self.repository.get_filing_by_id(filing_id)
        if not filing:
            raise FilingNotFoundError(f"Filing with ID '{filing_id}' does not exist.")

        primary_doc = filing.documents[0] if filing.documents else None
        content_hash = primary_doc.content_hash if primary_doc else "unknown"

        return FilingSourceReferenceDTO(
            filing_id=filing.filing_id,
            regulator=filing.regulator,
            accession_number=filing.accession_number,
            filer_cik=filing.filer_cik,
            official_url=f"https://www.sec.gov/edgar/browse/?CIK={filing.filer_cik}",
            primary_document_url=filing.primary_document_url,
            content_hash=content_hash,
            retrieved_timestamp=filing.acceptance_timestamp or filing.filing_date,
            source_attribution="U.S. Securities and Exchange Commission (SEC) EDGAR System",
            license_tier="Public Regulatory Disclosure",
        )
