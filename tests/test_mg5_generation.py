"""MG5 card error detection must catch a zero-exit-code failure."""
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from check_mg5_generation import assess

class MG5GenerationGate(unittest.TestCase):
    def test_catches_user_model_import_failure(self):
        with tempfile.TemporaryDirectory() as root:
            outputs,errors=assess(Path(root),
                "ERROR: mssm model has been replaced by MSSM_SLHA2 model.\n"+
                "Error detected in sub-command import model mssm\n"+
                "command not executed: generate ul dl~ > w+ z QCD=0 QED=2\n")
            self.assertTrue(errors)
            self.assertEqual(len(outputs["MG5_UL_DL_WZ"]),0)

    def test_requires_both_generated_matrices(self):
        with tempfile.TemporaryDirectory() as root:
            base=Path(root)
            for name in ("MG5_UL_DL_WZ","MG5_UL_DL_WA"):
                (base/name/"SubProcesses"/"P0_test").mkdir(parents=True)
                (base/name/"SubProcesses"/"P0_test"/"matrix.f").write_text("C test\n")
            outputs,errors=assess(base,"output standalone complete\n")
            self.assertFalse(errors)
            self.assertTrue(all(outputs.values()))

if __name__=="__main__":
    unittest.main()
