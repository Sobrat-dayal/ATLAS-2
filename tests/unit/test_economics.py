import datetime
import uuid
import pytest
from pydantic import ValidationError

from atlas.economics.numeric import CanonicalDecimal
from atlas.economics.enums import (
    EconomicObservationAvailability,
    EconomicRevisionStatus,
    EconomicRevisionPolicy,
    EconomicDataOperation,
)
from atlas.economics.periods import EconomicObservationPeriod
from atlas.economics.origin import EconomicDataOrigin
from atlas.economics.observations import EconomicObservation, LatestEconomicObservationItem
from atlas.economics.requests import EconomicObservationsRequest, LatestEconomicObservationsRequest, EconomicRevisionSelection
from atlas.economics.responses import EconomicObservationsResponse, LatestEconomicObservationsResponse
from atlas.economics.capabilities import EconomicProviderCapabilities


def test_canonical_decimal():
    # 208. DECIMAL PRECISION TEST
    val = CanonicalDecimal("325.421")
    assert str(val) == "325.421"
    
    # 209. LARGE ECONOMIC VALUE TEST
    large_val = CanonicalDecimal("29167800000000.1234")
    assert str(large_val) == "29167800000000.1234"
    
    # 210. SMALL RATE TEST
    small_val = CanonicalDecimal("0.0001")
    assert str(small_val) == "0.0001"
    
    # 211. ZERO OBSERVATION TEST
    zero_val = CanonicalDecimal("0")
    assert str(zero_val) == "0"
    
    # 212. NEGATIVE OBSERVATION TEST
    neg_val = CanonicalDecimal("-2.5")
    assert str(neg_val) == "-2.5"
    
    # 213. NAN TEST
    with pytest.raises(ValidationError):
        CanonicalDecimal("NaN")
        
    # 214. INFINITY TEST
    with pytest.raises(ValidationError):
        CanonicalDecimal("Infinity")
        
    # 215. FLOAT INPUT TEST
    with pytest.raises(ValidationError):
        # Depending on base CanonicalDecimal, float might be rejected or converted, usually strictly string for precision
        class Dummy(BaseModel):
            val: CanonicalDecimal
        Dummy(val=2.5)


def test_economic_observation_period():
    # 216. OBSERVATION PERIOD REFERENCE DATE TEST
    period = EconomicObservationPeriod(reference_date=datetime.date(2026, 8, 1))
    assert period.reference_date == datetime.date(2026, 8, 1)
    
    # 217. PERIOD BOUNDARY BOTH-OR-NONE TEST
    with pytest.raises(ValidationError, match="both be present or both be absent"):
        EconomicObservationPeriod(
            reference_date=datetime.date(2026, 8, 1),
            period_start=datetime.date(2026, 8, 1)
        )
        
    # 218. PERIOD INVALID RANGE TEST
    with pytest.raises(ValidationError, match="period_start cannot be after period_end"):
        EconomicObservationPeriod(
            reference_date=datetime.date(2026, 8, 1),
            period_start=datetime.date(2026, 8, 31),
            period_end=datetime.date(2026, 8, 1)
        )
        
    # 219. NO PERIOD BOUNDARY TEST
    period2 = EconomicObservationPeriod(reference_date=datetime.date(2026, 8, 1))
    assert period2.period_start is None
    assert period2.period_end is None


def test_economic_observation_availability():
    # 220. AVAILABILITY AVAILABLE TEST
    # 221. AVAILABILITY MISSING TEST
    # Tested within EconomicObservation
    pass


