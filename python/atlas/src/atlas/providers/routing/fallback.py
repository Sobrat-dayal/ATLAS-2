import logging

from atlas.providers.routing.models import (
    ProviderFailureDisposition,
    ProviderFallbackDecision,
    ProviderSelectionMode,
    ProviderSelectionPlan,
)

logger = logging.getLogger(__name__)


class ProviderFallbackPlanner:
    def classify_failure(self, error: Exception) -> ProviderFailureDisposition:
        # Deny by default
        error_str = str(error)

        # Translate generic error messages to classes (conceptually, assuming these are the exceptions or messages)
        # Timeout, UpstreamUnavailable, RateLimited -> Allowed
        if "PROVIDER_TIMEOUT" in error_str or "timeout" in error_str.lower():
            return ProviderFailureDisposition.FALLBACK_ALLOWED
        if (
            "PROVIDER_UPSTREAM_UNAVAILABLE" in error_str
            or "upstream unavailable" in error_str.lower()
        ):
            return ProviderFailureDisposition.FALLBACK_ALLOWED
        if "PROVIDER_RATE_LIMITED" in error_str or "rate limited" in error_str.lower():
            return ProviderFailureDisposition.FALLBACK_ALLOWED
        if "PROVIDER_INVALID_RESPONSE" in error_str:
            return ProviderFailureDisposition.FALLBACK_ALLOWED

        return ProviderFailureDisposition.FALLBACK_DENIED

    def plan_fallback(
        self, plan: ProviderSelectionPlan, failed_provider_key: str, error: Exception
    ) -> ProviderFallbackDecision:
        if plan.mode != ProviderSelectionMode.POLICY:
            return ProviderFallbackDecision(
                allowed=False,
                reason="Fallback disabled for explicit selection",
                failed_provider_key=failed_provider_key,
                next_provider_key=None,
                remaining_candidates=0,
            )

        if not plan.fallback_enabled:
            return ProviderFallbackDecision(
                allowed=False,
                reason="Fallback disabled by routing policy",
                failed_provider_key=failed_provider_key,
                next_provider_key=None,
                remaining_candidates=0,
            )

        disposition = self.classify_failure(error)
        if disposition != ProviderFailureDisposition.FALLBACK_ALLOWED:
            return ProviderFallbackDecision(
                allowed=False,
                reason="Failure classification denied fallback",
                failed_provider_key=failed_provider_key,
                next_provider_key=None,
                remaining_candidates=0,
            )

        # Find failed provider position
        failed_index = -1
        for i, cand in enumerate(plan.candidates):
            if cand.provider_key == failed_provider_key:
                failed_index = i
                break

        if failed_index == -1:
            # Failed provider was not in the plan
            return ProviderFallbackDecision(
                allowed=False,
                reason="Failed provider not found in selection plan",
                failed_provider_key=failed_provider_key,
                next_provider_key=None,
                remaining_candidates=0,
            )

        # Find next eligible candidate strictly forward
        for i in range(failed_index + 1, len(plan.candidates)):
            cand = plan.candidates[i]
            if cand.eligible:
                return ProviderFallbackDecision(
                    allowed=True,
                    reason="Fallback permitted to next eligible candidate",
                    failed_provider_key=failed_provider_key,
                    next_provider_key=cand.provider_key,
                    remaining_candidates=len(plan.candidates) - i - 1,
                )

        return ProviderFallbackDecision(
            allowed=False,
            reason="Fallback exhausted; no remaining eligible candidates",
            failed_provider_key=failed_provider_key,
            next_provider_key=None,
            remaining_candidates=0,
        )
