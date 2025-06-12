# tests/test_binenv.py
from agent.env_binsearch import BinSearchEnv
def test_binenv_shapes():
    env = BinSearchEnv()
    obs,_ = env.reset()
    assert obs.shape == (2,)
    nobs, r, done, _, _ = env.step(env.action_space.sample())
    assert nobs.shape == (2,)
    assert r in (-1.0, 10.0)
