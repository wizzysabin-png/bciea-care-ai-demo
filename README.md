# BCIEA Care AI — Improved Demo v3

A responsive breast-health education and patient-navigation prototype for BCIEA. It includes a public website, ChatGPT-style multilingual AI portal, referral workflow, staff command centre, demo messaging centre, local conversation history, voice input, safety triage, and privacy-aware case creation.

## Ultra layer (added on v3, nothing removed)
Purely additive files: `static/ultra.css`, `static/ultra.js`, `static/map3d.js`.
- **Scroll animations:** progress bar, staggered 3D reveals (flip / slide / zoom), parallax hero cards, floating 3D gems, count-up impact numbers, cursor glow.
- **3D Rwanda network map** (landing `#network`, admin Dashboard, mini version in the portal): rotating, drag-to-rotate, shows village -> sector -> district hub -> AI core (Kigali). In the portal every chat message lights a path, coloured by triage level.
- The map is an **illustrative simulation**: outline and hub positions are stylised and traffic is not patient data. Real geographic data would need GIS boundaries, consent and privacy review.
- Respects `prefers-reduced-motion`. To remove the layer, delete the three files and their tags.

## Important safety note
This prototype is **not a diagnostic medical device**. It cannot diagnose or rule out breast cancer and should not replace professional medical assessment. Before collecting real patient information, BCIEA should complete clinician review, privacy/data-protection review, security hardening, hosting review and referral-pathway validation.

## What is included in v3

### Public website `/`
- New responsive pink/white 3D-style design
- New BAI / BCIEA Care AI demo logo
- BCIEA impact-number section
- Eight health/support categories
- Hero illustration and local sample media
- Featured video placeholder
- Patient-journey section
- Animated scroll/reveal effects
- Mobile navigation

### AI portal `/portal`
- ChatGPT-style left sidebar
- New chat button
- Local conversation history using the browser's localStorage
- Topic shortcuts for breast health, screening, symptoms, emotional support, healthy living and privacy
- Kinyarwanda + English selector
- Browser microphone input where supported
- Save-chat button
- Clean full-width chat experience
- Slide-out care-plan drawer instead of showing every widget all the time
- Live urgency score, signals, care plan, consented case creation and human navigator request

### Staff dashboard `/admin`
- Modern sidebar dashboard
- Overview metrics
- Triage and barrier analytics
- Conversation list + conversation message viewer
- Referral priority queue, facility field, notes and status updates
- Privacy-minimised case list
- Demo message/broadcast centre
- Audit log
- Content/media guidance page

### Backend
- Existing API and deployment structure preserved
- Added `BroadcastMessage` table (safe additive database change)
- Added admin conversation/case/message APIs
- SQLite by default; PostgreSQL-ready via `DATABASE_URL`
- Optional Ollama mode remains disabled by default

## Run locally
1. Install Python 3.12 (recommended).
2. Open a terminal in this folder.
3. Create a virtual environment:
   - Windows: `python -m venv .venv && .venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`
4. Install: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and change `ADMIN_KEY`.
6. Start: `uvicorn app.main:app --reload`
7. Website: `http://127.0.0.1:8000`
8. Portal: `http://127.0.0.1:8000/portal`
9. Admin: `http://127.0.0.1:8000/admin`

## Update your existing Render deployment
You do **not** need to create a new Render service.

1. Upload/replace the files in the same GitHub repository you already connected to Render.
2. Keep the same repository root structure (`app/`, `requirements.txt`, `render.yaml`, etc.).
3. Commit the changes to the same branch Render uses (normally `main`).
4. Render should auto-deploy. If it does not, use **Manual Deploy > Deploy latest commit**.
5. Keep these environment variables in Render:
   - `PYTHON_VERSION=3.12.11`
   - `APP_NAME=BCIEA Care AI Demo`
   - `LLM_MODE=none`
   - `ADMIN_KEY=<your private strong value>`
6. For a fake-data demo you may use `DEMO_SEED=true`. Do not use demo seed for real operations.

## Logo and media
The demo logo is:
`app/static/assets/bai-logo.svg`

Sample local media is in:
`app/static/assets/`

To use an official BCIEA logo or approved photos, copy them into the assets folder and update the image path in `index.html`, `portal.html` and `admin.html`. The file `UPLOAD_YOUR_LOGO_HERE.txt` contains a quick reminder.

## Demo message centre
The dashboard's message centre stores draft/sent message records inside the app. **It does not actually send SMS, WhatsApp or email yet.** Connecting a real provider should be a later, reviewed step.

## Free Render warning
A free Render web service has temporary storage. SQLite data can disappear after restarts/redeploys. Use **fictional/demo information only** on the free demo. Real patient deployment should use an appropriately secured persistent database and approved infrastructure.

## Recommended production upgrades
- Staff accounts, MFA and role-based access control
- Persistent PostgreSQL
- Field-level encryption for sensitive information
- Secure backups and key management
- Approved WhatsApp/SMS/email provider integration
- Facility directory and appointment workflows
- Consent withdrawal and data-subject request workflows
- Kinyarwanda clinical/language QA
- Clinician validation of triage rules
- Monitoring, incident response and audit retention
- FHIR-compatible interoperability where appropriate