def test_economic_observation():
    series_id = uuid.uuid4()
    period = EconomicObservationPeriod(reference_date=datetime.date(2026, 8, 1))
    
    # 220. AVAILABLE TEST
    obs_avail = EconomicObservation(
        economic_series_id=series_id,
        period=period,
        availability=EconomicObservationAvailability.AVAILABLE,
        value=CanonicalDecimal("4.7")
    )
    assert obs_avail.value == CanonicalDecimal("4.7")
    
    # 221. MISSING TEST
    obs_missing = EconomicObservation(
        economic_series_id=series_id,
        period=period,
        availability=EconomicObservationAvailability.MISSING,
        value=None
    )
    assert obs_missing.value is None
    
    # 222. MISSING WITH ZERO TEST
    with pytest.raises(ValidationError, match="value must be None when availability is MISSING"):
        EconomicObservation(
            economic_series_id=series_id,
            period=period,
            availability=EconomicObservationAvailability.MISSING,
            value=CanonicalDecimal("0")
        )
        
    # 223. AVAILABLE WITHOUT VALUE TEST
    with pytest.raises(ValidationError, match="value cannot be None when availability is AVAILABLE"):
        EconomicObservation(
            economic_series_id=series_id,
            period=period,
            availability=EconomicObservationAvailability.AVAILABLE,
            value=None
        )
        
    # 225. DO NOT ASSUME FINAL TEST
    assert obs_avail.revision_status == EconomicRevisionStatus.UNKNOWN
    
    # 229, 230, 231. RELEASED_AT TEST
    tz_aware = datetime.datetime(2026, 8, 1, 10, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=2)))
    obs_release = EconomicObservation(
        economic_series_id=series_id,
        period=period,
        availability=EconomicObservationAvailability.AVAILABLE,
        value=CanonicalDecimal("4.7"),
        released_at=tz_aware
    )
    assert obs_release.released_at.tzinfo == datetime.timezone.utc
    
    with pytest.raises(ValidationError, match="timezone-aware"):
        EconomicObservation(
            economic_series_id=series_id,
            period=period,
            availability=EconomicObservationAvailability.AVAILABLE,
            value=CanonicalDecimal("4.7"),
            released_at=datetime.datetime(2026, 8, 1, 10, 0) # naive
        )


def test_economic_revision_selection():
    # 227. AS-OF DATE REQUIRED TEST
    with pytest.raises(ValidationError, match="as_of_date is required"):
        EconomicRevisionSelection(policy=EconomicRevisionPolicy.AS_OF)
        
    # 228. AS-OF DATE WITH LATEST TEST
    with pytest.raises(ValidationError, match="as_of_date must be None"):
        EconomicRevisionSelection(
            policy=EconomicRevisionPolicy.LATEST_AVAILABLE,
            as_of_date=datetime.date(2026, 8, 1)
        )


def test_economic_data_origin():
    # 232. RETRIEVED_AT TEST
    with pytest.raises(ValidationError, match="timezone-aware"):
        EconomicDataOrigin(
            provider_key="openbb",
            upstream_source="fred",
            retrieved_at=datetime.datetime.now() # naive
        )


def test_economic_observations_request():
    series_id = uuid.uuid4()
    
    # 244. DATE RANGE TEST
    with pytest.raises(ValidationError, match="start_date cannot be after end_date"):
        EconomicObservationsRequest(
            economic_series_id=series_id,
            start_date=datetime.date(2026, 8, 31),
            end_date=datetime.date(2026, 8, 1)
        )
        
    # 245. REQUEST LIMIT TEST
    with pytest.raises(ValidationError, match="limit must be between 1 and 10000"):
        EconomicObservationsRequest(economic_series_id=series_id, limit=0)
        
    # 246. UNBOUNDED REQUEST TEST
    with pytest.raises(ValidationError, match="requires at least a date range or limit"):
        EconomicObservationsRequest(economic_series_id=series_id)
        
    # Valid bounded request
    req = EconomicObservationsRequest(economic_series_id=series_id, limit=100)
    assert req.limit == 100


def test_latest_economic_observations_request():
    id1 = uuid.uuid4()
    id2 = uuid.uuid4()
    
    # 248. LATEST EMPTY BATCH TEST
    with pytest.raises(ValidationError, match="Batch must not be empty"):
        LatestEconomicObservationsRequest(economic_series_ids=tuple())
        
    # 249. LATEST DUPLICATE ID TEST
    with pytest.raises(ValidationError, match="Duplicate economic_series_ids are not allowed"):
        LatestEconomicObservationsRequest(economic_series_ids=(id1, id1))
        
    # 250. LATEST BATCH MAX TEST
    ids = tuple(uuid.uuid4() for _ in range(101))
    with pytest.raises(ValidationError, match="Batch limit is 100 series"):
        LatestEconomicObservationsRequest(economic_series_ids=ids)


