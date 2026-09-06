"""
fractallattice — Recursive 6-node processing lattice for LLMs.
Six nanobots process every input through a different lens.
"""
__version__ = "0.1.0"
from .core import Lattice, NANOBOT_PROMPTS, NANOBOT_NAMES, default_merge
__all__ = ["Lattice", "NANOBOT_PROMPTS", "NANOBOT_NAMES", "default_merge"]
