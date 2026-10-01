# Documentation-only Q&A verification: docs/id-reuse.md

Frozen questions, answered by a fresh dispatch restricted (best-effort)
to `docs/id-reuse.md` alone — no source code, no assertion record, no
other file.

## Questions and answers

1. **Does `_next_id` guarantee a deleted task's id is never reused?**
   No — conditional. Reuse occurs iff the deleted task held the current
   maximum id at the moment of deletion; it does not occur otherwise.
   Correctly cited the page's own explicit rejection of a flat yes/no
   simplification.
2. **Add 1,2,3; delete 3; add — what id?** Answered: 3 (reused). Correct.
3. **Add 1,2; delete 1 (not max); add — what id?** Answered: 3 (new,
   not reused). Correct.
4. **Does the page say the existing tests catch this?** Correctly
   reported the page doesn't mention a test suite at all — basis is
   direct execution and adversarial review, not test coverage.
5. **One stated open question?** Correctly quoted the page's own "is
   this even a real product requirement" open question.

## Independent verification against the real system

All five answers cross-checked against the real `src/tinytodo.py`
behavior (already independently reproduced three times over in this
exercise: initial research, adversarial review, model-blind
reconstruction, all converging on the same rule) — all five are
accurate. No documentation defect found in this pass.
