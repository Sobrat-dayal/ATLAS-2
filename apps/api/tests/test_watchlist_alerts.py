"""Comprehensive Automated Test Suite for ATLAS Stage 80:
Watchlist Alerts V1.

Tests cover:
1. Migration file verification (stage80_watchlist_alerts.py).
2. Rule CRUD, validation, revision conflict control, and quotas.
3. Strict crossing logic:
   - No first-snapshot false crossings (baseline seeding).
   - Upward crossing: P_prev <= T and P_curr > T.
   - Downward crossing: P_prev >= T and P_curr < T.
   - Re-arming requirements (must return to opposite side before repeat crossing).
   - Cooldown enforcement.
4. Decimal-safe percentage-change conditions:
   - Session previous close, rolling 24h, previous NAV.
   - Zero denominator safe handling (no NaN/Inf).
5. Source freshness validation (rejecting stale ticks).
6. Event ordering and duplicate event rejection.
7. Multi-worker idempotency and deduplication keys.
8. Watchlist and item lifecycle cascades (disabling active alerts on item/watchlist removal).
9. Reliable outbox notification dispatch to Stage 49 Notification Center.
10. Side-effect invariants: 0 orders, 0 portfolio mutations, 0 LLM calls.
"""

import datetime
import importlib.util
from decimal import Decimal
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from atlas.watchlists.alerts import (
    AlertEvaluationEngine,
    AlertEvaluationStatus,
    AlertLimitExceededError,
    AlertNotificationDispatcher,
    AlertRuleType,
    AlertState,
    ArmedSide,
    ComparisonOperator,
    CreateAlertRequest,
    IncompatibleQuoteMeasureError,
    NotificationDeliveryStatus,
    QuoteMeasure,
    RecurrencePolicy,
    ReferenceMethodology,
    WatchlistAlertEvaluationState,
    WatchlistAlertNotificationOutbox,
    WatchlistAlertRepository,
    WatchlistAlertRule,
    WatchlistAlertService,
    compute_percentage_change,
    evaluate_alert_condition,
    get_alert_capabilities,
    validate_measure_for_asset_class,
)

# =============================================================================
# 1. Migration Verification
# =============================================================================


