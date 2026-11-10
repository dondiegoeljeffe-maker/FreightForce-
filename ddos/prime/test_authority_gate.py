import unittest
from authority_gate import decide, TABS

class GateTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = {
            TABS[0]: [["LAW_ID", "LAW_TITLE", "RULE", "OWNER", "APPLICABLE_RUNTIMES", "ENFORCEMENT_CHECK", "FAILURE_RESPONSE", "TEST", "LAST_READBACK", "CERTIFICATION_STATE"]] + [[law] + [""] * 8 + ["CERTIFIED"] for law in ("RBP-001", "RBP-002", "RBP-003", "RBP-004")] + [["RBP-006", "", "PARALLEL_ELIGIBLE"] + [""] * 6 + ["PARALLEL_ELIGIBLE"]],
            TABS[1]: [["SECTION_NO", "SECTION", "CANONICAL_SURFACE", "STATUS"],
                      ["1", "Mission", "Current mandate", "CANONICAL"],
                      ["2", "Operating Laws", "LAW_REGISTRY", "CANONICAL"],
                      ["4", "Decision Rights", "EXECUTION_AUTHORITY_LADDER", "ACTIVE"]],
            TABS[2]: [["SMARTBRIEF", "SOURCE_ID", "EXISTING_WORK_ID", "OWNER", "STATE", "MISSING_ACCEPTANCE_GATE", "NEXT", "POD", "DISPOSITION"]] +
                     [["Example", "doc-1", "work-1", "Fo", "DONE", "NONE", "", "provider-proof", "KEEP"]]
        }
    def test_valid_contract(self):
        self.assertTrue(decide(self.snapshot, "work-1", "doc-1")[0])
    def test_canonical_freeze_denied(self):
        self.snapshot[TABS[0]][5][2] = "P0 FREEZE OVERRIDE"
        self.snapshot[TABS[0]][5][9] = "P0_FREEZE_OVERRIDE_ACTIVE"
        self.assertEqual(decide(self.snapshot, "work-1", "doc-1")[1], "P0_FREEZE_ACTIVE")
    def test_missing_freeze_law_denied(self):
        self.snapshot[TABS[0]].pop()
        self.assertEqual(decide(self.snapshot, "work-1", "doc-1")[1], "MISSING_LAW:RBP-006")
    def test_prefixed_apps_script_source(self):
        self.snapshot[TABS[2]][1][1] = "Apps Script doc-1"
        self.assertTrue(decide(self.snapshot, "work-1", "doc-1")[0])
    def test_archived_brief_denied(self):
        self.snapshot[TABS[2]][1][8] = "ARCHIVE / DEDUPED"
        self.assertEqual(decide(self.snapshot, "work-1", "doc-1")[1], "SMARTBRIEF_NOT_EXECUTION_ELIGIBLE")
    def test_missing_playbook_section_denied(self):
        self.snapshot[TABS[1]].pop()
        self.assertEqual(decide(self.snapshot, "work-1", "doc-1")[1], "PLAYBOOK_SECTION_NOT_ACTIVE:4")
    def test_partial_law_denied(self):
        self.snapshot[TABS[0]][2][-1] = "PARTIAL"
        self.assertEqual(decide(self.snapshot, "work-1", "doc-1")[1], "LAW_NOT_CERTIFIED:RBP-002")
    def test_closed_source_denied(self):
        self.snapshot[TABS[2]][1][4] = "CLOSED"
        self.assertEqual(decide(self.snapshot, "work-1", "doc-1")[1], "SMARTBRIEF_NOT_EXECUTION_ELIGIBLE")
    def test_missing_contract_denied(self):
        self.assertFalse(decide(self.snapshot, "work-2", "doc-1")[0])
    def test_uncertified_law_denied(self):
        self.snapshot[TABS[0]][1][-1] = "UNCERTIFIED"
        self.assertEqual(decide(self.snapshot, "work-1", "doc-1")[1], "LAW_NOT_CERTIFIED:RBP-001")
    def test_missing_tab_denied(self):
        del self.snapshot[TABS[1]]
        self.assertFalse(decide(self.snapshot, "work-1", "doc-1")[0])
    def test_unfinished_acceptance_denied(self):
        self.snapshot[TABS[2]][1][5] = "PROVIDER_POD_PENDING"
        self.assertFalse(decide(self.snapshot, "work-1", "doc-1")[0])

if __name__ == "__main__":
    unittest.main()
