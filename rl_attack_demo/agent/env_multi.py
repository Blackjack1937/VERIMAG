import numpy as np, gymnasium as gym
from .runner import ProgramRunner

class MultiOracleEnv(gym.Env):
    """8-bit: guess (0-255) or query an oracle (256-258)."""
    metadata = {"render_modes": []}

    def __init__(self, bin_path="bin/magic_crash", horizon=20):
        super().__init__()
        self.runner = ProgramRunner(bin_path, timeout=0.05)
        self.horizon = horizon

        self.action_space = gym.spaces.Discrete(259)          # 0–258
        self.observation_space = gym.spaces.Dict({
            "last_x": gym.spaces.Discrete(256),
            "last_y": gym.spaces.Discrete(256),
            "oracle": gym.spaces.Discrete(3),   # 0=none, 1=low, 2=high, etc.
        })
        self._reset_secret()

    # ---------------------------------------------------------------- utils
    def _reset_secret(self):
        self.secret = self.np_random.integers(256)
        self.steps  = 0
        self.state  = {"last_x": 0, "last_y": 0, "oracle": 0}

    def _obs(self):
        return np.array([self.state["last_x"],
                         self.state["last_y"],
                         self.state["oracle"]], dtype=np.uint8)

    # ---------------------------------------------------------------- gym API
    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed); self._reset_secret()
        return self._obs(), {}

    def step(self, action: int):
        self.steps += 1
        done, reward = False, 0.0

        # ----- guess
        if action < 256:
            y, rc = self.runner(action)
            reward = 10.0 if rc != 0 else -1.0     # small cost if miss
            self.state["last_x"] = action
            self.state["last_y"] = sum(y) & 0xFF
            done = (rc != 0)
        # ----- higher/lower
        elif action == 256:      # higher / lower
            reward = -0.2
            if self.secret < self.state["last_x"]:
                self._hi = self.state["last_x"] - 1
                self.state["oracle"] = 1
            elif self.secret > self.state["last_x"]:
                self._lo = self.state["last_x"] + 1
                self.state["oracle"] = 2
            else:                           # equal → win
                reward, done = 10.0, True
        # ----- parity
        elif action == 257:
            reward = -0.1
            self.state["oracle"] = self.secret & 1         # 0 even, 1 odd
        # ----- MSB
        else:  # 258
            reward = -0.1
            self.state["oracle"] = (self.secret >> 7) & 1  # top bit

        done = done or (self.steps >= self.horizon)
        return self._obs(), reward, done, False, {}
