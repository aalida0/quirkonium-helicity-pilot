"""On-shell ideal joint W/Z helicity angular density checks."""
import math,pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'src'))
from scalar_threshold_amplitudes import Setup,splitting,f00
from joint_wz_angles import (joint_density,azimuthal_cos1_amplitude,
                              azimuthal_cos2_amplitude,azimuthal_cos2_moment,
                              azimuthal_density)

class JointWZAngles(unittest.TestCase):
    def test_cos2_fraction_relation(self):
        for M in (250.,500.,1000.):
            for t in (.1,1.,3.,10.):
                b=Setup(M,splitting(M,t),'Z')
                self.assertAlmostEqual(azimuthal_cos2_amplitude(b),
                                       (1-f00(b))/4,delta=1e-14)
    def test_cos1_interference_sign_change(self):
        a=Setup(500.,splitting(500.,.1),'Z')
        b=Setup(500.,splitting(500.,3.),'Z')
        self.assertGreater(azimuthal_cos1_amplitude(a),0.)
        self.assertLess(azimuthal_cos1_amplitude(b),0.)
    def test_nonnegative_density(self):
        b=Setup(500.,splitting(500.,3.),'Z')
        for w in (-1.,-.7,0.,.4,1.):
            for z in (-1.,-.8,0.,.3,1.):
                for phi in (0.,math.pi/3,math.pi,4*math.pi/3):
                    self.assertGreaterEqual(joint_density(b,w,z,phi),-1e-14)
    def test_normalized_joint_density_and_moments(self):
        for tb in (1.,3.):
            b=Setup(500.,splitting(500.,tb),'Z')
            n,np=40,12; norm=c1=c2=0.
            for i in range(n):
                cw=-1+(i+.5)*2/n
                for j in range(n):
                    cz=-1+(j+.5)*2/n
                    for ip in range(np):
                        phi=2*math.pi*(ip+.5)/np
                        x=joint_density(b,cw,cz,phi)*(2/n)**2*(2*math.pi/np)
                        norm+=x
                        c1+=x*math.cos(phi)
                        c2+=x*math.cos(2*phi)
            self.assertAlmostEqual(norm,1.,delta=7e-4)
            self.assertAlmostEqual(c1,azimuthal_cos1_amplitude(b)/2,delta=5e-4)
            self.assertAlmostEqual(c2,azimuthal_cos2_moment(b),delta=1e-4)
    def test_one_dimensional_azimuth_normalization(self):
        b=Setup(500.,splitting(500.,3.),'Z')
        n=1000
        s=sum(azimuthal_density(b,2*math.pi*(i+.5)/n) for i in range(n))*2*math.pi/n
        self.assertAlmostEqual(s,1.,delta=1e-12)

if __name__=='__main__':
    unittest.main()
