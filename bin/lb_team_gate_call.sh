#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0
# Wrapper for lb_loop: team_gate_v2.sh requires <task_description> (usage: awk->7B->3B->sqlite pipeline).
# Task supplied via LB_TASK env var; defaults to steady-state loop verification task.
# Doctrine: pipeline stages call wrappers that satisfy instrument usage.
set -u
cd "$(dirname "$0")/.." || exit 1
TASK="${LB_TASK:-lb_loop steady-state pass: verify all prior stage cache-hits are sound and record to team_gate.db}"
exec bash bin/team_gate_v2.sh "$TASK"
