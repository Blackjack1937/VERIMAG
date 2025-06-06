import numpy as np, gymnasium as gym
from .runner import ProgramRunner

class CrashEnv(gym.Env):
    """Minimal black-box env (8-bit prototype)."""
    metadata = {"render_modes": []}

    def __init__(self, bin_path="bin/magic_crash", horizon=100):
        super().__init__()
        self.runner = ProgramRunner(bin_path)
        self.horizon = horizon
        # action: choose x ∈ [0..255]
        self.action_space = gym.spaces.Discrete(256)
        # observation: last_x ∈ [0..255], last_y_hash ∈ [0..255]
        self.observation_space = gym.spaces.MultiDiscrete([256, 256])
        self._steps = 0
        self._state = None

    @staticmethod
    def _hash_stdout(buf: bytes) -> int:
        return sum(buf) & 0xFF          # 8-bit checksum

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self._steps = 0
        x0 = self.action_space.sample()
        y0, _ = self.runner(x0)
        self._state = (x0, self._hash_stdout(y0))
        return np.array(self._state, dtype=np.uint8), {}

    def step(self, action):
        self._steps += 1
        y, rc = self.runner(int(action))
        reward = 10.0 if rc != 0 else 0.0
        self._state = (int(action), self._hash_stdout(y))
        done = self._steps >= self.horizon
        return np.array(self._state, dtype=np.uint8), reward, done, False, {}

