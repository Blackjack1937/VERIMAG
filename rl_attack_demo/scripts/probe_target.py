#!/usr/bin/env python
import random, tqdm
from agent.runner import ProgramRunner

PR = ProgramRunner("bin/magic_crash")

CRASHES, N = 0, 1000
for _ in tqdm.trange(N):
    x = random.randrange(256) # uniform 8-bit
    _, rc = PR(x)
    CRASHES += (rc != 0)

print(f"Crash rate ≈ {CRASHES/N:.3%} over {N} random inputs")
