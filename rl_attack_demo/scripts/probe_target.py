#!/usr/bin/env python
import random, tqdm
from pathlib import Path
from agent.runner import ProgramRunner

ROOT = Path(__file__).resolve().parents[1]   # racine du dépôt
BIN  = ROOT / "bin" / "magic_crash"

PR = ProgramRunner(BIN)

CRASHES, N = 0, 1000
for _ in tqdm.trange(N):
    x = random.randrange(256) # uniform 8-bit
    _, rc = PR(x)
    CRASHES += (rc != 0)

print(f"Crash rate ≈ {CRASHES/N:.3%} over {N} random inputs")
