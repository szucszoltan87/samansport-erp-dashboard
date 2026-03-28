# Security Audit Report — SamanSport ERP Dashboard

**Date:** 2026-03-20
**Branch:** `feature/phase-3-secrets-audit`
**Auditor:** Claude Code

---

## 1. `.env` in `.gitignore`

**Status: PASS**

- `.env` is listed in both `/.gitignore` (line 13) and `/app_layer/.gitignore` (line 3).
- `.env.example` is correctly excluded from the ignore rule with `!.env.example`.

## 2. Git History — Accidentally Committed Secrets

**Status: PASS**

Scanned `git log --all -p` for: `password`, `api_key`, `service_role`, `secret`, `eyJhbGciOi` (JWT prefix), and `sb_` (Supabase key prefix).

**Findings:**
- All occurrences of `password`, `api_key`, `service_role` are **placeholder values** (`your_password_here`, `your_api_key_here`, empty strings) in `.env.example`, roadmap docs, or code templates.
- **No real secrets, tokens, or API keys** were found in git history.
- The `.env` file was **never committed** to the repository.

## 3. `service_role` Key Usage in Python Code

**Status: PASS**

- `SUPABASE_SERVICE_ROLE_KEY` is **not used anywhere in Python code** (`app_layer/`).
- It is **correctly confined** to Deno Edge Functions:
  - `supabase/functions/_shared/supabase-admin.ts:9`
  - `supabase/functions/hydrate-all/index.ts:70`
  - `supabase/functions/cron-refresh/index.ts:46`
- The Python Streamlit app only uses `SUPABASE_ANON_KEY` (read-only, safe to expose).

## 4. SOAP Credentials — Frontend Exposure

**Status: LOW RISK (acceptable)**

- SOAP credentials (`THARANIS_API_KEY`, `THARANIS_UGYFELKOD`, `THARANIS_CEGKOD`) are loaded server-side in `tharanis_client.py` via `os.getenv()`.
- Streamlit runs Python on the server — these values are **never sent to the browser**.
- The API key defaults to an empty string (safe). Customer/company codes (`7354`, `ab`) are hardcoded defaults — these are tenant identifiers, not secrets.
- SOAP fallback sends credentials over HTTPS to `login.tharanis.hu`.

## 5. `.env.example`

**Status: PASS — already exists**

- Located at `app_layer/.env.example` with proper structure and clear comments.
- Service role key entry is present but empty, with a "NEVER commit actual values" warning.
- All required variables are documented.

---

## Additional Findings

### 5a. SSL Verification Disabled (MEDIUM)

**File:** `app_layer/tharanis_client.py:382`

```python
r = requests.post(_API_URL, ..., verify=False, timeout=120)
```

The SOAP fallback disables SSL certificate verification. Line 34 also suppresses the `Unverified HTTPS` warning. This makes the connection vulnerable to man-in-the-middle attacks.

**Recommendation:** Remove `verify=False` and the warning suppression. If the Tharanis server has a self-signed cert, pin the certificate or add it to the trust store instead.

### 5b. Edge Functions JWT Verification Disabled (MEDIUM)

**File:** `supabase/config.toml`

All four Edge Functions have `verify_jwt = false`. This means anyone who knows the function URL can invoke them without authentication.

**Recommendation:** Enable JWT verification (`verify_jwt = true`) and pass the anon key or service role key in the Authorization header when calling functions. This is tracked in the roadmap (Phase 3.2).

---

## Summary

| Check | Status | Severity |
|-------|--------|----------|
| `.env` in `.gitignore` | PASS | — |
| Secrets in git history | PASS | — |
| `service_role` in Python | PASS | — |
| SOAP creds in frontend | PASS | LOW |
| `.env.example` exists | PASS | — |
| SSL verification disabled | FINDING | MEDIUM |
| JWT verification disabled | FINDING | MEDIUM |

**Overall: No critical or high-severity issues.** Two medium-severity items flagged for remediation.
