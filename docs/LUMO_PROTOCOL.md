# Lumo Collaboration Protocol — OpenRoot Project

> **Established:** July 21, 2026  
> **User:** jesseray718 (jesse)  
> **Project:** openroot  
> **Device:** Samsung SM-A156U (Galaxy A15)

---

## 1. Session Memory Format

### Device Profile
- Model: SM-A156U
- Android: 10+
- Root Status: Non-rooted, Magisk zip on device
- Storage: 4.1G free / 46G total (91% used)
- RAM Available: ~850MB typical

### Project Structure
- Base: `~/openroot`
- Bin: `~/openroot/bin/`
- Output: `/sdcard/openroot/output/`
- Context: `/sdcard/openroot/context_bridge/context.json`
- Downloads: `/sdcard/Download/`

### Known Constraints
- `/sdcard` mounted noexec via FUSE — scripts live in `~/openroot/bin/`
- `/tmp` does not exist — use `$PREFIX/tmp` for temp files
- Symlinks from home to `/sdcard` fail silently
- `termux-clipboard-set` unreliable — use file-based clip_send/read

---

## 2. Coding Style Preferences

### Bash Standards
- Functions: Max 30 lines
- Comments: Header + inline for non-obvious logic
- Error handling: Fail early, log to `$LOG_DIR/`
- Paths: Absolute only (`~/openroot/...`)
- Variables: UPPERCASE constants, lowercase temps
- Shebang: `#!/data/data/com.termux/files/usr/bin/bash`

### Python Standards
- Lines: 80 char max
- Docstrings: All public functions
- Dependencies: Pin in requirements.txt

### Error Handling
| Level | Example | Action |
|-------|---------|--------|
| INFO | Log created | Acknowledge + summarize |
| WARNING | 91% disk | Flag + recommend action |
| ERROR | Permission denied | Provide fix + verification |
| CRITICAL | Out of space | Stop + prioritize cleanup |

---

## 3. Value Alignment

### Permaculture Principles
1. observe_and_interact → Read system before changes
2. catch_and_store_energy → Capture logs, snapshots
3. obtain_yield → Every script produces measurable output
4. apply_self_regulation → Monitor RAM/disk
5. use_renewable_resources → Reusable scripts
6. produce_no_waste → Clean trash, archive old data
7. design_from_patterns_to_details → Layer automation
8. integrate_not_segregate → Connect Termux, Shizuku, Markor
9. use_small_and_slow_solutions → Test incrementally
10. use_and_value_diversity → Redundancy (clip_send + clipboard)
11. use_edges_and_valuate_marginalia → Track known_issues
12. creatively_use_and_respond_to_change → Adapt constraints

### Agape Reminders
- Integrate naturally, never preachy
- Examples: "privacy-first design", "serves the least among us"
- Avoid: Moralizing, unsolicited value lectures

---

## 4. Tool Inventory

| Command | Purpose | Status |
|---------|---------|--------|
| `ctx summary` | Context bridge | ✅ Working |
| `cycle` | System snapshot | ✅ Working |
| `clip_send.sh` | Stage text | ✅ Working |
| `clip_read.sh` | Retrieve text | ✅ Working |
| `router.sh check` | Diagnostics | ✅ Working |
| `financial_health.sh` | LLC check | ✅ Working |

---

## 5. Version History

| Date | Update |
|------|--------|
| 2026-07-21 | Initial |

---

End of Protocol