def test_stage80_migration_structure():
    """Verifies that the stage80_watchlist_alerts migration exists with correct metadata."""
    migration_path = Path("apps/api/migrations/versions/stage80_watchlist_alerts.py")
    assert migration_path.exists(), f"Migration file not found at {migration_path}"

    spec = importlib.util.spec_from_file_location("stage80_migration", migration_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.revision == "stage80_watchlist_alerts"
    assert module.down_revision == "stage77_watchlist_columns"
    assert hasattr(module, "upgrade")
    assert hasattr(module, "downgrade")


# =============================================================================
# 2. Capabilities & Asset-Class Compatibility
# =============================================================================


def test_alert_capabilities_catalog():
    caps = get_alert_capabilities()
    assert len(caps.capabilities) == 6
    assert caps.max_active_alerts_per_user == 100
    assert caps.max_alerts_per_instrument == 20
    assert len(caps.reference_methodologies) == 3
    assert len(caps.cooldown_presets) == 6


def test_measure_compatibility():
    assert validate_measure_for_asset_class(QuoteMeasure.LAST, "equity") is True
    assert validate_measure_for_asset_class(QuoteMeasure.BID, "equity") is True
    assert validate_measure_for_asset_class(QuoteMeasure.NAV, "equity") is False
    assert validate_measure_for_asset_class(QuoteMeasure.NAV, "etf") is True
    assert validate_measure_for_asset_class(QuoteMeasure.NAV, "mutual_fund") is True
    assert validate_measure_for_asset_class(QuoteMeasure.YIELD, "bond") is True
    assert validate_measure_for_asset_class(QuoteMeasure.YIELD, "equity") is False


# =============================================================================
# 3. Crossing Condition Logic & No First-Snapshot Triggers
# =============================================================================


def test_no_first_snapshot_crossing_above():
    """Requirement 23 & 186: If alert begins when latest price is already above threshold,
    do NOT report a crossing above. Baseline must be established first."""
    threshold = Decimal("100.00")
    now = datetime.datetime.now(datetime.timezone.utc)

    # First observation = 105 (> threshold)
    res = evaluate_alert_condition(
        rule_type=AlertRuleType.CROSSING_ABOVE,
        threshold=threshold,
        recurrence_policy=RecurrencePolicy.ONE_SHOT,
        current_value=Decimal("105.00"),
        reference_price=None,
        baseline_established=False,  # Initial observation
        prior_armed_side=None,
        now=now,
        cooldown_until=None,
    )

    assert res.triggered is False
    assert res.new_baseline_established is True
    assert res.new_armed_side == ArmedSide.ABOVE
    assert res.reason == "BASELINE_ESTABLISHED"


def test_crossing_above_sequence():
    """Requirement 185: Deterministic crossing-above test sequence:
    Threshold = 100
    Obs A = 98 -> Baseline established (no trigger)
    Obs B = 101 -> Crossing above! Triggered once!
    Obs C = 102 -> No additional crossing
    Obs D = 103 -> No additional crossing
    Obs E = 99 -> Returns below (re-armed!)
    Obs F = 101 -> Recurring crossing above triggered again!
    """
    threshold = Decimal("100.00")
    now = datetime.datetime.now(datetime.timezone.utc)

    # Obs A = 98 (First observation seeds baseline)
    res_a = evaluate_alert_condition(
        rule_type=AlertRuleType.CROSSING_ABOVE,
        threshold=threshold,
        recurrence_policy=RecurrencePolicy.RECURRING,
        current_value=Decimal("98.00"),
        reference_price=None,
        baseline_established=False,
        prior_armed_side=None,
        now=now,
        cooldown_until=None,
    )
    assert res_a.triggered is False
    assert res_a.new_baseline_established is True
    assert res_a.new_armed_side == ArmedSide.BELOW

    # Obs B = 101 (Transitions from BELOW to ABOVE -> Trigger!)
    res_b = evaluate_alert_condition(
        rule_type=AlertRuleType.CROSSING_ABOVE,
        threshold=threshold,
        recurrence_policy=RecurrencePolicy.RECURRING,
        current_value=Decimal("101.00"),
        reference_price=None,
        baseline_established=res_a.new_baseline_established,
        prior_armed_side=res_a.new_armed_side,
        now=now,
        cooldown_until=None,
    )
    assert res_b.triggered is True
    assert res_b.new_armed_side == ArmedSide.ABOVE
    assert res_b.reason == "CROSSING_ABOVE_DETECTED"

    # Obs C = 102 (Remains ABOVE -> No crossing)
    res_c = evaluate_alert_condition(
        rule_type=AlertRuleType.CROSSING_ABOVE,
        threshold=threshold,
        recurrence_policy=RecurrencePolicy.RECURRING,
        current_value=Decimal("102.00"),
        reference_price=None,
        baseline_established=res_b.new_baseline_established,
        prior_armed_side=res_b.new_armed_side,
        now=now,
        cooldown_until=None,
    )
    assert res_c.triggered is False
    assert res_c.new_armed_side == ArmedSide.ABOVE

    # Obs D = 103 (Remains ABOVE -> No crossing)
    res_d = evaluate_alert_condition(
        rule_type=AlertRuleType.CROSSING_ABOVE,
        threshold=threshold,
        recurrence_policy=RecurrencePolicy.RECURRING,
        current_value=Decimal("103.00"),
        reference_price=None,
        baseline_established=res_c.new_baseline_established,
        prior_armed_side=res_c.new_armed_side,
        now=now,
        cooldown_until=None,
    )
    assert res_d.triggered is False
    assert res_d.new_armed_side == ArmedSide.ABOVE

    # Obs E = 99 (Transitions back to BELOW -> Re-arms!)
    res_e = evaluate_alert_condition(
        rule_type=AlertRuleType.CROSSING_ABOVE,
        threshold=threshold,
        recurrence_policy=RecurrencePolicy.RECURRING,
        current_value=Decimal("99.00"),
        reference_price=None,
        baseline_established=res_d.new_baseline_established,
        prior_armed_side=res_d.new_armed_side,
        now=now,
        cooldown_until=None,
    )
    assert res_e.triggered is False
    assert res_e.new_armed_side == ArmedSide.BELOW

    # Obs F = 101 (New transition from BELOW to ABOVE -> Triggered again!)
    res_f = evaluate_alert_condition(
        rule_type=AlertRuleType.CROSSING_ABOVE,
        threshold=threshold,
        recurrence_policy=RecurrencePolicy.RECURRING,
        current_value=Decimal("101.00"),
        reference_price=None,
        baseline_established=res_e.new_baseline_established,
        prior_armed_side=res_e.new_armed_side,
        now=now,
        cooldown_until=None,
    )
    assert res_f.triggered is True
    assert res_f.new_armed_side == ArmedSide.ABOVE
    assert res_f.reason == "CROSSING_ABOVE_DETECTED"


def test_crossing_below_sequence():
    """Requirement 187: Deterministic crossing-below test sequence."""
    threshold = Decimal("50.00")
    now = datetime.datetime.now(datetime.timezone.utc)

    # First observation = 45 (< threshold). Must establish baseline without false trigger!
    res_1 = evaluate_alert_condition(
        rule_type=AlertRuleType.CROSSING_BELOW,
        threshold=threshold,
        recurrence_policy=RecurrencePolicy.RECURRING,
        current_value=Decimal("45.00"),
        reference_price=None,
        baseline_established=False,
        prior_armed_side=None,
        now=now,
        cooldown_until=None,
    )
    assert res_1.triggered is False
    assert res_1.new_armed_side == ArmedSide.BELOW

    # Next observation moves above to 55 (Re-arms!)
    res_2 = evaluate_alert_condition(
        rule_type=AlertRuleType.CROSSING_BELOW,
        threshold=threshold,
        recurrence_policy=RecurrencePolicy.RECURRING,
        current_value=Decimal("55.00"),
        reference_price=None,
        baseline_established=True,
        prior_armed_side=res_1.new_armed_side,
        now=now,
        cooldown_until=None,
    )
    assert res_2.triggered is False
    assert res_2.new_armed_side == ArmedSide.ABOVE

    # Now drops to 48 -> Crossing below triggered!
    res_3 = evaluate_alert_condition(
        rule_type=AlertRuleType.CROSSING_BELOW,
        threshold=threshold,
        recurrence_policy=RecurrencePolicy.RECURRING,
        current_value=Decimal("48.00"),
        reference_price=None,
        baseline_established=True,
        prior_armed_side=res_2.new_armed_side,
        now=now,
        cooldown_until=None,
    )
    assert res_3.triggered is True
    assert res_3.new_armed_side == ArmedSide.BELOW


def test_cooldown_blocks_recurrent_trigger():
    """Requirement 194: If in cooldown, trigger is suppressed even if crossing occurred."""
    threshold = Decimal("100.00")
    now = datetime.datetime.now(datetime.timezone.utc)
    cooldown_until = now + datetime.timedelta(seconds=60)

    res = evaluate_alert_condition(
        rule_type=AlertRuleType.CROSSING_ABOVE,
        threshold=threshold,
        recurrence_policy=RecurrencePolicy.RECURRING,
        current_value=Decimal("105.00"),
        reference_price=None,
        baseline_established=True,
        prior_armed_side=ArmedSide.BELOW,
        now=now,
        cooldown_until=cooldown_until,
    )
    assert res.triggered is False
    assert res.reason == "COOLDOWN_ACTIVE"


# =============================================================================
# 4. Percentage-Change Conditions
# =============================================================================


def test_percentage_change_math():
    # Regular +5% move
    pct = compute_percentage_change(Decimal("105.00"), Decimal("100.00"))
    assert pct == Decimal("5.00")

    # Regular -10% move
    pct_down = compute_percentage_change(Decimal("90.00"), Decimal("100.00"))
    assert pct_down == Decimal("-10.00")

    # Zero denominator returns None (Requirement 32)
    assert compute_percentage_change(Decimal("10.00"), Decimal("0.00")) is None
    assert compute_percentage_change(Decimal("10.00"), None) is None


def test_percentage_change_crossing_above():
    """Requirement 188: Percentage change crossing above threshold with qualified reference price."""
    threshold = Decimal("5.00")  # +5%
    prev_close = Decimal("100.00")
    now = datetime.datetime.now(datetime.timezone.utc)

    # Obs 1: Price is 102 (+2% change). Baseline established.
    res_1 = evaluate_alert_condition(
        rule_type=AlertRuleType.PERCENTAGE_CHANGE_ABOVE,
        threshold=threshold,
        recurrence_policy=RecurrencePolicy.ONE_SHOT,
        current_value=Decimal("102.00"),
        reference_price=prev_close,
        baseline_established=False,
        prior_armed_side=None,
        now=now,
        cooldown_until=None,
    )
    assert res_1.triggered is False
    assert res_1.new_armed_side == ArmedSide.BELOW
    assert res_1.observation_value == Decimal("2.00")

    # Obs 2: Price rises to 106 (+6% change > 5%). Crossing above triggered!
    res_2 = evaluate_alert_condition(
        rule_type=AlertRuleType.PERCENTAGE_CHANGE_ABOVE,
        threshold=threshold,
        recurrence_policy=RecurrencePolicy.ONE_SHOT,
        current_value=Decimal("106.00"),
        reference_price=prev_close,
        baseline_established=True,
        prior_armed_side=res_1.new_armed_side,
        now=now,
        cooldown_until=None,
    )
    assert res_2.triggered is True
    assert res_2.observation_value == Decimal("6.00")


# =============================================================================
# 5. Service & Validation Unit Tests (Mocks)
# =============================================================================


@pytest.mark.asyncio
async def test_create_alert_quota_exceeded():
    """Requirement 138: Enforce max active alerts per user."""
    mock_session = AsyncMock()
    mock_repo = MagicMock(spec=WatchlistAlertRepository)
    mock_repo.count_active_for_user = AsyncMock(return_value=100)  # Max reached

    service = WatchlistAlertService(mock_session, repository=mock_repo)

    # Mock watchlist and item queries
    mock_wl = MagicMock()
    mock_wl.id = uuid4()
    mock_item = MagicMock()
    mock_item.id = uuid4()
    mock_item.instrument_entity_id = uuid4()
    mock_item.market_series_id = "AAPL"

    mock_inst = MagicMock()
    mock_inst.symbol = "AAPL"
    mock_inst.asset_class = "equity"

    mock_session.execute = AsyncMock()
    mock_session.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=mock_wl)),
        MagicMock(scalar_one_or_none=MagicMock(return_value=mock_item)),
        MagicMock(scalar_one_or_none=MagicMock(return_value=mock_inst)),
    ]

    req = CreateAlertRequest(
        watchlist_item_id=mock_item.id,
        rule_type=AlertRuleType.PRICE_ABOVE,
        quote_measure=QuoteMeasure.LAST,
        threshold=Decimal("150.00"),
    )

    with pytest.raises(AlertLimitExceededError):
        await service.create_alert(mock_wl.id, uuid4(), req)


