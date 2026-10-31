"""Canonical Option Contract Registry (Stage 141).

Maintains contract master data, OSI mapping, underlying resolution, and seeded test fixtures.
"""

from __future__ import annotations

from typing import Dict, List, Optional
from atlas.options.contracts.adjustments import (
    CorporateOptionAdjustmentRecord,
    OptionAdjustmentRegistry,
)
from atlas.options.contracts.deliverables import (
    make_adjusted_deliverable,
    make_cash_index_deliverable,
    make_custom_lot_deliverable,
    make_standard_equity_deliverable,
)
from atlas.options.contracts.identifiers import format_osi_symbol
from atlas.options.domain import (
    AtlasOptionContract,
    ContractAdjustmentStatus,
    ExerciseStyle,
    OptionType,
    SettlementMethod,
)


class OptionContractRegistry:
    """Security master registry for listed options contracts."""

    def __init__(self, populate_seed_data: bool = True):
        self._contracts: Dict[str, AtlasOptionContract] = {}
        self._osi_index: Dict[str, str] = {}  # osi_symbol -> option_contract_id
        self._underlying_index: Dict[str, List[str]] = {}  # underlying_symbol -> [contract_id]
        self.adjustment_registry = OptionAdjustmentRegistry()

        if populate_seed_data:
            self._load_seed_contracts()

    def register_contract(self, contract: AtlasOptionContract) -> None:
        self._contracts[contract.option_contract_id] = contract

        if contract.osi_symbol:
            self._osi_index[contract.osi_symbol] = contract.option_contract_id

        underlying = contract.underlying_symbol.upper()
        if underlying not in self._underlying_index:
            self._underlying_index[underlying] = []
        if contract.option_contract_id not in self._underlying_index[underlying]:
            self._underlying_index[underlying].append(contract.option_contract_id)

    def get_contract(self, contract_id: str) -> Optional[AtlasOptionContract]:
        # Direct canonical lookup or via OSI index
        if contract_id in self._contracts:
            return self._contracts[contract_id]
        if contract_id in self._osi_index:
            return self._contracts[self._osi_index[contract_id]]
        return None

    def list_contracts_for_underlying(
        self,
        underlying_symbol: str,
        expiration_date: Optional[str] = None,
        option_type: Optional[OptionType] = None,
    ) -> List[AtlasOptionContract]:
        underlying = underlying_symbol.strip().upper()
        contract_ids = self._underlying_index.get(underlying, [])
        results = [self._contracts[cid] for cid in contract_ids if cid in self._contracts]

        if expiration_date:
            results = [c for c in results if c.expiration_date == expiration_date]
        if option_type:
            results = [c for c in results if c.option_type == option_type]

        # Sort by expiration date, then strike price
        results.sort(key=lambda c: (c.expiration_date, c.strike_price))
        return results

    def list_expirations_for_underlying(self, underlying_symbol: str) -> List[str]:
        contracts = self.list_contracts_for_underlying(underlying_symbol)
        expirations = sorted(list(set(c.expiration_date for c in contracts)))
        return expirations

    def _load_seed_contracts(self) -> None:
        """Seed realistic institutional options contracts covering reference fixtures A through R."""
        # 1. SPY standard vanilla contracts (Fixtures A, B, C, D, E, F)
        # Expiration: 2024-06-21
        spy_exp = "2024-06-21"
        spy_strikes = [80.0, 90.0, 95.0, 100.0, 105.0, 110.0, 115.0, 120.0, 500.0, 510.0, 520.0]

        for strike in spy_strikes:
            for opt_type in (OptionType.CALL, OptionType.PUT):
                type_char = "c" if opt_type == OptionType.CALL else "p"
                strike_slug = str(int(strike)) if strike.is_integer() else str(strike).replace(".", "_")
                cid = f"opt_spy_20240621_{type_char}_{strike_slug}"
                osi = format_osi_symbol("SPY", spy_exp, opt_type, strike)

                contract = AtlasOptionContract(
                    option_contract_id=cid,
                    underlying_instrument_id="inst_etf_spy",
                    underlying_symbol="SPY",
                    market_id="US_OPTIONS",
                    exchange_id="CBOE",
                    osi_symbol=osi,
                    option_type=opt_type,
                    strike_price=strike,
                    strike_currency="USD",
                    expiration_date=spy_exp,
                    last_trading_date="2024-06-21",
                    exercise_style=ExerciseStyle.AMERICAN,
                    settlement_method=SettlementMethod.PHYSICAL,
                    contract_multiplier=100.0,
                    deliverable=make_standard_equity_deliverable("SPY"),
                    adjustment_status=ContractAdjustmentStatus.STANDARD,
                )
                self.register_contract(contract)

        # 2. AAPL standard vanilla contracts across two expirations (2024-06-21 and 2024-07-19)
        # Allows testing multi-expiration calendars (Fixture M)
        aapl_expirations = ["2024-06-21", "2024-07-19"]
        aapl_strikes = [170.0, 175.0, 180.0, 185.0, 190.0, 195.0, 200.0]

        for exp in aapl_expirations:
            for strike in aapl_strikes:
                for opt_type in (OptionType.CALL, OptionType.PUT):
                    type_char = "c" if opt_type == OptionType.CALL else "p"
                    strike_slug = str(int(strike))
                    cid = f"opt_aapl_{exp.replace('-', '')}_{type_char}_{strike_slug}"
                    osi = format_osi_symbol("AAPL", exp, opt_type, strike)

                    contract = AtlasOptionContract(
                        option_contract_id=cid,
                        underlying_instrument_id="inst_eq_aapl",
                        underlying_symbol="AAPL",
                        market_id="US_OPTIONS",
                        exchange_id="CBOE",
                        osi_symbol=osi,
                        option_type=opt_type,
                        strike_price=strike,
                        strike_currency="USD",
                        expiration_date=exp,
                        last_trading_date=exp,
                        exercise_style=ExerciseStyle.AMERICAN,
                        settlement_method=SettlementMethod.PHYSICAL,
                        contract_multiplier=100.0,
                        deliverable=make_standard_equity_deliverable("AAPL"),
                        adjustment_status=ContractAdjustmentStatus.STANDARD,
                    )
                    self.register_contract(contract)

        # 3. Indian NSE NIFTY contract with lot size 50 and currency INR (Fixture N)
        nifty_exp = "2024-06-27"
        nifty_strikes = [21500.0, 22000.0, 22500.0]
        for strike in nifty_strikes:
            for opt_type in (OptionType.CALL, OptionType.PUT):
                type_char = "c" if opt_type == OptionType.CALL else "p"
                cid = f"opt_nifty_20240627_{type_char}_{int(strike)}"
                contract = AtlasOptionContract(
                    option_contract_id=cid,
                    underlying_instrument_id="inst_idx_nifty50",
                    underlying_symbol="NIFTY",
                    market_id="NSE_DERIVATIVES",
                    exchange_id="NSE",
                    osi_symbol=f"NIFTY24JUN{int(strike)}{'CE' if opt_type == OptionType.CALL else 'PE'}",
                    option_type=opt_type,
                    strike_price=strike,
                    strike_currency="INR",
                    expiration_date=nifty_exp,
                    last_trading_date="2024-06-27",
                    exercise_style=ExerciseStyle.EUROPEAN,
                    settlement_method=SettlementMethod.CASH,
                    contract_multiplier=50.0,  # Crucial non-100 lot size!
                    deliverable=make_custom_lot_deliverable("NIFTY", 50.0),
                    adjustment_status=ContractAdjustmentStatus.STANDARD,
                )
                self.register_contract(contract)

        # 4. Nonstandard Corporate Adjusted Option Contract (Fixtures G, O)
        # Result of 3-for-2 split + $250 special cash distribution
        adj_contract = AtlasOptionContract(
            option_contract_id="opt_xyz_adj_split_c_50",
            underlying_instrument_id="inst_eq_xyz",
            underlying_symbol="XYZ",
            market_id="US_OPTIONS",
            exchange_id="CBOE",
            osi_symbol="XYZ1  240621C00050000",
            option_type=OptionType.CALL,
            strike_price=50.0,
            strike_currency="USD",
            expiration_date="2024-06-21",
            last_trading_date="2024-06-21",
            exercise_style=ExerciseStyle.AMERICAN,
            settlement_method=SettlementMethod.PHYSICAL,
            contract_multiplier=100.0,
            deliverable=make_adjusted_deliverable("XYZ", 150.0, cash_amount=250.0, memo="3-for-2 split + $250 special dividend"),
            adjustment_status=ContractAdjustmentStatus.ADJUSTED_CORPORATE_ACTION,
            adjustment_memo="OCC Memo #54321: Adjusted for 3-for-2 split and $2.50/share special cash dividend",
            corporate_action_id="ca_xyz_split_2024",
        )
        self.register_contract(adj_contract)

        adj_record = CorporateOptionAdjustmentRecord(
            adjustment_id="adj_rec_xyz_2024",
            effective_date="2024-05-15",
            underlying_symbol="XYZ",
            corporate_action_type="STOCK_SPLIT",
            original_contract_id="opt_xyz_standard_c_50",
            adjusted_contract_id="opt_xyz_adj_split_c_50",
            original_multiplier=100.0,
            adjusted_multiplier=100.0,
            original_deliverable=make_standard_equity_deliverable("XYZ"),
            adjusted_deliverable=make_adjusted_deliverable("XYZ", 150.0, cash_amount=250.0),
            source_memo="OCC Information Memo #54321",
        )
        self.adjustment_registry.register_adjustment(adj_record)
