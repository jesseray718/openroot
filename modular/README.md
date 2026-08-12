# Modular Layer

Everything in OpenRoot is intended to be decomposable.

Any subsystem (physical node, measurement tool, seed, oracle interface, mesh hop, thermal surface) should be extractable as a clean module that can be:
- used alone
- improved by outsiders
- reassembled with modules from other open-source projects
- pushed back upstream

The test for every module remains the same: does this raise α_A for the lowest node?