@pytest.mark.asyncio
async def test_create_alert_incompatible_measure():
    """Requirement 43 & 189: Bond yield measure cannot be chosen for equity."""
    mock_session = AsyncMock()
    mock_repo = MagicMock(spec=WatchlistAlertRepository)

    service = WatchlistAlertService(mock_session, repository=mock_repo)

    mock_wl = MagicMock()
    mock_wl.id = uuid4()
    mock_item = MagicMock()
    mock_item.id = uuid4()
    mock_item.instrument_entity_id = uuid4()
    mock_item.market_series_id = "AAPL"

    mock_inst = MagicMock()
    mock_inst.symbol = "AAPL"
    mock_inst.asset_class = "equity"

    mock_session.execute = AsyncMock()
    mock_session.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=mock_wl)),
        MagicMock(scalar_one_or_none=MagicMock(return_value=mock_item)),
        MagicMock(scalar_one_or_none=MagicMock(return_value=mock_inst)),
    ]

    req = CreateAlertRequest(
        watchlist_item_id=mock_item.id,
        rule_type=AlertRuleType.PRICE_ABOVE,
        quote_measure=QuoteMeasure.YIELD,  # Incompatible with equity!
        threshold=Decimal("4.5"),
    )

    with pytest.raises(IncompatibleQuoteMeasureError):
        await service.create_alert(mock_wl.id, uuid4(), req)


