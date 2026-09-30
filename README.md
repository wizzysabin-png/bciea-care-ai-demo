# BCIEA Care AI — MVP

A privacy-conscious prototype for breast-health education, patient navigation, symptom intake, referral support, multilingual chat, and human escalation.

## Important
This is **not a diagnostic medical device** and must not be used to diagnose or rule out breast cancer. Clinical workflows, triage rules, language content, privacy controls, hosting, and referral pathways must be reviewed by BCIEA clinical/legal/data-protection teams before real patient deployment.

## Features
- English + Kinyarwanda patient chat
- Browser voice input (where supported)
- Conservative rule-based safety triage
- Breast-health knowledge retrieval
- Patient/case capture with consent flag
- Referral creation and status management
- Admin dashboard
- Audit log
- SQLite by default; PostgreSQL-ready through `DATABASE_URL`
- Optional local Ollama integration (disabled by default)

## Run locally
1. Install Python 3.11+
2. Open a terminal in this folder
3. Create a virtual environment:
   - Windows: `python -m venv .venv && .venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`
4. Install packages: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and change `ADMIN_KEY`
6. Start: `uvicorn app.main:app --reload`
7. Open: http://127.0.0.1:8000
8. Admin: http://127.0.0.1:8000/admin

## Admin access
The admin page asks for the value of `ADMIN_KEY`. This is intentionally simple for the MVP. Replace it with real user accounts, MFA, RBAC, password hashing, and SSO before production.

## Optional local LLM
Set `LLM_MODE=ollama` and run an Ollama model locally. The app will use the LLM only to draft a response after the safety engine and knowledge retrieval run. No cloud LLM is configured by default.

## Suggested next production upgrades
- Proper identity provider + MFA + role-based access control
- PostgreSQL + encrypted fields + managed secrets
- Clinician/navigator queues
- FHIR interoperability
- WhatsApp/SMS integration
- Facility directory and appointment booking
- Consent withdrawal and data-subject request workflows
- Encryption key management, backups, monitoring, incident response
- Clinical validation and Kinyarwanda QA with health professionals
