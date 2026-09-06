# 100-round prediction (this topic + SSH + sqlite + tidbit + 7B)

Ground truth from 2026-09-02 A15 session: Python pasted at $, heredoc split, git add PATH, t remote -v, second clone, primer then succeeded.

Rounds 1-12 already happened in some form. 13-100 are the same families on a cycle.

Severity 5 will waste a session if ignored:

1. Python at bash
2. Split heredoc
3. Wrong pane paths
4. Placeholder IP 192.168.1.x
5. Tilde in paste
6. rm of cwd
7. 7B on A15
8. unique-ID wipe of Syncthing
9. New modules while canon false
10. Token leak

sqlite table error_pred holds all 100 after rounds_sim.py.
Query:

python3 .../tidbit.py module git
python3 .../rounds_sim.py

Do not re-simulate by hand in chat. The table is the simulation.
