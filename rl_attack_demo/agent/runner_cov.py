import subprocess, tempfile, mmap, os, pathlib, numpy as np
from typing import Tuple

class ProgramRunnerCov:
    MAP_SIZE = 64 * 1024 

    def __init__(self, bin_path: str, timeout: float = 0.3):
        self.bin_path = pathlib.Path(bin_path).absolute()
        if not self.bin_path.exists():
            raise FileNotFoundError(self.bin_path)
        self.timeout = timeout

    def __call__(self, x: int) -> Tuple[bytes, int, np.ndarray]:
        with tempfile.NamedTemporaryFile() as tmp_map:
            cmd = ["afl-showmap", "-q", "-o", tmp_map.name, str(self.bin_path)]
            proc = subprocess.run(
                cmd, input=f"{x}\n".encode(),
                capture_output=True, timeout=self.timeout
            )

            size = os.path.getsize(tmp_map.name)
            if size == 0:              
                bitmap = np.zeros(self.MAP_SIZE, dtype=np.uint8)
            else:
                with open(tmp_map.name, "rb") as f:
                    mm = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)
                    bitmap = np.frombuffer(mm, dtype=np.uint8).copy()
                    mm.close()

            return proc.stdout, proc.returncode, bitmap