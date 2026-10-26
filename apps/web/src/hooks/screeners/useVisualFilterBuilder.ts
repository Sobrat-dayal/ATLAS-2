"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  ConditionValidationIssue,
  FilterCriterion,
  FilterOperator,
  ScreenerFilterDefinition,
  ScreenerUniverseDefinition,
  VisualFilterCondition,
} from "@/lib/screeners/types";
import { getMagnitudeMultiplier, validateVisualConditions } from "@/lib/screeners/validation";
import { generateQueryPreview } from "@/lib/screeners/preview";

interface UseVisualFilterBuilderProps {
  filtersRegistry: ScreenerFilterDefinition[];
  universes: ScreenerUniverseDefinition[];
  selectedUniverseId: string;
  appliedFilters: FilterCriterion[];
  onApplyQuery: (criteria: FilterCriterion[]) => void;
  isLoading?: boolean;
}

export function useVisualFilterBuilder({
  filtersRegistry,
  universes,
  selectedUniverseId,
  appliedFilters,
  onApplyQuery,
  isLoading = false,
}: UseVisualFilterBuilderProps) {
  // Convert applied FilterCriterion[] to VisualFilterCondition[] on initial load
  const initialApplied = useMemo(() => {
    return appliedFilters.map((af, idx) => {
      const def = filtersRegistry.find((f) => f.filter_id === af.filter_id);
      return {
        conditionId: af.condition_id || `applied-cond-${idx + 1}-${af.filter_id}`,
        filterId: af.filter_id,
        operator: af.operator,
        value: String(af.value),
        secondaryValue: af.secondary_value ? String(af.secondary_value) : null,
        currency: af.currency || (def?.currency_options ? def.currency_options[0] : null),
        magnitude: "UNITS" as const,
        status: "valid" as const,
      };
    });
  }, [appliedFilters, filtersRegistry]);

  const [draftConditions, setDraftConditions] = useState<VisualFilterCondition[]>(initialApplied);
  const [appliedConditions, setAppliedConditions] = useState<VisualFilterCondition[]>(initialApplied);
  const [isLibraryOpen, setIsLibraryOpen] = useState(false);
  const [selectedFilterForInspect, setSelectedFilterForInspect] = useState<ScreenerFilterDefinition | null>(null);
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);

  // Sync draft when appliedFilters updates from outside (e.g. preset or URL load)
  useEffect(() => {
    setDraftConditions(initialApplied);
    setAppliedConditions(initialApplied);
  }, [initialApplied]);

  // Client-side immediate validation & contradiction evaluation
  const validationResult = useMemo(() => {
    return validateVisualConditions(
      draftConditions,
      filtersRegistry,
      selectedUniverseId,
      universes
    );
  }, [draftConditions, filtersRegistry, selectedUniverseId, universes]);

  // Is dirty calculation
  const isDirty = useMemo(() => {
    if (draftConditions.length !== appliedConditions.length) return true;
    return draftConditions.some((d, idx) => {
      const a = appliedConditions[idx];
      if (!a) return true;
      return (
        d.filterId !== a.filterId ||
        d.operator !== a.operator ||
        d.value !== a.value ||
        d.secondaryValue !== a.secondaryValue ||
        d.currency !== a.currency ||
        d.magnitude !== a.magnitude
      );
    });
  }, [draftConditions, appliedConditions]);

  // Actions
  const handleAddCondition = useCallback(
    (filterId: string) => {
      if (draftConditions.length >= 20) return;
      const def = filtersRegistry.find((f) => f.filter_id === filterId);
      if (!def) return;

      const newCond: VisualFilterCondition = {
        conditionId: `cond-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`,
        filterId,
        operator: def.default_operator,
        value: "",
        secondaryValue: null,
        currency: def.currency_options ? def.currency_options[0] : null,
        magnitude: (def.magnitude_options?.[0] as any) || "UNITS",
        status: "incomplete",
        validationMessage: "Threshold required",
      };

      setDraftConditions((prev) => [...prev, newCond]);
    },
    [draftConditions.length, filtersRegistry]
  );

  const handleUpdateCondition = useCallback(
    (conditionId: string, updates: Partial<VisualFilterCondition>) => {
      setDraftConditions((prev) =>
        prev.map((c) => (c.conditionId === conditionId ? { ...c, ...updates, isDirty: true } : c))
      );
    },
    []
  );

  const handleRemoveCondition = useCallback((conditionId: string) => {
    setDraftConditions((prev) => prev.filter((c) => c.conditionId !== conditionId));
  }, []);

  const handleDuplicateCondition = useCallback(
    (conditionId: string) => {
      if (draftConditions.length >= 20) return;
      const target = draftConditions.find((c) => c.conditionId === conditionId);
      if (!target) return;

      const duplicated: VisualFilterCondition = {
        ...target,
        conditionId: `cond-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`,
        isDirty: true,
      };

      setDraftConditions((prev) => [...prev, duplicated]);
    },
    [draftConditions]
  );

  const handleClearConditions = useCallback(() => {
    setDraftConditions([]);
  }, []);

  const handleDiscardChanges = useCallback(() => {
    setDraftConditions(appliedConditions);
  }, [appliedConditions]);

  const handleApplyFilters = useCallback(() => {
    if (!validationResult.isValid) return;

    // Convert visual draft conditions into canonical FilterCriterion[]
    const canonicalCriteria: FilterCriterion[] = draftConditions.map((cond) => {
      const def = filtersRegistry.find((f) => f.filter_id === cond.filterId);
      let numVal: number | string = cond.value;

      // Normalize monetary magnitude factor
      if (def?.editor_type === "monetary_input" && cond.magnitude && cond.magnitude !== "UNITS") {
        const mult = getMagnitudeMultiplier(cond.magnitude);
        const parsed = Number(cond.value);
        if (Number.isFinite(parsed)) {
          numVal = (parsed * mult).toString();
        }
      }

      return {
        condition_id: cond.conditionId,
        filter_id: cond.filterId,
        operator: cond.operator,
        value: numVal,
        secondary_value: cond.secondaryValue || null,
        currency: cond.currency || null,
        unit: def?.unit_kind || null,
      };
    });

    onApplyQuery(canonicalCriteria);
    setAppliedConditions(draftConditions);
  }, [validationResult.isValid, draftConditions, filtersRegistry, onApplyQuery]);

  // Plain-English query preview summary
  const queryPreview = useMemo(() => {
    return generateQueryPreview(
      validationResult.updatedConditions,
      filtersRegistry,
      selectedUniverseId,
      universes,
      validationResult.isValid,
      validationResult.issues.some((i) => i.code === "SCREENER_CONTRADICTORY_CONDITIONS"),
      validationResult.warnings
    );
  }, [validationResult, filtersRegistry, selectedUniverseId, universes]);

  return {
    conditions: validationResult.updatedConditions,
    appliedConditions,
    isDirty,
    isValid: validationResult.isValid,
    issues: validationResult.issues,
    warnings: validationResult.warnings,
    queryPreview,
    isLibraryOpen,
    selectedFilterForInspect,
    isPreviewOpen,
    isLoading,
    toggleLibrary: () => setIsLibraryOpen((prev) => !prev),
    setIsLibraryOpen,
    setInspectFilter: setSelectedFilterForInspect,
    setIsPreviewOpen,
    addCondition: handleAddCondition,
    updateCondition: handleUpdateCondition,
    removeCondition: handleRemoveCondition,
    duplicateCondition: handleDuplicateCondition,
    clearConditions: handleClearConditions,
    discardChanges: handleDiscardChanges,
    applyFilters: handleApplyFilters,
  };
}
