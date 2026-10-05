from atlas.capabilities.registry import CapabilityRegistry, CapabilityDefinition
from atlas.capabilities.types import CapabilityPermissionClass, CapabilityExposure

# Entities
from .entities import (
    EntityGetInput, EntityOutput, entity_get_factory,
    EntityTypeListInput, EntityTypeListOutput, entity_type_list_factory
)

# Resolution
from .resolution import (
    EntityResolutionRequest, EntityResolutionResponse, entity_resolve_factory
)

# Identifiers
from .identifiers import (
    IdentifierSchemeListInput, IdentifierSchemeListOutput, identifier_scheme_list_factory,
    EntityIdentifiersListInput, EntityIdentifiersListOutput, entity_identifiers_list_factory
)

# Aliases
from .aliases import (
    AliasTypeListInput, AliasTypeListOutput, alias_type_list_factory,
    EntityAliasesListInput, EntityAliasesListOutput, entity_aliases_list_factory
)

# Relationships
from .relationships import (
    RelationshipTypeListInput, RelationshipTypeListOutput, relationship_type_list_factory,
    EntityRelationshipsListInput, EntityRelationshipsListOutput, entity_relationships_list_factory
)

# Provenance
from .provenance import (
    ProvenanceSourceListInput, ProvenanceSourceListResponse, provenance_source_list_factory,
    EntityProvenanceListInput, TargetProvenanceListResponse, entity_provenance_list_factory,
    IdentifierProvenanceListInput, identifier_provenance_list_factory,
    AliasProvenanceListInput, alias_provenance_list_factory,
    RelationshipProvenanceListInput, relationship_provenance_list_factory
)

# Providers
from atlas.providers.catalog import register_provider_capabilities
from atlas.providers.bootstrap import build_provider_registry