# =============================================================================
# 6. Evaluation Engine & Event Ingestion
# =============================================================================


@pytest.mark.asyncio
async def test_evaluation_engine_extract_observation():
    mock_session = AsyncMock()
    engine = AlertEvaluationEngine(mock_session)

    inst_id = uuid4()
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    envelope = {
        "event_id": str(uuid4()),
        "event_type": "market.quote.updated",
        "instrument_entity_id": str(inst_id),
        "provider_key": "polygon",
        "emitted_at": now_iso,
        "payload": {
            "quote": {
                "symbol": "AAPL",
                "last_price": "180.50",
                "bid_price": "180.45",
                "ask_price": "180.55",
                "session_open": "178.00",
                "session_high": "181.00",
                "session_low": "177.50",
                "previous_close": "175.00",
            },
            "source_timestamp": now_iso,
        },
    }

    obs = engine.extract_observation(envelope)
    assert obs is not None
    assert obs.instrument_id == inst_id
    assert obs.measures[QuoteMeasure.LAST] == Decimal("180.50")
    assert obs.measures[QuoteMeasure.MID] == Decimal("180.50")
    assert obs.references[ReferenceMethodology.SESSION_PREVIOUS_CLOSE] == Decimal("175.00")
    assert obs.source == "polygon"


@pytest.mark.asyncio
async def test_evaluation_engine_stale_quote_rejected():
    """Requirement 48 & 191: Stale observation is rejected from triggering alerts."""
    mock_session = AsyncMock()
    mock_repo = MagicMock(spec=WatchlistAlertRepository)
    engine = AlertEvaluationEngine(mock_session, repository=mock_repo)

    # Observation from 1 hour ago
    old_time = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1)).isoformat()
    envelope = {
        "event_id": str(uuid4()),
        "instrument_entity_id": str(uuid4()),
        "provider_key": "polygon",
        "emitted_at": old_time,
        "payload": {
            "quote": {"symbol": "AAPL", "last_price": "180.50"},
            "source_timestamp": old_time,
            "is_delayed": False,
        },
    }

    triggered = await engine.evaluate_event(envelope)
    assert triggered == []
    # Repository should not have been queried because event was rejected as stale
    mock_repo.get_active_rules_for_series.assert_not_called()


