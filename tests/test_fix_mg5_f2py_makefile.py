"""Pure Python regression for reversible MG5 f2py launcher patch."""
import sys
import unittest
import tempfile
from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch,Mock
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from fix_mg5_f2py_makefile import replace_launcher,shim_source,main

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
    def test_shim_uses_venv_python_without_resolving_symlink(self):
        py=Path("/home/example/research/.venv-mg5-f2py/bin/python")
        contents=shim_source(py)
        self.assertIn(str(py),contents)
        self.assertIn(' -m numpy.f2py "$@"',contents)
        self.assertNotIn("/usr/bin/python3.10",contents)

    def test_variable_based_makefile_uses_local_shim_without_modifying_source(self):
        # Real generated makefiles can construct the command via a variable.
        import numpy
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            prefix=folder/"venv"
            bindir=prefix/"bin"
            bindir.mkdir(parents=True)
            py=str(bindir/"python")
            for name in ("MG5_UL_DL_WZ","MG5_UL_DL_WA"):
                makefile=folder/name/"SubProcesses"/"P1"/"makefile"
                makefile.parent.mkdir(parents=True)
                makefile.write_text(
                    "F2PY = f2py$(PYTHON_VERSION)\n"
                    "matrix2py.so:\n\t$(F2PY) -c matrix.f -m matrix2py\n")
            mocked=Mock(returncode=0,stdout=numpy.__version__+"\n",stderr="")
            args=["fix_mg5_f2py_makefile.py","--root",str(folder),"--apply"]
            with (patch.object(sys,"argv",args),
                  patch.object(sys,"executable",py),
                  patch.object(sys,"prefix",str(prefix)),
                  patch.object(sys,"base_prefix","/usr"),
                  patch("fix_mg5_f2py_makefile.subprocess.run",return_value=mocked),
                  redirect_stdout(StringIO())):
                main()
            shim=bindir/"f2py3.10"
            self.assertTrue(shim.is_file())
            self.assertEqual(shim.read_text(),shim_source(Path(py)))
            self.assertTrue(shim.stat().st_mode & 0o111)
            for name in ("MG5_UL_DL_WZ","MG5_UL_DL_WA"):
                makefile=folder/name/"SubProcesses"/"P1"/"makefile"
                self.assertIn("$(F2PY)",makefile.read_text())
                self.assertFalse((makefile.parent/
                                  "makefile.before_quirkonium_f2py").exists())

    def test_accept_existing_venv_f2py3_10_from_numpy(self):
        import numpy
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            prefix=folder/"venv"
            bindir=prefix/"bin"
            bindir.mkdir(parents=True)
            py=str(bindir/"python")
            original="#!/usr/bin/env python\n# numpy-installed launcher\n"
            launcher=bindir/"f2py3.10"
            launcher.write_text(original)
            launcher.chmod(0o755)
            for name in ("MG5_UL_DL_WZ","MG5_UL_DL_WA"):
                makefile=folder/name/"SubProcesses"/"P1"/"makefile"
                makefile.parent.mkdir(parents=True)
                makefile.write_text("F2PY = f2py$(PYTHON_VERSION)\n")
            mocked=Mock(returncode=0,stdout=numpy.__version__+"\n",stderr="")
            args=["fix_mg5_f2py_makefile.py","--root",str(folder),"--apply"]
            with (patch.object(sys,"argv",args),
                  patch.object(sys,"executable",py),
                  patch.object(sys,"prefix",str(prefix)),
                  patch.object(sys,"base_prefix","/usr"),
                  patch("fix_mg5_f2py_makefile.subprocess.run",return_value=mocked),
                  redirect_stdout(StringIO())):
                main()
            self.assertEqual(launcher.read_text(),original)
            self.assertTrue(launcher.stat().st_mode & 0o111)

    def test_preserves_nonf2py_commands(self):
        raw="\tgfortran -c matrix.f\n\tf2py3.10 -c matrix.f\n"
        out,_=replace_launcher(raw,Path("/tmp/venv/bin/python"))
        self.assertIn("gfortran -c matrix.f",out)

if __name__=="__main__":
    unittest.main()
