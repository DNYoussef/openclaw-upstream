# GuardSpine Main Repo Audit (Recheck)

Date: 2026-02-02
Repo: D:\Projects\GuardSpine
Scope: Backend API, evidence bundles, auth, webhooks, connectors, and integration surfaces.

## Status vs 2026-02-01

Fixed (12):

- Auth enforcement added on routers via Depends(require_auth/require_admin).
- Webhook signature missing now rejects; per-provider verification implemented.
- Credential encryption replaced with Fernet (requires GUARDSPINE_FERNET_KEY).
- OAuth state persistence + token exchange implemented.
- Signing service now Ed25519 with required GUARDSPINE_SIGNING_KEY.
- Webhook rate limiting added.
- Evidence bundle schema + hash chain updated to v0.2.0.
- Bundle signatures now generated via signing_service (no mock signatures).
- Demo data/seeded connectors gated behind GUARDSPINE_DEMO_MODE.
- Webhook test endpoint gated to demo/dev only.
- Auth data now persisted to disk (local JSON store).
- OIDC SSO callback implemented (code exchange + id_token verification).

Still Open (1):

- SAML callback handling remains unimplemented.

## Findings (Current)

1. LOW — SAML callback handling not implemented
   - Evidence: handle_sso_callback returns saml_not_implemented when saml_response is provided.
   - Impact: SAML IdPs cannot complete SSO flow yet.
   - Files: D:\Projects\GuardSpine\backend\app\services\auth_service.py
