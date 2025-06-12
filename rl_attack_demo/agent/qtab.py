import numpy as np, random


class QTableAgent:
    def __init__(self, alpha=0.1, gamma=0.9,
                 eps_start=1.0, eps_end=0.05, eps_decay=500):
        self.q = np.zeros((256 * 256, 256), dtype=np.float32)
        self.alpha, self.gamma = alpha, gamma
        self.eps_start, self.eps_end, self.eps_decay = eps_start, eps_end, eps_decay
        self.steps = 0

    # ---------------- internal helpers -------------------------------------
    @staticmethod
    def _idx(obs):
        lo, hi = obs
        return (lo << 8) | hi          # unique 16-bit key

    def _eps(self):
        self.steps += 1
        return self.eps_end + (self.eps_start - self.eps_end) * \
               np.exp(-1.0 * self.steps / self.eps_decay)

    # ---------------- public API -------------------------------------------
    def act(self, obs):
        if random.random() < self._eps():
            return random.randrange(256)
        idx = self._idx(obs)
        return int(self.q[idx].argmax())

    def learn(self, obs, act, rew, next_obs, done):
        idx, nidx = self._idx(obs), self._idx(next_obs)
        target = rew if done else rew + self.gamma * self.q[nidx].max()
        self.q[idx, act] += self.alpha * (target - self.q[idx, act])
