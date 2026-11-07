# Independent MadGraph5 electroweak control — PREPARED, NOT EXECUTED

MG5's `mssm` particle names `ul`, `dl` are left-handed squarks, whose *SM electroweak* W/Z/photon gauge vertices correspond to those of a scalar weak doublet. They carry QCD color rather than infracolor; **do not compare color-averaged production cross sections or bound-state decay rates directly**.

Execute from the research repository root:

```bash
mkdir -p validation/local_logs
cd validation/local_logs
/path/to/MG5_aMC/bin/mg5_aMC ../../madgraph/mssm_ew_procs.mg5 |& tee madgraph_generation.log
```

**Validation requirements:** inspect the generated `SubProcesses/*/matrix.f` and Feynman diagrams. Retain the two scalar exchanges, seagull W/V contact vertex, and s-channel W. Set pure-left first-generation squark mixing and the same EW input scheme as `MODEL_SPECIFICATION.md`; suppress first-generation Yukawa/Higgs contamination. For the mass card choose physically consistent masses and ensure correct CKM. Export numerical fixed-color squared matrix elements with a controlled nonzero incoming relative velocity, extrapolate to threshold, and only then compare with `src/scalar_threshold_amplitudes.py`. Standalone compilation is version dependent; don't treat successful generation as a validated matrix-element match.

This control does not by itself establish an arbitrary-gauge Goldstone Slavnov–Taylor identity. `check lorentz ul dl~ > w+ z QCD=0 QED=2` tests Lorentz invariance, not full gauge identities. In some MG5 versions `check gauge` only checks external gluons. A genuine independent helicity check requires fixed-helicity matrix-element output, not just an unpolarized cross section.

**Status until user-machine logs are returned:** PREPARED / UNEXECUTED. Log MG5 version, card checksum, diagram count, input masses, relative velocity, MEs, and numerical tolerances. Original particle names: https://madgraph.mi.infn.it/sm_particles.html.
