import pytest
import uuid
import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from atlas.entities.models import Entity, EntityType
from atlas.relationships.models import EntityRelationship
from atlas.relationships.schemas import EntityRelationshipCreate
from atlas.relationships.service import RelationshipService

@pytest.fixture
async def setup_entities(db_session: AsyncSession):
    company_1 = Entity(entity_id=uuid.uuid4(), entity_type=EntityType.COMPANY, created_by="test")
    company_2 = Entity(entity_id=uuid.uuid4(), entity_type=EntityType.COMPANY, created_by="test")
    security_1 = Entity(entity_id=uuid.uuid4(), entity_type=EntityType.SECURITY, created_by="test")
    
    db_session.add_all([company_1, company_2, security_1])
    await db_session.flush()
    return {"c1": company_1, "c2": company_2, "s1": security_1}


@pytest.mark.asyncio
async def test_relationship_canonicalization(db_session: AsyncSession, setup_entities):
    c1 = setup_entities["c1"]
    s1 = setup_entities["s1"]

    service = RelationshipService(db_session)
    
    # Test inverse canonicalization
    # "issued_by" canonical is "issued"
    data = EntityRelationshipCreate(
        target_entity_id=c1.entity_id,
        relationship_type_key="issued_by"
    )
    
    rel = await service.create_relationship(s1.entity_id, data)
    assert rel.relationship_type_key == "issued"
    assert rel.source_entity_id == c1.entity_id
    assert rel.target_entity_id == s1.entity_id

    # Test symmetric canonicalization
    c2 = setup_entities["c2"]
    
    # ensure source_id < target_id
    min_c = min(c1.entity_id, c2.entity_id)
    max_c = max(c1.entity_id, c2.entity_id)

    data_sym = EntityRelationshipCreate(
        target_entity_id=c1.entity_id,
        relationship_type_key="competitor_of"
    )
    rel_sym = await service.create_relationship(c2.entity_id, data_sym)
    
    assert rel_sym.relationship_type_key == "competitor_of"
    assert rel_sym.source_entity_id == min_c
    assert rel_sym.target_entity_id == max_c
