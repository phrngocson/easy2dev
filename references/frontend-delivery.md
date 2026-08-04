# Frontend delivery

Use this contract whenever a delivery slice creates, changes, repairs, or verifies a user interface. It complements API mapping and feature delivery; it does not make frontend code the owner of backend business rules.

## 1. Discover the existing frontend

Before choosing a style or tool:

1. Inspect the real routes, layouts, components, state management, API clients, assets, fonts, design tokens, CSS conventions, tests, build commands, and supported viewports.
2. Reconstruct the current visual language from repository and runtime evidence. Existing product conventions take priority unless the user approved a redesign.
3. Identify the users, primary task, information hierarchy, interaction states, accessibility constraints, and device contexts relevant to the slice.
4. For API-backed UI, reconcile `docs/API_MAPPING.md`, `docs/api-map.json`, authoritative operations, real client wrappers, and authentication/permission behavior before integration.

Do not ask the user to repeat facts already visible in the repository, design assets, accepted specs, or running application.

## 2. Resolve frontend capability before implementation

Use this ordered capability gate:

1. Inventory frontend or design skills already available in the current session and the agent's discoverable installed-skill catalog. Do this read-only; do not install or modify anything during discovery.
2. Match skills to the actual slice, such as visual design, the detected framework, accessibility, frontend testing, data visualization, or performance. Do not require a hard-coded skill name.
3. If a relevant installed skill exists, read its `SKILL.md` completely, load only its task-relevant references, announce why it applies, and follow it for the frontend slice.
4. If no relevant installed skill exists, invoke the `find-skills` skill and follow its search and quality-verification workflow with a query specific to the need. Prefer a maintained, reputable, inspectable candidate over a generic popularity match.
5. Present vetted candidates and the exact installation action, but never install a discovered skill without explicit user authorization.
6. If `find-skills` is unavailable, no suitable skill is found, or the user declines installation, continue with repository conventions and general frontend capability. This is a fallback path, not permission to leave the frontend undesigned.

Finding or loading a skill does not expand repository, dependency, external-service, or deployment authority.

## 3. Resolve design intent when guidance is missing

First infer what is safe from the existing product, audience, domain, brand assets, and design system. Ask the user only about unresolved choices that materially change the result, normally no more than one to three related questions:

- desired character or visual mood, with a recommended default;
- concrete reference products or brand constraints;
- density, content priority, or device/accessibility needs when these are genuinely ambiguous.

Do not make the user choose implementation libraries, folder structure, or cosmetic details the agent can decide consistently. Record the resolved design intent in the feature plan or spec so later changes do not silently drift.

## 4. Implement a complete UI slice

- Keep components and state ownership modular, with explicit boundaries between presentation, application state, API clients, and backend-owned rules.
- Reuse the established design system and tokens before adding parallel primitives. Any new dependency must follow the dependency manifest and lockfile contract.
- Connect only to mapped, authoritative API operations. Do not invent routes, fabricate successful requests, or move authorization and business invariants into the client.
- Design applicable loading, empty, error, success, validation, disabled, permission-denied, retry, and recovery states.
- Preserve keyboard use, focus visibility, semantic structure, readable contrast, and meaningful labels. Treat accessibility as behavior, not a final polish pass.
- Verify narrow and wide layouts at the supported breakpoints. Avoid solving one viewport by breaking another.
- Protect unaffected routes and shared components with focused regression coverage.

## 5. Keep frontend evidence separate

Report each applicable layer independently:

1. formatting, lint, type checking, and static analysis;
2. component/unit tests and state-transition coverage;
3. production build;
4. API contract and integration tests using real supported behavior;
5. browser runtime smoke for primary and failure paths;
6. responsive and accessibility checks;
7. human visual and usability acceptance.

A passing build does not prove the UI is usable, visually correct, connected to the real backend, or accepted by the user. Never declare frontend `GO` while a required browser, responsive, accessibility, real-integration, or manual-acceptance layer is unverified.
