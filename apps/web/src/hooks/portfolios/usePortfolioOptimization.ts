"use client";

import { useCallback, useEffect, useState } from "react";
import {
  archiveOptimizationStudy,
  createOptimizationStudy,
  executeOptimizationRun,
  getLatestOptimizationRun,
  getOptimizationMethodologies,
  getOptimizationRun,
  getOptimizationStudy,
  getOptimizationUniverse,
  listOptimizationRuns,
  listOptimizationStudies,
  validateOptimizationConstraints,
} from "@/lib/portfolios/optimization/api";
import {
  ConstraintValidationResultDTO,
  CreateOptimizationStudyRequestDTO,
  ExecuteOptimizationRequestDTO,
  OptimizationConstraintRequestDTO,
  OptimizationMethodologiesDTO,
  OptimizationObjective,
  OptimizationStudyDTO,
  PortfolioOptimizationRunDTO,
  UniverseAssetDTO,
} from "@/lib/portfolios/optimization/types";

export type OptimizationWorkspaceTab =
  | "frontier"
  | "comparison"
  | "constraints"
  | "diagnostics"
  | "sensitivity"
  | "studies";

export interface UsePortfolioOptimizationReturn {
  activeRun: PortfolioOptimizationRunDTO | null;
  activeStudy: OptimizationStudyDTO | null;
  studies: OptimizationStudyDTO[];
  runs: PortfolioOptimizationRunDTO[];
  universe: UniverseAssetDTO[];
  methodologies: OptimizationMethodologiesDTO | null;
  activeTab: OptimizationWorkspaceTab;
  selectedObjective: OptimizationObjective;
  riskAversion: number;
  targetReturn: number | undefined;
  constraints: OptimizationConstraintRequestDTO[];
  validationResult: ConstraintValidationResultDTO | null;
  loading: boolean;
  solving: boolean;
  error: string | null;
  setActiveTab: (tab: OptimizationWorkspaceTab) => void;
  setSelectedObjective: (obj: OptimizationObjective) => void;
  setRiskAversion: (lambda: number) => void;
  setTargetReturn: (ret: number | undefined) => void;
  setConstraints: (constraints: OptimizationConstraintRequestDTO[]) => void;
  addConstraint: (c: OptimizationConstraintRequestDTO) => void;
  removeConstraint: (index: number) => void;
  validateConstraints: () => Promise<void>;
  selectStudy: (studyId: string) => Promise<void>;
  createStudy: (req: CreateOptimizationStudyRequestDTO) => Promise<void>;
  archiveStudy: (studyId: string) => Promise<void>;
  selectRun: (runId: string) => Promise<void>;
  executeRun: (overrides?: Partial<ExecuteOptimizationRequestDTO>) => Promise<void>;
  refresh: () => Promise<void>;
}

