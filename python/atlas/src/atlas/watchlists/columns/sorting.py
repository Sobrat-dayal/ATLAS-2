"""Financial multi-asset sorting engine for Watchlist Columns (Stage 77).

Implements 3-state cycling (ASC, DESC, manual default), deterministic tie-breakers,
missing-values-last semantics, and financial currency/unit comparability checks.
"""

from decimal import Decimal
from typing import Any, List, Optional, Tuple

from .schemas import WatchlistRowProjection


class WatchlistSortingEngine:
    """
    Sorts projected watchlist rows while preserving financial comparability
    and deterministic tie-breakers.
    """

    @classmethod
    def sort_rows(
        cls,
        rows: List[WatchlistRowProjection],
        sort_column_id: Optional[str],
        direction: Optional[str],
    ) -> Tuple[List[WatchlistRowProjection], bool]:
        """
        Sorts the given projected rows by the specified column and direction.

        Returns:
            Tuple of (sorted_rows, incompatible_units_detected).
        """
        if not sort_column_id or direction not in ("asc", "desc"):
            # Default manual order (restores Stage 76 manual position)
            sorted_rows = sorted(rows, key=lambda r: (r.manual_position, str(r.item_id)))
            return sorted_rows, False

        is_desc = direction == "desc"

        from .registry import get_column_definition

        col_def = get_column_definition(sort_column_id)
        is_numeric = (col_def and col_def.sort_policy == "numeric") or sort_column_id in (
            "quote.latest_measure",
            "quote.change",
        )
        is_monetary = col_def and col_def.value_type == "MONETARY"

        # Check for mixed currencies on monetary columns or market quotes
        incompatible_units = False
        if sort_column_id == "quote.latest_measure" or is_monetary:
            currencies = set()
            measure_kinds = set()
            for r in rows:
                cell = r.values.get(sort_column_id)
                if cell and cell.status == "AVAILABLE" and cell.value is not None:
                    if cell.unit:
                        currencies.add(cell.unit.upper())
                    if cell.currency:
                        currencies.add(cell.currency.upper())
                    if cell.measure_kind:
                        measure_kinds.add(cell.measure_kind.lower())
            if len(currencies) > 1 or len(measure_kinds) > 1:
                incompatible_units = True

        def sort_key(row: WatchlistRowProjection) -> Tuple[int, Any, int, str]:
            cell = row.values.get(sort_column_id)
            has_val = False
            raw_val: Any = None

            if cell is not None and cell.status == "AVAILABLE" and cell.value is not None:
                val = cell.value
                # Verify non-empty
                if isinstance(val, str):
                    val_str = val.strip()
                    if val_str != "" and val_str != "—":
                        has_val = True
                        raw_val = val_str
                else:
                    has_val = True
                    raw_val = val

            # Primary key: 0 if valid value, 1 if missing.
            # This ensures missing values ALWAYS sort last regardless of direction!
            if not has_val:
                return (1, 0, row.manual_position, str(row.item_id))

            # Parse value according to type
            parsed_val: Any = raw_val
            if is_numeric:
                try:
                    cleaned = (
                        str(raw_val).replace("%", "").replace("+", "").replace(",", "").strip()
                    )
                    parsed_val = float(Decimal(cleaned))
                except Exception:
                    parsed_val = 0.0
            elif isinstance(raw_val, str):
                parsed_val = raw_val.lower()

            # If incompatible units, prepend unit so like-currencies group together cleanly
            unit_val = (cell.currency or cell.unit or "").upper() if cell else ""
            if incompatible_units and unit_val:
                parsed_val = (unit_val, parsed_val)

            return (0, parsed_val, row.manual_position, str(row.item_id))

        # Sort with missing-values-last semantics
        valid_rows = [r for r in rows if sort_key(r)[0] == 0]
        missing_rows = [r for r in rows if sort_key(r)[0] == 1]

        # First sort by deterministic tie-breakers (manual_position ascending, then item_id)
        valid_rows.sort(key=lambda r: (r.manual_position, str(r.item_id)))
        # Stable sort by parsed value preserves tie-breaker order for tied values
        valid_rows.sort(key=lambda r: sort_key(r)[1], reverse=is_desc)

        # Missing rows always maintain manual relative order
        missing_rows.sort(key=lambda r: (r.manual_position, str(r.item_id)))

        return valid_rows + missing_rows, incompatible_units
