#!/usr/bin/env python
import tqdm, numpy as np, pandas as pd, pathlib, pickle
from agent.env_binsearch import BinSearchEnv
from agent.qtab import QTableAgent

env, agent = BinSearchEnv(), QTableAgent()
EP, rewards = 20000, []
for _ in tqdm.trange(EP):
    obs,_ = env.reset()
    ep_ret, done = 0.0, False
    while not done:
        a = agent.act(obs)
        nobs,r,done,_,_ = env.step(a)
        agent.learn(obs,a,r,nobs,done)
        obs, ep_ret = nobs, ep_ret + r
    rewards.append(ep_ret)

print("mean-last-100 :", np.mean(rewards[-100:]))

out = pathlib.Path("outputs"); out.mkdir(exist_ok=True)
pd.DataFrame({"reward": rewards}).to_csv(out/"binsearch_rewards.csv", index=False)
pickle.dump(agent.q, open(out/"qtable_bin.pkl", "wb"))