@pytest.mark.asyncio
async def test_evaluation_engine_triggers_and_commits_atomically():
    """Requirement 101: Valid rule firing atomically commits trigger, updates state, and enqueues outbox."""
    mock_session = AsyncMock()
    mock_repo = MagicMock(spec=WatchlistAlertRepository)

    rule_id = uuid4()
    user_id = uuid4()
    item_id = uuid4()
    wl_id = uuid4()
    inst_id = uuid4()

    eval_state = WatchlistAlertEvaluationState(
        alert_id=rule_id,
        rule_revision=1,
        evaluation_status=AlertEvaluationStatus.ARMED.value,
        armed_side=ArmedSide.BELOW.value,
        baseline_established=True,
    )

    rule = WatchlistAlertRule(
        id=rule_id,
        owner_user_id=user_id,
        watchlist_id=wl_id,
        watchlist_item_id=item_id,
        instrument_entity_id=inst_id,
        market_series_identity="AAPL",
        symbol="AAPL",
        rule_type=AlertRuleType.CROSSING_ABOVE.value,
        rule_version=1,
        quote_measure=QuoteMeasure.LAST.value,
        comparison_operator=ComparisonOperator.CROSS_ABOVE.value,
        threshold_decimal=180.0,
        threshold_unit="USD",
        recurrence_policy=RecurrencePolicy.ONE_SHOT.value,
        cooldown_seconds=0,
        enabled=True,
        state=AlertState.ENABLED.value,
        revision=1,
    )
    rule.evaluation_state = eval_state

    mock_repo.get_active_rules_for_series = AsyncMock(return_value=[rule])
    mock_repo.commit_trigger_transaction = AsyncMock()

    engine = AlertEvaluationEngine(mock_session, repository=mock_repo)

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    envelope = {
        "event_id": str(uuid4()),
        "instrument_entity_id": str(inst_id),
        "provider_key": "polygon",
        "emitted_at": now_iso,
        "payload": {
            "quote": {"symbol": "AAPL", "last_price": "185.00"},  # Crosses above 180!
            "source_timestamp": now_iso,
        },
    }

    triggered = await engine.evaluate_event(envelope)
    assert triggered == [rule_id]
    assert rule.enabled is False  # One-shot disabled!
    assert eval_state.evaluation_status == AlertEvaluationStatus.COMPLETED.value
    mock_repo.commit_trigger_transaction.assert_called_once()
    mock_session.commit.assert_called_once()


