#!/usr/bin/env python
import pathlib, tqdm, numpy as np, pandas as pd, torch
from agent.env import CrashEnv
from agent.dqn import DQNAgent

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

env = CrashEnv(n_bits=16)             # 65 536 actions
agent = DQNAgent(n_bits=16, device=DEVICE)
out_dir = pathlib.Path("outputs"); out_dir.mkdir(exist_ok=True)

EPISODES = 20_000
TARGET_SYNC = 1_000
BATCH = 128

rewards, losses = [], []

for ep in tqdm.trange(EPISODES, desc="DQN Phase-1"):
    obs, _ = env.reset()
    total_r, done = 0, False
    while not done:
        a = agent.act(obs)
        nobs, r, done, _, _ = env.step(a)
        agent.remember(obs, a, r, nobs, done)
        loss = agent.train_step(BATCH)
        obs = nobs
        total_r += r
        if loss:
            losses.append(loss)
    rewards.append(total_r)

    if ep % TARGET_SYNC == 0:
        agent.sync_target()

    if ep % 100 == 0 and ep:      # log
        print(f"ep {ep}  meanR100={np.mean(rewards[-100:]):.1f}")

# save logs and model
pd.DataFrame({"reward": rewards}).to_csv(out_dir/"phase1_rewards.csv", index=False)
torch.save(agent.policy.state_dict(), out_dir/"dqn16.pth")
best = np.argmax(agent.policy(torch.tensor([[i, 0] for i in range(2**16)],
                                          dtype=torch.float32, device=DEVICE)).cpu().numpy())
(open(out_dir/"witnesses16.txt", "w")
 .write(f"{int(best)}\n"))

print("Training finished, files saved in outputs/")
