# HOW-TO

Tested on Ubuntu / Kali Rolling, Python 3.10+, optional NVIDIA GPU.

---

## 0 · Set-up the Python env

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt          # numpy, gymnasium, torch, …
sudo apt install build-essential clang afl++   # AFL++ for Phase 2
```

---

## 1 · Build the C targets

```bash
# normal binary  (Phase 0 / 1)
make -C targets

# instrumented binary with CFG bitmap (Phase 2)
make -C targets cov                   # uses afl-clang-fast
```

You should now have

```
bin/magic_crash          (classic run)
bin/magic_crash_cov      (64 k CFG bitmap)
```

---

## 2 · Run the unit tests

```bash
python -m pytest -q      # three tests → should pass
```

---

## 3 · Phase 0 – tabular Q-learning (8-bit)

```bash
python scripts/train_phase0.py
python scripts/plot.py           # makes outputs/phase0_curve.png
```

Outputs: `qtable.pkl`, `witnesses.txt`, learning-curve PNG.

---

## 4 · Phase 1 – DQN, 16-bit, black-box

```bash
python scripts/train_phase1.py        # GPU strongly recommended
```

Creates `outputs/phase1_rewards.csv` + `dqn16.pth`.

(**Note:** a full 20 000-episode run takes ≈ 27 h on a GTX 1050 Ti;
for a quick demo you can stop after 2 000 episodes.)

---

## 5 · Phase 2 – DQN + coverage bonus (grey-box)

```bash
python scripts/train_phase2.py
```

*Uses `afl-showmap` to read the 64 k CFG bitmap and adds
`λ · Δcoverage` (λ = 0.05) to the reward.*

Outputs: `phase2_rewards.csv`, `dqn16_cov.pth`.

---

## 6 · Evaluate a saved policy

```bash
python scripts/eval_policy.py --phase 2 --episodes 500
```

Prints crash-rate and (for Phase 2) average new blocks per episode.

---

## Typical timings (GTX 1050 Ti mobile)

| Phase | Episodes | Time | Crash-rate |
|-------|----------|------|-----------|
| 0     | 5 000    |  4 min (CPU) | 81 % |
| 1     | 20 000   | 27 h  | 65 % |
| 2     | 15 000   | 15 min | 68 % | 

*(Phase 1 full run omitted in demo due to runtime; use GPU cluster for full training.)*

---

### Troubleshooting

* **`FileNotFoundError: magic_crash_cov`** – run `make -C targets cov`.
* **`TimeoutExpired` from `afl-showmap`** – increase `runner_timeout`
  (default 0.3 s) in `CrashEnvCov`.
* **GPU not detected** – check `nvidia-smi`; install proprietary driver and a CUDA build of PyTorch.