def register_all_handlers(registry: CapabilityRegistry):
    # --- entities ---
    registry.register(
        CapabilityDefinition(
            key="entity.get",
            version=1,
            title="Get Entity",
            description="Retrieve an entity by ID",
            category="Entities",
            permission_class=CapabilityPermissionClass.READ,
            required_permissions=["atlas.access"],
            exposure=CapabilityExposure.APPLICATION,
            requires_confirmation=False,
            input_model=EntityGetInput,
            output_model=EntityOutput
        ),
        entity_get_factory
    )
    registry.register(
        CapabilityDefinition(
            key="entity.type.list",
            version=1,
            title="List Entity Types",
            description="List supported entity types",
            category="Entities",
            permission_class=CapabilityPermissionClass.READ,
            required_permissions=["atlas.access"],
            exposure=CapabilityExposure.APPLICATION,
            requires_confirmation=False,
            input_model=EntityTypeListInput,
            output_model=EntityTypeListOutput
        ),
        entity_type_list_factory
    )

    # --- resolution ---
    registry.register(
        CapabilityDefinition(
            key="entity.resolve",
            version=1,
            title="Resolve Entity",
            description="Resolve a string query to an entity",
            category="Resolution",
            permission_class=CapabilityPermissionClass.READ,
            required_permissions=["atlas.access"],
            exposure=CapabilityExposure.APPLICATION,
            requires_confirmation=False,
            input_model=EntityResolutionRequest,
            output_model=EntityResolutionResponse
        ),
        entity_resolve_factory
    )

    # --- identifiers ---
    registry.register(
        CapabilityDefinition(
            key="identifier.scheme.list",
            version=1,
            title="List Identifier Schemes",
            description="List identifier schemes",
            category="Identifiers",
            permission_class=CapabilityPermissionClass.READ,
            required_permissions=["atlas.access"],
            exposure=CapabilityExposure.APPLICATION,
            requires_confirmation=False,
            input_model=IdentifierSchemeListInput,
            output_model=IdentifierSchemeListOutput
        ),
        identifier_scheme_list_factory
    )
    registry.register(
        CapabilityDefinition(
            key="entity.identifiers.list",
            version=1,
            title="List Entity Identifiers",
            description="List identifiers for an entity",
            category="Identifiers",
            permission_class=CapabilityPermissionClass.READ,
            required_permissions=["atlas.access"],
            exposure=CapabilityExposure.APPLICATION,
            requires_confirmation=False,
            input_model=EntityIdentifiersListInput,
            output_model=EntityIdentifiersListOutput
        ),
        entity_identifiers_list_factory
    )

    # --- aliases ---
    registry.register(
        CapabilityDefinition(
            key="alias.type.list",
            version=1,
            title="List Alias Types",
            description="List alias types",
            category="Aliases",
            permission_class=CapabilityPermissionClass.READ,
            required_permissions=["atlas.access"],
            exposure=CapabilityExposure.APPLICATION,
            requires_confirmation=False,
            input_model=AliasTypeListInput,
            output_model=AliasTypeListOutput
        ),
        alias_type_list_factory
    )
    registry.register(
        CapabilityDefinition(
            key="entity.aliases.list",
            version=1,
            title="List Entity Aliases",
            description="List aliases for an entity",
            category="Aliases",
            permission_class=CapabilityPermissionClass.READ,
            required_permissions=["atlas.access"],
            exposure=CapabilityExposure.APPLICATION,
            requires_confirmation=False,
            input_model=EntityAliasesListInput,
            output_model=EntityAliasesListOutput
        ),
        entity_aliases_list_factory
    )

    # --- relationships ---
    registry.register(
        CapabilityDefinition(
            key="relationship.type.list",
            version=1,
            title="List Relationship Types",
            description="List relationship types",
            category="Relationships",
            permission_class=CapabilityPermissionClass.READ,
            required_permissions=["atlas.access"],
            exposure=CapabilityExposure.APPLICATION,
            requires_confirmation=False,
            input_model=RelationshipTypeListInput,
            output_model=RelationshipTypeListOutput
        ),
        relationship_type_list_factory
    )
    registry.register(
        CapabilityDefinition(
            key="entity.relationships.list",
            version=1,
            title="List Entity Relationships",
            description="List relationships for an entity",
            category="Relationships",
            permission_class=CapabilityPermissionClass.READ,
            required_permissions=["atlas.access"],
            exposure=CapabilityExposure.APPLICATION,
            requires_confirmation=False,
            input_model=EntityRelationshipsListInput,
            output_model=EntityRelationshipsListOutput
        ),
        entity_relationships_list_factory
    )

    # --- provenance ---
    registry.register(
        CapabilityDefinition(
            key="provenance.source.list",
            version=1,
            title="List Provenance Sources",
            description="List provenance sources",
            category="Provenance",
            permission_class=CapabilityPermissionClass.READ,
            required_permissions=["atlas.access"],
            exposure=CapabilityExposure.APPLICATION,
            requires_confirmation=False,
            input_model=ProvenanceSourceListInput,
            output_model=ProvenanceSourceListResponse
        ),
        provenance_source_list_factory
    )
    registry.register(
        CapabilityDefinition(
            key="entity.provenance.list",
            version=1,
            title="List Entity Provenance",
            description="List provenance for an entity",
            category="Provenance",
            permission_class=CapabilityPermissionClass.READ,
            required_permissions=["atlas.access"],
            exposure=CapabilityExposure.APPLICATION,
            requires_confirmation=False,
            input_model=EntityProvenanceListInput,
            output_model=TargetProvenanceListResponse
        ),
        entity_provenance_list_factory
    )
    registry.register(
        CapabilityDefinition(
            key="identifier.provenance.list",
            version=1,
            title="List Identifier Provenance",
            description="List provenance for an identifier",
            category="Provenance",
            permission_class=CapabilityPermissionClass.READ,
            required_permissions=["atlas.access"],
            exposure=CapabilityExposure.APPLICATION,
            requires_confirmation=False,
            input_model=IdentifierProvenanceListInput,
            output_model=TargetProvenanceListResponse
        ),
        identifier_provenance_list_factory
    )
    registry.register(
        CapabilityDefinition(
            key="alias.provenance.list",
            version=1,
            title="List Alias Provenance",
            description="List provenance for an alias",
            category="Provenance",
            permission_class=CapabilityPermissionClass.READ,
            required_permissions=["atlas.access"],
            exposure=CapabilityExposure.APPLICATION,
            requires_confirmation=False,
            input_model=AliasProvenanceListInput,
            output_model=TargetProvenanceListResponse
        ),
        alias_provenance_list_factory
    )
    registry.register(
        CapabilityDefinition(
            key="relationship.provenance.list",
            version=1,
            title="List Relationship Provenance",
            description="List provenance for a relationship",
            category="Provenance",
            permission_class=CapabilityPermissionClass.READ,
            required_permissions=["atlas.access"],
            exposure=CapabilityExposure.APPLICATION,
            requires_confirmation=False,
            input_model=RelationshipProvenanceListInput,
            output_model=TargetProvenanceListResponse
        ),
        relationship_provenance_list_factory
    )

    # --- providers ---
    # Register provider capabilities (list, get)
    provider_registry = build_provider_registry()
    register_provider_capabilities(registry, provider_registry)
