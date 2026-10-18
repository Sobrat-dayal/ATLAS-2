"""Service Layer for Saved Chart Layouts (Stage 74).

Coordinates:
- Layout quota enforcement (max 50 layouts per user)
- Document size and payload validation
- Name normalization and case-insensitive uniqueness checking
- Optimistic concurrency control (revision checks)
- Single-default layout maintenance
- Clean separation between relational metadata and JSONB configuration aggregate
- Safe duplication and export envelopes
"""

import datetime
import uuid
from typing import Optional

from .migrations import migrate_layout_document
from .models import ChartLayoutModel
from .normalization import normalize_layout_name, sanitize_display_name
from .repository import ChartLayoutRepository
from .schemas import (
    ChartLayoutCreateRequest,
    ChartLayoutDetailResponse,
    ChartLayoutExportEnvelope,
    ChartLayoutListResponse,
    ChartLayoutMetadataPatchRequest,
    ChartLayoutSummaryResponse,
    ChartLayoutUpdateRequest,
)
from .validation import (
    MAX_LAYOUTS_PER_USER,
    LayoutQuotaExceededError,
    validate_layout_document_payload,
)


class LayoutNotFoundError(Exception):
    """Raised when a layout is not found or is not owned by the principal."""

    pass


class LayoutNameConflictError(Exception):
    """Raised when a user attempts to create or rename a layout to an existing normalized name."""

    pass


class LayoutRevisionConflictError(Exception):
    """Raised when optimistic concurrency revision check fails."""

    def __init__(self, current_revision: int, expected_revision: int):
        super().__init__(
            f"Precondition Failed: Expected revision {expected_revision}, "
            f"but current database revision is {current_revision}."
        )
        self.current_revision = current_revision
        self.expected_revision = expected_revision


