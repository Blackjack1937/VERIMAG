#!/usr/bin/env python
"""
Training script for the multi-oracle 8-bit task.

Actions 0-255  : guess x
Action  256     : ask higher / lower  (cost −0.2, oracle ∈ {1,2})
Action  257     : ask parity (even/odd)  (cost −0.1)
Action  258     : ask MSB (bit7)        (cost −0.1)
Reward +10 on correct guess, −1 on wrong guess
"""

import pathlib, tqdm, numpy as np, pandas as pd, torch
from agent.env_multi import MultiOracleEnv
from agent.dqn import DQNAgent

DEVICE       = "cuda" if torch.cuda.is_available() else "cpu"
EPISODES     = 5_000
TARGET_SYNC  = 1_000
BATCH        = 128
OUT_DIR      = pathlib.Path("outputs")
OUT_DIR.mkdir(exist_ok=True)

env   = MultiOracleEnv()
agent = DQNAgent(n_bits=8, device=DEVICE)   

rewards, losses = [], []

for ep in tqdm.trange(EPISODES, desc="Phase-Multi"):
    obs, _ = env.reset()
    ep_ret, done = 0.0, False

    while not done:
        a = agent.act(obs)
        nobs, r, done, _, _ = env.step(a)
        agent.remember(obs, a, r, nobs, done)
        loss = agent.train_step(BATCH)
        if loss:
            losses.append(loss)
        obs, ep_ret = nobs, ep_ret + r

    rewards.append(ep_ret)

    if ep % TARGET_SYNC == 0:
        agent.sync_target()
    if ep % 100 == 0 and ep:
        print(f"ep {ep:5d}  meanR100 = {np.mean(rewards[-100:]):.2f}")

# ---------------------------------------------------------------- save
pd.DataFrame({"reward": rewards}).to_csv(OUT_DIR / "multi_rewards.csv", index=False)
torch.save(agent.policy.state_dict(), OUT_DIR / "dqn_multi.pth")
print("Done – files saved in outputs/")
