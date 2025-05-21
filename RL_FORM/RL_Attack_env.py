import numpy as np
import random
import matplotlib.pyplot as plt
from collections import deque

class TargetProgram:
    """
    Represents the vulnerable program. The attacker interacts with it via the `execute` method.
    """
    def __init__(self, fixed_random_seed=True):
        self.fixed_random_seed = fixed_random_seed
        # If fixed_random_seed is True, y_r is chosen once and stays constant for all runs
        # else, its rechosen each reset
        self.y_r = random.randint(1, 100) if fixed_random_seed else None

    def reset(self):
        """Resets the random components of the program for a new execution."""
        if not self.fixed_random_seed:
            self.y_r = random.randint(1, 100)

    def execute(self, x, y):
        """
        Simulates program execution with inputs (x, y).
        Returns a reward signal:
          +10 if x == 42 and y_total > 150 (successful attack),
          +5 if x == 42 but y_total <= 150 (partial success),
          -1 otherwise.
        """
        y_c = random.randint(1, 100)  # Dynamic random component
        y_total = self.y_r + y_c if self.y_r is not None else y_c
        
        if x == 42 and y_total > 150:
            return 10  # success
        if x == 42:
            return 5   #  p^artial progress
        return -1      # fail


class RLAttackAgent:
    """
    A simple Q-Learning agent to find the best attack strategy.
    """
    def __init__(self, state_size, action_size, learning_rate=0.1, discount_factor=0.9, exploration_rate=0.5):
        self.state_size = state_size
        self.action_size = action_size
        self.q_table = np.zeros((state_size, action_size))

        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = exploration_rate  # epsilon-greedy exploration rate

    def choose_action(self, state):
        """Choose an action using epsilon-greedy exploration."""
        if np.random.rand() < self.epsilon:
            return random.randint(0, self.action_size - 1)
        else:
            return np.argmax(self.q_table[state])

    def update_q_value(self, state, action, reward, next_state):
        """Updates the Q-table using the Bellman equation."""
        best_next_action = np.argmax(self.q_table[next_state])
        td_target = reward + self.gamma * self.q_table[next_state, best_next_action]
        td_error = td_target - self.q_table[state, action]
        self.q_table[state, action] += self.lr * td_error

    def decay_exploration(self, decay_rate=0.99, min_epsilon=0.01):
        """Reduce exploration rate over time."""
        self.epsilon = max(min_epsilon, self.epsilon * decay_rate)



# Setting up the environment
target_program = TargetProgram(fixed_random_seed=True)
agent = RLAttackAgent(state_size=50, action_size=50,
                      learning_rate=0.1, discount_factor=0.9, exploration_rate=0.5)

episodes = 100  #   n of episodes for training
max_steps = 100 # max steps per episode to prevent infinite loops

rewards_per_episode = []  #total reward per episode
window = 10  # window size for moving average smoothing

for episode in range(episodes):
    target_program.reset()
    state = random.randint(0, 49)  # Init (simplistic) state
    done = False
    episode_reward = 0

    for step in range(max_steps):
        action = agent.choose_action(state)
        x = action // 10         
        y = (action % 50) * 10  
        reward = target_program.execute(x, y)
        next_state = x

        agent.update_q_value(state, action, reward, next_state)


        # accumulate total reward
        episode_reward += reward
        state = next_state
        if reward == 10:
            done = True
            break
    rewards_per_episode.append(episode_reward)
    # decay the exploration rate
    agent.decay_exploration(decay_rate=0.99)
    if episode % 10 == 0:
        print(f"Episode {episode}, Reward: {episode_reward}, Epsilon: {agent.epsilon:.3f}")


# Plot 
# smooth the rewards with a moving average
if len(rewards_per_episode) >= window:
    smoothed_rewards = np.convolve(rewards_per_episode, 
                                   np.ones(window)/window, mode='valid')
else:
    smoothed_rewards = rewards_per_episode  #not enough data to smooth

plt.plot(smoothed_rewards)
plt.xlabel("Episodes")
plt.ylabel("Smoothed Total Reward")
plt.title("Learning Progress Over Episodes")
plt.show()

print("\nTraining completed. Final Q-table sample:")
print(agent.q_table[:5, :5], "...")  # small portion for brevity