export function usePortfolioOptimization(portfolioId: string): UsePortfolioOptimizationReturn {
  const [activeRun, setActiveRun] = useState<PortfolioOptimizationRunDTO | null>(null);
  const [activeStudy, setActiveStudy] = useState<OptimizationStudyDTO | null>(null);
  const [studies, setStudies] = useState<OptimizationStudyDTO[]>([]);
  const [runs, setRuns] = useState<PortfolioOptimizationRunDTO[]>([]);
  const [universe, setUniverse] = useState<UniverseAssetDTO[]>([]);
  const [methodologies, setMethodologies] = useState<OptimizationMethodologiesDTO | null>(null);
  const [activeTab, setActiveTab] = useState<OptimizationWorkspaceTab>("frontier");
  const [selectedObjective, setSelectedObjective] = useState<OptimizationObjective>("MINIMUM_VARIANCE");
  const [riskAversion, setRiskAversion] = useState<number>(2.0);
  const [targetReturn, setTargetReturn] = useState<number | undefined>(undefined);
  const [constraints, setConstraints] = useState<OptimizationConstraintRequestDTO[]>([]);
  const [validationResult, setValidationResult] = useState<ConstraintValidationResultDTO | null>(null);

  const [loading, setLoading] = useState<boolean>(true);
  const [solving, setSolving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    if (!portfolioId) return;
    setLoading(true);
    setError(null);
    try {
      const [runRes, studiesRes, universeRes, methRes] = await Promise.all([
        getLatestOptimizationRun(portfolioId),
        listOptimizationStudies(portfolioId).catch(() => ({ items: [], total: 0 })),
        getOptimizationUniverse(portfolioId).catch(() => []),
        getOptimizationMethodologies(portfolioId).catch(() => null),
      ]);

      setActiveRun(runRes);
      setSelectedObjective(runRes.objective_type);
      setStudies(studiesRes.items || []);
      setUniverse(universeRes || []);
      setMethodologies(methRes);

      if (runRes.study_id) {
        const found = (studiesRes.items || []).find((s) => s.study_id === runRes.study_id);
        if (found) setActiveStudy(found);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load portfolio optimization data.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [portfolioId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const addConstraint = useCallback((c: OptimizationConstraintRequestDTO) => {
    setConstraints((prev) => [...prev, c]);
  }, []);

  const removeConstraint = useCallback((index: number) => {
    setConstraints((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const validateConstraintsAction = useCallback(async () => {
    if (!portfolioId) return;
    try {
      const symbols = universe.map((u) => u.symbol);
      const res = await validateOptimizationConstraints(portfolioId, constraints, symbols);
      setValidationResult(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Constraint validation failed.";
      setValidationResult({
        is_feasible: false,
        message: msg,
        constraint_count: constraints.length,
        conflicts: [msg],
      });
    }
  }, [portfolioId, constraints, universe]);

  const selectStudy = useCallback(
    async (studyId: string) => {
      if (!portfolioId || !studyId) return;
      try {
        const study = await getOptimizationStudy(portfolioId, studyId);
        setActiveStudy(study);
        setSelectedObjective(study.default_objective);
        const runsList = await listOptimizationRuns(portfolioId, studyId);
        setRuns(runsList.items || []);
        if (runsList.items && runsList.items.length > 0) {
          setActiveRun(runsList.items[0]);
        }
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Failed to load optimization study.";
        setError(msg);
      }
    },
    [portfolioId]
  );

  const createStudy = useCallback(
    async (req: CreateOptimizationStudyRequestDTO) => {
      if (!portfolioId) return;
      try {
        const newStudy = await createOptimizationStudy(portfolioId, req);
        setStudies((prev) => [newStudy, ...prev]);
        setActiveStudy(newStudy);
        setSelectedObjective(newStudy.default_objective);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Failed to create optimization study.";
        setError(msg);
        throw err;
      }
    },
    [portfolioId]
  );

  const archiveStudy = useCallback(
    async (studyId: string) => {
      if (!portfolioId || !studyId) return;
      try {
        await archiveOptimizationStudy(portfolioId, studyId);
        setStudies((prev) => prev.filter((s) => s.study_id !== studyId));
        if (activeStudy?.study_id === studyId) {
          setActiveStudy(null);
        }
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Failed to archive optimization study.";
        setError(msg);
        throw err;
      }
    },
    [portfolioId, activeStudy]
  );

  const selectRun = useCallback(
    async (runId: string) => {
      if (!portfolioId || !runId) return;
      try {
        const run = await getOptimizationRun(portfolioId, runId);
        setActiveRun(run);
        setSelectedObjective(run.objective_type);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Failed to load optimization run.";
        setError(msg);
      }
    },
    [portfolioId]
  );

  const executeRun = useCallback(
    async (overrides?: Partial<ExecuteOptimizationRequestDTO>) => {
      if (!portfolioId) return;
      setSolving(true);
      setError(null);
      try {
        const payload: ExecuteOptimizationRequestDTO = {
          study_id: activeStudy?.study_id,
          objective_type: selectedObjective,
          risk_aversion: riskAversion,
          target_return: targetReturn,
          constraints: constraints.length > 0 ? constraints : undefined,
          is_long_only: true,
          ...overrides,
        };

        const result = await executeOptimizationRun(portfolioId, payload);
        setActiveRun(result);
        setRuns((prev) => [result, ...prev]);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Optimization solver failed to converge.";
        setError(msg);
        throw err;
      } finally {
        setSolving(false);
      }
    },
    [portfolioId, activeStudy, selectedObjective, riskAversion, targetReturn, constraints]
  );

  return {
    activeRun,
    activeStudy,
    studies,
    runs,
    universe,
    methodologies,
    activeTab,
    selectedObjective,
    riskAversion,
    targetReturn,
    constraints,
    validationResult,
    loading,
    solving,
    error,
    setActiveTab,
    setSelectedObjective,
    setRiskAversion,
    setTargetReturn,
    setConstraints,
    addConstraint,
    removeConstraint,
    validateConstraints: validateConstraintsAction,
    selectStudy,
    createStudy,
    archiveStudy,
    selectRun,
    executeRun,
    refresh: loadData,
  };
}
