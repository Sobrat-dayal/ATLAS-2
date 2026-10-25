"use client";

import { useCallback, useEffect, useState } from "react";
import {
  getFinancialStatement,
  getStatementCatalog,
  getStatementSources,
  StatementApiError,
} from "@/lib/companies/statements/api";
import {
  ComparisonMode,
  ConsolidationScope,
  FinancialStatementResponse,
  ScaleType,
  StatementCatalogResponse,
  StatementPeriodType,
  StatementSourceMetadataDTO,
  StatementType,
} from "@/lib/companies/statements/types";

export interface UseCompanyStatementsProps {
  companyId: string;
  initialStatementType?: StatementType;
  initialPeriodType?: StatementPeriodType;
  initialScale?: ScaleType;
  initialComparisonMode?: ComparisonMode;
  initialScope?: ConsolidationScope;
}

export function useCompanyStatements({
  companyId,
  initialStatementType = "income_statement",
  initialPeriodType = "annual",
  initialScale = "billions",
  initialComparisonMode = "none",
  initialScope = "consolidated",
}: UseCompanyStatementsProps) {
  const [statementType, setStatementType] = useState<StatementType>(initialStatementType);
  const [periodType, setPeriodType] = useState<StatementPeriodType>(initialPeriodType);
  const [scale, setScale] = useState<ScaleType>(initialScale);
  const [comparisonMode, setComparisonMode] = useState<ComparisonMode>(initialComparisonMode);
  const [consolidationScope, setConsolidationScope] = useState<ConsolidationScope>(initialScope);

  const [catalog, setCatalog] = useState<StatementCatalogResponse | null>(null);
  const [statement, setStatement] = useState<FinancialStatementResponse | null>(null);
  const [sources, setSources] = useState<StatementSourceMetadataDTO[] | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState<number>(0);

  // Expanded row concept IDs
  const [expandedRows, setExpandedRows] = useState<Set<string>>(
    new Set([
      "revenue",
      "cost_of_revenue",
      "operating_expenses",
      "current_assets",
      "non_current_assets",
      "current_liabilities",
      "non_current_liabilities",
      "equity",
    ])
  );

  // Load catalog
  useEffect(() => {
    let active = true;
    if (!companyId) return;

    getStatementCatalog(companyId, consolidationScope)
      .then((cat) => {
        if (active) setCatalog(cat);
      })
      .catch((err) => {
        if (active) console.warn("Could not load statements catalog:", err);
      });

    return () => {
      active = false;
    };
  }, [companyId, consolidationScope]);

  // Load statement data asynchronously without synchronous setState in effect body
  useEffect(() => {
    let active = true;
    if (!companyId) return;

    const safePeriodType =
      statementType === "balance_sheet" && periodType === "ttm" ? "annual" : periodType;

    Promise.all([
      getFinancialStatement(companyId, statementType, {
        period_type: safePeriodType,
        consolidation_scope: consolidationScope,
        scale,
        comparison_mode: comparisonMode,
        max_periods: 5,
      }),
      getStatementSources(companyId, statementType, consolidationScope).catch(() => ({ sources: [] })),
    ])
      .then(([stmt, src]) => {
        if (!active) return;
        setStatement(stmt);
        setSources(src.sources);
        setError(null);
        setIsLoading(false);
      })
      .catch((err) => {
        if (!active) return;
        const msg = err instanceof StatementApiError ? err.message : (err as Error).message;
        setError(msg || "Failed to load financial statement.");
        setIsLoading(false);
      });

    return () => {
      active = false;
    };
  }, [companyId, statementType, periodType, consolidationScope, scale, comparisonMode, refreshTrigger]);

  const refetch = useCallback(() => {
    setIsLoading(true);
    setRefreshTrigger((prev) => prev + 1);
  }, []);

  const toggleRow = useCallback((conceptId: string) => {
    setExpandedRows((prev) => {
      const next = new Set(prev);
      if (next.has(conceptId)) {
        next.delete(conceptId);
      } else {
        next.add(conceptId);
      }
      return next;
    });
  }, []);

  const expandAll = useCallback(() => {
    if (!statement) return;
    const allGroupIds = statement.rows.filter((r) => r.is_group).map((r) => r.concept_id);
    setExpandedRows(new Set(allGroupIds));
  }, [statement]);

  const collapseAll = useCallback(() => {
    setExpandedRows(new Set());
  }, []);

  const handleSetStatementType = useCallback(
    (type: StatementType) => {
      setStatementType(type);
      setIsLoading(true);
      if (type === "balance_sheet" && periodType === "ttm") {
        setPeriodType("annual");
      }
    },
    [periodType]
  );

  return {
    statementType,
    setStatementType: handleSetStatementType,
    periodType,
    setPeriodType,
    scale,
    setScale,
    comparisonMode,
    setComparisonMode,
    consolidationScope,
    setConsolidationScope,
    catalog,
    statement,
    sources,
    isLoading,
    error,
    expandedRows,
    toggleRow,
    expandAll,
    collapseAll,
    refetch,
  };
}