def test_economic_observations_response():
    series_id = uuid.uuid4()
    origin = EconomicDataOrigin(
        provider_key="test",
        upstream_source="test",
        retrieved_at=datetime.datetime.now(datetime.timezone.utc)
    )
    
    period1 = EconomicObservationPeriod(reference_date=datetime.date(2026, 8, 1))
    period2 = EconomicObservationPeriod(reference_date=datetime.date(2026, 9, 1))
    
    obs1 = EconomicObservation(
        economic_series_id=series_id,
        period=period1,
        availability=EconomicObservationAvailability.AVAILABLE,
        value=CanonicalDecimal("1.1")
    )
    obs2 = EconomicObservation(
        economic_series_id=series_id,
        period=period2,
        availability=EconomicObservationAvailability.AVAILABLE,
        value=CanonicalDecimal("1.2")
    )
    
    # 251. SERIES CONSISTENCY TEST
    obs_wrong = EconomicObservation(
        economic_series_id=uuid.uuid4(),
        period=period1,
        availability=EconomicObservationAvailability.AVAILABLE,
        value=CanonicalDecimal("1.1")
    )
    with pytest.raises(ValidationError, match="Observation series ID does not match"):
        EconomicObservationsResponse(
            economic_series_id=series_id,
            origin=origin,
            revision_policy=EconomicRevisionPolicy.LATEST_AVAILABLE,
            observations=(obs_wrong,)
        )
        
    # 253. UNSORTED RESPONSE TEST
    with pytest.raises(ValidationError, match="ordered by reference_date ascending"):
        EconomicObservationsResponse(
            economic_series_id=series_id,
            origin=origin,
            revision_policy=EconomicRevisionPolicy.LATEST_AVAILABLE,
            observations=(obs2, obs1)
        )
        
    # 254. LATEST AVAILABLE DUPLICATE PERIOD TEST
    obs1_dup = EconomicObservation(
        economic_series_id=series_id,
        period=period1,
        availability=EconomicObservationAvailability.AVAILABLE,
        value=CanonicalDecimal("1.15"),
        vintage_date=datetime.date(2026, 8, 15)
    )
    with pytest.raises(ValidationError, match="Multiple observations for same reference date not allowed"):
        EconomicObservationsResponse(
            economic_series_id=series_id,
            origin=origin,
            revision_policy=EconomicRevisionPolicy.LATEST_AVAILABLE,
            observations=(obs1, obs1_dup)
        )
        
    # 256. ALL-VINTAGES SAME-PERIOD TEST
    obs1_vintage = EconomicObservation(
        economic_series_id=series_id,
        period=period1,
        availability=EconomicObservationAvailability.AVAILABLE,
        value=CanonicalDecimal("1.1"),
        vintage_date=datetime.date(2026, 8, 5)
    )
    EconomicObservationsResponse(
        economic_series_id=series_id,
        origin=origin,
        revision_policy=EconomicRevisionPolicy.ALL_VINTAGES,
        observations=(obs1_vintage, obs1_dup)
    )
    
    # 258. VINTAGE ORDER TEST
    with pytest.raises(ValidationError, match="ordered by vintage_date ascending"):
        EconomicObservationsResponse(
            economic_series_id=series_id,
            origin=origin,
            revision_policy=EconomicRevisionPolicy.ALL_VINTAGES,
            observations=(obs1_dup, obs1_vintage)
        )
    
    # 257. EXACT DUPLICATE VINTAGE TEST
    with pytest.raises(ValidationError, match="Exact duplicate observations"):
        EconomicObservationsResponse(
            economic_series_id=series_id,
            origin=origin,
            revision_policy=EconomicRevisionPolicy.ALL_VINTAGES,
            observations=(obs1, obs1)
        )


def test_latest_economic_observation_item():
    series_id = uuid.uuid4()
    # 260. LATEST ITEM ID CONSISTENCY TEST
    obs_wrong = EconomicObservation(
        economic_series_id=uuid.uuid4(),
        period=EconomicObservationPeriod(reference_date=datetime.date(2026, 8, 1)),
        availability=EconomicObservationAvailability.AVAILABLE,
        value=CanonicalDecimal("1.0")
    )
    with pytest.raises(ValidationError, match="Observation economic_series_id must match"):
        LatestEconomicObservationItem(
            economic_series_id=series_id,
            observation=obs_wrong
        )
        
    # 261. LATEST NONE TEST
    item = LatestEconomicObservationItem(economic_series_id=series_id, observation=None)
    assert item.observation is None


def test_economic_provider_capabilities():
    # 264. IMMUTABLE OPERATION SET
    # 265. IMMUTABLE REVISION-POLICY SET
    cap = EconomicProviderCapabilities(
        operations=frozenset([EconomicDataOperation.OBSERVATIONS]),
        revision_policies=frozenset([EconomicRevisionPolicy.LATEST_AVAILABLE])
    )
    assert EconomicDataOperation.OBSERVATIONS in cap.operations
    assert EconomicRevisionPolicy.LATEST_AVAILABLE in cap.revision_policies
