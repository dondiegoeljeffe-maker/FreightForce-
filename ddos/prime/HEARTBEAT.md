# Prime heartbeat specification — NOT YET SCHEDULED
At each authorized runtime invocation:
- Read existing Master Ledger open work and canonical inventory.
- Select the highest-priority executable item without a new tracker.
- Check custody: owned source location, revision, accessible artifact, owner and recovery instructions.
- Check public endpoints when appropriate and bounded.
- Repair within granted authority, run tests, capture receipts, and write/read back canonical results.
- If blocked, preserve WORK_ID, owner, exact blocker, next action and retry policy.
No heartbeat is active until an owner-controlled runner is configured, invoked, and its provider logs independently verified.
