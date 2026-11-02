"""Tenant-scoped workflow definitions with immutable published versions."""

from __future__ import annotations

import uuid

from atlas.workflows.domain import WorkflowDefinition, WorkflowGraph, WorkflowVersion
from atlas.workflows.errors import WorkflowNotFoundError
from atlas.workflows.validation import CompiledWorkflow, validate_and_compile


class WorkflowRegistryService:
    """In-memory registry until workflow persistence and runtime workers exist."""

    def __init__(self) -> None:
        self._workflows: dict[str, WorkflowDefinition] = {}

    def create(
        self,
        *,
        tenant_id: str,
        owner_id: str,
        name: str,
        description: str,
        graph: WorkflowGraph,
    ) -> WorkflowDefinition:
        workflow_id = str(uuid.uuid4())
        version = WorkflowVersion(
            version_id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            version=1,
            graph=graph,
            status="DRAFT",
        )
        workflow = WorkflowDefinition(
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            owner_id=owner_id,
            name=name,
            description=description,
            status="DRAFT",
            versions=(version,),
        )
        self._workflows[workflow_id] = workflow
        return workflow

    def get(self, *, workflow_id: str, tenant_id: str, owner_id: str) -> WorkflowDefinition:
        workflow = self._workflows.get(workflow_id)
        if workflow is None or workflow.tenant_id != tenant_id or workflow.owner_id != owner_id:
            raise WorkflowNotFoundError(f"Workflow '{workflow_id}' was not found.")
        return workflow

    def list(self, *, tenant_id: str, owner_id: str) -> list[WorkflowDefinition]:
        return [
            workflow
            for workflow in self._workflows.values()
            if workflow.tenant_id == tenant_id and workflow.owner_id == owner_id
        ]

    def validate(
        self, *, workflow_id: str, tenant_id: str, owner_id: str
    ) -> CompiledWorkflow:
        workflow = self.get(workflow_id=workflow_id, tenant_id=tenant_id, owner_id=owner_id)
        return validate_and_compile(workflow.versions[-1].graph)

    def publish(self, *, workflow_id: str, tenant_id: str, owner_id: str) -> WorkflowDefinition:
        workflow = self.get(workflow_id=workflow_id, tenant_id=tenant_id, owner_id=owner_id)
        validate_and_compile(workflow.versions[-1].graph)
        version = workflow.versions[-1]
        published = WorkflowVersion(
            version_id=version.version_id,
            workflow_id=version.workflow_id,
            version=version.version,
            graph=version.graph,
            status="PUBLISHED",
        )
        updated = WorkflowDefinition(
            workflow_id=workflow.workflow_id,
            tenant_id=workflow.tenant_id,
            owner_id=workflow.owner_id,
            name=workflow.name,
            description=workflow.description,
            status="PUBLISHED",
            versions=(*workflow.versions[:-1], published),
        )
        self._workflows[workflow_id] = updated
        return updated