import numpy as np, gymnasium as gym
from .runner_cov import ProgramRunnerCov

class CrashEnvCov(gym.Env):
    """
    Reward = 10 (crash) + λ * (# nouveaux blocs découverts)
    """
    metadata = {"render_modes": []}

    def __init__(self, bin_path="bin/magic_crash_cov",
                 n_bits=16, horizon=100, lambda_cov=0.05, 
                 runner_timeout: float = 0.3):
        super().__init__()
        self.runner = ProgramRunnerCov(bin_path, timeout=runner_timeout)
        self.n_bits = n_bits
        self.horizon = horizon
        self.lambda_cov = lambda_cov

        self.action_space = gym.spaces.Discrete(2 ** n_bits)
        self.observation_space = gym.spaces.Box(
            low=0, high=np.iinfo(np.uint32).max, shape=(2,), dtype=np.uint32
        )
        self._steps = 0
        self._state = None
        self._cum_bitmap = np.zeros(64 * 1024, dtype=np.uint8)  # global episode bitmap

    #gym API
    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self._steps = 0
        self._cum_bitmap.fill(0)

        x0 = self.action_space.sample()
        y0, rc0, bm0 = self.runner(x0)
        self._cum_bitmap |= bm0

        self._state = np.array([x0, rc0], dtype=np.uint32)    #cheap obs
        return self._state.copy(), {}

    def step(self, action):
        self._steps += 1
        out, rc, bitmap = self.runner(int(action))

        #reward
        crash_r = 10.0 if rc != 0 else 0.0
        new_blocks = np.logical_and(bitmap, np.logical_not(self._cum_bitmap)).sum()
        cov_r = self.lambda_cov * new_blocks
        reward = crash_r + cov_r


        # update bitmap & state


        self._cum_bitmap |= bitmap
        self._state = np.array([int(action), rc], dtype=np.uint32)
        done = self._steps >= self.horizon
        return self._state.copy(), reward, done, False, {}
