#!/usr/bin/env python3
"""DDOS Prime pre-dispatch authority gate. Never executes a business action.
Requires a live owner-authorized Google Sheets service account; fails closed.
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

SHEET_ID = "1DAD4kLdf7A450Yu_J1yFSpO6HtbgPRPgFIGuzWN2krk"
REQUIRED_LAWS = ("RBP-001", "RBP-002", "RBP-003", "RBP-004")
BLOCKED = ("UNCERTIFIED", "PENDING", "UNVERIFIED", "BLOCKED", "PARTIAL")
TABS = ("LAW_REGISTRY!A1:J250", "OPERATING_PLAYBOOK_INDEX!A1:D100",
        "SMARTBRIEF_CLOSURE_REGISTER!A1:J1500")

def decide(snapshot, work_id, source_id):
    if not work_id or not source_id:
        return False, "MISSING_WORK_ID_OR_SOURCE"
    if not all(tab in snapshot for tab in TABS):
        return False, "MISSING_CANONICAL_TAB"
    laws = snapshot[TABS[0]]
    if not laws or len(laws[0]) < 10 or laws[0][0] != "LAW_ID" or laws[0][9] != "CERTIFICATION_STATE":
        return False, "INVALID_LAW_REGISTRY_SCHEMA"
    found = {r[0]: r for r in laws[1:] if len(r) >= 10}
    for law in REQUIRED_LAWS:
        if law not in found:
            return False, "MISSING_LAW:" + law
        if found[law][9].strip().upper() != "CERTIFIED":
            return False, "LAW_NOT_CERTIFIED:" + law
    playbook = snapshot[TABS[1]]
    if not playbook or playbook[0][:4] != ["SECTION_NO", "SECTION", "CANONICAL_SURFACE", "STATUS"]:
        return False, "INVALID_PLAYBOOK_SCHEMA"
    required_sections = {str(r[0]): r for r in playbook[1:] if len(r) >= 4}
    for section in ("1", "2", "4"):
        if section not in required_sections or required_sections[section][3].upper() not in ("CANONICAL", "ACTIVE"):
            return False, "PLAYBOOK_SECTION_NOT_ACTIVE:" + section
    briefs = snapshot[TABS[2]]
    if not briefs or briefs[0][:3] != ["SMARTBRIEF", "SOURCE_ID", "EXISTING_WORK_ID"] or len(briefs[0]) < 9:
        return False, "INVALID_SMARTBRIEF_SCHEMA"
    matches = [r for r in briefs[1:] if len(r) >= 9 and
               work_id in [v.strip() for v in r[2].split(";")] and
               source_id in [v.strip() for v in r[1].split(";")]]
    if not matches:
        return False, "NO_MATCHING_SMARTBRIEF_CONTRACT"
    if any(any(flag in r[8].upper() for flag in ("ARCHIVE", "SUPERSEDED", "CLOSED", "CANCELLED")) or
           any(flag in r[4].upper() for flag in ("CLOSED", "CANCELLED")) for r in matches):
        return False, "SMARTBRIEF_NOT_EXECUTION_ELIGIBLE"
    if not all(r[5].strip().upper() in ("", "NONE", "COMPLETE", "PASSED") for r in matches):
        return False, "SMARTBRIEF_ACCEPTANCE_INCOMPLETE"
    return True, "AUTHORIZED_FOR_SEPARATE_EXECUTOR_REVIEW"

def live_snapshot():
    import google.auth
    from google.auth.transport.requests import Request
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
    creds.refresh(Request())
    output = {}
    for tab in TABS:
        url = ("https://sheets.googleapis.com/v4/spreadsheets/" + SHEET_ID +
               "/values/" + urllib.parse.quote(tab, safe="") )
        req = urllib.request.Request(url, headers={"Authorization": "Bearer " + creds.token})
        with urllib.request.urlopen(req, timeout=15) as response:
            output[tab] = json.load(response).get("values", [])
    return output

def main():
    work_id = os.environ.get("DDOS_WORK_ID", "")
    source_id = os.environ.get("DDOS_SOURCE_ID", "")
    try:
        snapshot = live_snapshot()
        allowed, reason = decide(snapshot, work_id, source_id)
    except Exception as exc:
        allowed, reason = False, "LIVE_CANONICAL_READ_FAILED:" + type(exc).__name__
    result = {"worker": "Diego Prime", "gate": "pre-dispatch",
              "timestamp_utc": datetime.now(timezone.utc).isoformat(),
              "work_id": work_id, "source_id": source_id,
              "allowed": allowed, "reason": reason,
              "executed": False, "ledger_written": False}
    print(json.dumps(result, sort_keys=True))
    return 0 if allowed else 2

if __name__ == "__main__":
    sys.exit(main())
