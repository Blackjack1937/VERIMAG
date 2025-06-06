# When (and how) we plug in symbolic execution

We **do not** run a symbolic executor inside every RL step (too heavy).  
Instead we plan three milestones:

| Phase | Description | Purpose |
|-------|-------------|---------|
| **0 – Black-box RL** | Plain Q-table on 8-bit input; crash reward only. | Baseline / smoke test. |
| **1 – Grey-box RL** | Same agent on 32-bit input, DQN; optional coverage bonus. | Reach crashes on larger space. |
| **2 – SymExec + CNN boost** | **One-off symbolic pass** (KLEE/angr) → path predicates → dataset → train 1-D CNN `g_θ`. At run-time the env adds `part_id = g_θ(x_last)` to the state and a small “new-partition” bonus to `R`. | Faster exploration of deep / rare paths while keeping run-time black-box. |
| **3 – Full White-box** | Hybrid loop that alternates concrete RL steps with online symbolic queries (Driller-style). | For real programs when Phase 2 plateaus. |

> **Exit criterion for Phase 1 → Phase 2**  
> If the DQN’s success‐rate stalls below the random-fuzzing baseline after 5 M steps, we switch on the SymExec + CNN module.

