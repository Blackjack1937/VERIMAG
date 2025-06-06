from setuptools import setup, find_packages
setup(
    name="rl_attack_demo",
    version="0.0.1",
    packages=find_packages(include=["agent", "agent.*"]),
    python_requires=">=3.10",
)
