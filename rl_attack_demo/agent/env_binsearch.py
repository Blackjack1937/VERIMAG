# agent/env_binsearch.py
import numpy as np, gymnasium as gym


class BinSearchEnv(gym.Env):
    """
    Action = guess in [0, 255].
    Reward = +10 on hit, -1 per step, +0.05 per interval shrink.
    Horizon = 10.
    """
    metadata = {"render_modes": []}

    def __init__(self, n_bits: int = 8, horizon: int = 10):
        super().__init__()
        self.N = 1 << n_bits
        self.horizon = horizon

        self.action_space = gym.spaces.Discrete(self.N)
        self.observation_space = gym.spaces.MultiDiscrete([self.N, self.N])
        self._secret = None
        self._lo, self._hi, self._steps = 0, self.N - 1, 0

    #gym API
    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self._secret = self.np_random.integers(self.N)
        self._lo, self._hi, self._steps = 0, self.N - 1, 0
        return np.array([self._lo, self._hi], dtype=np.uint8), {}

    def step(self, action: int):
        self._steps += 1
        prev_size = self._hi - self._lo
        reward, done = -1.0, False

        if action == self._secret:
            reward, done = 10.0, True
        elif action < self._secret:
            self._lo = max(self._lo, action + 1)
        else:  # action > secret
            self._hi = min(self._hi, action - 1)

        # dense bonus for shrinking the interval
        new_size = self._hi - self._lo
        reward += (prev_size - new_size) * 0.20

        done = done or (self._steps >= self.horizon)
        return np.array([self._lo, self._hi], dtype=np.uint8), reward, done, False, {}
