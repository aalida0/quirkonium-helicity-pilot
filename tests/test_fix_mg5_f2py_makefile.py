"""Pure Python regression for reversible MG5 f2py launcher patch."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from fix_mg5_f2py_makefile import replace_launcher

class TestMG5F2PYMakefile(unittest.TestCase):
    def test_patch_hardcoded_numpy_121_launcher(self):
        raw="F2PY=f2py3.10\nmatrix2py.so:\n\tf2py3.10 -c matrix.f -m matrix2py --f77exec=gfortran\n"
        result,count=replace_launcher(raw,Path("/tmp/venv/bin/python"))
        self.assertEqual(count,2)
        self.assertNotIn("f2py3.10",result)
        self.assertIn("/tmp/venv/bin/python -m numpy.f2py -c matrix.f",result)
        result2,count2=replace_launcher(result,Path("/tmp/venv/bin/python"))
        self.assertEqual(count2,0)
        self.assertEqual(result,result2)
    def test_refuse_unknown_makefile_format(self):
        with self.assertRaisesRegex(ValueError,"No f2py3.10"):
            replace_launcher("matrix2py.so:\n\tpython -c foo\n","/tmp/python")
    def test_preserves_nonf2py_commands(self):
        raw="\tgfortran -c matrix.f\n\tf2py3.10 -c matrix.f\n"
        out,_=replace_launcher(raw,Path("/tmp/venv/bin/python"))
        self.assertIn("gfortran -c matrix.f",out)

if __name__=="__main__":
    unittest.main()
