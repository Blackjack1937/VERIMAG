import numpy as np, gymnasium as gym
from .runner import ProgramRunner


class CrashEnv(gym.Env):
    """
    Black-box env.  n_bits = 16 par défaut (Phase 1).
    Observation = (last_x , hash(stdout))  => Discrete(2^n_bits) × Discrete(256)
    Action      = Discrete(2^n_bits)
    """

    metadata = {"render_modes": []}

    def __init__(self, bin_path="bin/magic_crash", n_bits: int = 16,
                 horizon: int = 100):
        super().__init__()
        self.runner = ProgramRunner(bin_path)
        self.n_bits = n_bits
        self.horizon = horizon

        self.action_space = gym.spaces.Discrete(2 ** n_bits)
        self.observation_space = gym.spaces.Dict({
            "last_x": gym.spaces.Discrete(2 ** n_bits),
            "last_y": gym.spaces.Discrete(256),           # 8-bit checksum
        })
        self._steps = 0
        self._state = None

    @staticmethod
    def _hash_stdout(buf: bytes) -> int:
        return sum(buf) & 0xFF

    # gym API
    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self._steps = 0
        x0 = self.action_space.sample()
        y0, _ = self.runner(x0)
        self._state = {"last_x": x0, "last_y": self._hash_stdout(y0)}
        return self._obs_to_np(), {}

    def step(self, action):
        self._steps += 1
        y, rc = self.runner(int(action))
        reward = 10.0 if rc != 0 else 0.0
        self._state = {"last_x": int(action), "last_y": self._hash_stdout(y)}
        done = self._steps >= self.horizon
        return self._obs_to_np(), reward, done, False, {}

    # util 
    def _obs_to_np(self):
        return np.array([self._state["last_x"], self._state["last_y"]],
                        dtype=np.uint32)
