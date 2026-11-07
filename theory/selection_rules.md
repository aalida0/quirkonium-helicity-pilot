# Spin-zero selection-rule diagnostic

For a two-body decay of total spin J, a necessary helicity constraint in the Jacob–Wick convention is |λ1−λ2|≤J. For J=0, λ1=λ2. Since an on-shell photon has λγ=±1, an on-shell W must have λW=±1. No longitudinal W can appear, and f_L(W)=0 whenever the Wγ decay occurs. This is not an amplitude prediction and does not establish a nonzero width.

For a spin-zero parent → WZ both (λW,λZ)=(0,0) and transverse ±1±1 are allowed. Angular momentum **cannot** determine the relative fractions; only full amplitudes can.

For a spin-zero parent, emission direction is isotropic in its rest frame. In a specified W helicity frame, normalized *ideal* lepton polar-angle densities (after integrating azimuth, neglecting cuts, masses, and interference) are:
- pure longitudinal W: (3/4)(1−cos²θ)
- equal mixture of ± transverse W: (3/8)(1+cos²θ)

These are universal templates; do not describe them as a new quirk prediction.

Run: `python src/kinematic_selection.py` (requires SciPy for numerical integration).

**Important:** This code intentionally does not calculate Fok–Kribs/Forsyth quirk amplitudes or validate any branching ratio.