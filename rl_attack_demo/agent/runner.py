import subprocess
from pathlib import Path

class ProgramRunner:
    """Run a compiled binary with one int on stdin."""
    def __init__(self, bin_path: str, timeout: float = 0.05):
        self.bin_path = Path(bin_path).absolute()
        if not self.bin_path.exists():
            raise FileNotFoundError(self.bin_path)
        self.timeout = timeout

    def __call__(self, x: int):
        proc = subprocess.run(
            [str(self.bin_path)],
            input=f"{x}\n".encode(),
            capture_output=True,
            timeout=self.timeout,
        )
        return proc.stdout, proc.returncode
