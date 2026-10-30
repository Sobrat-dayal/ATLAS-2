"""Service Orchestrator for Stage 119 - Universal Saved System and Cross-Module Library."""

from __future__ import annotations

import logging
import math
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from atlas.saved.configurations import (
    migrate_configuration,
    validate_and_sanitize_configuration_payload,
)
from atlas.saved.enums import (
    SavedBulkActionType,
    SavedModule,
    SavedReferenceSemantics,
    SavedSortOption,
    SavedTargetType,
)
from atlas.saved.errors import (
    SavedConfigurationInvalidError,
    SavedError,
    SavedItemAccessDeniedError,
    SavedItemNotFoundError,
    SavedTargetAccessDeniedError,
)
from atlas.saved.models import (
    ResolvedTarget,
    SavedCollection,
    SavedItem,
    SavedViewConfiguration,
)
from atlas.saved.repository import SavedRepository
from atlas.saved.resolvers import TargetResolver
from atlas.saved.schemas import (
    BulkActionItemResultDTO,
    CreateSavedCollectionRequest,
    CreateSavedConfigurationRequest,
    CreateSavedItemRequest,
    CreateSavedTagRequest,
    ResolvedTargetDTO,
    ResolveTargetRequest,
    SavedBulkActionRequest,
    SavedBulkActionResponseDTO,
    SavedCollectionDTO,
    SavedCollectionTreeDTO,
    SavedItemDTO,
    SavedItemListResponseDTO,
    SavedLibrarySummaryDTO,
    SavedTagDTO,
    SavedViewConfigurationDTO,
    UpdateSavedCollectionRequest,
    UpdateSavedItemRequest,
    ValidateConfigurationRequest,
    ValidateConfigurationResponse,
)

logger = logging.getLogger(__name__)


