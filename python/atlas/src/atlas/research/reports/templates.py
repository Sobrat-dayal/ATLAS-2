"""Institutional Research Report Templates Registry (Stage 107)."""

from typing import Dict, List, Optional

from atlas.research.domain import ResearchReportTemplate
from atlas.research.enums import ReportBlockType, ReportSectionType, ResearchReportType

BUILTIN_TEMPLATES: Dict[str, ResearchReportTemplate] = {
    "tpl-company-research": ResearchReportTemplate(
        template_id="tpl-company-research",
        template_version=1,
        report_type=ResearchReportType.COMPANY_RESEARCH,
        title="Institutional Company Fundamental Research Report",
        description="Comprehensive fundamental equity and credit research initiation report with financial trends, peer benchmarking, thesis synthesis, and risk factors.",
        required_sections=[
            ReportSectionType.EXECUTIVE_SUMMARY,
            ReportSectionType.COMPANY_OVERVIEW,
            ReportSectionType.BUSINESS_MODEL,
            ReportSectionType.INDUSTRY_CONTEXT,
            ReportSectionType.FINANCIAL_PERFORMANCE,
            ReportSectionType.INVESTMENT_THESIS,
            ReportSectionType.KEY_RISKS,
            ReportSectionType.DISCLOSURES,
        ],
        default_sections=[
            {
                "section_type": ReportSectionType.EXECUTIVE_SUMMARY.value,
                "heading": "1. Executive Summary & Investment Thesis Summary",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "This research report provides a source-grounded fundamental evaluation of the subject company, examining historical financial statement trajectories, competitive peer benchmarking, and key catalysts over a multi-year horizon.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.COMPANY_OVERVIEW.value,
                "heading": "2. Corporate Background & Operating Segments",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "The company operates across multiple core business segments, generating recurring product and service revenues subject to seasonal and macroeconomic demand cycles.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.BUSINESS_MODEL.value,
                "heading": "3. Business Model & Value Drivers",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Core commercial value drivers include pricing power, customer retention, distribution scale, and continuous capital reinvestment into research and development.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.INDUSTRY_CONTEXT.value,
                "heading": "4. Industry Dynamics & Competitive Moat",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Industry structure exhibits high barriers to entry, technological specialization, and established supplier-customer relationships across major geographic markets.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.FINANCIAL_PERFORMANCE.value,
                "heading": "5. Historical Financial Trend & Margin Analysis",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Analysis of multi-year financial statements demonstrates historical revenue compound growth, operating margin durability, and cash conversion discipline.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.PEER_BENCHMARKING.value,
                "heading": "6. Cross-Sectional Peer Benchmarking",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Evaluating the company against verified peer group competitors highlights distinct positioning across operating margins, return on invested capital, and financial leverage.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.INVESTMENT_THESIS.value,
                "heading": "7. Structured Investment Thesis",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "The central investment thesis is grounded in sustainable competitive advantages, favorable unit economics, and cash generation capability supported by empirical filing evidence.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.KEY_RISKS.value,
                "heading": "8. Key Risks & Uncertainties",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Material risks include supply chain bottlenecks, regulatory scrutiny, foreign exchange volatility, and competitive price erosion.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.REFERENCES.value,
                "heading": "9. Source Evidence & Citations",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.REFERENCES.value,
                        "content_text": "Citations are deterministically compiled from SEC EDGAR Form 10-K/10-Q filings, canonical financial facts, and verified macroeconomic observations.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.DISCLOSURES.value,
                "heading": "10. Institutional Disclosures & Limitations",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "This research document represents independent analytical synthesis authored for evaluation purposes. It does not constitute an automated investment recommendation, endorsement, or price target forecast.",
                    }
                ],
            },
        ],
    ),
    "tpl-equity-initiation": ResearchReportTemplate(
        template_id="tpl-equity-initiation",
        template_version=1,
        report_type=ResearchReportType.EQUITY_INITIATION_DRAFT,
        title="Equity Research Initiation Draft",
        description="Institutional initiation report template with full bull/bear scenarios, valuation context, and catalyst timeline.",
        required_sections=[
            ReportSectionType.EXECUTIVE_SUMMARY,
            ReportSectionType.BUSINESS_MODEL,
            ReportSectionType.FINANCIAL_PERFORMANCE,
            ReportSectionType.PEER_BENCHMARKING,
            ReportSectionType.INVESTMENT_THESIS,
            ReportSectionType.BULL_BEAR_CASE,
            ReportSectionType.KEY_RISKS,
            ReportSectionType.CATALYSTS,
            ReportSectionType.DISCLOSURES,
        ],
        default_sections=[
            {
                "section_type": ReportSectionType.EXECUTIVE_SUMMARY.value,
                "heading": "1. Executive Summary & Thesis Highlights",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Initiating research coverage with a detailed synthesis of unit economics, historical financial trajectories, and market structure.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.BUSINESS_MODEL.value,
                "heading": "2. Business Model & Competitive Moat",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Comprehensive analysis of revenue streams, gross margin structure, and operational leverage potential.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.FINANCIAL_PERFORMANCE.value,
                "heading": "3. Financial Review & Ratio Analysis",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Multi-period statement comparisons and canonical ratio performance.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.PEER_BENCHMARKING.value,
                "heading": "4. Peer Group Cross-Sectional Comparison",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Benchmarking operating margins, growth, and leverage against verified industry peers.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.INVESTMENT_THESIS.value,
                "heading": "5. Core Investment Thesis",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Primary investment thesis and underlying factual evidence.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.BULL_BEAR_CASE.value,
                "heading": "6. Two-Sided Scenario: Bull vs. Bear Case",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Explicit structuring of upside catalysts versus downside headwinds and sensitivity factors.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.CATALYSTS.value,
                "heading": "7. Potential Catalysts & Milestones",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Scheduled product releases, regulatory decisions, and upcoming earnings announcements.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.KEY_RISKS.value,
                "heading": "8. Key Risks to Thesis",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Macroeconomic headwinds, customer concentration, and execution risks.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.DISCLOSURES.value,
                "heading": "9. Analyst Disclosures & Limitations",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Institutional research disclaimer and limitation disclosures.",
                    }
                ],
            },
        ],
    ),
    "tpl-earnings-review": ResearchReportTemplate(
        template_id="tpl-earnings-review",
        template_version=1,
        report_type=ResearchReportType.EARNINGS_REVIEW,
        title="Quarterly Earnings Performance Review",
        description="Focused earnings report analyzing reported quarterly revenues, operating income, cash flows, and filing disclosures against historical trends.",
        required_sections=[
            ReportSectionType.EXECUTIVE_SUMMARY,
            ReportSectionType.FINANCIAL_PERFORMANCE,
            ReportSectionType.PROFITABILITY_CASH_FLOW,
            ReportSectionType.KEY_RISKS,
            ReportSectionType.REFERENCES,
            ReportSectionType.DISCLOSURES,
        ],
        default_sections=[
            {
                "section_type": ReportSectionType.EXECUTIVE_SUMMARY.value,
                "heading": "1. Quarterly Earnings Highlights & Key Takeaways",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Summary of quarterly financial results disclosed in the latest Form 10-Q filing.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.FINANCIAL_PERFORMANCE.value,
                "heading": "2. Revenue Growth & Operating Margin Performance",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Analysis of segment revenue progression and operating margin performance relative to prior quarters.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.PROFITABILITY_CASH_FLOW.value,
                "heading": "3. Cash Flow & Working Capital Dynamics",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Operating cash flow conversion, capital expenditures, and free cash flow generation.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.KEY_RISKS.value,
                "heading": "4. Guidance & Disclosed Uncertainties",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Management commentary on operating outlook and emerging risk disclosures.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.REFERENCES.value,
                "heading": "5. Verified Filing Citations",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.REFERENCES.value,
                        "content_text": "Source evidence grounded in verified SEC Form 10-Q and earnings disclosures.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.DISCLOSURES.value,
                "heading": "6. Disclosures",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Institutional research limitations and factual scope disclosure.",
                    }
                ],
            },
        ],
    ),
    "tpl-macro-research": ResearchReportTemplate(
        template_id="tpl-macro-research",
        template_version=1,
        report_type=ResearchReportType.MACROECONOMIC_RESEARCH,
        title="Macroeconomic Research & Indicator Analysis",
        description="Economic research report examining multi-series macroeconomic indicators, inflation dynamics, policy rates, and historical vintages.",
        required_sections=[
            ReportSectionType.EXECUTIVE_SUMMARY,
            ReportSectionType.FINANCIAL_PERFORMANCE,
            ReportSectionType.METHODOLOGY,
            ReportSectionType.KEY_RISKS,
            ReportSectionType.REFERENCES,
        ],
        default_sections=[
            {
                "section_type": ReportSectionType.EXECUTIVE_SUMMARY.value,
                "heading": "1. Macroeconomic Context & Policy Environment",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Overview of prevailing economic conditions, inflation trajectories, and monetary policy decisions.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.FINANCIAL_PERFORMANCE.value,
                "heading": "2. Economic Indicator Trends & Time-Series Alignment",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Analysis of consumer price indices, policy benchmark rates, and real economic output.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.METHODOLOGY.value,
                "heading": "3. Statistical Methodology & Vintage Qualifications",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Frequency alignment policies, seasonal adjustment factors, and data release vintage handling.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.KEY_RISKS.value,
                "heading": "4. Macroeconomic Risks & Vulnerabilities",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Downside risks to growth, inflation persistence, and financial stability considerations.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.REFERENCES.value,
                "heading": "5. Official Economic Source Citations",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.REFERENCES.value,
                        "content_text": "Official statistical publications from central banks and governmental statistical bureaus.",
                    }
                ],
            },
        ],
    ),
    "tpl-investment-thesis": ResearchReportTemplate(
        template_id="tpl-investment-thesis",
        template_version=1,
        report_type=ResearchReportType.INVESTMENT_THESIS,
        title="Structured Investment Thesis Memorandum",
        description="Evidence-backed investment thesis document structuring central hypotheses, bull/bear scenarios, assumptions, and catalyst milestones.",
        required_sections=[
            ReportSectionType.EXECUTIVE_SUMMARY,
            ReportSectionType.INVESTMENT_THESIS,
            ReportSectionType.BULL_BEAR_CASE,
            ReportSectionType.KEY_RISKS,
            ReportSectionType.CATALYSTS,
            ReportSectionType.DISCLOSURES,
        ],
        default_sections=[
            {
                "section_type": ReportSectionType.EXECUTIVE_SUMMARY.value,
                "heading": "1. Thesis Summary",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Executive summary of the structured investment thesis, horizon, and underlying findings.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.INVESTMENT_THESIS.value,
                "heading": "2. Central Investment Thesis & Supporting Arguments",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Structured arguments backed by empirical analytical findings and filing citations.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.BULL_BEAR_CASE.value,
                "heading": "3. Two-Sided Analysis: Bull vs. Bear Case",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Balanced assessment of optimistic upside drivers versus pessimistic downside vulnerabilities.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.CATALYSTS.value,
                "heading": "4. Key Catalysts & Timeline",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Identified operational, corporate, or macroeconomic catalysts.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.KEY_RISKS.value,
                "heading": "5. Risks & Falsification Criteria",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Conditions under which the investment thesis would be invalidated or revised.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.DISCLOSURES.value,
                "heading": "6. Non-Predictive Disclaimer",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "This thesis represents qualitative analytical interpretation and is not an investment guarantee or advisory recommendation.",
                    }
                ],
            },
        ],
    ),
    "tpl-general-memo": ResearchReportTemplate(
        template_id="tpl-general-memo",
        template_version=1,
        report_type=ResearchReportType.GENERAL_RESEARCH_MEMORANDUM,
        title="Institutional Research Memorandum",
        description="Flexible, clean research memorandum template for analytical briefs, question synthesis, and evidence reviews.",
        required_sections=[
            ReportSectionType.EXECUTIVE_SUMMARY,
            ReportSectionType.METHODOLOGY,
            ReportSectionType.REFERENCES,
            ReportSectionType.DISCLOSURES,
        ],
        default_sections=[
            {
                "section_type": ReportSectionType.EXECUTIVE_SUMMARY.value,
                "heading": "1. Research Objective & Key Observations",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Statement of research scope, questions investigated, and core synthesized conclusions.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.METHODOLOGY.value,
                "heading": "2. Analytical Methodology & Investigation Process",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Data retrieval parameters, calculation methodology, and source selection rationale.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.REFERENCES.value,
                "heading": "3. References & Source Anchors",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.REFERENCES.value,
                        "content_text": "Source evidence and primary document citations.",
                    }
                ],
            },
            {
                "section_type": ReportSectionType.DISCLOSURES.value,
                "heading": "4. Disclosures & Scope Limitations",
                "content_blocks": [
                    {
                        "block_type": ReportBlockType.PARAGRAPH.value,
                        "content_text": "Standard institutional research disclosures.",
                    }
                ],
            },
        ],
    ),
}


def list_report_templates(report_type: Optional[ResearchReportType] = None) -> List[ResearchReportTemplate]:
    """Retrieve active research report templates, optionally filtered by type."""
    templates = list(BUILTIN_TEMPLATES.values())
    if report_type:
        templates = [t for t in templates if t.report_type == report_type]
    return templates


def get_report_template(template_id: str) -> Optional[ResearchReportTemplate]:
    """Fetch a specific report template by identifier."""
    return BUILTIN_TEMPLATES.get(template_id)
