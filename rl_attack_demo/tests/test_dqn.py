from agent.dqn import DQNAgent
import numpy as np

def test_dqn_learn_step():
    ag = DQNAgent(n_bits=8, device="cpu")   # small variant for test speed
    # push a fake transition with reward
    s  = np.array([0, 0], dtype=np.float32)
    s2 = np.array([1, 0], dtype=np.float32)
    ag.remember(s, 1, 10.0, s2, False)
    loss_before = ag.train_step(batch_size=1)
    assert loss_before > 0
