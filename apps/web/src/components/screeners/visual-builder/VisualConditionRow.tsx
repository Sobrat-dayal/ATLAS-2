"use client";

import React from "react";
import {
  AlertTriangle,
  Copy,
  Info,
  Trash2,
  XCircle,
} from "lucide-react";
import {
  CountryOption,
  ExchangeOption,
  FilterOperator,
  ScreenerFilterDefinition,
  SectorOption,
  VisualFilterCondition,
} from "@/lib/screeners/types";
import { DecimalFilterInput } from "./editors/DecimalFilterInput";
import { MonetaryFilterInput } from "./editors/MonetaryFilterInput";
import { PercentageFilterInput } from "./editors/PercentageFilterInput";
import { RangeFilterInput } from "./editors/RangeFilterInput";
import { EnumFilterSelect } from "./editors/EnumFilterSelect";

interface VisualConditionRowProps {
  condition: VisualFilterCondition;
  index: number;
  totalConditions: number;
  filtersRegistry: ScreenerFilterDefinition[];
  exchanges: ExchangeOption[];
  geographies: CountryOption[];
  industries: SectorOption[];
  onUpdate: (conditionId: string, updates: Partial<VisualFilterCondition>) => void;
  onRemove: (conditionId: string) => void;
  onDuplicate: (conditionId: string) => void;
  onInspect: (filter: ScreenerFilterDefinition) => void;
}

const OPERATOR_DISPLAY_NAMES: Record<string, string> = {
  gt: "> (Greater Than)",
  gte: ">= (Greater or Equal)",
  lt: "< (Less Than)",
  lte: "<= (Less or Equal)",
  eq: "= (Equals)",
  ne: "!= (Not Equal)",
  between: "Between (Range)",
  in: "In (Any of)",
};

