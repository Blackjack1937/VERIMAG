import numpy as np, random

class QTableAgent:
    def __init__(self, alpha=0.1, gamma=0.9, eps=0.1):
        self.q = np.zeros((256*256, 256), dtype=np.float32)  # (obs idx, action)
        self.alpha, self.gamma, self.eps = alpha, gamma, eps
    def _idx(self, obs):
        x, y = obs       # both 0-255
        return (y << 8) | x
    def act(self, obs):
        idx = self._idx(obs)
        if random.random() < self.eps:
            return random.randrange(256)
        return int(self.q[idx].argmax())
    def learn(self, obs, act, rew, next_obs, done):
        idx, nidx = self._idx(obs), self._idx(next_obs)
        target = rew + (0 if done else self.gamma * self.q[nidx].max())
        self.q[idx, act] += self.alpha * (target - self.q[idx, act])
