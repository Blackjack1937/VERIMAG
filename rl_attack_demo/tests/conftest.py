import subprocess, pathlib, pytest, os

ROOT = pathlib.Path(__file__).resolve().parents[1]
TARGETS = ROOT / "targets"
@pytest.fixture(scope="session", autouse=True)
def build_binaries_once():
    """Compile normal + instrumented target before any test."""
    print("\n⏳ Building binaries for tests…")
    #normal
    subprocess.run(["make", "-C", str(TARGETS)], check=True)
    # afl
    env = os.environ.copy()
    env["CC"] = "afl-clang-fast"
    subprocess.run(["make", "-C", str(TARGETS), "cov"], env=env, check=True)
