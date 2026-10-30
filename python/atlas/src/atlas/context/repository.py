"""
Thread-Safe Repository for ATLAS Stage 121: Global Workspace Linking.
"""

import threading
import uuid
from datetime import datetime
from typing import Any, Optional

from .enums import ContextDimension, ContextScope, SubscriptionMode
from .errors import (
    ContextChannelAccessDeniedError,
    ContextChannelLimitExceededError,
    ContextChannelNotFoundError,
    ContextMembershipDuplicateError,
    ContextMembershipNotFoundError,
    ContextRevisionConflictError,
)
from .models import LinkChannel, LinkSubscription

MAX_CHANNELS_PER_SCOPE = 32


class ContextRepository:
    """Thread-safe in-memory and database-backed repository for Global Context Linking."""

    def __init__(self):
        self._lock = threading.RLock()
        self._channels: dict[str, LinkChannel] = {}
        self._memberships: dict[str, LinkSubscription] = {}  # subscription_id -> LinkSubscription
        self._snapshots: list[dict[str, Any]] = []
        self._audit_events: list[dict[str, Any]] = []

    def create_channel(
        self,
        owner_user_id: str,
        name: str,
        display_color_token: str = "#3b82f6",
        workspace_id: Optional[str] = None,
        scope: ContextScope = ContextScope.WORKSPACE,
        supported_dimensions: Optional[list[ContextDimension]] = None,
        initial_context: Optional[dict[str, Any]] = None,
    ) -> LinkChannel:
        """Create a new context link channel with validation."""
        with self._lock:
            # Check channel limit
            existing = [
                c
                for c in self._channels.values()
                if c.owner_user_id == owner_user_id
                and (c.workspace_id == workspace_id if workspace_id else True)
            ]
            if len(existing) >= MAX_CHANNELS_PER_SCOPE:
                raise ContextChannelLimitExceededError(MAX_CHANNELS_PER_SCOPE)

            channel_id = f"chan_{uuid.uuid4().hex[:12]}"
            now = datetime.utcnow()
            channel = LinkChannel(
                channel_id=channel_id,
                owner_user_id=owner_user_id,
                workspace_id=workspace_id,
                scope=scope,
                name=name,
                display_color_token=display_color_token,
                enabled=True,
                supported_dimensions=supported_dimensions
                or [
                    ContextDimension.INSTRUMENT,
                    ContextDimension.COMPANY,
                    ContextDimension.PORTFOLIO,
                    ContextDimension.DATE_RANGE,
                    ContextDimension.TIMEFRAME,
                    ContextDimension.REPORTING_CURRENCY,
                ],
                context_snapshot=initial_context or {},
                revision=1,
                created_at=now,
                updated_at=now,
            )
            self._channels[channel_id] = channel
            self._log_audit(channel_id, owner_user_id, "CHANNEL_CREATED", channel.to_dict())
            return channel

    def get_channel(self, channel_id: str) -> LinkChannel:
        """Retrieve a channel by ID."""
        with self._lock:
            channel = self._channels.get(channel_id)
            if not channel:
                raise ContextChannelNotFoundError(channel_id)
            return channel

    def list_channels(
        self,
        user_id: str,
        workspace_id: Optional[str] = None,
        scope: Optional[ContextScope] = None,
    ) -> list[LinkChannel]:
        """List channels matching scope, user, or workspace."""
        with self._lock:
            res: list[LinkChannel] = []
            for c in self._channels.values():
                if c.owner_user_id != user_id:
                    continue
                if scope and c.scope != scope:
                    continue
                if workspace_id:
                    # Return workspace-scoped channels for this workspace PLUS application-scoped channels
                    if c.workspace_id == workspace_id or c.scope == ContextScope.USER_APPLICATION:
                        res.append(c)
                else:
                    res.append(c)
            return sorted(res, key=lambda x: x.created_at)

    def update_channel(
        self,
        channel_id: str,
        user_id: str,
        name: Optional[str] = None,
        display_color_token: Optional[str] = None,
        scope: Optional[ContextScope] = None,
        enabled: Optional[bool] = None,
        supported_dimensions: Optional[list[ContextDimension]] = None,
    ) -> LinkChannel:
        """Update metadata of an existing link channel."""
        with self._lock:
            channel = self.get_channel(channel_id)
            if channel.owner_user_id != user_id:
                raise ContextChannelAccessDeniedError(channel_id)

            if name is not None:
                channel.name = name
            if display_color_token is not None:
                channel.display_color_token = display_color_token
            if scope is not None:
                channel.scope = scope
            if enabled is not None:
                channel.enabled = enabled
            if supported_dimensions is not None:
                channel.supported_dimensions = supported_dimensions

            channel.updated_at = datetime.utcnow()
            self._log_audit(channel_id, user_id, "CHANNEL_UPDATED", channel.to_dict())
            return channel

    def delete_channel(self, channel_id: str, user_id: str) -> None:
        """Delete a channel and drop its panel memberships."""
        with self._lock:
            channel = self.get_channel(channel_id)
            if channel.owner_user_id != user_id:
                raise ContextChannelAccessDeniedError(channel_id)

            del self._channels[channel_id]
            # Remove associated memberships
            to_del = [sid for sid, m in self._memberships.items() if m.channel_id == channel_id]
            for sid in to_del:
                del self._memberships[sid]

            self._log_audit(channel_id, user_id, "CHANNEL_DELETED", {"channel_id": channel_id})

    def add_membership(
        self,
        channel_id: str,
        panel_instance_id: str,
        mode: SubscriptionMode = SubscriptionMode.BIDIRECTIONAL,
        inbound_dimensions: Optional[list[ContextDimension]] = None,
        outbound_dimensions: Optional[list[ContextDimension]] = None,
        priority_policy: str = "NORMAL",
    ) -> LinkSubscription:
        """Subscribe a panel instance to a channel."""
        with self._lock:
            # Check channel existence
            channel = self.get_channel(channel_id)

            # Prevent duplicate subscription in same channel
            for m in self._memberships.values():
                if m.channel_id == channel_id and m.panel_instance_id == panel_instance_id:
                    raise ContextMembershipDuplicateError(channel_id, panel_instance_id)

            sub_id = f"sub_{uuid.uuid4().hex[:12]}"
            sub = LinkSubscription(
                subscription_id=sub_id,
                channel_id=channel_id,
                panel_instance_id=panel_instance_id,
                mode=mode,
                inbound_dimensions=inbound_dimensions or channel.supported_dimensions,
                outbound_dimensions=outbound_dimensions or channel.supported_dimensions,
                active=True,
                priority_policy=priority_policy,
                created_at=datetime.utcnow(),
            )
            self._memberships[sub_id] = sub
            return sub

    def list_memberships(self, channel_id: str) -> list[LinkSubscription]:
        """List active panel subscriptions for a channel."""
        with self._lock:
            return [m for m in self._memberships.values() if m.channel_id == channel_id]

    def list_panel_memberships(self, panel_instance_id: str) -> list[LinkSubscription]:
        """List channel subscriptions for a specific panel."""
        with self._lock:
            return [
                m for m in self._memberships.values() if m.panel_instance_id == panel_instance_id
            ]

    def update_membership(
        self,
        subscription_id: str,
        mode: Optional[SubscriptionMode] = None,
        inbound_dimensions: Optional[list[ContextDimension]] = None,
        outbound_dimensions: Optional[list[ContextDimension]] = None,
        active: Optional[bool] = None,
    ) -> LinkSubscription:
        """Update dimensions or mode for a panel subscription."""
        with self._lock:
            sub = self._memberships.get(subscription_id)
            if not sub:
                raise ContextMembershipNotFoundError(subscription_id)

            if mode is not None:
                sub.mode = mode
            if inbound_dimensions is not None:
                sub.inbound_dimensions = inbound_dimensions
            if outbound_dimensions is not None:
                sub.outbound_dimensions = outbound_dimensions
            if active is not None:
                sub.active = active

            return sub

    def remove_membership(self, subscription_id: str) -> None:
        """Remove a specific panel subscription."""
        with self._lock:
            if subscription_id in self._memberships:
                del self._memberships[subscription_id]

    def remove_panel_memberships(self, panel_instance_id: str) -> None:
        """Prune all memberships when a panel instance is deleted."""
        with self._lock:
            to_remove = [
                sid
                for sid, m in self._memberships.items()
                if m.panel_instance_id == panel_instance_id
            ]
            for sid in to_remove:
                del self._memberships[sid]

    def update_context_state(
        self,
        channel_id: str,
        user_id: str,
        context_updates: dict[str, Any],
        expected_revision: Optional[int] = None,
    ) -> LinkChannel:
        """Update context snapshot with monotonic revision increment and optimistic concurrency."""
        with self._lock:
            channel = self.get_channel(channel_id)
            if channel.owner_user_id != user_id:
                raise ContextChannelAccessDeniedError(channel_id)

            if expected_revision is not None and channel.revision != expected_revision:
                raise ContextRevisionConflictError(expected_revision, channel.revision)

            # Detect if there are real changes
            has_changes = False
            for k, v in context_updates.items():
                if channel.context_snapshot.get(k) != v:
                    has_changes = True
                    break

            if not has_changes:
                return channel

            channel.context_snapshot.update(context_updates)
            channel.revision += 1
            channel.updated_at = datetime.utcnow()

            # Record snapshot
            self._snapshots.append(
                {
                    "snapshot_id": f"snp_{uuid.uuid4().hex[:12]}",
                    "channel_id": channel_id,
                    "revision": channel.revision,
                    "context_payload": dict(channel.context_snapshot),
                    "created_by": user_id,
                    "created_at": channel.updated_at,
                }
            )

            self._log_audit(
                channel_id,
                user_id,
                "CONTEXT_UPDATED",
                {"revision": channel.revision, "updates": context_updates},
            )
            return channel

    def _log_audit(
        self, channel_id: str, user_id: str, event_type: str, payload: dict[str, Any]
    ) -> None:
        self._audit_events.append(
            {
                "audit_id": f"aud_{uuid.uuid4().hex[:12]}",
                "channel_id": channel_id,
                "user_id": user_id,
                "event_type": event_type,
                "payload": payload,
                "created_at": datetime.utcnow(),
            }
        )

    def ensure_default_channels(
        self, user_id: str, workspace_id: Optional[str] = None
    ) -> list[LinkChannel]:
        """Ensure canonical default link channels (Link A, Link B, Link C, Link D) exist."""
        with self._lock:
            existing = self.list_channels(user_id, workspace_id)
            if existing:
                return existing

            default_defs = [
                ("Group A (Core Equity)", "#3b82f6", {"INSTRUMENT": "AAPL", "TIMEFRAME": "1D"}),
                (
                    "Group B (Macro & Rates)",
                    "#10b981",
                    {"ECONOMIC_SERIES": "CPI", "TIMEFRAME": "1M"},
                ),
                ("Group C (Derivatives)", "#f59e0b", {"INSTRUMENT": "NVDA", "TIMEFRAME": "15m"}),
                (
                    "Group D (Portfolio & Risk)",
                    "#f43f5e",
                    {"PORTFOLIO": "port_institutional_alpha"},
                ),
            ]

            created: list[LinkChannel] = []
            for name, color, initial_ctx in default_defs:
                ch = self.create_channel(
                    owner_user_id=user_id,
                    name=name,
                    display_color_token=color,
                    workspace_id=workspace_id,
                    scope=ContextScope.WORKSPACE if workspace_id else ContextScope.USER_APPLICATION,
                    initial_context=initial_ctx,
                )
                created.append(ch)
            return created
