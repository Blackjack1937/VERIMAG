import numpy as np
import random
import matplotlib.pyplot as plt

class TargetProgram:
    """
    Represents the vulnerable program. The attacker interacts with it via the `execute` method.
    """
    def __init__(self, fixed_random_seed=True):
        self.fixed_random_seed = fixed_random_seed
        self.y_r = random.randint(1, 100) if fixed_random_seed else None

    def reset(self):
        """ Resets the random components of the program for a new execution. """
        if not self.fixed_random_seed:
            self.y_r = random.randint(1, 100)

    def execute(self, x, y):
        """
        Simulates program execution with inputs (x, y). Returns a reward signal.
        """
        y_c = random.randint(1, 100)  # Dynamic random component
        y_total = self.y_r + y_c if self.y_r is not None else y_c
        
        if x == 42 and y_total > 150:
            return 10  # Successful attack
        return -1  # Failed attempt


class RLAttackAgent:
    """
    A simple Q-Learning agent to find the best attack strategy.
    """
    def __init__(self, state_size, action_size, learning_rate=0.1, discount_factor=0.9, exploration_rate=1.0):
        self.state_size = state_size
        self.action_size = action_size
        self.q_table = np.zeros((state_size, action_size))
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = exploration_rate  # Exploration rate for epsilon-greedy

    def choose_action(self, state):
        """ Chooses an action using an epsilon-greedy strategy. """
        if np.random.rand() < self.epsilon:
            return random.randint(0, self.action_size - 1)
        return np.argmax(self.q_table[state])

    def update_q_value(self, state, action, reward, next_state):
        """ Updates the Q-table using the Bellman equation. """
        best_next_action = np.argmax(self.q_table[next_state])
        self.q_table[state, action] += self.lr * (reward + self.gamma * self.q_table[next_state, best_next_action] - self.q_table[state, action])

    def decay_exploration(self, decay_rate=0.995, min_epsilon=0.01):
        """ Reduces exploration rate over time. """
        self.epsilon = max(min_epsilon, self.epsilon * decay_rate)


# Setting up the environment
target_program = TargetProgram()
agent = RLAttackAgent(state_size=50, action_size=50)  # Example: Discrete states and actions

episodes = 1000  # Number of learning iterations
rewards_per_episode = []  # Track rewards over time

for episode in range(episodes):
    target_program.reset()
    state = random.randint(0, 49)  # Initial state representation (simplified)
    done = False
    episode_reward = 0

    while not done:
        action = agent.choose_action(state)
        x, y = action % 50, action % 50  # Example: Mapping action to input (adjust for real case)
        reward = target_program.execute(x, y)
        next_state = (state + 1) % 50  # Simplified next state logic

        agent.update_q_value(state, action, reward, next_state)
        state = next_state
        episode_reward += reward
        
        if reward == 10:
            done = True  # Successful exploitation

    rewards_per_episode.append(episode_reward)
    agent.decay_exploration()

# Plot the learning curve
plt.plot(rewards_per_episode)
plt.xlabel("Episodes")
plt.ylabel("Total Reward")
plt.title("Learning Progress Over Episodes")
plt.show()

print("Training completed. Q-table:")
print(agent.q_table)
