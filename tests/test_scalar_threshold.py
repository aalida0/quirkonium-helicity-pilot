"""Run from repository root: python -m unittest discover -s tests -v"""
import pathlib
import sys
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'src'))
from scalar_threshold_amplitudes import *

class ScalarThresholdPhysics(unittest.TestCase):
    def test_ew_charge_and_scheme(self):
        self.assertAlmostEqual(QU-QD,1.)
        self.assertAlmostEqual(S2+C2,1.)
    def test_widths_against_publication(self):
        for M in (180.,200.,250.,350.,500.,1000.,2000.):
            for t in (0.1,0.3,1.,3.,10.):
                for V in ('Z','gamma'):
                    b=Setup(M,splitting(M,t),V)
                    with self.subTest(M=M,t=t,V=V):
                        self.assertAlmostEqual(amplitude_width(b)/published_width(b),1.,delta=3e-11)
    def test_em_ward(self):
        for M in (180.,250.,500.,1000.,2000.):
            for t in (0.1,1.,3.,10.):
                b=Setup(M,splitting(M,t),'gamma')
                self.assertLess(ward_photon(b),5e-13)
    def test_forbidden_w_long_gamma_transverse(self):
        b=Setup(500.,splitting(500.,10.),'gamma')
        _,kw,_=b.vectors()
        eW=(kw[3]/MW,0.,0.,kw[0]/MW)
        for eG in ((0.,1.,0.,0.),(0.,0.,1.,0.)):
            self.assertAlmostEqual(amplitude(b,eW,eG),0.,delta=1e-12)
    def test_helicity_projection_of_published_pieces(self):
        for M in (250.,500.,1000.):
            for t in (0.1,1.,3.,10.):
                b=Setup(M,splitting(M,t),'Z')
                _,T,L=published_pieces(b)
                self.assertAlmostEqual(f00(b),L/(T+L),delta=3e-11)
    def test_degenerate_closed_form(self):
        for M in (180.,500.,1000.):
            b=Setup(M,0.,'Z')
            K=(M*M-MW*MW-MZ*MZ)/2
            predicted=MW**2*MZ**2/(2*K*K+MW**2*MZ**2)
            self.assertAlmostEqual(f00(b),predicted,delta=1e-13)
    def test_erratum_asymptotic_limit(self):
        for t in (0.1,1.,3.,10.):
            cos2=(1-t*t)/(1+t*t)
            R=C2*cos2*cos2/(8*S2*S2*(QU+QD)**2)
            asymptotic=R/(1+R)
            b=Setup(100000.,splitting(100000.,t),'Z')
            self.assertAlmostEqual(f00(b),asymptotic,delta=4e-6)
    def test_wavefunction_cancels(self):
        b=Setup(500.,splitting(500.,10.),'Z')
        for R2 in (0.01,1.,100.):
            self.assertAlmostEqual(amplitude_width(b,R2)/published_width(b,R2),1.,delta=1e-11)
        self.assertGreater(f00(b),0.)
    def test_integrated_lepton_distribution(self):
        for f in (0.,0.25,0.9,1.):
            N=10000
            integral=sum(w_lepton_density(-1+(i+0.5)*2/N,f) for i in range(N))*2/N
            self.assertAlmostEqual(integral,1.,delta=2e-8)

if __name__=='__main__':
    unittest.main()
