import unittest
from authority_gate import decide, TABS

class GateTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = {
            TABS[0]: [["LAW_ID"] + [""] * 9] + [[law] + [""] * 8 + ["CERTIFIED"] for law in ("RBP-001", "RBP-002", "RBP-003", "RBP-004")],
            TABS[1]: [["SECTION_NO", "SECTION", "CANONICAL_SURFACE", "STATUS"]],
            TABS[2]: [["SMARTBRIEF", "SOURCE_ID", "EXISTING_WORK_ID", "OWNER", "STATE", "MISSING_ACCEPTANCE_GATE", "NEXT", "POD", "DISPOSITION"]] +
                     [["Example", "doc-1", "work-1", "Fo", "DONE", "NONE", "", "provider-proof", "KEEP"]]
        }
    def test_valid_contract(self):
        self.assertTrue(decide(self.snapshot, "work-1", "doc-1")[0])
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
