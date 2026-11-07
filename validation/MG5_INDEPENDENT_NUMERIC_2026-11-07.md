
# Independent MG5 numerical threshold check — 2026-11-07

## Verdict: PASS scoped to one tree-level benchmark

Independent MG5_aMC 3.5.1 MSSM_SLHA2 standalones evaluated the helicity-summed,
initial-color-averaged squared amplitudes at M=500 GeV, tanbeta=3, with
on-shell external vectors and incoming relative momentum q=0.

| channel | MG5 averaged ME2 | analytic fixed-color ME2 | analytic /3 target | signed relative residual |
|---|---:|---:|---:|---:|
| W+Z | 5.3175200794627446e-3 | 0.01595256023838295 | 5.317520079460985e-3 | +3.311e-13 |
| W+gamma | 1.6806924742524885e-3 | 0.005042077422755888 | 1.680692474251963e-3 | +3.126e-13 |

Generated source confirmed 4 expected electroweak diagrams (contact,
s-channel W, up- and down-squark exchanges), unmixed first-generation
USQMIX and DSQMIX, with IDEN=9 and CF=3, giving factor 1/3. The
electroweak inputs in the corrected SLHA card match the analytic scheme
(mW 80.379 GeV; mZ 91.1876 GeV; alphaW 0.0338). Fixed scalar masses
are (244.8313730872, 255.1686269128) GeV in u/d order.

## Controlled cause of previous mismatch: oversized numeric fields

The old preview serializer wrote 21-character values with .15E, e.g.
1.326638757554207E+02, in an SLHA reader that is sensitive to field
width. In controlled user-executed tests with identical physics and momenta:

| Input | WZ ME2 | Wgamma ME2 |
|---|---:|---:|
| Original MSSM card | 1.2920738170162260e-2 | 1.5897248828443651e-3 |
| Only alpha_inv reformatted compactly | 1.2920738170162260e-2 | 1.5897248828443651e-3 |
| Only alpha_inv reformatted in 21-character form | 1.2920738170162664e+2 | 1.5897248828443651e+1 |

Oversized numeric fields increase both ME2 by exactly 10000, matching
an exponent misread E+02 -> E+0. The precise offending Fortran reader
statement remains untraced, but the input-serialization mechanism is
experimentally established for these standalone outputs. The earlier huge
numbers with the old preview card were artifacts, NOT model predictions.

The corrected Python writer uses .12E fields of at most 20 characters.
The compact review filename is param_card_quirkonium_review_compact.dat;
the former long-format review cards are preserved as regression evidence.
Original generated param_card.dat files were never overwritten.

## Reproducibility

User-run local logs from 2026-11-07 report both numeric comparisons
and the 10000x controlled A/B effect. The initial 50-test run reported
48 passes, one failure and one error due to stale synthetic fixture
formatting; the two fixtures are now corrected in the repository, with
an extra regression for dangerous wide fields. This regression repair
has NOT yet been rerun on the user's machine.

    python -m unittest discover -s tests -v
    python scripts/mg5_threshold_preflight.py --mass 500 --tanbeta 3 --write-cards
    .venv-mg5-f2py/bin/python scripts/mg5_slha_fieldwidth_gate.py --mass 500 --tanbeta 3 --channel both
    .venv-mg5-f2py/bin/python scripts/mg5_matrix2py_compare.py --channel Z --mass 500 --tanbeta 3
    .venv-mg5-f2py/bin/python scripts/mg5_matrix2py_compare.py --channel gamma --mass 500 --tanbeta 3

Locally saved raw evidence (generated and git-ignored):
validation/local_logs/threshold_benchmarks/M500_tanbeta3_slha_width_gate.json;
validation/local_logs/threshold_benchmarks/M500_tanbeta3_Z/matrix2py_result.json;
validation/local_logs/threshold_benchmarks/M500_tanbeta3_gamma/matrix2py_result.json.

## Limitations / next gates

This is a genuine independent code-level ME check for the two summed
tree-level channels at one benchmark. It does NOT validate helicity-by-helicity
complex amplitudes and relative phases, general-gauge identities, arbitrary
mass points, model-parameter viability, bound-state dynamics, observability,
or literature novelty. The previous overall NO-GO on AMPLITUDE mismatch is
lifted, but NO paper readiness or novel result is implied. The next priority
is a short benchmark-grid and fixed-helicity audit, alongside completion of
the cited/citing literature audit and a distinct pheno claim.