class SavedService:
    """Primary application service for the Universal Saved library."""

    def __init__(self, repository: Optional[SavedRepository] = None) -> None:
        self.repository = repository or SavedRepository()

    # -------------------------------------------------------------------------
    # Saved Items
    # -------------------------------------------------------------------------

    def save_item(
        self,
        user_id: str,
        request: CreateSavedItemRequest,
        organization_id: Optional[str] = None,
        user_entitlements: Optional[List[str]] = None,
    ) -> SavedItemDTO:
        # 1. Resolve target resource
        resolved = TargetResolver.resolve_target(
            user_id=user_id,
            target_type=request.target_type,
            target_id=request.target_id,
            requested_revision_id=request.target_revision_id,
            organization_id=organization_id,
            user_entitlements=user_entitlements,
        )

        if not resolved.authorized:
            raise SavedTargetAccessDeniedError(request.target_type.value, request.target_id)

        # 2. View configuration validation if supplied
        if request.view_configuration_id:
            config = self.repository.get_configuration(request.view_configuration_id)
            if not config or config.owner_user_id != user_id:
                raise SavedConfigurationInvalidError(
                    f"View configuration '{request.view_configuration_id}' not found."
                )

        # 3. Create domain model
        item_id = str(uuid.uuid4())
        item = SavedItem(
            saved_item_id=item_id,
            owner_user_id=user_id,
            organization_id=organization_id,
            target_type=request.target_type,
            target_id=request.target_id.strip(),
            target_revision_id=request.target_revision_id,
            target_module=resolved.target_module,
            canonical_title=resolved.canonical_title,
            display_title_override=request.display_title_override,
            user_note=request.user_note,
            favorite=request.favorite,
            pinned=request.pinned,
            view_configuration_id=request.view_configuration_id,
            semantics=SavedReferenceSemantics.USER_OWNED_VIEW_CONFIGURATION
            if request.view_configuration_id
            else SavedReferenceSemantics.LIVE_REFERENCE,
        )

        persisted = self.repository.save_item(item, idempotency_key=request.idempotency_key)

        # 4. Associate collections
        for cid in request.collection_ids:
            try:
                self.repository.add_item_to_collection(cid, persisted.saved_item_id, user_id)
            except Exception as e:
                logger.warning(
                    f"Could not assign collection {cid} to saved item {persisted.saved_item_id}: {e}"
                )

        # 5. Associate tags
        for tag_name in request.tags:
            if tag_name.strip():
                try:
                    self.repository.assign_tag_to_item(
                        persisted.saved_item_id, tag_name.strip(), user_id
                    )
                except Exception as e:
                    logger.warning(
                        f"Could not assign tag {tag_name} to item {persisted.saved_item_id}: {e}"
                    )

        return self._to_item_dto(persisted, resolved)

    def get_item(
        self,
        saved_item_id: str,
        user_id: str,
        user_entitlements: Optional[List[str]] = None,
    ) -> SavedItemDTO:
        item = self.repository.get_item(saved_item_id)
        if not item or item.is_deleted:
            raise SavedItemNotFoundError(saved_item_id)
        if item.owner_user_id != user_id:
            raise SavedItemAccessDeniedError(saved_item_id, user_id)

        resolved = TargetResolver.resolve_target(
            user_id=user_id,
            target_type=item.target_type,
            target_id=item.target_id,
            requested_revision_id=item.target_revision_id,
            organization_id=item.organization_id,
            user_entitlements=user_entitlements,
        )
        return self._to_item_dto(item, resolved)

    def update_item(
        self,
        saved_item_id: str,
        user_id: str,
        request: UpdateSavedItemRequest,
        user_entitlements: Optional[List[str]] = None,
    ) -> SavedItemDTO:
        updated = self.repository.update_item(
            saved_item_id=saved_item_id,
            user_id=user_id,
            display_title_override=request.display_title_override,
            user_note=request.user_note,
            favorite=request.favorite,
            pinned=request.pinned,
            target_revision_id=request.target_revision_id,
            expected_row_version=request.expected_row_version,
        )
        resolved = TargetResolver.resolve_target(
            user_id=user_id,
            target_type=updated.target_type,
            target_id=updated.target_id,
            requested_revision_id=updated.target_revision_id,
            organization_id=updated.organization_id,
            user_entitlements=user_entitlements,
        )
        return self._to_item_dto(updated, resolved)

    def soft_delete_item(self, saved_item_id: str, user_id: str) -> None:
        self.repository.soft_delete_item(saved_item_id, user_id)

    def restore_item(
        self,
        saved_item_id: str,
        user_id: str,
        user_entitlements: Optional[List[str]] = None,
    ) -> SavedItemDTO:
        restored = self.repository.restore_item(saved_item_id, user_id)
        resolved = TargetResolver.resolve_target(
            user_id=user_id,
            target_type=restored.target_type,
            target_id=restored.target_id,
            requested_revision_id=restored.target_revision_id,
            organization_id=restored.organization_id,
            user_entitlements=user_entitlements,
        )
        return self._to_item_dto(restored, resolved)

    def toggle_favorite(self, saved_item_id: str, user_id: str, favorite: bool) -> SavedItemDTO:
        item = self.repository.update_item(
            saved_item_id=saved_item_id, user_id=user_id, favorite=favorite
        )
        resolved = TargetResolver.resolve_target(
            user_id=user_id, target_type=item.target_type, target_id=item.target_id
        )
        return self._to_item_dto(item, resolved)

    def toggle_pin(self, saved_item_id: str, user_id: str, pinned: bool) -> SavedItemDTO:
        item = self.repository.update_item(
            saved_item_id=saved_item_id, user_id=user_id, pinned=pinned
        )
        resolved = TargetResolver.resolve_target(
            user_id=user_id, target_type=item.target_type, target_id=item.target_id
        )
        return self._to_item_dto(item, resolved)

    def list_items(
        self,
        user_id: str,
        search: Optional[str] = None,
        target_type: Optional[SavedTargetType] = None,
        target_module: Optional[SavedModule] = None,
        collection_id: Optional[str] = None,
        tag_name: Optional[str] = None,
        tag: Optional[str] = None,
        favorite: Optional[bool] = None,
        pinned: Optional[bool] = None,
        sort_by: SavedSortOption = SavedSortOption.RECENTLY_SAVED,
        page: int = 1,
        page_size: int = 50,
        user_entitlements: Optional[List[str]] = None,
    ) -> SavedItemListResponseDTO:
        effective_tag = tag_name or tag
        items, total_count = self.repository.list_items(
            user_id=user_id,
            search=search,
            target_type=target_type,
            target_module=target_module,
            collection_id=collection_id,
            tag_name=effective_tag,
            favorite=favorite,
            pinned=pinned,
            sort_by=sort_by,
            page=page,
            page_size=page_size,
        )

        dtos = []
        for item in items:
            resolved = TargetResolver.resolve_target(
                user_id=user_id,
                target_type=item.target_type,
                target_id=item.target_id,
                requested_revision_id=item.target_revision_id,
                organization_id=item.organization_id,
                user_entitlements=user_entitlements,
            )
            dtos.append(self._to_item_dto(item, resolved))

        total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1
        return SavedItemListResponseDTO(
            items=dtos,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def resolve_target(
        self,
        user_id: str,
        request: ResolveTargetRequest,
        organization_id: Optional[str] = None,
        user_entitlements: Optional[List[str]] = None,
    ) -> ResolvedTargetDTO:
        res = TargetResolver.resolve_target(
            user_id=user_id,
            target_type=request.target_type,
            target_id=request.target_id,
            requested_revision_id=request.requested_revision_id,
            organization_id=organization_id,
            user_entitlements=user_entitlements,
        )
        return ResolvedTargetDTO(
            target_type=res.target_type,
            target_id=res.target_id,
            exists=res.exists,
            authorized=res.authorized,
            entitled=res.entitled,
            status=res.status,
            canonical_title=res.canonical_title,
            target_module=res.target_module,
            safe_deep_link=res.safe_deep_link,
            target_revision_id=res.target_revision_id,
            latest_revision_id=res.latest_revision_id,
            warnings=res.warnings,
        )

    # -------------------------------------------------------------------------
    # Collections
    # -------------------------------------------------------------------------

    def create_collection(
        self,
        user_id: str,
        request: CreateSavedCollectionRequest,
        organization_id: Optional[str] = None,
    ) -> SavedCollectionDTO:
        col = self.repository.create_collection(
            owner_user_id=user_id,
            name=request.name,
            description=request.description,
            parent_collection_id=request.parent_collection_id,
            sort_order=request.sort_order,
            organization_id=organization_id,
        )
        return self._to_collection_dto(col)

    def update_collection(
        self,
        collection_id: str,
        user_id: str,
        request: UpdateSavedCollectionRequest,
    ) -> SavedCollectionDTO:
        updated = self.repository.update_collection(
            collection_id=collection_id,
            user_id=user_id,
            name=request.name,
            description=request.description,
            parent_collection_id=request.parent_collection_id,
            sort_order=request.sort_order,
            expected_row_version=request.expected_row_version,
        )
        return self._to_collection_dto(updated)

    def delete_collection(self, collection_id: str, user_id: str) -> None:
        self.repository.delete_collection(collection_id, user_id)

    def list_collections(self, user_id: str) -> List[SavedCollectionDTO]:
        cols = self.repository.list_collections(user_id)
        return [self._to_collection_dto(c) for c in cols]

    def get_collection_tree(self, user_id: str) -> List[SavedCollectionTreeDTO]:
        cols = self.repository.list_collections(user_id)
        dto_map: Dict[str, SavedCollectionTreeDTO] = {
            c.collection_id: SavedCollectionTreeDTO(
                collection=self._to_collection_dto(c), children=[]
            )
            for c in cols
        }

        root_trees: List[SavedCollectionTreeDTO] = []
        for c in cols:
            tree_node = dto_map[c.collection_id]
            if c.parent_collection_id and c.parent_collection_id in dto_map:
                dto_map[c.parent_collection_id].children.append(tree_node)
            else:
                root_trees.append(tree_node)

        return root_trees

    def add_items_to_collection(
        self,
        collection_id: str,
        user_id: str,
        saved_item_ids: List[str],
    ) -> None:
        for iid in saved_item_ids:
            try:
                self.repository.add_item_to_collection(collection_id, iid, user_id)
            except Exception as e:
                logger.warning(f"Failed adding item {iid} to collection {collection_id}: {e}")

    def remove_item_from_collection(
        self, collection_id: str, user_id: str, saved_item_id: str
    ) -> None:
        self.repository.remove_item_from_collection(collection_id, saved_item_id, user_id)

    # -------------------------------------------------------------------------
    # Tags
    # -------------------------------------------------------------------------

    def create_tag(self, user_id: str, request: CreateSavedTagRequest) -> SavedTagDTO:
        tag = self.repository.get_or_create_tag(user_id, request.name)
        return SavedTagDTO(
            tag_id=tag.tag_id,
            name=tag.name,
            normalized_name=tag.normalized_name,
            item_count=0,
            created_at=tag.created_at,
        )

    def list_tags(self, user_id: str) -> List[SavedTagDTO]:
        tags_with_counts = self.repository.list_tags(user_id)
        return [
            SavedTagDTO(
                tag_id=t.tag_id,
                name=t.name,
                normalized_name=t.normalized_name,
                item_count=count,
                created_at=t.created_at,
            )
            for t, count in tags_with_counts
        ]

    def assign_tag(self, saved_item_id: str, user_id: str, tag_name: str) -> SavedTagDTO:
        tag = self.repository.assign_tag_to_item(saved_item_id, tag_name, user_id)
        return SavedTagDTO(
            tag_id=tag.tag_id,
            name=tag.name,
            normalized_name=tag.normalized_name,
            item_count=1,
            created_at=tag.created_at,
        )

    def remove_tag(self, saved_item_id: str, user_id: str, tag_id: str) -> None:
        self.repository.remove_tag_from_item(saved_item_id, tag_id, user_id)

    # -------------------------------------------------------------------------
    # View Configurations
    # -------------------------------------------------------------------------

    def save_configuration(
        self,
        user_id: str,
        request: CreateSavedConfigurationRequest,
    ) -> SavedViewConfigurationDTO:
        sanitized_payload, payload_hash = validate_and_sanitize_configuration_payload(
            config_type=request.configuration_type,
            schema_version=request.schema_version,
            payload=request.payload,
        )

        config_id = str(uuid.uuid4())
        config = SavedViewConfiguration(
            configuration_id=config_id,
            configuration_type=request.configuration_type,
            schema_version=request.schema_version,
            owner_user_id=user_id,
            payload=sanitized_payload,
            payload_hash=payload_hash,
            target_module=request.target_module,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        persisted = self.repository.save_configuration(config)
        return SavedViewConfigurationDTO(
            configuration_id=persisted.configuration_id,
            configuration_type=persisted.configuration_type,
            schema_version=persisted.schema_version,
            payload=persisted.payload,
            payload_hash=persisted.payload_hash,
            target_module=persisted.target_module,
            created_at=persisted.created_at,
            updated_at=persisted.updated_at,
        )

    def get_configuration(self, configuration_id: str, user_id: str) -> SavedViewConfigurationDTO:
        config = self.repository.get_configuration(configuration_id)
        if not config or config.owner_user_id != user_id:
            raise SavedConfigurationInvalidError(
                f"View configuration '{configuration_id}' not found."
            )
        return SavedViewConfigurationDTO(
            configuration_id=config.configuration_id,
            configuration_type=config.configuration_type,
            schema_version=config.schema_version,
            payload=config.payload,
            payload_hash=config.payload_hash,
            target_module=config.target_module,
            created_at=config.created_at,
            updated_at=config.updated_at,
        )

    def validate_configuration(
        self,
        user_id: str,
        request: ValidateConfigurationRequest,
    ) -> ValidateConfigurationResponse:
        sanitized_payload, payload_hash = validate_and_sanitize_configuration_payload(
            config_type=request.configuration_type,
            schema_version=request.schema_version,
            payload=request.payload,
        )

        migrated_payload = None
        migrated_version = None
        warnings = []

        if request.target_version and request.target_version != request.schema_version:
            try:
                migrated_payload = migrate_configuration(
                    config_type=request.configuration_type,
                    from_version=request.schema_version,
                    to_version=request.target_version,
                    payload=sanitized_payload,
                )
                migrated_version = request.target_version
            except Exception as e:
                warnings.append(f"Migration warning: {e}")

        return ValidateConfigurationResponse(
            valid=True,
            schema_version=request.schema_version,
            sanitized_payload=sanitized_payload,
            payload_hash=payload_hash,
            migrated_payload=migrated_payload,
            migrated_version=migrated_version,
            warnings=warnings,
        )

    # -------------------------------------------------------------------------
    # Bulk Operations
    # -------------------------------------------------------------------------

    def execute_bulk_action(
        self,
        user_id: str,
        request: SavedBulkActionRequest,
        user_entitlements: Optional[List[str]] = None,
    ) -> SavedBulkActionResponseDTO:
        results: List[BulkActionItemResultDTO] = []
        succeeded = 0
        failed = 0

        for item_id in request.saved_item_ids:
            try:
                if request.action == SavedBulkActionType.FAVORITE:
                    self.toggle_favorite(item_id, user_id, favorite=True)
                elif request.action == SavedBulkActionType.UNFAVORITE:
                    self.toggle_favorite(item_id, user_id, favorite=False)
                elif request.action == SavedBulkActionType.PIN:
                    self.toggle_pin(item_id, user_id, pinned=True)
                elif request.action == SavedBulkActionType.UNPIN:
                    self.toggle_pin(item_id, user_id, pinned=False)
                elif request.action == SavedBulkActionType.ADD_TO_COLLECTION:
                    if not request.collection_id:
                        raise SavedError("collection_id is required for ADD_TO_COLLECTION")
                    self.repository.add_item_to_collection(request.collection_id, item_id, user_id)
                elif request.action == SavedBulkActionType.REMOVE_FROM_COLLECTION:
                    if not request.collection_id:
                        raise SavedError("collection_id is required for REMOVE_FROM_COLLECTION")
                    self.repository.remove_item_from_collection(
                        request.collection_id, item_id, user_id
                    )
                elif request.action == SavedBulkActionType.ADD_TAG:
                    if not request.tag_name:
                        raise SavedError("tag_name is required for ADD_TAG")
                    self.assign_tag(item_id, user_id, request.tag_name)
                elif request.action == SavedBulkActionType.REMOVE_TAG:
                    if not request.tag_name:
                        raise SavedError("tag_name is required for REMOVE_TAG")
                    norm = request.tag_name.strip().lower()
                    tag_id = self.repository._user_tags.get((user_id, norm))
                    if tag_id:
                        self.remove_tag(item_id, user_id, tag_id)
                elif request.action == SavedBulkActionType.DELETE:
                    self.soft_delete_item(item_id, user_id)
                elif request.action == SavedBulkActionType.RESTORE:
                    self.restore_item(item_id, user_id)

                results.append(BulkActionItemResultDTO(saved_item_id=item_id, success=True))
                succeeded += 1
            except Exception as e:
                results.append(
                    BulkActionItemResultDTO(saved_item_id=item_id, success=False, error=str(e))
                )
                failed += 1

        return SavedBulkActionResponseDTO(
            action=request.action,
            total_requested=len(request.saved_item_ids),
            succeeded_count=succeeded,
            failed_count=failed,
            results=results,
        )

    # -------------------------------------------------------------------------
    # Summary KPIs
    # -------------------------------------------------------------------------

    def get_library_summary(self, user_id: str) -> SavedLibrarySummaryDTO:
        data = self.repository.get_library_summary(user_id)
        return SavedLibrarySummaryDTO(**data)

    # -------------------------------------------------------------------------
    # Internal Helpers
    # -------------------------------------------------------------------------

    def _to_item_dto(self, item: SavedItem, resolved: ResolvedTarget) -> SavedItemDTO:
        collection_ids = self.repository.get_item_collection_ids(item.saved_item_id)
        tags = self.repository.get_item_tag_names(item.saved_item_id)

        return SavedItemDTO(
            saved_item_id=item.saved_item_id,
            owner_user_id=item.owner_user_id,
            organization_id=item.organization_id,
            target_type=item.target_type,
            target_id=item.target_id,
            target_revision_id=item.target_revision_id,
            target_module=item.target_module,
            canonical_title=resolved.canonical_title,
            display_title=item.effective_title,
            user_note=item.user_note,
            favorite=item.favorite,
            pinned=item.pinned,
            view_configuration_id=item.view_configuration_id,
            semantics=item.semantics,
            collection_ids=collection_ids,
            tags=tags,
            availability_status=resolved.status,
            safe_deep_link=resolved.safe_deep_link,
            warnings=resolved.warnings,
            saved_at=item.saved_at,
            updated_at=item.updated_at,
            deleted_at=item.deleted_at,
            row_version=item.row_version,
        )

    def _to_collection_dto(self, col: SavedCollection) -> SavedCollectionDTO:
        item_count = self.repository.get_collection_item_count(col.collection_id)
        return SavedCollectionDTO(
            collection_id=col.collection_id,
            owner_user_id=col.owner_user_id,
            name=col.name,
            description=col.description,
            parent_collection_id=col.parent_collection_id,
            item_count=item_count,
            sort_order=col.sort_order,
            created_at=col.created_at,
            updated_at=col.updated_at,
            row_version=col.row_version,
        )
