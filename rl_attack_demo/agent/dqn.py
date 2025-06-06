# agent/dqn.py
import random, collections, numpy as np, torch, torch.nn as nn, torch.optim as optim


class ReplayBuffer:
    def __init__(self, capacity=100_000):
        self.buf = collections.deque(maxlen=capacity)

    def push(self, *transition):
        self.buf.append(transition)

    def sample(self, batch_size):
        batch = random.sample(self.buf, batch_size)
        return map(np.array, zip(*batch))

    def __len__(self):
        return len(self.buf)



class QNet(nn.Module):
    """MLP that maps an observation vector to |A| logits (16-bit: 65536)."""
    def __init__(self, n_bits=16):
        super().__init__()
        self.n_bits = n_bits
        n_actions = 2 ** n_bits
        self.net = nn.Sequential(
            nn.Linear(2, 512), nn.ReLU(),
            nn.Linear(512, 512), nn.ReLU(),
            nn.Linear(512, n_actions),
        )

    def forward(self, x):
        # x shape (batch, 2)  already float32
        return self.net(x)


class DQNAgent:
    def __init__(self, n_bits=16, lr=1e-3, gamma=0.9,
                 eps_start=1.0, eps_end=0.05, eps_decay=50_000,
                 device="cpu"):
        self.n_bits = n_bits
        self.n_actions = 2 ** n_bits
        self.gamma = gamma
        self.device = torch.device(device)
        self.policy = QNet(n_bits).to(self.device)
        self.target = QNet(n_bits).to(self.device)
        self.target.load_state_dict(self.policy.state_dict())
        self.opt = optim.Adam(self.policy.parameters(), lr=lr)
        self.replay = ReplayBuffer()
        self.eps_start, self.eps_end, self.eps_decay = eps_start, eps_end, eps_decay
        self.step_cnt = 0

    #utils
    def _eps(self):
        return self.eps_end + (self.eps_start - self.eps_end) * \
            np.exp(-1. * self.step_cnt / self.eps_decay)

    def act(self, obs_np):
        self.step_cnt += 1
        if random.random() < self._eps():
            return random.randrange(self.n_actions)
        obs_t = torch.tensor(obs_np, dtype=torch.float32,
                             device=self.device).unsqueeze(0)
        with torch.no_grad():
            qvals = self.policy(obs_t).squeeze(0)
            return int(torch.argmax(qvals).item())

    #learn
    def remember(self, *transition):
        self.replay.push(*transition)

    def train_step(self, batch_size=128):
        if len(self.replay) < batch_size:
            return 0.0
        s, a, r, s2, done = self.replay.sample(batch_size)
        s = torch.tensor(s, dtype=torch.float32, device=self.device)
        a = torch.tensor(a, dtype=torch.long, device=self.device)
        r = torch.tensor(r, dtype=torch.float32, device=self.device)
        s2 = torch.tensor(s2, dtype=torch.float32, device=self.device)
        done = torch.tensor(done, dtype=torch.float32, device=self.device)

        q_sa = self.policy(s).gather(1, a[:, None]).squeeze(1)
        with torch.no_grad():
            q_next = self.target(s2).max(1).values
            td_target = r + self.gamma * (1 - done) * q_next

        loss = nn.functional.mse_loss(q_sa, td_target)
        self.opt.zero_grad(); loss.backward(); self.opt.step()
        return loss.item()

    def sync_target(self):
        self.target.load_state_dict(self.policy.state_dict())
