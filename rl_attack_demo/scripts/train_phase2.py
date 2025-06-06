#!/usr/bin/env python
import pathlib, tqdm, numpy as np, pandas as pd, torch
from agent.env_cov import CrashEnvCov
from agent.dqn import DQNAgent

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
env   = CrashEnvCov(lambda_cov=0.05)          #bitmap CFG
agent = DQNAgent(device=DEVICE)

EPISODES, TARGET_SYNC, BATCH = 15_000, 1_000, 128
out_dir = pathlib.Path("outputs"); out_dir.mkdir(exist_ok=True)

rewards = []

for ep in tqdm.trange(EPISODES, desc="Phase-2 (cov bonus)"):
    obs,_ = env.reset()
    total, done = 0.0, False
    while not done:
        a = agent.act(obs)
        nobs,r,done,_,_ = env.step(a)
        agent.remember(obs,a,r,nobs,done)
        agent.train_step(BATCH)
        obs = nobs; total += r
    rewards.append(total)
    if ep % TARGET_SYNC == 0:
        agent.sync_target()
    if ep % 100 == 0 and ep:
        print(f"ep {ep:5d}  meanR100 = {np.mean(rewards[-100:]):.1f}")


pd.DataFrame({"reward": rewards}).to_csv(out_dir/"phase2_rewards.csv", index=False)
torch.save(agent.policy.state_dict(), out_dir/"dqn16_cov.pth")
print("done")
