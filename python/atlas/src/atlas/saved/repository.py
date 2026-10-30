"""Thread-Safe In-Memory and Transactional Repository for Stage 119 - Universal Saved System."""

from __future__ import annotations

import logging
import threading
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from atlas.saved.enums import (
    SavedAuditEventType,
    SavedModule,
    SavedSortOption,
    SavedTargetType,
)
from atlas.saved.errors import (
    SavedCollectionAccessDeniedError,
    SavedCollectionDuplicateNameError,
    SavedCollectionHierarchyCycleError,
    SavedCollectionMaxDepthError,
    SavedCollectionMembershipExistsError,
    SavedCollectionMembershipNotFoundError,
    SavedCollectionNotFoundError,
    SavedItemAccessDeniedError,
    SavedItemAlreadyExistsError,
    SavedItemNotFoundError,
    SavedItemVersionConflictError,
)
from atlas.saved.models import (
    SavedAuditEvent,
    SavedCollection,
    SavedCollectionMembership,
    SavedItem,
    SavedTag,
    SavedViewConfiguration,
)

logger = logging.getLogger(__name__)


class SavedRepository:
    """
    High-performance thread-safe repository managing saved items, collections,
    memberships, tags, notes, view configurations, and audit events.
    """

    MAX_COLLECTION_DEPTH = 5

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._items: Dict[str, SavedItem] = {}
        self._user_items: Dict[str, Set[str]] = {}  # user_id -> set(item_ids)
        self._user_target_map: Dict[
            Tuple[str, SavedTargetType, str], str
        ] = {}  # (user_id, type, target_id) -> item_id
        self._idempotency_map: Dict[
            Tuple[str, str], str
        ] = {}  # (user_id, idempotency_key) -> item_id

        self._collections: Dict[str, SavedCollection] = {}
        self._user_collections: Dict[str, Set[str]] = {}  # user_id -> set(collection_ids)
        self._memberships: Dict[
            Tuple[str, str], SavedCollectionMembership
        ] = {}  # (collection_id, item_id) -> membership
        self._item_collections: Dict[str, Set[str]] = {}  # item_id -> set(collection_ids)
        self._collection_items: Dict[str, Set[str]] = {}  # collection_id -> set(item_ids)

        self._tags: Dict[str, SavedTag] = {}
        self._user_tags: Dict[Tuple[str, str], str] = {}  # (user_id, normalized_name) -> tag_id
        self._item_tags: Dict[str, Set[str]] = {}  # item_id -> set(tag_ids)
        self._tag_items: Dict[str, Set[str]] = {}  # tag_id -> set(item_ids)

        self._configurations: Dict[str, SavedViewConfiguration] = {}
        self._audit_events: List[SavedAuditEvent] = []

    # -------------------------------------------------------------------------
    # Audit Events
    # -------------------------------------------------------------------------

    def record_audit_event(
        self,
        event_type: SavedAuditEventType,
        actor_user_id: str,
        target_entity_id: str,
        details: Dict[str, Any],
    ) -> SavedAuditEvent:
        with self._lock:
            event = SavedAuditEvent(
                event_id=str(uuid.uuid4()),
                event_type=event_type,
                actor_user_id=actor_user_id,
                target_entity_id=target_entity_id,
                details=details,
                created_at=datetime.now(timezone.utc),
            )
            self._audit_events.append(event)
            return event

    def get_audit_events(self, limit: int = 100) -> List[SavedAuditEvent]:
        with self._lock:
            return deepcopy(self._audit_events[-limit:])

    # -------------------------------------------------------------------------
    # Saved Items
    # -------------------------------------------------------------------------

    def save_item(
        self,
        item: SavedItem,
        idempotency_key: Optional[str] = None,
    ) -> SavedItem:
        with self._lock:
            # 1. Idempotency lookup
            if idempotency_key:
                idem_key = (item.owner_user_id, idempotency_key.strip())
                existing_id = self._idempotency_map.get(idem_key)
                if existing_id and existing_id in self._items:
                    existing = self._items[existing_id]
                    if not existing.is_deleted:
                        return deepcopy(existing)

            # 2. Duplicate reference check per user & target
            target_key = (item.owner_user_id, item.target_type, item.target_id)
            existing_target_item_id = self._user_target_map.get(target_key)
            if existing_target_item_id and existing_target_item_id in self._items:
                existing = self._items[existing_target_item_id]
                if not existing.is_deleted:
                    raise SavedItemAlreadyExistsError(
                        target_type=item.target_type.value,
                        target_id=item.target_id,
                        existing_saved_item_id=existing.saved_item_id,
                    )
                else:
                    # Item was previously soft-deleted; re-activate it cleanly
                    existing.deleted_at = None
                    existing.updated_at = datetime.now(timezone.utc)
                    existing.row_version += 1
                    if item.display_title_override:
                        existing.display_title_override = item.display_title_override
                    if item.user_note:
                        existing.user_note = item.user_note
                    if item.favorite:
                        existing.favorite = item.favorite
                    if item.pinned:
                        existing.pinned = item.pinned
                    return deepcopy(existing)

            # 3. Store new item
            self._items[item.saved_item_id] = deepcopy(item)
            self._user_items.setdefault(item.owner_user_id, set()).add(item.saved_item_id)
            self._user_target_map[target_key] = item.saved_item_id

            if idempotency_key:
                self._idempotency_map[(item.owner_user_id, idempotency_key.strip())] = (
                    item.saved_item_id
                )

            self.record_audit_event(
                SavedAuditEventType.ITEM_SAVED,
                actor_user_id=item.owner_user_id,
                target_entity_id=item.saved_item_id,
                details={
                    "target_type": item.target_type.value,
                    "target_id": item.target_id,
                    "target_module": item.target_module.value,
                },
            )
            return deepcopy(item)

    def get_item(self, saved_item_id: str, include_deleted: bool = False) -> Optional[SavedItem]:
        with self._lock:
            item = self._items.get(saved_item_id)
            if not item:
                return None
            if item.is_deleted and not include_deleted:
                return None
            return deepcopy(item)

    def update_item(
        self,
        saved_item_id: str,
        user_id: str,
        display_title_override: Optional[str] = None,
        user_note: Optional[str] = None,
        favorite: Optional[bool] = None,
        pinned: Optional[bool] = None,
        target_revision_id: Optional[str] = None,
        expected_row_version: Optional[int] = None,
    ) -> SavedItem:
        with self._lock:
            item = self._items.get(saved_item_id)
            if not item or item.is_deleted:
                raise SavedItemNotFoundError(saved_item_id)
            if item.owner_user_id != user_id:
                raise SavedItemAccessDeniedError(saved_item_id, user_id)

            if expected_row_version is not None and item.row_version != expected_row_version:
                raise SavedItemVersionConflictError(
                    saved_item_id=saved_item_id,
                    current_version=item.row_version,
                    provided_version=expected_row_version,
                )

            changed = False
            if display_title_override is not None:
                item.display_title_override = display_title_override
                changed = True
            if user_note is not None:
                item.user_note = user_note
                changed = True
            if favorite is not None:
                item.favorite = favorite
                changed = True
            if pinned is not None:
                item.pinned = pinned
                changed = True
            if target_revision_id is not None:
                item.target_revision_id = target_revision_id
                changed = True

            if changed:
                item.updated_at = datetime.now(timezone.utc)
                item.row_version += 1
                self.record_audit_event(
                    SavedAuditEventType.ITEM_UPDATED,
                    actor_user_id=user_id,
                    target_entity_id=saved_item_id,
                    details={"row_version": item.row_version},
                )

            return deepcopy(item)

    def soft_delete_item(self, saved_item_id: str, user_id: str) -> None:
        with self._lock:
            item = self._items.get(saved_item_id)
            if not item or item.is_deleted:
                raise SavedItemNotFoundError(saved_item_id)
            if item.owner_user_id != user_id:
                raise SavedItemAccessDeniedError(saved_item_id, user_id)

            item.deleted_at = datetime.now(timezone.utc)
            item.updated_at = datetime.now(timezone.utc)
            item.row_version += 1

            self.record_audit_event(
                SavedAuditEventType.ITEM_REMOVED,
                actor_user_id=user_id,
                target_entity_id=saved_item_id,
                details={},
            )

    def restore_item(self, saved_item_id: str, user_id: str) -> SavedItem:
        with self._lock:
            item = self._items.get(saved_item_id)
            if not item:
                raise SavedItemNotFoundError(saved_item_id)
            if item.owner_user_id != user_id:
                raise SavedItemAccessDeniedError(saved_item_id, user_id)
            if not item.is_deleted:
                return deepcopy(item)

            item.deleted_at = None
            item.updated_at = datetime.now(timezone.utc)
            item.row_version += 1

            self.record_audit_event(
                SavedAuditEventType.ITEM_RESTORED,
                actor_user_id=user_id,
                target_entity_id=saved_item_id,
                details={},
            )
            return deepcopy(item)

    def list_items(
        self,
        user_id: str,
        search: Optional[str] = None,
        target_type: Optional[SavedTargetType] = None,
        target_module: Optional[SavedModule] = None,
        collection_id: Optional[str] = None,
        tag_name: Optional[str] = None,
        favorite: Optional[bool] = None,
        pinned: Optional[bool] = None,
        sort_by: SavedSortOption = SavedSortOption.RECENTLY_SAVED,
        page: int = 1,
        page_size: int = 50,
        include_deleted: bool = False,
    ) -> Tuple[List[SavedItem], int]:
        with self._lock:
            user_item_ids = self._user_items.get(user_id, set())
            candidates = [self._items[iid] for iid in user_item_ids if iid in self._items]

            if not include_deleted:
                candidates = [i for i in candidates if not i.is_deleted]

            # 1. Filters
            if target_type:
                candidates = [i for i in candidates if i.target_type == target_type]
            if target_module:
                candidates = [i for i in candidates if i.target_module == target_module]
            if favorite is not None:
                candidates = [i for i in candidates if i.favorite == favorite]
            if pinned is not None:
                candidates = [i for i in candidates if i.pinned == pinned]
            if collection_id:
                col_item_ids = self._collection_items.get(collection_id, set())
                candidates = [i for i in candidates if i.saved_item_id in col_item_ids]
            if tag_name:
                norm_tag = tag_name.strip().lower()
                tag_id = self._user_tags.get((user_id, norm_tag))
                if tag_id:
                    tag_item_ids = self._tag_items.get(tag_id, set())
                    candidates = [i for i in candidates if i.saved_item_id in tag_item_ids]
                else:
                    candidates = []

            # 2. Text Search
            if search and search.strip():
                query = search.strip().lower()
                matched = []
                for item in candidates:
                    title_match = query in item.effective_title.lower()
                    id_match = query in item.target_id.lower()
                    note_match = item.user_note is not None and query in item.user_note.lower()

                    # Tag match
                    assigned_tags = self.get_item_tag_names(item.saved_item_id)
                    tag_match = any(query in t.lower() for t in assigned_tags)

                    if title_match or id_match or note_match or tag_match:
                        matched.append(item)
                candidates = matched

            # 3. Sort
            def sort_key(item: SavedItem):
                # Pinned items take precedence in all non-custom sorts
                pinned_val = 0 if item.pinned else 1
                if sort_by == SavedSortOption.RECENTLY_SAVED:
                    return (pinned_val, -item.saved_at.timestamp())
                elif sort_by == SavedSortOption.RECENTLY_UPDATED:
                    return (pinned_val, -item.updated_at.timestamp())
                elif sort_by == SavedSortOption.NAME_ASC:
                    return (pinned_val, item.effective_title.lower())
                elif sort_by == SavedSortOption.NAME_DESC:
                    return (pinned_val, item.effective_title.lower())
                elif sort_by == SavedSortOption.RESOURCE_TYPE:
                    return (pinned_val, item.target_type.value)
                return (pinned_val, -item.saved_at.timestamp())

            reverse = sort_by == SavedSortOption.NAME_DESC
            candidates.sort(key=sort_key, reverse=reverse)

            total_count = len(candidates)
            start = (page - 1) * page_size
            end = start + page_size
            paginated = candidates[start:end]

            return [deepcopy(i) for i in paginated], total_count

    # -------------------------------------------------------------------------
    # Collections
    # -------------------------------------------------------------------------

    def create_collection(
        self,
        owner_user_id: str,
        name: str,
        description: Optional[str] = None,
        parent_collection_id: Optional[str] = None,
        sort_order: int = 0,
        organization_id: Optional[str] = None,
    ) -> SavedCollection:
        with self._lock:
            clean_name = name.strip()
            # Duplicate name check in user scope
            existing_cols = [
                self._collections[cid]
                for cid in self._user_collections.get(owner_user_id, set())
                if cid in self._collections and not self._collections[cid].is_deleted
            ]
            if any(c.name.lower() == clean_name.lower() for c in existing_cols):
                raise SavedCollectionDuplicateNameError(clean_name)

            # Validate parent hierarchy
            if parent_collection_id:
                parent = self._collections.get(parent_collection_id)
                if not parent or parent.is_deleted:
                    raise SavedCollectionNotFoundError(parent_collection_id)
                if parent.owner_user_id != owner_user_id:
                    raise SavedCollectionAccessDeniedError(parent_collection_id, owner_user_id)
                depth = self._calculate_collection_depth(parent_collection_id)
                if depth >= self.MAX_COLLECTION_DEPTH:
                    raise SavedCollectionMaxDepthError(self.MAX_COLLECTION_DEPTH)

            col_id = str(uuid.uuid4())
            col = SavedCollection(
                collection_id=col_id,
                owner_user_id=owner_user_id,
                organization_id=organization_id,
                name=clean_name,
                description=description.strip() if description else None,
                parent_collection_id=parent_collection_id,
                sort_order=sort_order,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            self._collections[col_id] = deepcopy(col)
            self._user_collections.setdefault(owner_user_id, set()).add(col_id)
            self._collection_items[col_id] = set()

            self.record_audit_event(
                SavedAuditEventType.COLLECTION_CREATED,
                actor_user_id=owner_user_id,
                target_entity_id=col_id,
                details={"name": clean_name},
            )
            return deepcopy(col)

    def _calculate_collection_depth(self, collection_id: str) -> int:
        depth = 1
        curr_id = collection_id
        visited = set()
        while curr_id:
            if curr_id in visited:
                break
            visited.add(curr_id)
            col = self._collections.get(curr_id)
            if not col or not col.parent_collection_id:
                break
            depth += 1
            curr_id = col.parent_collection_id
        return depth

    def get_collection(
        self, collection_id: str, include_deleted: bool = False
    ) -> Optional[SavedCollection]:
        with self._lock:
            col = self._collections.get(collection_id)
            if not col:
                return None
            if col.is_deleted and not include_deleted:
                return None
            return deepcopy(col)

    def update_collection(
        self,
        collection_id: str,
        user_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        parent_collection_id: Optional[str] = None,
        sort_order: Optional[int] = None,
        expected_row_version: Optional[int] = None,
    ) -> SavedCollection:
        with self._lock:
            col = self._collections.get(collection_id)
            if not col or col.is_deleted:
                raise SavedCollectionNotFoundError(collection_id)
            if col.owner_user_id != user_id:
                raise SavedCollectionAccessDeniedError(collection_id, user_id)

            if expected_row_version is not None and col.row_version != expected_row_version:
                raise SavedItemVersionConflictError(
                    collection_id, col.row_version, expected_row_version
                )

            if name is not None and name.strip():
                clean_name = name.strip()
                # Check duplicate name among siblings
                existing_cols = [
                    self._collections[cid]
                    for cid in self._user_collections.get(user_id, set())
                    if cid in self._collections
                    and cid != collection_id
                    and not self._collections[cid].is_deleted
                ]
                if any(c.name.lower() == clean_name.lower() for c in existing_cols):
                    raise SavedCollectionDuplicateNameError(clean_name)
                col.name = clean_name

            if description is not None:
                col.description = description.strip() if description else None

            if sort_order is not None:
                col.sort_order = sort_order

            if parent_collection_id is not None:
                if parent_collection_id == "":
                    col.parent_collection_id = None
                else:
                    if parent_collection_id == collection_id:
                        raise SavedCollectionHierarchyCycleError(
                            collection_id, parent_collection_id
                        )
                    parent = self._collections.get(parent_collection_id)
                    if not parent or parent.is_deleted:
                        raise SavedCollectionNotFoundError(parent_collection_id)
                    if parent.owner_user_id != user_id:
                        raise SavedCollectionAccessDeniedError(parent_collection_id, user_id)

                    # Cycle detection: check if collection_id is an ancestor of target parent
                    curr = parent_collection_id
                    visited = set()
                    while curr:
                        if curr == collection_id:
                            raise SavedCollectionHierarchyCycleError(
                                collection_id, parent_collection_id
                            )
                        visited.add(curr)
                        p_col = self._collections.get(curr)
                        if (
                            not p_col
                            or not p_col.parent_collection_id
                            or p_col.parent_collection_id in visited
                        ):
                            break
                        curr = p_col.parent_collection_id

                    # Depth check
                    depth = self._calculate_collection_depth(parent_collection_id) + 1
                    if depth > self.MAX_COLLECTION_DEPTH:
                        raise SavedCollectionMaxDepthError(self.MAX_COLLECTION_DEPTH)

                    col.parent_collection_id = parent_collection_id

            col.updated_at = datetime.now(timezone.utc)
            col.row_version += 1

            self.record_audit_event(
                SavedAuditEventType.COLLECTION_UPDATED,
                actor_user_id=user_id,
                target_entity_id=collection_id,
                details={"name": col.name},
            )
            return deepcopy(col)

    def delete_collection(self, collection_id: str, user_id: str) -> None:
        with self._lock:
            col = self._collections.get(collection_id)
            if not col or col.is_deleted:
                raise SavedCollectionNotFoundError(collection_id)
            if col.owner_user_id != user_id:
                raise SavedCollectionAccessDeniedError(collection_id, user_id)

            # Soft delete collection
            col.deleted_at = datetime.now(timezone.utc)
            col.updated_at = datetime.now(timezone.utc)
            col.row_version += 1

            # Remove memberships from active index (saved items remain intact in library)
            item_ids = list(self._collection_items.get(collection_id, set()))
            for iid in item_ids:
                self._memberships.pop((collection_id, iid), None)
                if iid in self._item_collections:
                    self._item_collections[iid].discard(collection_id)
            self._collection_items[collection_id] = set()

            # Re-parent children to parent of deleted collection
            for cid in self._user_collections.get(user_id, set()):
                child = self._collections.get(cid)
                if child and not child.is_deleted and child.parent_collection_id == collection_id:
                    child.parent_collection_id = col.parent_collection_id
                    child.updated_at = datetime.now(timezone.utc)
                    child.row_version += 1

            self.record_audit_event(
                SavedAuditEventType.COLLECTION_DELETED,
                actor_user_id=user_id,
                target_entity_id=collection_id,
                details={},
            )

    def list_collections(self, user_id: str) -> List[SavedCollection]:
        with self._lock:
            col_ids = self._user_collections.get(user_id, set())
            active = [
                self._collections[cid]
                for cid in col_ids
                if cid in self._collections and not self._collections[cid].is_deleted
            ]
            active.sort(key=lambda c: (c.sort_order, c.name.lower()))
            return [deepcopy(c) for c in active]

    def add_item_to_collection(self, collection_id: str, saved_item_id: str, user_id: str) -> None:
        with self._lock:
            col = self._collections.get(collection_id)
            if not col or col.is_deleted:
                raise SavedCollectionNotFoundError(collection_id)
            if col.owner_user_id != user_id:
                raise SavedCollectionAccessDeniedError(collection_id, user_id)

            item = self._items.get(saved_item_id)
            if not item or item.is_deleted:
                raise SavedItemNotFoundError(saved_item_id)
            if item.owner_user_id != user_id:
                raise SavedItemAccessDeniedError(saved_item_id, user_id)

            pair = (collection_id, saved_item_id)
            if pair in self._memberships:
                raise SavedCollectionMembershipExistsError(collection_id, saved_item_id)

            sort_order = len(self._collection_items.get(collection_id, set()))
            membership = SavedCollectionMembership(
                collection_id=collection_id,
                saved_item_id=saved_item_id,
                added_at=datetime.now(timezone.utc),
                sort_order=sort_order,
            )
            self._memberships[pair] = membership
            self._collection_items.setdefault(collection_id, set()).add(saved_item_id)
            self._item_collections.setdefault(saved_item_id, set()).add(collection_id)

    def remove_item_from_collection(
        self, collection_id: str, saved_item_id: str, user_id: str
    ) -> None:
        with self._lock:
            col = self._collections.get(collection_id)
            if not col or col.is_deleted:
                raise SavedCollectionNotFoundError(collection_id)
            if col.owner_user_id != user_id:
                raise SavedCollectionAccessDeniedError(collection_id, user_id)

            pair = (collection_id, saved_item_id)
            if pair not in self._memberships:
                raise SavedCollectionMembershipNotFoundError(collection_id, saved_item_id)

            del self._memberships[pair]
            if collection_id in self._collection_items:
                self._collection_items[collection_id].discard(saved_item_id)
            if saved_item_id in self._item_collections:
                self._item_collections[saved_item_id].discard(collection_id)

    def get_collection_item_count(self, collection_id: str) -> int:
        with self._lock:
            return len(self._collection_items.get(collection_id, set()))

    def get_item_collection_ids(self, saved_item_id: str) -> List[str]:
        with self._lock:
            return sorted(list(self._item_collections.get(saved_item_id, set())))

    # -------------------------------------------------------------------------
    # Tags
    # -------------------------------------------------------------------------

    def get_or_create_tag(self, owner_user_id: str, name: str) -> SavedTag:
        with self._lock:
            clean_name = name.strip()
            norm = clean_name.lower()
            key = (owner_user_id, norm)
            existing_id = self._user_tags.get(key)
            if existing_id and existing_id in self._tags:
                return deepcopy(self._tags[existing_id])

            tag_id = str(uuid.uuid4())
            tag = SavedTag(
                tag_id=tag_id,
                owner_user_id=owner_user_id,
                name=clean_name,
                normalized_name=norm,
                created_at=datetime.now(timezone.utc),
            )
            self._tags[tag_id] = deepcopy(tag)
            self._user_tags[key] = tag_id
            self._tag_items[tag_id] = set()

            self.record_audit_event(
                SavedAuditEventType.TAG_CREATED,
                actor_user_id=owner_user_id,
                target_entity_id=tag_id,
                details={"name": clean_name},
            )
            return deepcopy(tag)

    def assign_tag_to_item(self, saved_item_id: str, tag_name: str, user_id: str) -> SavedTag:
        with self._lock:
            item = self._items.get(saved_item_id)
            if not item or item.is_deleted:
                raise SavedItemNotFoundError(saved_item_id)
            if item.owner_user_id != user_id:
                raise SavedItemAccessDeniedError(saved_item_id, user_id)

            tag = self.get_or_create_tag(user_id, tag_name)
            self._item_tags.setdefault(saved_item_id, set()).add(tag.tag_id)
            self._tag_items.setdefault(tag.tag_id, set()).add(saved_item_id)

            self.record_audit_event(
                SavedAuditEventType.TAG_ASSIGNED,
                actor_user_id=user_id,
                target_entity_id=saved_item_id,
                details={"tag_id": tag.tag_id, "tag_name": tag.name},
            )
            return tag

    def remove_tag_from_item(self, saved_item_id: str, tag_id: str, user_id: str) -> None:
        with self._lock:
            item = self._items.get(saved_item_id)
            if not item or item.is_deleted:
                raise SavedItemNotFoundError(saved_item_id)
            if item.owner_user_id != user_id:
                raise SavedItemAccessDeniedError(saved_item_id, user_id)

            if saved_item_id in self._item_tags:
                self._item_tags[saved_item_id].discard(tag_id)
            if tag_id in self._tag_items:
                self._tag_items[tag_id].discard(saved_item_id)

            self.record_audit_event(
                SavedAuditEventType.TAG_REMOVED,
                actor_user_id=user_id,
                target_entity_id=saved_item_id,
                details={"tag_id": tag_id},
            )

    def list_tags(self, user_id: str) -> List[Tuple[SavedTag, int]]:
        with self._lock:
            results = []
            for (uid, _), tid in self._user_tags.items():
                if uid == user_id and tid in self._tags:
                    tag = self._tags[tid]
                    count = len(self._tag_items.get(tid, set()))
                    results.append((deepcopy(tag), count))
            results.sort(key=lambda t: t[0].name.lower())
            return results

    def get_item_tag_names(self, saved_item_id: str) -> List[str]:
        with self._lock:
            tids = self._item_tags.get(saved_item_id, set())
            names = [self._tags[tid].name for tid in tids if tid in self._tags]
            return sorted(names)

    # -------------------------------------------------------------------------
    # View Configurations
    # -------------------------------------------------------------------------

    def save_configuration(self, config: SavedViewConfiguration) -> SavedViewConfiguration:
        with self._lock:
            self._configurations[config.configuration_id] = deepcopy(config)
            self.record_audit_event(
                SavedAuditEventType.CONFIG_SAVED,
                actor_user_id=config.owner_user_id,
                target_entity_id=config.configuration_id,
                details={"type": config.configuration_type.value, "version": config.schema_version},
            )
            return deepcopy(config)

    def get_configuration(self, configuration_id: str) -> Optional[SavedViewConfiguration]:
        with self._lock:
            config = self._configurations.get(configuration_id)
            return deepcopy(config) if config else None

    # -------------------------------------------------------------------------
    # Library Summary KPIs
    # -------------------------------------------------------------------------

    def get_library_summary(self, user_id: str) -> Dict[str, int]:
        with self._lock:
            user_item_ids = self._user_items.get(user_id, set())
            active_items = [
                self._items[iid]
                for iid in user_item_ids
                if iid in self._items and not self._items[iid].is_deleted
            ]

            total_saved = len(active_items)
            favorites = sum(1 for i in active_items if i.favorite)
            pinned = sum(1 for i in active_items if i.pinned)

            # Collections count
            active_cols = [
                self._collections[cid]
                for cid in self._user_collections.get(user_id, set())
                if cid in self._collections and not self._collections[cid].is_deleted
            ]

            # Tags count
            tags = [
                tid
                for (uid, _), tid in self._user_tags.items()
                if uid == user_id and tid in self._tags
            ]

            # Recent saves in last 7 days
            now = datetime.now(timezone.utc)
            recent = sum(1 for i in active_items if (now - i.saved_at).total_seconds() <= 7 * 86400)

            return {
                "total_saved_items": total_saved,
                "favorite_count": favorites,
                "pinned_count": pinned,
                "collection_count": len(active_cols),
                "tag_count": len(tags),
                "recent_saves_count": recent,
            }
