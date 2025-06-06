#!/usr/bin/env python
import pathlib
import pickle

import numpy as np
import pandas as pd
import tqdm

from rl_attack_demo.agent.env0 import CrashEnv
from agent.qtab import QTableAgent

# ------------------------------------------------------------------
# phase 0  : tabular training
# ------------------------------------------------------------------
env, agent = CrashEnv(), QTableAgent()
EPISODES = 5000
rewards = []

for _ in tqdm.trange(EPISODES, desc="Training"):
    obs, _ = env.reset()
    episode_return, done = 0.0, False

    while not done:
        action = agent.act(obs)
        next_obs, r, done, _, _ = env.step(action)
        agent.learn(obs, action, r, next_obs, done)
        obs = next_obs
        episode_return += r

    rewards.append(episode_return)

print("mean reward (last 100) :", np.mean(rewards[-100:]))


out_dir = pathlib.Path("outputs")
out_dir.mkdir(exist_ok=True)

#Q-table
pickle.dump(agent.q, open(out_dir / "qtable.pkl", "wb"))

#best input
best_action = int(agent.q.max(1).argmax() % 256)  # devrait être 133
print("Best action learnt =", best_action)
(out_dir / "witnesses.txt").write_text(f"{best_action}\n")
#courbe d'apprentissage
pd.DataFrame({"reward": rewards}).to_csv(out_dir / "rewards.csv", index=False)
print("Saved: qtable.pkl, witnesses.txt, rewards.csv -> outputs/")
