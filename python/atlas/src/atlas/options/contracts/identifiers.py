"""Options Symbology and Identifier Handling (Stage 141).

Supports:
- U.S. OCC/OSI 21-character symbology parsing and formatting
- Non-U.S. exchange symbology conventions (e.g. Indian NSE, European Eurex)
- Stable canonical contract identity mapping
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from atlas.options.domain import OptionType


def format_osi_symbol(
    root: str,
    expiration_date: str,  # YYYY-MM-DD
    option_type: OptionType | str,
    strike_price: float,
) -> str:
    """Format a standard 21-character OCC / OSI symbol.

    Convention:
    - Root: 6 characters, left-aligned, right-padded with spaces
    - Expiration: YYMMDD (6 characters)
    - Type: 'C' for Call, 'P' for Put (1 character)
    - Strike: Strike price multiplied by 1000, 8 digits, zero-padded (8 characters)
    Total length: 21 characters.
    """
    clean_root = root.strip().upper()[:6].ljust(6)

    # Parse date
    dt = datetime.strptime(expiration_date, "%Y-%m-%d")
    yymmdd = dt.strftime("%y%m%d")

    opt_char = "C" if str(option_type).upper().endswith("CALL") or str(option_type).upper() == "C" else "P"

    strike_int = int(round(strike_price * 1000.0))
    strike_str = f"{strike_int:08d}"

    return f"{clean_root}{yymmdd}{opt_char}{strike_str}"


def parse_osi_symbol(osi: str) -> Dict[str, Any]:
    """Parse a standard 21-character OCC / OSI symbol."""
    if len(osi) != 21:
        raise ValueError(f"OSI symbol must be exactly 21 characters, got {len(osi)}: '{osi}'")

    root = osi[:6].strip()
    yymmdd = osi[6:12]
    opt_char = osi[12].upper()
    strike_str = osi[13:21]

    # Parse expiration
    dt = datetime.strptime(yymmdd, "%y%m%d")
    # Handle Y2K window (assuming 2000-2099)
    year = dt.year if dt.year >= 2000 else dt.year + 100
    expiration_date = f"{year:04d}-{dt.month:02d}-{dt.day:02d}"

    option_type = OptionType.CALL if opt_char == "C" else OptionType.PUT
    strike_price = float(int(strike_str)) / 1000.0

    return {
        "root": root,
        "expiration_date": expiration_date,
        "option_type": option_type,
        "strike_price": strike_price,
    }


def parse_indian_nse_symbol(symbol: str) -> Optional[Dict[str, Any]]:
    """Parse Indian NSE options series identifier, e.g. NIFTY24JUN22000CE."""
    # Pattern: ROOT + YY + MMM + STRIKE + CE/PE
    pattern = r"^([A-Z]+)(\d{2})([A-Z]{3})(\d+)(CE|PE)$"
    match = re.match(pattern, symbol.strip().upper())
    if not match:
        return None

    root, yy, mmm, strike_str, opt_type_code = match.groups()
    option_type = OptionType.CALL if opt_type_code == "CE" else OptionType.PUT
    strike_price = float(strike_str)

    return {
        "root": root,
        "year_suffix": yy,
        "month_str": mmm,
        "strike_price": strike_price,
        "option_type": option_type,
        "market": "NSE_DERIVATIVES",
    }
