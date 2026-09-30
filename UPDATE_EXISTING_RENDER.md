# Updating the same Render demo

Use the **same GitHub repository and same Render Web Service** you already created.

1. On GitHub, replace the old project files with the contents of this folder. Keep `app`, `requirements.txt`, `render.yaml`, `.python-version`, and the other files at repository root.
2. Commit to `main` (or whichever branch your Render service watches).
3. In Render > Environment, keep:
   - `PYTHON_VERSION` = `3.12.11`
   - `APP_NAME` = `BCIEA Care AI Demo`
   - `LLM_MODE` = `none`
   - `ADMIN_KEY` = your private strong secret
4. Render normally auto-deploys the new commit. If not: Deploys > Manual Deploy > Deploy latest commit.
5. If dependency errors appear: Deploys > Manual Deploy > Clear build cache & deploy.
6. Visit `/health`, then `/`, `/portal`, and `/admin`.

Do not put real patient information into the free demo.
