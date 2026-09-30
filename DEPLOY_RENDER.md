# Deploy BCIEA Care AI on Render (Free Demo)

> DEMO ONLY: Do not enter real patient names, phone numbers, medical records, or other sensitive health information on the free demo deployment.

## 1. Put this folder on GitHub
1. Create a GitHub account if needed.
2. Create a new repository, for example `bciea-care-ai-demo`.
3. Upload all files from this folder to the repository root.

## 2. Create the Render service
1. Go to https://render.com and sign in.
2. Choose **New > Web Service**.
3. Connect GitHub and select the `bciea-care-ai-demo` repository.
4. If Render detects `render.yaml`, you can use the Blueprint flow. Otherwise set:
   - Runtime: Python
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Plan: Free
5. Add environment variables:
   - `APP_NAME=BCIEA Care AI Demo`
   - `ADMIN_KEY=<create a strong secret value>`
   - `LLM_MODE=none`
   - `DEMO_SEED=true` (loads clearly-labelled FAKE cases so the admin dashboard is not empty; remove for any real use)
6. Deploy.

## 3. Open the demo
Render will give you a URL similar to:
`https://bciea-care-ai-demo.onrender.com`

Website (news + info): `https://YOUR-RENDER-URL/`

AI Portal: `https://YOUR-RENDER-URL/portal`

Admin dashboard (enter the `ADMIN_KEY` shown in Render > Environment):
`https://YOUR-RENDER-URL/admin`

Health test:
`https://YOUR-RENDER-URL/health`

## Important limitation of the free demo
This MVP uses SQLite by default. Render free web services use an ephemeral filesystem, so demo records can disappear after a restart, redeploy, or idle spin-down. This is acceptable for a demonstration using fake data only, not for real BCIEA patient information.

For a real pilot, move to a persistent PostgreSQL database and complete the privacy/security/clinical review before collecting real patient data.
