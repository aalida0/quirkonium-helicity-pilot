# Research discipline

- This branch is the **scalar threshold pilot**, not an established publication.
- Never change the model charge/hypercharge convention without updating all amplitudes and benchmarks.
- Use source arXiv:2504.02940 Appendix A.3 and 2026 erratum PRD 113 079901 for mass splitting; do not use pre-erratum free-Delta exclusion plots.
- For physics changes, rerun `python -m unittest discover -s tests -v` and `python src/scalar_threshold_amplitudes.py`. Document thresholds and new limitations.
- Keep exact distinction between analytical amplitude, published-rate reproduction, gauge Ward checks, an independent generator, and detector simulation.
- Do not label unverified parameter points 'allowed', claim novel results without citation-network audit, or expand to scan before the physics/model gates close.
- Commit only source, checks, concise numerical evidence and scientific documentation; figures are regenerated locally.
