# Provider Routing Architecture

This document describes the Provider Routing and Fallback architecture for ATLAS.

## Core Concepts

1.  **Provider Routing Policy**: A configuration bound to a `ProviderDomain` (e.g., `market_data`, `news`) and an owner (User or System). It defines a list of candidates in a specific priority order.
2.  **Provider Selection Plan**: The evaluation of a Routing Policy in real-time. It maps the static candidates to their real-time state:
    *   Is the provider currently enabled?
    *   Are the required credentials fully provided?
    *   Is the provider healthy based on recent probes?
3.  **Fallback Planning**: The deterministic evaluation of what happens when the primary selected provider fails during execution.

## Boundary Rules

*   **ATLAS must never silently choose the first registered Provider.** The user or system must explicitly define the routing policy.
*   **Health may make a Provider ineligible, but health must never silently reorder a user's configured Provider chain.** Order is strict. If the #1 provider is unhealthy, it is marked ineligible, and the router proceeds to the #2 provider. It does not swap their positions in the configuration.
*   **Explicit Provider selection must not unexpectedly fall back to another Provider.** If a specific provider is requested by a domain service, only that provider is evaluated. Fallback applies only to domain-based routing.
*   **Provider Routing is domain-scoped.**
*   **Fallback is deny-by-default for business failures and unauthorized actions.** If the user asks for AAPL and the provider correctly answers "Invalid Symbol", we must not fall back to provider #2, because the error is fatal. Fallback applies to network issues, rate limits, timeouts, or unexpected upstream unavailability.
*   **Selection planning performs no external calls, health probes, or secret decryption.** It uses the locally cached configuration state and the latest `ProviderHealthMonitor` results.

## Components

1.  **Repository (`ProviderRoutingRepository`)**: Persists policies to `provider_routing_policies` and `provider_routing_candidates`.
2.  **Service (`ProviderRoutingService`)**: Manages CRUD for routing policies, ensuring validations (max candidates = 16, valid domains).
3.  **Selection (`ProviderSelectionService`)**: Generates a `ProviderSelectionPlan` by cross-referencing candidates with `ProviderConfigurationService` and `ProviderHealthService`.
4.  **Fallback (`ProviderFallbackPlanner`)**: Given a `ProviderSelectionPlan` and an error, determines if fallback is allowed and selects the next eligible candidate strictly sequentially.
5.  **Resolver (`RoutedProviderResolver`)**: A high-level wrapper over `ConfiguredProviderResolver` that uses the `ProviderSelectionPlan` to instantiate the chosen `BaseProvider`.
