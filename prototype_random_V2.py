import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

X_MIN, X_MAX = 0, 50
Y_MIN, Y_MAX = 0, 1500
TARGET_X = 42
TARGET_Y_THRESHOLD = 800
NUM_ITERATIONS = 50000 # Number of iterations per run
NUM_RUNS = 10 # Number of runs

all_probabilities = []
success_counts = []
x_vals = []
y_vals = []

for run in range(NUM_RUNS):
    success_count = 0
    total_attempts = 0
    probabilities = []

    for _ in range(NUM_ITERATIONS):
        x = np.random.randint(X_MIN, X_MAX + 1)
        y = np.random.randint(Y_MIN, Y_MAX + 1)

        if x == TARGET_X and y > TARGET_Y_THRESHOLD:
            success_count += 1
            x_vals.append(x)
            y_vals.append(y)
        total_attempts += 1
        probabilities.append(success_count / total_attempts)

    all_probabilities.append(probabilities)
    success_counts.append(success_count)

all_probabilities = np.array(all_probabilities)

# Display results
print(f"Simulation with random attacks on target ({TARGET_X}, y > {TARGET_Y_THRESHOLD})")
print(f"Total runs: {NUM_RUNS}")
print(f"Total attempts per run: {NUM_ITERATIONS}")
print(f"Total successful attacks across runs: {sum(success_counts)}")
print(f"Average probability of success: {np.mean([success_counts[i] / NUM_ITERATIONS for i in range(NUM_RUNS)]):.6f}")


plt.figure(figsize=(10, 5))


for i in range(NUM_RUNS):
    plt.plot(all_probabilities[i], alpha=0.5, label=f'Run {i+1}' if i < 2 else "_")

plt.xlabel("Iterations")
plt.ylabel("Probability of Success")
plt.title("Evolution of Success Probability Over Iterations")
plt.legend(loc="upper right", fontsize=8, frameon=False)
plt.show()

plt.figure(figsize=(8, 6))

if len(x_vals) > 5:
    # use KDE only if there are multiple successful points
    #sns.kdeplot(x=x_vals, y=y_vals, cmap="Reds", fill=True, bw_adjust=0.5)
    sns.kdeplot(x=x_vals, y=y_vals, cmap="Reds", fill=True, bw_adjust=0.5, warn_singular=False)
    plt.title("Heatmap of Successful Attack Inputs")
else:
    # scatter plot if KDE fails
    plt.scatter(x_vals, y_vals, color="red", label="Successful Attacks")

# Plot
plt.xlabel("x values")
plt.ylabel("y values")
plt.title("Heatmap / Scatter of Successful Attack Inputs")
if len(x_vals) > 0:
    plt.legend()
plt.show()
