import pandas as pd, matplotlib.pyplot as plt
df = pd.read_csv("outputs/rewards.csv")
df["ma50"] = df["reward"].rolling(50).mean()
plt.plot(df["ma50"])
plt.xlabel("Episode"); plt.ylabel("Reward (50-ep MA)")
plt.title("Phase-0 learning curve")
plt.savefig("outputs/phase0_curve.png", dpi=150); plt.close()
