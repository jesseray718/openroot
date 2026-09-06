---
name: Tighten offline tools
about: hive.sh / offline_rank.py / query_agent.py
title: "Tighten offline tools (hive.sh / offline_rank.py / query_agent.py)"
labels: enhancement, offline, swarm
---

The three offline tools were promoted to main in f112bca but need hardening.

Tasks:
1. Verify the three files exist and are executable on a fresh clone
2. Document the intended call chain: query → offline_rank → hive
3. Make them discoverable from the front door
4. Ensure they write clean entries into the thermodynamic / PoPW ledger
5. Add a one-line smoke test that can be run offline
