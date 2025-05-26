#!/usr/bin/env python
import tqdm, numpy as np
from agent.env import CrashEnv
from agent.qtab import QTableAgent

env, agent = CrashEnv(), QTableAgent()
EP, rewards = 5000, []

for _ in tqdm.trange(EP):
    obs,_ = env.reset()
    tot, done = 0, False
    while not done:
        a = agent.act(obs)
        nobs,r,done,_,_ = env.step(a)
        agent.learn(obs,a,r,nobs,done)
        obs = nobs
        tot += r
    rewards.append(tot)

print("mean last 100 :", np.mean(rewards[-100:]))