export function VisualConditionRow({
  condition,
  index,
  totalConditions,
  filtersRegistry,
  exchanges,
  geographies,
  industries,
  onUpdate,
  onRemove,
  onDuplicate,
  onInspect,
}: VisualConditionRowProps) {
  const currentFilter = filtersRegistry.find((f) => f.filter_id === condition.filterId);

  // Enum options derivation
  const enumOptions = React.useMemo(() => {
    if (condition.filterId === "exchange_mic") {
      return exchanges.map((e) => ({ value: e.mic, label: `${e.mic} (${e.name})`, count: e.count }));
    }
    if (condition.filterId === "listing_country_code" || condition.filterId === "issuer_country_code") {
      return geographies.map((g) => ({ value: g.code, label: `${g.name} (${g.code})`, count: g.count }));
    }
    if (condition.filterId === "sector") {
      return industries.map((s) => ({ value: s.name, label: s.name, count: s.count }));
    }
    if (condition.filterId === "industry") {
      const allInds: Array<{ value: string; label: string }> = [];
      industries.forEach((s) => {
        s.industries.forEach((ind) => {
          allInds.push({ value: ind, label: `${ind} (${s.name})` });
        });
      });
      return allInds;
    }
    return [];
  }, [condition.filterId, exchanges, geographies, industries]);

  const handleMetricChange = (newMetricId: string) => {
    const newDef = filtersRegistry.find((f) => f.filter_id === newMetricId);
    if (!newDef) return;

    onUpdate(condition.conditionId, {
      filterId: newMetricId,
      operator: newDef.default_operator,
      value: "",
      secondaryValue: null,
      currency: newDef.currency_options ? newDef.currency_options[0] : null,
      magnitude: (newDef.magnitude_options?.[0] as any) || "UNITS",
      status: "incomplete",
      validationMessage: null,
      fieldErrors: {},
    });
  };

  const hasError = condition.status === "invalid";
  const isIncomplete = condition.status === "incomplete";

  return (
    <div
      className={`group relative flex flex-wrap items-center justify-between gap-2.5 rounded border p-2.5 transition-colors ${
        hasError
          ? "border-destructive/60 bg-destructive/5"
          : isIncomplete
          ? "border-amber-500/50 bg-amber-500/5"
          : "border-border/60 bg-card/60 hover:border-border hover:bg-card"
      }`}
    >
      {/* Left side: Metric Select & Operator Select */}
      <div className="flex flex-wrap items-center gap-2">
        {/* Metric Selector Dropdown */}
        <select
          value={condition.filterId}
          onChange={(e) => handleMetricChange(e.target.value)}
          aria-label="Filter metric"
          className="h-7 max-w-48 truncate rounded border border-border/70 bg-background/90 px-2 text-xs font-medium text-foreground transition-colors hover:border-border focus:border-primary focus:outline-none"
        >
          {filtersRegistry.map((f) => (
            <option key={f.filter_id} value={f.filter_id}>
              {f.display_name}
            </option>
          ))}
        </select>

        {/* Operator Selector */}
        {currentFilter && (
          <select
            value={condition.operator}
            onChange={(e) =>
              onUpdate(condition.conditionId, {
                operator: e.target.value as FilterOperator,
              })
            }
            aria-label="Comparison operator"
            className="h-7 rounded border border-border/70 bg-background/90 px-2 text-xs font-mono text-muted-foreground transition-colors hover:border-border focus:border-primary focus:outline-none"
          >
            {currentFilter.allowed_operators.map((op) => (
              <option key={op} value={op}>
                {OPERATOR_DISPLAY_NAMES[op] || op.toUpperCase()}
              </option>
            ))}
          </select>
        )}

        {/* Typed Value Editor */}
        {condition.operator === "between" ? (
          <RangeFilterInput
            minValue={condition.value}
            maxValue={condition.secondaryValue || ""}
            onChangeMin={(val) => onUpdate(condition.conditionId, { value: val })}
            onChangeMax={(val) => onUpdate(condition.conditionId, { secondaryValue: val })}
            unitLabel={
              currentFilter?.unit_kind === "percent"
                ? "%"
                : currentFilter?.unit_kind === "multiple"
                ? "x"
                : condition.currency || undefined
            }
            hasError={hasError || isIncomplete}
          />
        ) : currentFilter?.editor_type === "monetary_input" ? (
          <MonetaryFilterInput
            value={condition.value}
            currency={condition.currency || "USD"}
            magnitude={condition.magnitude || "UNITS"}
            currencyOptions={currentFilter.currency_options}
            magnitudeOptions={currentFilter.magnitude_options}
            onChangeValue={(val) => onUpdate(condition.conditionId, { value: val })}
            onChangeCurrency={(cur) => onUpdate(condition.conditionId, { currency: cur })}
            onChangeMagnitude={(mag) => onUpdate(condition.conditionId, { magnitude: mag })}
            hasError={hasError || isIncomplete}
          />
        ) : currentFilter?.editor_type === "percent_input" || currentFilter?.editor_type === "multiple_input" ? (
          <PercentageFilterInput
            value={condition.value}
            onChange={(val) => onUpdate(condition.conditionId, { value: val })}
            unitKind={currentFilter.unit_kind}
            hasError={hasError || isIncomplete}
          />
        ) : currentFilter?.editor_type === "enum_multi_select" || currentFilter?.editor_type === "enum_select" ? (
          <EnumFilterSelect
            value={condition.value}
            options={enumOptions}
            isMulti={condition.operator === "in"}
            onChange={(val) => onUpdate(condition.conditionId, { value: val })}
            hasError={hasError || isIncomplete}
          />
        ) : (
          <DecimalFilterInput
            value={condition.value}
            onChange={(val) => onUpdate(condition.conditionId, { value: val })}
            unitLabel={currentFilter?.unit_kind === "shares" ? "shares" : undefined}
            hasError={hasError || isIncomplete}
          />
        )}

        {/* Info button */}
        {currentFilter && (
          <button
            type="button"
            onClick={() => onInspect(currentFilter)}
            title="Inspect metric definition"
            aria-label={`Inspect ${currentFilter.display_name} definition`}
            className="rounded p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
          >
            <Info className="h-3.5 w-3.5" />
          </button>
        )}
      </div>

      {/* Right side: Status indicator & Action buttons */}
      <div className="flex items-center gap-2">
        {/* Error / Warning indicator */}
        {hasError && condition.validationMessage && (
          <span className="flex items-center gap-1 text-[11px] font-medium text-destructive">
            <XCircle className="h-3.5 w-3.5 shrink-0" />
            <span className="max-w-xs truncate">{condition.validationMessage}</span>
          </span>
        )}
        {isIncomplete && condition.validationMessage && (
          <span className="flex items-center gap-1 text-[11px] font-medium text-amber-500">
            <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
            <span className="max-w-xs truncate">{condition.validationMessage}</span>
          </span>
        )}

        {/* Duplicate button */}
        <button
          type="button"
          onClick={() => onDuplicate(condition.conditionId)}
          title="Duplicate condition"
          aria-label="Duplicate condition"
          className="rounded p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
        >
          <Copy className="h-3.5 w-3.5" />
        </button>

        {/* Remove button */}
        <button
          type="button"
          onClick={() => onRemove(condition.conditionId)}
          title="Remove condition"
          aria-label={`Remove condition ${index + 1}`}
          className="rounded p-1 text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
        >
          <Trash2 className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  );
}
