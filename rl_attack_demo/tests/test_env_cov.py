from agent.env_cov import CrashEnvCov

def test_cov_reward_positive():
    env = CrashEnvCov(n_bits=8, lambda_cov=1.0, horizon=10, runner_timeout=0.3)
    obs, _ = env.reset()
    _, r1, _, _, _ = env.step(1)
    assert r1 >= 0.0
