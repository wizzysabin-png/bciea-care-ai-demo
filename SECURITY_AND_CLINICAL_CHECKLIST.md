# Security and Clinical Deployment Checklist

Do not deploy this MVP to real patients until these are addressed.

## Clinical governance
- Appoint a clinical owner.
- Review every triage rule with licensed clinicians.
- Approve Kinyarwanda translations with health professionals and native speakers.
- Define emergency, urgent, routine, and referral pathways.
- Test false negatives and false positives.
- Create escalation and incident procedures.

## Privacy and data protection
- Complete a DPIA.
- Define controller/processor roles.
- Create patient-facing consent and privacy notices.
- Minimize stored data.
- Encrypt sensitive fields and backups.
- Implement access control, MFA, staff offboarding, and audit review.
- Define retention/deletion rules and data-subject request procedures.
- Review hosting location and any cross-border transfers.

## Technical
- Replace MVP admin key with accounts + RBAC + MFA.
- Use PostgreSQL in production.
- Put the app behind HTTPS.
- Add rate limiting and WAF/reverse proxy.
- Add secrets management.
- Add backup/restore tests.
- Add monitoring, error tracking, and security logs.
- Run dependency, code, and penetration testing.

## AI quality
- Maintain an approved knowledge base with versioning and citations.
- Evaluate hallucination rate, unsafe advice, language quality, and escalation accuracy.
- Keep a human-review queue.
- Never allow an LLM to override hard safety rules.
