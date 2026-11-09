# Prime operating contract
1. Inspect canonical work ID and existing artifacts before making changes; merge over create.
2. Build locally in the owner-controlled repository when tools allow; use scoped branches for production changes.
3. Verify source, public URLs, and tests; do not infer delivery from a worker's assertion.
4. Hand off only unavailable capabilities; require reproducible source and provider receipts.
5. Write outcomes to existing Master Ledger and Client Zero Master File through authorized connectors, then read back.
6. Do not mark CLOSED until provider execution and canonical evidence are verified.
7. Escalate credentials, spending, legal decisions, public statements, and irreversible actions.
8. Keep secrets out of git; use an owner-managed secrets store.
9. This repository is public and currently also hosts website branches. Keep runtime code isolated under ddos/ and do not change gh-pages.
