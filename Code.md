### 🚀 Roadmap : 1ʳᵉ version “end-to-end” (Python agent ↔ C binary)


## 0 — Tech foundations

| item               | pick                                                                                           |
| ------------------ | ---------------------------------------------------------------------------------------------- |
| **OS/toolchain**   | Linux, `gcc -static` for deterministic binaries                                                |
| **Python**         | 3.10+, `venv`, `pip-tools`                                                                     |
| **RL libs**        | keep it minimal: just `numpy`, `gymnasium==0.29` (for wrappers), optional `torch` from Phase 1 |
| **Process runner** | `subprocess.run(stdin=PIPE, capture_output=True, timeout=X)`                                   |

---

## 1 — Project skeleton

1. **Repo layout**

   ```
   /agent/         ← RL code (gym env + algorithm)
   /targets/       ← all C test programs   (Makefile compiles to ./bin/…)
   /scripts/       ← run_experiments.py, plot.py
   /docs/          ← README, Formalization.md, Objectif.md
   /tests/         ← pytest basic sanity (agent learns on tiny env)
   ```
2. **CI baseline** : GitHub Actions running “Phase 0 smoke-test” in < 2 min.

---

## 2 — Target side

| step                             | detail                                                                                                                   |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| **2.1 Choose MVP vulnerability** | keep obvious *magic-number* + *threshold* as in `if(x==42){ if(y>1000) crash(); }` so the surface fits 1 × 32-bit input. |
| **2.2 Build script**             | `targets/Makefile` → `./bin/magic_crash` (no ASLR for now)                                                               |
| **2.3 Wrapper**                  | tiny Python class `ProgramRunner`:  `run(x:int) → (stdout, exitcode, elapsed)`                                           |
| **2.4 Reward detector**          | `if exitcode != 0 => +10` else `+0` (matches Formalisation § 3.4)                                                        |

> **Deliverable**: running `python scripts/probe_target.py` prints crash probability for uniform random inputs.

---

## 3 — Gym-style environment

```python
import gymnasium as gym
class CrashEnv(gym.Env):
    observation_space = gym.spaces.MultiDiscrete([256, 256]) # y_k,x_k 8 bits each for Phase 0
    action_space      = gym.spaces.Discrete(256)             # choose x in [0,255]
    def step(self, action): ...
    def reset(self, *, seed=None, options=None): ...
```

* **State** `(y_last, x_last)` exactly as Formalisation § 3.1.
* **Horizon** `H=100`, `gamma=0.9`.
* **No leakage of `y_r`**: env keeps internal seed stable for an episode, re-rolls between episodes.

---

## 4 — Phase 0 agent: tabular Q-learning

1. **Resolution**: 8-bit action/state (fits table 256 × 256).
2. **Code**: `agent/qtab.py` with ε-greedy, α = 0.1, replay disabled.
3. **Training loop**: `train.py --episodes 5000` logs `reward_per_episode.csv`.

> **Success criterion**: within 5000 episodes the agent finds the crash ≥ 80 % of the time on the final policy.

---

## 5 — Instrumentation & plots 

* Matplotlib “learning curve” + moving average.
* Save best exploit input(s) to `outputs/witnesses.txt`.
* CLI `python scripts/eval_policy.py --bin ./bin/magic_crash --policy qtable.pkl`.

---

## 6 — Phase 1 scaffold (parallel, low-priority)

While Phase 0 runs, create stubs:

* `agent/dqn.py` (PyTorch) — ready but not wired.
* Decide serialization format for replay buffer (`np.savez`).
* Investigate `torch.jit` for later speed-ups.

---

## 7 — Quality gates

| gate            | tool                                                           |
| --------------- | -------------------------------------------------------------- |
| style           | `ruff`, `black`, `mypy --strict`                               |
| tests           | `pytest -q tests/` (mock ProgramRunner + check Bellman update) |
| reproducibility | `scripts/run_seeded.sh 5` → same average score ± 5 %           |

---

## 8 — Risks & mitigations

* **Target hangs** → enforce `timeout=0.1 s`; count as reward 0.
* **Noise in `y_c` too high** → clip output to 8 bits hash.
* **Q-table blows** when raising bit-width n → switch to DQN (Phase 1).

---

## 9 — Milestone checklist

* [ ] Repo scaffolding & CI
* [ ] `ProgramRunner` + crash detector
* [ ] `CrashEnv` passing Gym sanity test
* [ ] Q-learning converges on 8-bit task
* [ ] Scripts: train / eval / plot
* [ ] Doc update: HOW-TO reproduce Phase 0

---

## 10 — After Phase 0 (outlook)

| Phase | key upgrade                                                        | risk                |
| ----- | ------------------------------------------------------------------ | ------------------- |
| **1** | 32-bit DQN, still black-box                                        | network stability   |
| **2** | add grey-box bonus (coverage bitmap via `gcc -fsanitize=coverage`) | IPC perf            |
| **3** | white-box hints (static CFG, WP) + CNN                             | feature engineering |

Each new phase keeps the *same* interface; only the agent implementation, reward shaping, and optional env “bonus” change.
