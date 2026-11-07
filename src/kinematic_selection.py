"""Pure kinematic spin-zero W-gamma tests, not quirkonium amplitudes."""
from math import isclose

def allowed_two_body_helicities(parent_spin, spin1_helicities, spin2_helicities):
    """For a spin-J parent, |lambda_1-lambda_2| <= J is necessary."""
    return [(a,b) for a in spin1_helicities for b in spin2_helicities
            if abs(a-b) <= parent_spin]

def normalized_longitudinal_template(costheta):
    """Normalized W->l nu polar angle density for pure helicity zero."""
    return 0.75*(1-costheta**2)

def normalized_equal_transverse_template(costheta):
    """Parity-symmetric equal +1/-1 W polarization mixture."""
    return 0.375*(1+costheta**2)

if __name__ == "__main__":
    pairs=allowed_two_body_helicities(0,(-1,0,1),(-1,1))
    assert pairs==[(-1,-1),(1,1)],pairs
    from scipy.integrate import quad
    for f in (normalized_longitudinal_template, normalized_equal_transverse_template):
        assert isclose(quad(f,-1,1)[0],1.0,abs_tol=1e-12)
    print("PASS: spin-zero Wgamma transverse-only helicities and normalized ideal W decay templates")