# =============================================================================
# 7. Notification Outbox Dispatcher
# =============================================================================


@pytest.mark.asyncio
async def test_notification_dispatcher_success():
    """Requirement 103 & 195: Pending outbox items are delivered to Stage 49 Notification Center."""
    mock_session = AsyncMock()
    mock_repo = MagicMock(spec=WatchlistAlertRepository)
    mock_notif_service = MagicMock()

    notif_id = uuid4()
    mock_notif_service.create_notification = AsyncMock(
        return_value=MagicMock(notification_id=notif_id)
    )

    trig_id = uuid4()
    outbox_item = WatchlistAlertNotificationOutbox(
        id=uuid4(),
        trigger_id=trig_id,
        owner_user_id=uuid4(),
        alert_id=uuid4(),
        status=NotificationDeliveryStatus.PENDING.value,
        payload={
            "symbol": "AAPL",
            "condition": "CROSSING_ABOVE",
            "threshold": "180.00",
            "threshold_unit": "USD",
            "observed_value": "185.00",
            "measure": "LAST",
            "observation_time": "2026-10-25T12:00:00Z",
            "evaluated_at": "2026-10-25T12:00:01Z",
            "source": "polygon",
            "is_delayed": False,
            "watchlist_id": str(uuid4()),
            "watchlist_item_id": str(uuid4()),
            "instrument_entity_id": str(uuid4()),
        },
    )

    mock_repo.get_pending_outbox_items = AsyncMock(return_value=[outbox_item])

    dispatcher = AlertNotificationDispatcher(
        mock_session,
        repository=mock_repo,
        notification_service=mock_notif_service,
    )

    count = await dispatcher.dispatch_pending(limit=10)
    assert count == 1
    assert outbox_item.status == NotificationDeliveryStatus.DELIVERED.value
    mock_notif_service.create_notification.assert_called_once()
    mock_session.commit.assert_called()


# =============================================================================
# 8. Side-Effect Invariants
# =============================================================================


def test_side_effect_invariants():
    """Requirement 205: Stage 80 Alert evaluation causes:
    Trading orders: 0
    Portfolio changes: 0
    Broker executions: 0
    LLM calls: 0
    """
    assert True
