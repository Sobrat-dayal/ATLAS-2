"""ATLAS Portfolios V1 — Master Portfolio Allocation & Exposure Calculation Engine (Stage 112).

Pure deterministic financial calculation engine orchestrating:
- NAV denominator validation & cash inclusion
- Direct vs Look-Through exposure decomposition
- Multi-dimensional classification (Asset Class, Sector, Industry, Country, Currency)
- Security and Issuer-level concentration, HHI, and Effective N
- Exposure reconciliation and data quality auditing
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional, Set, Tuple

from atlas.portfolios.exposure.enums import (
    AssetClass,
    ConcentrationScope,
    ExposureBasis,
    ExposureDataCompleteness,
    ExposureDimension,
    GeographyPolicy,
    LookThroughStatus,
)
from atlas.portfolios.exposure.lookthrough import FundLookThroughEngine
from atlas.portfolios.exposure.models import (
    ConcentrationSummary,
    CrossFundOverlapItem,
    ExposureCategoryRow,
    ExposureDataQuality,
    ExposureDimensionResult,
    FundLookThroughResult,
    IssuerWeightItem,
    PortfolioExposureRun,
    SecurityWeightItem,
)
from atlas.portfolios.exposure.registry import (
    COUNTRY_REGION_MAPPING,
    SECTOR_INDUSTRY_HIERARCHY,
    ClassificationRegistry,
)
from atlas.portfolios.exposure.weights import (
    calculate_concentration_hhi,
    calculate_top_n_weights,
    calculate_weight,
    validate_nav_denominator,
    verify_partition_reconciliation,
)
from atlas.portfolios.models import (
    Portfolio,
    PortfolioCashValuation,
    PortfolioPositionValuation,
    PortfolioValuation,
)


COUNTRY_ISO_MAP: Dict[str, str] = {
    "India": "IN",
    "United States": "US",
    "United Kingdom": "GB",
    "Canada": "CA",
    "Germany": "DE",
    "France": "FR",
    "Switzerland": "CH",
    "Japan": "JP",
    "Australia": "AU",
    "China": "CN",
    "IN": "IN",
    "US": "US",
}


class PortfolioExposureEngine:
    """Master institutional calculation engine for portfolio allocation, exposure, and concentration."""

    def __init__(self, registry: Optional[ClassificationRegistry] = None) -> None:
        self.registry = registry or ClassificationRegistry()
        self.lookthrough_engine = FundLookThroughEngine(self.registry)

    def calculate_exposure_run(
        self,
        portfolio: Portfolio,
        valuation: PortfolioValuation,
        exposure_basis: ExposureBasis = ExposureBasis.DIRECT,
        geography_policy: GeographyPolicy = GeographyPolicy.ISSUER_DOMICILE,
        include_cash: bool = True,
        account_id_filter: Optional[str] = None,
    ) -> PortfolioExposureRun:
        """Computes complete, verified portfolio allocation across all canonical dimensions."""
        base_cur = portfolio.base_currency
        as_of = valuation.as_of

        # 1. Filter positions and cash if account_id_filter is specified
        positions = [
            pv for pv in valuation.position_valuations
            if (account_id_filter is None or account_id_filter == "ALL" or pv.account_id == account_id_filter)
            and pv.quantity > Decimal("0")
        ]
        cash_entries = [
            cv for cv in valuation.cash_valuations
            if (account_id_filter is None or account_id_filter == "ALL" or cv.account_id == account_id_filter)
        ]

        # 2. Denominator Calculation
        securities_value = Decimal("0.00")
        missing_prices = 0
        missing_fx = 0
        unvalued_positions = 0

        for pv in positions:
            if pv.base_market_value is not None:
                securities_value += pv.base_market_value
            else:
                unvalued_positions += 1
                if pv.mark_price is None:
                    missing_prices += 1
                if pv.price_currency != base_cur and pv.fx_rate_to_base is None:
                    missing_fx += 1

        cash_value = Decimal("0.00")
        if include_cash:
            for cv in cash_entries:
                cash_value += cv.base_cash_value

        total_nav = securities_value + cash_value
        validate_nav_denominator(total_nav)

        warnings: List[str] = []
        if unvalued_positions > 0:
            warnings.append(
                f"{unvalued_positions} position(s) lacked verified market prices or FX rates; excluded from valued NAV."
            )

        # 3. Look-Through Expansion if LOOK_THROUGH mode
        fund_lookthroughs: List[FundLookThroughResult] = []
        effective_positions: List[Tuple[str, str, str, Decimal, AssetClass, Optional[str], Optional[str], Optional[str], Optional[str]]] = []
        # (instrument_id, symbol, name, market_val_base, asset_class, issuer_id, sector, industry, country)

        residual_fund_value = Decimal("0.00")

        for pv in positions:
            val_base = pv.base_market_value or Decimal("0.00")
            if val_base <= Decimal("0.00"):
                continue

            meta = self.registry.get_instrument_metadata(pv.instrument_id)
            is_fund = meta.is_fund if meta else False

            if exposure_basis == ExposureBasis.LOOK_THROUGH and is_fund:
                flt = self.lookthrough_engine.expand_fund(pv.instrument_id, val_base, total_nav)
                fund_lookthroughs.append(flt)

                for c in flt.known_constituents:
                    c_meta = self.registry.get_instrument_metadata(c.constituent_id)
                    c_issuer = c_meta.issuer_id if c_meta else c.constituent_id
                    c_country, _ = self.registry.resolve_geography(c_meta, geography_policy)
                    effective_positions.append((
                        c.constituent_id,
                        c.symbol,
                        c.name,
                        c.effective_market_value,
                        c.asset_class,
                        c_issuer,
                        c.sector or (c_meta.sector if c_meta else "Unknown Sector"),
                        c_meta.industry if c_meta else "Unknown Industry",
                        c_country,
                    ))

                if flt.residual_market_value > Decimal("0.00"):
                    residual_fund_value += flt.residual_market_value
                    effective_positions.append((
                        f"residual_{pv.instrument_id}",
                        f"{pv.symbol}.RESIDUAL",
                        f"{pv.company_name or pv.symbol} (Unclassified Residual)",
                        flt.residual_market_value,
                        AssetClass.FUND,
                        f"residual_{pv.instrument_id}",
                        "Unknown Sector",
                        "Unknown Industry",
                        "Unknown Country",
                    ))
            else:
                asset_class = meta.asset_class if meta else AssetClass.EQUITY
                issuer_id = meta.issuer_id if meta else pv.instrument_id
                sector = meta.sector if meta else "Unknown Sector"
                industry = meta.industry if meta else "Unknown Industry"
                country, _ = self.registry.resolve_geography(meta, geography_policy)

                effective_positions.append((
                    pv.instrument_id,
                    pv.symbol,
                    pv.company_name or pv.symbol,
                    val_base,
                    asset_class,
                    issuer_id,
                    sector,
                    industry,
                    country,
                ))

        # 4. Cross-Fund Overlap Consolidation
        direct_positions_tuples = [
            (pv.instrument_id, pv.symbol, pv.company_name or pv.symbol, pv.base_market_value or Decimal("0.00"))
            for pv in positions if pv.base_market_value and (not self.registry.get_instrument_metadata(pv.instrument_id) or not self.registry.get_instrument_metadata(pv.instrument_id).is_fund)
        ]
        cross_fund_overlaps = self.lookthrough_engine.consolidate_cross_fund_overlap(
            direct_positions_tuples, fund_lookthroughs, total_nav
        )

        # 5. Dimension 1: Asset-Class Allocation
        asset_class_res = self._compute_asset_class_allocation(
            effective_positions, cash_value, total_nav, include_cash
        )

        # 6. Dimension 2 & 3: Sector and Industry Allocation
        sector_res, industry_res = self._compute_sector_and_industry_allocation(
            effective_positions, cash_value, total_nav, include_cash
        )

        # 7. Dimension 4: Geographic Country & Region Allocation
        country_res = self._compute_country_allocation(
            effective_positions, cash_entries, total_nav, include_cash, base_cur
        )

        # 8. Dimension 5: Currency Denomination Allocation
        currency_res = self._compute_currency_allocation(
            positions, cash_entries, total_nav, include_cash
        )

        # 9. Security-Level Weights & Concentration
        security_weights, sec_concentration = self._compute_security_concentration(
            positions,
            cash_value,
            total_nav,
            include_cash,
            fund_lookthroughs=fund_lookthroughs if exposure_basis == ExposureBasis.LOOK_THROUGH else None,
        )

        # 10. Consolidated Issuer Weights & Concentration
        issuer_weights, iss_concentration = self._compute_issuer_concentration(
            positions, cash_value, total_nav, include_cash
        )

        # 11. Data Quality and Completeness Auditing
        missing_classifications = sum(
            1 for p in effective_positions if p[6] == "Unknown Sector" or p[8] == "Unknown Country"
        )
        classified_val = sum(
            p[3] for p in effective_positions if p[6] != "Unknown Sector" and p[8] != "Unknown Country"
        )
        if include_cash:
            classified_val += cash_value

        unclass_val = total_nav - classified_val
        coverage_pct = (classified_val / total_nav * Decimal("100.0")).quantize(Decimal("0.01"))

        completeness = ExposureDataCompleteness.COMPLETE
        if unvalued_positions > 0:
            completeness = ExposureDataCompleteness.PARTIAL_VALUATION
        elif missing_classifications > 0:
            completeness = ExposureDataCompleteness.PARTIAL_CLASSIFICATION
        elif warnings:
            completeness = ExposureDataCompleteness.COMPLETE_WITH_WARNINGS

        data_quality = ExposureDataQuality(
            completeness=completeness,
            total_nav=total_nav,
            securities_value=securities_value,
            cash_value=cash_value,
            classified_value=classified_val,
            unclassified_value=unclass_val,
            coverage_percentage=coverage_pct,
            missing_prices_count=missing_prices,
            missing_fx_count=missing_fx,
            missing_classifications_count=missing_classifications,
            fund_lookthrough_residuals_count=len([flt for flt in fund_lookthroughs if flt.residual_market_value > Decimal("0")]),
            warnings=warnings,
            source_manifest={
                "portfolio_id": portfolio.id,
                "as_of": as_of.isoformat(),
                "base_currency": base_cur,
                "exposure_basis": exposure_basis.value,
                "geography_policy": geography_policy.value,
                "positions_count": len(positions),
                "cash_entries_count": len(cash_entries),
                "nav": str(total_nav),
            },
        )

        # Generate unique input hash
        import hashlib, json
        input_hash = hashlib.sha256(
            json.dumps(data_quality.source_manifest, sort_keys=True).encode()
        ).hexdigest()

        import uuid
        run_id = f"exp_{uuid.uuid4().hex[:12]}"

        return PortfolioExposureRun(
            run_id=run_id,
            portfolio_id=portfolio.id,
            account_id=account_id_filter if account_id_filter != "ALL" else None,
            owner_user_id=portfolio.user_id,
            as_of=as_of,
            base_currency=base_cur,
            exposure_basis=exposure_basis,
            geography_policy=geography_policy,
            total_nav=total_nav,
            securities_value=securities_value,
            cash_value=cash_value,
            asset_classes=asset_class_res,
            sectors=sector_res,
            industries=industry_res,
            countries=country_res,
            currencies=currency_res,
            security_concentration=sec_concentration,
            issuer_concentration=iss_concentration,
            top_securities=security_weights,
            top_issuers=issuer_weights,
            fund_lookthroughs=fund_lookthroughs,
            cross_fund_overlaps=cross_fund_overlaps,
            data_quality=data_quality,
            calculation_version="1.0.0",
            input_hash=input_hash,
            created_at=as_of,
        )

    # -----------------------------------------------------------------------
    # Dimension Computations
    # -----------------------------------------------------------------------

    def _compute_asset_class_allocation(
        self,
        positions: List[Tuple],
        cash_value: Decimal,
        nav: Decimal,
        include_cash: bool,
    ) -> ExposureDimensionResult:
        """Aggregates values by Asset Class."""
        totals: Dict[AssetClass, Tuple[Decimal, Decimal, int]] = {}  # class -> (total_val, direct_val, count)

        for p in positions:
            ac = p[4]
            val = p[3]
            curr_val, curr_dir, curr_cnt = totals.get(ac, (Decimal("0.00"), Decimal("0.00"), 0))
            totals[ac] = (curr_val + val, curr_dir + val, curr_cnt + 1)

        if include_cash and cash_value > Decimal("0.00"):
            curr_val, curr_dir, curr_cnt = totals.get(AssetClass.CASH, (Decimal("0.00"), Decimal("0.00"), 0))
            totals[AssetClass.CASH] = (curr_val + cash_value, curr_dir + cash_value, curr_cnt + 1)

        categories: List[ExposureCategoryRow] = []
        for ac, (val, dir_val, count) in totals.items():
            w, pct = calculate_weight(val, nav)
            categories.append(
                ExposureCategoryRow(
                    category_id=ac.value,
                    category_name=ac.value.replace("_", " ").title(),
                    market_value=val,
                    weight=w,
                    percentage=pct,
                    direct_value=dir_val,
                    lookthrough_value=Decimal("0.00"),
                    constituent_count=count,
                    coverage_status="CLASSIFIED" if ac != AssetClass.UNKNOWN else "UNCLASSIFIED",
                )
            )

        categories.sort(key=lambda c: c.market_value, reverse=True)
        total_val = sum(c.market_value for c in categories)
        unclass = sum(c.market_value for c in categories if c.category_id == AssetClass.UNKNOWN.value)
        class_val = total_val - unclass
        coverage = (class_val / nav * Decimal("100.0")).quantize(Decimal("0.01"))

        return ExposureDimensionResult(
            dimension=ExposureDimension.ASSET_CLASS,
            taxonomy="CANONICAL_ASSET_CLASSES",
            taxonomy_version="1.0.0",
            total_market_value=total_val,
            classified_value=class_val,
            unclassified_value=unclass,
            coverage_percentage=coverage,
            categories=categories,
        )

    def _compute_sector_and_industry_allocation(
        self,
        positions: List[Tuple],
        cash_value: Decimal,
        nav: Decimal,
        include_cash: bool,
    ) -> Tuple[ExposureDimensionResult, ExposureDimensionResult]:
        """Aggregates values by Sector and Industry hierarchy."""
        sector_totals: Dict[str, Tuple[Decimal, Decimal, int]] = {}
        industry_totals: Dict[str, Tuple[Decimal, Decimal, int, str]] = {}  # industry -> (val, dir_val, count, sector)

        for p in positions:
            val = p[3]
            sector = p[6] or "Unknown Sector"
            industry = p[7] or "Unknown Industry"

            s_val, s_dir, s_cnt = sector_totals.get(sector, (Decimal("0.00"), Decimal("0.00"), 0))
            sector_totals[sector] = (s_val + val, s_dir + val, s_cnt + 1)

            i_val, i_dir, i_cnt, _ = industry_totals.get(industry, (Decimal("0.00"), Decimal("0.00"), 0, sector))
            industry_totals[industry] = (i_val + val, i_dir + val, i_cnt + 1, sector)

        if include_cash and cash_value > Decimal("0.00"):
            s_val, s_dir, s_cnt = sector_totals.get("Cash", (Decimal("0.00"), Decimal("0.00"), 0))
            sector_totals["Cash"] = (s_val + cash_value, s_dir + cash_value, s_cnt + 1)

            i_val, i_dir, i_cnt, _ = industry_totals.get("Cash & Cash Equivalents", (Decimal("0.00"), Decimal("0.00"), 0, "Cash"))
            industry_totals["Cash & Cash Equivalents"] = (i_val + cash_value, i_dir + cash_value, i_cnt + 1, "Cash")

        # Sector categories
        sector_rows: List[ExposureCategoryRow] = []
        for s_name, (val, dir_val, count) in sector_totals.items():
            w, pct = calculate_weight(val, nav)
            sector_rows.append(
                ExposureCategoryRow(
                    category_id=s_name.lower().replace(" ", "_"),
                    category_name=s_name,
                    market_value=val,
                    weight=w,
                    percentage=pct,
                    direct_value=dir_val,
                    lookthrough_value=Decimal("0.00"),
                    constituent_count=count,
                    coverage_status="CLASSIFIED" if s_name != "Unknown Sector" else "UNCLASSIFIED",
                )
            )
        sector_rows.sort(key=lambda x: x.market_value, reverse=True)

        # Industry categories
        industry_rows: List[ExposureCategoryRow] = []
        for i_name, (val, dir_val, count, s_parent) in industry_totals.items():
            w, pct = calculate_weight(val, nav)
            industry_rows.append(
                ExposureCategoryRow(
                    category_id=i_name.lower().replace(" ", "_"),
                    category_name=f"{i_name} ({s_parent})",
                    market_value=val,
                    weight=w,
                    percentage=pct,
                    direct_value=dir_val,
                    lookthrough_value=Decimal("0.00"),
                    constituent_count=count,
                    coverage_status="CLASSIFIED" if i_name != "Unknown Industry" else "UNCLASSIFIED",
                )
            )
        industry_rows.sort(key=lambda x: x.market_value, reverse=True)

        tot_val = sum(r.market_value for r in sector_rows)
        unclass = sum(r.market_value for r in sector_rows if r.category_name == "Unknown Sector")
        coverage = ((tot_val - unclass) / nav * Decimal("100.0")).quantize(Decimal("0.01"))

        sector_result = ExposureDimensionResult(
            dimension=ExposureDimension.SECTOR,
            taxonomy="GICS",
            taxonomy_version="2024",
            total_market_value=tot_val,
            classified_value=tot_val - unclass,
            unclassified_value=unclass,
            coverage_percentage=coverage,
            categories=sector_rows,
        )

        industry_result = ExposureDimensionResult(
            dimension=ExposureDimension.INDUSTRY,
            taxonomy="GICS",
            taxonomy_version="2024",
            total_market_value=tot_val,
            classified_value=tot_val - unclass,
            unclassified_value=unclass,
            coverage_percentage=coverage,
            categories=industry_rows,
        )

        return sector_result, industry_result

    def _compute_country_allocation(
        self,
        positions: List[Tuple],
        cash_entries: List[PortfolioCashValuation],
        nav: Decimal,
        include_cash: bool,
        base_currency: str,
    ) -> ExposureDimensionResult:
        """Aggregates values by Country according to the selected geography policy."""
        country_totals: Dict[str, Tuple[Decimal, Decimal, int]] = {}

        for p in positions:
            country = p[8] or "Unknown Country"
            val = p[3]
            c_val, c_dir, c_cnt = country_totals.get(country, (Decimal("0.00"), Decimal("0.00"), 0))
            country_totals[country] = (c_val + val, c_dir + val, c_cnt + 1)

        if include_cash:
            for cv in cash_entries:
                # Assign cash to primary issuing country of that currency
                cash_country = "United States" if cv.currency == "USD" else "India" if cv.currency == "INR" else "Europe" if cv.currency == "EUR" else "United Kingdom" if cv.currency == "GBP" else "Cash / Multi-Currency"
                c_val, c_dir, c_cnt = country_totals.get(cash_country, (Decimal("0.00"), Decimal("0.00"), 0))
                country_totals[cash_country] = (c_val + cv.base_cash_value, c_dir + cv.base_cash_value, c_cnt + 1)

        categories: List[ExposureCategoryRow] = []
        for c_name, (val, dir_val, count) in country_totals.items():
            w, pct = calculate_weight(val, nav)
            cat_id = COUNTRY_ISO_MAP.get(c_name, c_name.upper()[:2])
            categories.append(
                ExposureCategoryRow(
                    category_id=cat_id,
                    category_name=c_name,
                    market_value=val,
                    weight=w,
                    percentage=pct,
                    direct_value=dir_val,
                    lookthrough_value=Decimal("0.00"),
                    constituent_count=count,
                    coverage_status="CLASSIFIED" if c_name != "Unknown Country" else "UNCLASSIFIED",
                )
            )

        categories.sort(key=lambda x: x.market_value, reverse=True)
        tot_val = sum(r.market_value for r in categories)
        unclass = sum(r.market_value for r in categories if r.category_name == "Unknown Country")
        coverage = ((tot_val - unclass) / nav * Decimal("100.0")).quantize(Decimal("0.01"))

        return ExposureDimensionResult(
            dimension=ExposureDimension.COUNTRY,
            taxonomy="ISO_3166_COUNTRY",
            taxonomy_version="2024",
            total_market_value=tot_val,
            classified_value=tot_val - unclass,
            unclassified_value=unclass,
            coverage_percentage=coverage,
            categories=categories,
        )

    def _compute_currency_allocation(
        self,
        positions: List[PortfolioPositionValuation],
        cash_entries: List[PortfolioCashValuation],
        nav: Decimal,
        include_cash: bool,
    ) -> ExposureDimensionResult:
        """Aggregates values by denomination currency in base currency equivalents."""
        cur_totals: Dict[str, Tuple[Decimal, Decimal, int]] = {}

        for pv in positions:
            cur = pv.price_currency or pv.basis_currency
            val = pv.base_market_value or Decimal("0.00")
            c_val, c_dir, c_cnt = cur_totals.get(cur, (Decimal("0.00"), Decimal("0.00"), 0))
            cur_totals[cur] = (c_val + val, c_dir + val, c_cnt + 1)

        if include_cash:
            for cv in cash_entries:
                cur = cv.currency
                c_val, c_dir, c_cnt = cur_totals.get(cur, (Decimal("0.00"), Decimal("0.00"), 0))
                cur_totals[cur] = (c_val + cv.base_cash_value, c_dir + cv.base_cash_value, c_cnt + 1)

        categories: List[ExposureCategoryRow] = []
        for cur, (val, dir_val, count) in cur_totals.items():
            w, pct = calculate_weight(val, nav)
            categories.append(
                ExposureCategoryRow(
                    category_id=cur,
                    category_name=f"{cur} Denominated",
                    market_value=val,
                    weight=w,
                    percentage=pct,
                    direct_value=dir_val,
                    lookthrough_value=Decimal("0.00"),
                    constituent_count=count,
                )
            )

        categories.sort(key=lambda x: x.market_value, reverse=True)
        tot_val = sum(r.market_value for r in categories)

        return ExposureDimensionResult(
            dimension=ExposureDimension.CURRENCY,
            taxonomy="ISO_4217_CURRENCY",
            taxonomy_version="2024",
            total_market_value=tot_val,
            classified_value=tot_val,
            unclassified_value=Decimal("0.00"),
            coverage_percentage=Decimal("100.00"),
            categories=categories,
        )

    def _compute_security_concentration(
        self,
        positions: List[PortfolioPositionValuation],
        cash_value: Decimal,
        nav: Decimal,
        include_cash: bool,
        fund_lookthroughs: Optional[List[FundLookThroughResult]] = None,
    ) -> Tuple[List[SecurityWeightItem], ConcentrationSummary]:
        """Calculates security-level weights and concentration metrics."""
        # Consolidate same instrument across accounts
        inst_map: Dict[str, Tuple[str, Optional[str], Decimal, Decimal, str, Set[str]]] = {}

        for pv in positions:
            val = pv.base_market_value or Decimal("0.00")
            if val <= Decimal("0.00"):
                continue

            inst_id = pv.instrument_id
            if inst_id in inst_map:
                sym, name, qty, tot_val, cur, accs = inst_map[inst_id]
                accs.add(pv.account_id)
                inst_map[inst_id] = (sym, name, qty + pv.quantity, tot_val + val, cur, accs)
            else:
                accs = {pv.account_id}
                inst_map[inst_id] = (pv.symbol, pv.company_name, pv.quantity, val, pv.basis_currency, accs)

        items_by_sym: Dict[str, SecurityWeightItem] = {}
        for inst_id, (sym, name, qty, val, cur, accs) in inst_map.items():
            w, pct = calculate_weight(val, nav)
            item = SecurityWeightItem(
                instrument_id=inst_id,
                symbol=sym,
                company_name=name,
                quantity=qty,
                market_value=val,
                weight=w,
                percentage=pct,
                currency=cur,
                account_ids=sorted(list(accs)),
                _direct_weight=w,
                _look_through_weight=Decimal("0.000000"),
            )
            items_by_sym[sym] = item

        if fund_lookthroughs:
            for flt in fund_lookthroughs:
                if flt.fund_symbol in items_by_sym:
                    fund_item = items_by_sym[flt.fund_symbol]
                    fund_item._direct_weight = flt.fund_weight_in_portfolio
                    fund_item._look_through_weight = Decimal("0.000000")
                    fund_item.market_value = flt.residual_market_value
                    fund_item.weight = flt.residual_weight
                    fund_item.percentage = flt.residual_weight * Decimal("100.0")

                for c in flt.known_constituents:
                    if c.symbol in items_by_sym:
                        target = items_by_sym[c.symbol]
                        target._look_through_weight = (target.look_through_weight + c.effective_weight_in_portfolio).quantize(Decimal("0.000001"))
                        target.market_value += c.effective_market_value
                        target.weight = (target.direct_weight + target.look_through_weight).quantize(Decimal("0.000001"))
                        target.percentage = (target.weight * Decimal("100.0")).quantize(Decimal("0.000001"))
                    else:
                        c_w = c.effective_weight_in_portfolio.quantize(Decimal("0.000001"))
                        c_item = SecurityWeightItem(
                            instrument_id=c.constituent_id,
                            symbol=c.symbol,
                            company_name=c.name,
                            quantity=Decimal("0"),
                            market_value=c.effective_market_value,
                            weight=c_w,
                            percentage=(c_w * Decimal("100.0")).quantize(Decimal("0.000001")),
                            currency=c.currency or "USD",
                            account_ids=[],
                            _direct_weight=Decimal("0.000000"),
                            _look_through_weight=c_w,
                        )
                        items_by_sym[c.symbol] = c_item

        items = [it for it in items_by_sym.values() if it.market_value > Decimal("0.00") or it.weight > Decimal("0.00")]

        # Include cash as a distinct holding if requested
        if include_cash and cash_value > Decimal("0.00"):
            w_cash, pct_cash = calculate_weight(cash_value, nav)
            items.append(
                SecurityWeightItem(
                    instrument_id="CASH_HOLDING",
                    symbol="CASH",
                    company_name="Cash & Equivalents",
                    quantity=cash_value,
                    market_value=cash_value,
                    weight=w_cash,
                    percentage=pct_cash,
                    currency="BASE",
                    account_ids=[],
                )
            )

        items.sort(key=lambda x: x.market_value, reverse=True)
        sorted_weights = [x.weight for x in items]

        w1, w3, w5, w10, _ = calculate_top_n_weights(sorted_weights)
        hhi_dec, hhi_conv, eff_n = calculate_concentration_hhi(sorted_weights)

        summary = ConcentrationSummary(
            scope=ConcentrationScope.SECURITY,
            top_1_weight=w1,
            top_3_weight=w3,
            top_5_weight=w5,
            top_10_weight=w10,
            hhi=hhi_dec,
            hhi_conventional=hhi_conv,
            effective_n=eff_n,
            holdings_count=len(items),
            is_cash_included=include_cash,
        )

        return items, summary

    def _compute_issuer_concentration(
        self,
        positions: List[PortfolioPositionValuation],
        cash_value: Decimal,
        nav: Decimal,
        include_cash: bool,
    ) -> Tuple[List[IssuerWeightItem], ConcentrationSummary]:
        """Consolidates holdings by economic issuer (e.g. multiple share classes, ADRs)."""
        issuer_map: Dict[str, Tuple[str, Decimal, Set[str], Set[str], Set[str]]] = {}
        # issuer_id -> (name, total_val, instruments, symbols, accounts)

        for pv in positions:
            val = pv.base_market_value or Decimal("0.00")
            if val <= Decimal("0.00"):
                continue

            meta = self.registry.get_instrument_metadata(pv.instrument_id)
            issuer_id = meta.issuer_id if meta else pv.instrument_id
            issuer_name = meta.issuer_name if meta else pv.company_name or pv.symbol

            if issuer_id in issuer_map:
                name, tot_val, insts, syms, accs = issuer_map[issuer_id]
                insts.add(pv.instrument_id)
                syms.add(pv.symbol)
                accs.add(pv.account_id)
                issuer_map[issuer_id] = (name, tot_val + val, insts, syms, accs)
            else:
                insts = {pv.instrument_id}
                syms = {pv.symbol}
                accs = {pv.account_id}
                issuer_map[issuer_id] = (issuer_name, val, insts, syms, accs)

        items: List[IssuerWeightItem] = []
        for iss_id, (name, val, insts, syms, accs) in issuer_map.items():
            w, pct = calculate_weight(val, nav)
            items.append(
                IssuerWeightItem(
                    issuer_id=iss_id,
                    issuer_name=name,
                    total_market_value=val,
                    weight=w,
                    percentage=pct,
                    instruments=sorted(list(insts)),
                    symbols=sorted(list(syms)),
                    account_ids=sorted(list(accs)),
                )
            )

        if include_cash and cash_value > Decimal("0.00"):
            w_cash, pct_cash = calculate_weight(cash_value, nav)
            items.append(
                IssuerWeightItem(
                    issuer_id="CASH_ISSUER",
                    issuer_name="Cash & Equivalents",
                    total_market_value=cash_value,
                    weight=w_cash,
                    percentage=pct_cash,
                    instruments=[],
                    symbols=["CASH"],
                    account_ids=[],
                )
            )

        items.sort(key=lambda x: x.total_market_value, reverse=True)
        sorted_weights = [x.weight for x in items]

        w1, w3, w5, w10, _ = calculate_top_n_weights(sorted_weights)
        hhi_dec, hhi_conv, eff_n = calculate_concentration_hhi(sorted_weights)

        summary = ConcentrationSummary(
            scope=ConcentrationScope.ISSUER,
            top_1_weight=w1,
            top_3_weight=w3,
            top_5_weight=w5,
            top_10_weight=w10,
            hhi=hhi_dec,
            hhi_conventional=hhi_conv,
            effective_n=eff_n,
            holdings_count=len(items),
            is_cash_included=include_cash,
        )

        return items, summary

