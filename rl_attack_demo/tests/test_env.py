from agent.env import CrashEnv
from pathlib import Path
root = Path(__file__).resolve().parents[1]
env = CrashEnv(bin_path=root / "bin" / "magic_crash", n_bits=8)
def test_step_shapes():
    env = CrashEnv()
    obs,_ = env.reset()
    assert obs.shape == (2,)
    nobs,r,done,_,_ = env.step(123)
    assert nobs.shape == (2,)
    assert r in (0.0, 10.0)
