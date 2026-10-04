# ATLAS Decision Log

## Stage 9: Global Settings
1. `/settings` is the global Settings utility.
2. Main Settings is not one of the 20 core modules, but instead acts as a global utility surface accessible from the bottom-left gear icon.
3. Settings categories use one centralized registry (`config/settings-registry.ts`) to manage routes, titles, descriptions, and search indexing.
4. Settings search is metadata-driven; it uses the centralized registry for rapid client-side filtering without heavy AI dependencies.
5. Global settings (application-wide behavior) and Section settings (module-specific behavior) are distinct systems.
6. Stage 7 Appearance is reused, not duplicated, by plugging directly into the new Settings panel components.
7. Stage 8 Background is reused, not duplicated. The existing engine drives the full settings page natively.
8. Global Settings persists locally where appropriate (`localStorage`, `IndexedDB`).
9. Sensitive credentials (API Keys, Brokers) are not stored insecurely in `localStorage`. Their pages currently exist as structure foundations until a secure vault is built.
10. Unimplemented systems use honest foundation states rather than fake, non-functional inputs.
11. Settings use immediate apply for low-risk UI preferences (Theme, Density, Background).
12. Sensitive future settings will use explicit Save actions.
13. Stable setting IDs are used across the configuration layer.
14. Global preference reset is scoped (e.g. Appearance Reset vs All Settings Reset vs Delete Background Images) to prevent unintended data loss.
15. Secrets will be excluded from any future settings export functionalities.
16. The settings architecture supports future cloud synchronization once an auth layer is provided.
17. Settings precedence is defined as: Defaults → Global → Section → Workspace → Widget.
18. Trading defaults will remain paper/confirmation-first for safety.
19. Agent external actions will remain approval-first.
20. Stage 10 will own per-module (section) settings.
