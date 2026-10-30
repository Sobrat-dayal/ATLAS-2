"""
Business Logic & Event Coordination Service for ATLAS Stage 121: Global Workspace Linking.
"""

from typing import Any, Optional

from .capabilities import CAPABILITIES_CATALOG, get_panel_capability
from .enums import ContextDimension, ContextScope, SubscriptionMode, TransformationType
from .errors import (
    ContextChannelAccessDeniedError,
    ContextEventLoopDetectedError,
    ContextEventStaleError,
)
from .models import (
    ContextSelectionEvent,
    LinkChannel,
    LinkSubscription,
    PanelContextCapability,
    ResolvedEntity,
)
from .repository import ContextRepository
from .resolution import CanonicalEntityResolver


class ContextLinkingService:
    """Service orchestrating channel lifecycles, event dispatching, and entity resolution."""

    def __init__(self, repository: Optional[ContextRepository] = None):
        self._repo = repository or ContextRepository()
        self._resolver = CanonicalEntityResolver()
        self._processed_event_ids: set[str] = set()

    def list_channels(
        self,
        user_id: str,
        workspace_id: Optional[str] = None,
        scope: Optional[ContextScope] = None,
    ) -> list[LinkChannel]:
        """List active link channels, ensuring default channels exist if empty."""
        channels = self._repo.list_channels(user_id, workspace_id, scope)
        if not channels and workspace_id:
            channels = self._repo.ensure_default_channels(user_id, workspace_id)
        return channels

    def create_channel(
        self,
        user_id: str,
        name: str,
        display_color_token: str = "#3b82f6",
        workspace_id: Optional[str] = None,
        scope: ContextScope = ContextScope.WORKSPACE,
        supported_dimensions: Optional[list[ContextDimension]] = None,
        initial_context: Optional[dict[str, Any]] = None,
    ) -> LinkChannel:
        """Create a link channel for user or workspace."""
        return self._repo.create_channel(
            owner_user_id=user_id,
            name=name,
            display_color_token=display_color_token,
            workspace_id=workspace_id,
            scope=scope,
            supported_dimensions=supported_dimensions,
            initial_context=initial_context,
        )

    def get_channel(self, channel_id: str, user_id: str) -> LinkChannel:
        """Retrieve a link channel, validating ownership."""
        ch = self._repo.get_channel(channel_id)
        if ch.owner_user_id != user_id:
            raise ContextChannelAccessDeniedError(channel_id)
        return ch

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
        """Update channel configuration."""
        return self._repo.update_channel(
            channel_id=channel_id,
            user_id=user_id,
            name=name,
            display_color_token=display_color_token,
            scope=scope,
            enabled=enabled,
            supported_dimensions=supported_dimensions,
        )

    def delete_channel(self, channel_id: str, user_id: str) -> None:
        """Delete link channel."""
        self._repo.delete_channel(channel_id, user_id)

    def list_memberships(self, channel_id: str, user_id: str) -> list[LinkSubscription]:
        """List subscriptions for channel."""
        self.get_channel(channel_id, user_id)  # Validate ownership
        return self._repo.list_memberships(channel_id)

    def add_membership(
        self,
        channel_id: str,
        user_id: str,
        panel_instance_id: str,
        mode: SubscriptionMode = SubscriptionMode.BIDIRECTIONAL,
        inbound_dimensions: Optional[list[ContextDimension]] = None,
        outbound_dimensions: Optional[list[ContextDimension]] = None,
        priority_policy: str = "NORMAL",
    ) -> LinkSubscription:
        """Register a panel into a channel."""
        self.get_channel(channel_id, user_id)
        return self._repo.add_membership(
            channel_id=channel_id,
            panel_instance_id=panel_instance_id,
            mode=mode,
            inbound_dimensions=inbound_dimensions,
            outbound_dimensions=outbound_dimensions,
            priority_policy=priority_policy,
        )

    def update_membership(
        self,
        subscription_id: str,
        user_id: str,
        mode: Optional[SubscriptionMode] = None,
        inbound_dimensions: Optional[list[ContextDimension]] = None,
        outbound_dimensions: Optional[list[ContextDimension]] = None,
        active: Optional[bool] = None,
    ) -> LinkSubscription:
        """Update dimensions and mode for membership."""
        return self._repo.update_membership(
            subscription_id=subscription_id,
            mode=mode,
            inbound_dimensions=inbound_dimensions,
            outbound_dimensions=outbound_dimensions,
            active=active,
        )

    def remove_membership(self, subscription_id: str, user_id: str) -> None:
        """Remove membership."""
        self._repo.remove_membership(subscription_id)

    def get_channel_state(self, channel_id: str, user_id: str) -> dict[str, Any]:
        """Get active context snapshot."""
        ch = self.get_channel(channel_id, user_id)
        return {
            "channel_id": ch.channel_id,
            "revision": ch.revision,
            "context": ch.context_snapshot,
            "updated_at": ch.updated_at.isoformat(),
        }

    def update_channel_state(
        self,
        channel_id: str,
        user_id: str,
        context_updates: dict[str, Any],
        expected_revision: Optional[int] = None,
    ) -> LinkChannel:
        """Update context with optimistic revision check."""
        return self._repo.update_context_state(
            channel_id=channel_id,
            user_id=user_id,
            context_updates=context_updates,
            expected_revision=expected_revision,
        )

    def resolve_entity(
        self,
        query: str,
        entity_type: str = "INSTRUMENT",
        target_transformation: Optional[TransformationType] = None,
    ) -> ResolvedEntity:
        """Resolve a query to a canonical entity and optionally transform it."""
        if entity_type == "INSTRUMENT":
            resolved = self._resolver.resolve_instrument(query)
        elif entity_type == "COMPANY":
            resolved = self._resolver.resolve_company(query)
        elif entity_type == "PORTFOLIO":
            resolved = self._resolver.resolve_portfolio(query)
        elif entity_type == "BENCHMARK":
            resolved = self._resolver.resolve_benchmark(query)
        elif entity_type == "ECONOMIC_SERIES":
            resolved = self._resolver.resolve_economic_series(query)
        else:
            resolved = self._resolver.resolve_instrument(query)

        if target_transformation:
            return self._resolver.transform_entity(resolved.entity_id, target_transformation)

        return resolved

    def get_capabilities(self, panel_type_id: Optional[str] = None) -> list[PanelContextCapability]:
        """Retrieve capability definitions for panels."""
        if panel_type_id:
            cap = get_panel_capability(panel_type_id)
            return [cap] if cap else []
        return list(CAPABILITIES_CATALOG.values())

    def dispatch_event(self, event: ContextSelectionEvent) -> dict[str, Any]:
        """Process an inbound context selection event with deduplication and loop detection."""
        # 1. Deduplication check
        if event.event_id in self._processed_event_ids:
            return {
                "status": "DUPLICATE_DROPPED",
                "event_id": event.event_id,
                "delivered_count": 0,
            }

        # 2. Loop detection via causation echo
        if event.causation_id and event.causation_id in self._processed_event_ids:
            # Check if this panel originated the causation
            if event.origin_panel_instance_id and event.payload.get("echo_suppressed"):
                raise ContextEventLoopDetectedError(event.event_id, event.causation_id)

        # 3. Channel revision validation
        channel = self._repo.get_channel(event.channel_id)
        if event.context_revision < channel.revision:
            raise ContextEventStaleError(event.context_revision, channel.revision)

        # 4. Update channel context
        updates = {event.dimension.value: event.canonical_target_id}
        if "symbol" in event.payload:
            updates["SYMBOL"] = event.payload["symbol"]
        if "timeframe" in event.payload:
            updates["TIMEFRAME"] = event.payload["timeframe"]
        if "reporting_currency" in event.payload:
            updates["REPORTING_CURRENCY"] = event.payload["reporting_currency"]

        updated_channel = self._repo.update_context_state(
            channel_id=event.channel_id,
            user_id=event.origin_user_id or channel.owner_user_id,
            context_updates=updates,
        )

        # 5. Locate active subscribers
        memberships = self._repo.list_memberships(event.channel_id)
        delivered_to: list[str] = []

        for m in memberships:
            if not m.active:
                continue
            if m.mode == SubscriptionMode.INDEPENDENT or m.mode == SubscriptionMode.PUBLISH:
                continue
            if m.panel_instance_id == event.origin_panel_instance_id:
                # Do not echo back to origin panel
                continue
            if event.dimension not in m.inbound_dimensions:
                continue

            delivered_to.append(m.panel_instance_id)

        self._processed_event_ids.add(event.event_id)
        if len(self._processed_event_ids) > 10000:
            self._processed_event_ids.clear()

        return {
            "status": "DELIVERED",
            "event_id": event.event_id,
            "channel_id": event.channel_id,
            "revision": updated_channel.revision,
            "delivered_count": len(delivered_to),
            "delivered_panel_ids": delivered_to,
        }