class ChartLayoutService:
    def __init__(self, repository: ChartLayoutRepository):
        self.repository = repository

    async def list_layouts(
        self,
        owner_user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
    ) -> ChartLayoutListResponse:
        """Lists user layouts with bounded pagination and summary projections."""
        page = max(1, page)
        page_size = min(100, max(1, page_size))
        skip = (page - 1) * page_size

        total = await self.repository.count_layouts(owner_user_id, search=search)
        models = await self.repository.list_layouts(
            owner_user_id=owner_user_id,
            skip=skip,
            limit=page_size,
            search=search,
        )

        items = [self._to_summary(m) for m in models]
        return ChartLayoutListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_layout(
        self,
        layout_id: uuid.UUID,
        owner_user_id: uuid.UUID,
    ) -> ChartLayoutDetailResponse:
        """Retrieves a single layout document, enforcing ownership isolation."""
        model = await self.repository.get_by_id(layout_id, owner_user_id)
        if not model:
            raise LayoutNotFoundError(f"Layout '{layout_id}' not found.")
        return self._to_detail(model)

    async def create_layout(
        self,
        owner_user_id: uuid.UUID,
        request: ChartLayoutCreateRequest,
    ) -> ChartLayoutDetailResponse:
        """Creates a new saved chart layout, enforcing quotas and name uniqueness."""
        # 1. Enforce quota
        count = await self.repository.count_layouts(owner_user_id)
        if count >= MAX_LAYOUTS_PER_USER:
            raise LayoutQuotaExceededError(
                f"Layout limit exceeded. Maximum {MAX_LAYOUTS_PER_USER} layouts per user."
            )

        # 2. Normalize and check name
        display_name = sanitize_display_name(request.name)
        norm_name = normalize_layout_name(request.name)

        existing = await self.repository.get_by_normalized_name(owner_user_id, norm_name)
        if existing:
            raise LayoutNameConflictError(
                f"A saved chart layout named '{display_name}' already exists."
            )

        # 3. Validate document
        validated_doc = validate_layout_document_payload(request.document.model_dump())

        # 4. Handle default flag
        if request.is_default:
            await self.repository.clear_default(owner_user_id)

        model = await self.repository.create_layout(
            owner_user_id=owner_user_id,
            name=display_name,
            normalized_name=norm_name,
            description=request.description,
            document=validated_doc.model_dump(),
            is_default=request.is_default,
        )
        await self.repository.session.commit()
        return self._to_detail(model)

    async def update_layout(
        self,
        layout_id: uuid.UUID,
        owner_user_id: uuid.UUID,
        request: ChartLayoutUpdateRequest,
    ) -> ChartLayoutDetailResponse:
        """
        Updates an existing layout document with atomic optimistic concurrency control.
        """
        # Verify existence
        existing = await self.repository.get_by_id(layout_id, owner_user_id)
        if not existing:
            raise LayoutNotFoundError(f"Layout '{layout_id}' not found.")

        # Check revision for fast fail
        if existing.revision != request.expected_revision:
            raise LayoutRevisionConflictError(
                current_revision=existing.revision,
                expected_revision=request.expected_revision,
            )

        # Validate document
        validated_doc = validate_layout_document_payload(request.document.model_dump())

        updated = await self.repository.update_layout(
            layout_id=layout_id,
            owner_user_id=owner_user_id,
            expected_revision=request.expected_revision,
            document=validated_doc.model_dump(),
        )

        if not updated:
            # Re-read to provide accurate current revision in error
            refetched = await self.repository.get_by_id(layout_id, owner_user_id)
            current_rev = refetched.revision if refetched else 0
            raise LayoutRevisionConflictError(
                current_revision=current_rev,
                expected_revision=request.expected_revision,
            )

        await self.repository.session.commit()
        return self._to_detail(updated)

    async def patch_metadata(
        self,
        layout_id: uuid.UUID,
        owner_user_id: uuid.UUID,
        request: ChartLayoutMetadataPatchRequest,
    ) -> ChartLayoutDetailResponse:
        """Renames or updates metadata without modifying the chart document."""
        existing = await self.repository.get_by_id(layout_id, owner_user_id)
        if not existing:
            raise LayoutNotFoundError(f"Layout '{layout_id}' not found.")

        display_name = None
        norm_name = None
        if request.name is not None:
            display_name = sanitize_display_name(request.name)
            norm_name = normalize_layout_name(request.name)
            if norm_name != existing.normalized_name:
                collision = await self.repository.get_by_normalized_name(owner_user_id, norm_name)
                if collision:
                    raise LayoutNameConflictError(
                        f"A layout named '{display_name}' already exists."
                    )

        if request.is_default is True:
            await self.repository.clear_default(owner_user_id, except_layout_id=layout_id)

        updated = await self.repository.patch_metadata(
            layout_id=layout_id,
            owner_user_id=owner_user_id,
            name=display_name,
            normalized_name=norm_name,
            description=request.description,
            is_default=request.is_default,
        )

        await self.repository.session.commit()
        return self._to_detail(updated or existing)

    async def duplicate_layout(
        self,
        layout_id: uuid.UUID,
        owner_user_id: uuid.UUID,
        new_name: Optional[str] = None,
    ) -> ChartLayoutDetailResponse:
        """Duplicates an existing layout under a new UUID and distinct name."""
        source = await self.repository.get_by_id(layout_id, owner_user_id)
        if not source:
            raise LayoutNotFoundError(f"Layout '{layout_id}' not found.")

        # Check quota
        count = await self.repository.count_layouts(owner_user_id)
        if count >= MAX_LAYOUTS_PER_USER:
            raise LayoutQuotaExceededError(
                f"Layout limit exceeded. Maximum {MAX_LAYOUTS_PER_USER} layouts per user."
            )

        # Generate candidate name if not specified
        if not new_name:
            candidate_name = f"{source.name} (Copy)"
        else:
            candidate_name = new_name

        display_name = sanitize_display_name(candidate_name)
        norm_name = normalize_layout_name(candidate_name)

        # If name exists, add suffix
        counter = 2
        while await self.repository.get_by_normalized_name(owner_user_id, norm_name):
            candidate_name = f"{source.name} (Copy {counter})"
            display_name = sanitize_display_name(candidate_name)
            norm_name = normalize_layout_name(candidate_name)
            counter += 1

        new_model = await self.repository.create_layout(
            owner_user_id=owner_user_id,
            name=display_name,
            normalized_name=norm_name,
            description=source.description,
            document=source.layout_document,
            is_default=False,
        )
        await self.repository.session.commit()
        return self._to_detail(new_model)

    async def delete_layout(
        self,
        layout_id: uuid.UUID,
        owner_user_id: uuid.UUID,
    ) -> bool:
        """Deletes a user-owned layout."""
        success = await self.repository.delete_layout(layout_id, owner_user_id)
        if not success:
            raise LayoutNotFoundError(f"Layout '{layout_id}' not found.")
        await self.repository.session.commit()
        return True

    async def export_layout(
        self,
        layout_id: uuid.UUID,
        owner_user_id: uuid.UUID,
    ) -> ChartLayoutExportEnvelope:
        """Generates a secure portable export envelope containing only allowlisted config."""
        detail = await self.get_layout(layout_id, owner_user_id)
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        return ChartLayoutExportEnvelope(
            format="atlas_chart_layout",
            export_version=1,
            exported_at=now_iso,
            layout_name=detail.name,
            document_schema_version=detail.document_schema_version,
            layout_document=detail.document,
        )

    def _to_summary(self, model: ChartLayoutModel) -> ChartLayoutSummaryResponse:
        doc = model.layout_document
        layout_type = doc.get("layout_id", "single") if isinstance(doc, dict) else "single"
        panels = doc.get("panels", []) if isinstance(doc, dict) else []
        chart_count = len(panels) if isinstance(panels, list) else 1

        schema_version = (
            getattr(model, "document_schema_version", None)
            or (doc.get("schema_version", 1) if isinstance(doc, dict) else 1)
            or 1
        )

        return ChartLayoutSummaryResponse(
            id=model.id,
            name=model.name,
            description=model.description,
            layout_type=layout_type,
            chart_count=chart_count,
            is_default=model.is_default,
            revision=model.revision,
            document_schema_version=schema_version,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_detail(self, model: ChartLayoutModel) -> ChartLayoutDetailResponse:
        summary = self._to_summary(model)
        validated_doc = migrate_layout_document(model.layout_document)

        return ChartLayoutDetailResponse(
            id=model.id,
            owner_user_id=model.owner_user_id,
            name=model.name,
            normalized_name=model.normalized_name,
            description=model.description,
            layout_type=summary.layout_type,
            chart_count=summary.chart_count,
            is_default=model.is_default,
            revision=model.revision,
            document_schema_version=summary.document_schema_version,
            document=validated_doc,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
