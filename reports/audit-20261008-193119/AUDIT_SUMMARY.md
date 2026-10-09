# OPENROOT NODE AUDIT — 20261008-193119

Read-only. Tokens redacted. Secret-file contents not read.


===== 0. AUDIT META =====
Started : 2026-10-08T19:31:19-05:00
Host    : optiplex3060
Mode    : read-only


===== 1. HOST & HARDWARE =====
 Static hostname: optiplex3060
         Chassis: desktop 🖥️
Operating System: Ubuntu 24.04.5 LTS
          Kernel: Linux 7.0.0-34-generic
 19:31:19 up 11 days,  4:52,  6 users,  load average: 0.36, 0.25, 0.38
CPU(s):                                  6
Model name:                              Intel(R) Core(TM) i5-8500 CPU @ 3.00GHz
Thread(s) per core:                      1
Core(s) per socket:                      6
CPU(s) scaling MHz:                      20%
               total        used        free      shared  buff/cache   available
Mem:            15Gi       4.3Gi       220Mi        32Mi        11Gi        11Gi
Swap:           15Gi       3.9Gi        11Gi
NAME     SIZE TYPE FSTYPE   MOUNTPOINT
loop0      4K loop squashfs /snap/bare/5
loop1    8.7M loop squashfs /snap/ruff/1700
loop2     74M loop squashfs /snap/core22/2437
loop3   66.8M loop squashfs /snap/core24/1643
loop4   66.8M loop squashfs /snap/core24/2124
loop5  531.4M loop squashfs /snap/gnome-42-2204/247
loop6  531.5M loop squashfs /snap/gnome-42-2204/263
loop7  614.5M loop squashfs /snap/gnome-46-2404/164
loop8  615.3M loop squashfs /snap/gnome-46-2404/168
loop9    1.5G loop squashfs /snap/kf5-core22/3
loop10   402M loop squashfs /snap/mesa-2404/1839
loop11  44.7M loop squashfs /snap/snapd/28254
loop13    74M loop squashfs /snap/core22/2955
loop14  50.3M loop squashfs /snap/snapd/27738
loop15   8.7M loop squashfs /snap/ruff/1696
sda      2.7T disk          
├─sda1   976M part vfat     /boot/efi
├─sda2   1.4T part ext4     /data
├─sda3  15.8G part swap     [SWAP]
└─sda4   1.4T part ext4     /
sdb    114.6G disk iso9660  
└─sdb1 114.6G part exfat    /mnt/sdb1
sdc     57.6G disk          
└─sdc1  57.6G part exfat    
sr0     1024M rom           


===== 2. FILESYSTEM USAGE =====
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda4       1.4T  391G  906G  31% /
efivarfs        256K   99K  153K  40% /sys/firmware/efi/efivars
/dev/sdb1       115G   78G   37G  68% /mnt/sdb1
/dev/sda1       975M   15M  960M   2% /boot/efi
/dev/sda2       1.4T  119G  1.2T  10% /data
[audit] walking ~ for du (slowest step)


===== 3. HOME FOOTPRINT (top 35 by size) =====
326G	/home/jesse
129G	/home/jesse/openroot
46G	/home/jesse/optiplex-archive
40G	/home/jesse/archives
37G	/home/jesse/snap
12G	/home/jesse/wisdom-scaffold
9.7G	/home/jesse/.local
8.6G	/home/jesse/wisdom-recovery
8.0G	/home/jesse/harvest_hold
6.0G	/home/jesse/rag-venv
5.0G	/home/jesse/backup_a15_termux
3.9G	/home/jesse/kai_recovery
2.6G	/home/jesse/Kai
2.6G	/home/jesse/Desktop
2.4G	/home/jesse/attic
1.8G	/home/jesse/src
1.3G	/home/jesse/repo_audit_workspace
1.3G	/home/jesse/code
801M	/home/jesse/.npm
686M	/home/jesse/.openroot_venv
540M	/home/jesse/openroot-history-backup.git
528M	/home/jesse/github
425M	/home/jesse/github-traffic-scripts
425M	/home/jesse/github-mirror
423M	/home/jesse/une-push
420M	/home/jesse/une
395M	/home/jesse/.npm-global
335M	/home/jesse/openroot-build
325M	/home/jesse/knowledge-node
200M	/home/jesse/github3
189M	/home/jesse/openroot-swarm-publish
189M	/home/jesse/openroot-public-boundary-pr
189M	/home/jesse/openroot-newton-pr
189M	/home/jesse/openroot-newton-integration-20261003T080401Z
189M	/home/jesse/openroot-main-current-20261002T211546


===== 4. SERVICES & SCHEDULERS =====
--- newton-daemon (system scope) ---
inactive
not-found
NRestarts=0
ExecMainStartTimestamp=
ExecMainPID=0
ActiveState=inactive
SubState=dead
--- newton-daemon (user scope) ---
failed
--- running system services ---
  UNIT                          LOAD   ACTIVE SUB     DESCRIPTION
  anacron.service               loaded active running Run anacron jobs
  avahi-daemon.service          loaded active running Avahi mDNS/DNS-SD Stack
  cron.service                  loaded active running Regular background program processing daemon
  cups-browsed.service          loaded active running Make remote CUPS printers available locally
  cups.service                  loaded active running CUPS Scheduler
  dbus.service                  loaded active running D-Bus System Message Bus
  fail2ban.service              loaded active running Fail2Ban Service
  fwupd.service                 loaded active running Firmware update daemon
  getty@tty1.service            loaded active running Getty on tty1
  kerneloops.service            loaded active running Tool to automatically collect and submit kernel crash signatures
  llama-server.service          loaded active running llama.cpp server (OptiPlex heavy spoke - Qwen2.5-Coder-7B)
  ModemManager.service          loaded active running Modem Manager
  NetworkManager.service        loaded active running Network Manager
  ollama.service                loaded active running Ollama Service
  openroot-rapl-sampler.service loaded active running OpenRoot RAPL counter sampler (root: reads /sys/class/powercap)
  polkit.service                loaded active running Authorization Manager
  rsyslog.service               loaded active running System Logging Service
  rtkit-daemon.service          loaded active running RealtimeKit Scheduling Policy Service
  smartmontools.service         loaded active running Self Monitoring and Reporting Technology (SMART) Daemon
  snapd.service                 loaded active running Snap Daemon
  ssh.service                   loaded active running OpenBSD Secure Shell server
  syncthing@jesse.service       loaded active running Syncthing - Open Source Continuous File Synchronization for jesse
  systemd-journald.service      loaded active running Journal Service
  systemd-logind.service        loaded active running User Login Management
  systemd-machined.service      loaded active running Virtual Machine and Container Registration Service
  systemd-resolved.service      loaded active running Network Name Resolution
  systemd-timesyncd.service     loaded active running Network Time Synchronization
  systemd-udevd.service         loaded active running Rule-based Manager for Device Events and Files
  tailscaled.service            loaded active running Tailscale node agent
--- running user services ---
  UNIT                         LOAD   ACTIVE SUB     DESCRIPTION
  dbus.service                 loaded active running D-Bus User Message Bus
  filter-chain.service         loaded active running PipeWire filter chain daemon
  gnome-keyring-daemon.service loaded active running GNOME Keyring daemon
  openai-relay-9999.service    loaded active running OpenRoot OpenAI relay :9999 -> :11434 (kai9000 endpoint)
  openclaw-gateway.service     loaded active running OpenClaw Gateway (v2026.7.1-2)
  openroot-dash.service        loaded active running OpenRoot edge dashboard (:8766)
  openroot-edge.service        loaded active running OpenRoot edge autopilot (keeper + daemon + claim/mint loop)
  pipewire-pulse.service       loaded active running PipeWire PulseAudio
  pipewire.service             loaded active running PipeWire Multimedia Service
  wireplumber.service          loaded active running Multimedia Service Session Manager

Legend: LOAD   → Reflects whether the unit definition was properly loaded.
        ACTIVE → The high-level unit activation state, i.e. generalization of SUB.
        SUB    → The low-level unit activation state, values depend on unit type.

10 loaded units listed.
--- self-hosted actions runner ---
2900057 bash -c echo "--- self-hosted actions runner ---"      pgrep -af "Runner.Listener|actions-runner" | head -5
--- cron ---
0 3 * * * /usr/bin/python3 /home/jesse/src/openroot-thesis/scripts/mesh_governor.py >> /home/jesse/src/openroot-thesis/audit_reports/mesh_governor.log 2>&1
15 3 * * * /usr/bin/python3 /home/jesse/github-audit/repo_loop.py >> /home/jesse/github-audit/repo-loop.log 2>&1
0 */6 * * * OPENROOT_MODEL=qwen2.5:3b /usr/bin/python3 /home/jesse/openroot/bin/watchdog_once.py # OPENROOT-UPLIFT
*/30 * * * * /home/jesse/openroot/bin/ws_auto_sync.sh
*/15 * * * * cd /home/jesse/openroot && python3 bin/superloop_composite_v3.py >> logs/superloop.log 2>&1
# OPENROOT BOTS [CRONBRIDGEV1]
0 * * * * cd /home/jesse/openroot && python3 bin/measure_thermal_v1.py --digest >> logs/cron_thermal.log 2>&1
0 6 * * * cd /home/jesse/openroot && bin/task_dispatch_v1.sh >> logs/cron_dispatch.log 2>&1
*/10 * * * * /usr/bin/python3 /home/jesse/openroot/bin/lumo_ingest.py >> /home/jesse/openroot/logs/lumo_ingest.log 2>&1
0 3 * * * cd /home/jesse/openroot && python3 bin/file_ledger_v2.py index && python3 bin/file_ledger_parallel_v1.py 2 && python3 bin/ecosystem_v2.py >> logs/nightly_ecosystem_$(date +\%Y\%m\%d).log 2>&1


===== 5. NEWTON DAEMON LOG (tail) =====
-- No entries --
Oct 08 18:15:10 optiplex3060 systemd[1184]: Starting newton-daemon.service - Newton Chain Telemetry (one block per run)...
Oct 08 18:15:10 optiplex3060 python3[2894792]: /usr/bin/python3: can't open file '/home/jesse/openroot/bin/newton_daemon.py': [Errno 2] No such file or directory
Oct 08 18:15:10 optiplex3060 systemd[1184]: newton-daemon.service: Main process exited, code=exited, status=2/INVALIDARGUMENT
Oct 08 18:15:10 optiplex3060 systemd[1184]: newton-daemon.service: Failed with result 'exit-code'.
Oct 08 18:15:10 optiplex3060 systemd[1184]: Failed to start newton-daemon.service - Newton Chain Telemetry (one block per run).
Oct 08 18:30:10 optiplex3060 systemd[1184]: Starting newton-daemon.service - Newton Chain Telemetry (one block per run)...
Oct 08 18:30:10 optiplex3060 python3[2896137]: /usr/bin/python3: can't open file '/home/jesse/openroot/bin/newton_daemon.py': [Errno 2] No such file or directory
Oct 08 18:30:10 optiplex3060 systemd[1184]: newton-daemon.service: Main process exited, code=exited, status=2/INVALIDARGUMENT
Oct 08 18:30:10 optiplex3060 systemd[1184]: newton-daemon.service: Failed with result 'exit-code'.
Oct 08 18:30:10 optiplex3060 systemd[1184]: Failed to start newton-daemon.service - Newton Chain Telemetry (one block per run).
Oct 08 18:45:02 optiplex3060 systemd[1184]: Starting newton-daemon.service - Newton Chain Telemetry (one block per run)...
Oct 08 18:45:02 optiplex3060 python3[2896953]: /usr/bin/python3: can't open file '/home/jesse/openroot/bin/newton_daemon.py': [Errno 2] No such file or directory
Oct 08 18:45:02 optiplex3060 systemd[1184]: newton-daemon.service: Main process exited, code=exited, status=2/INVALIDARGUMENT
Oct 08 18:45:02 optiplex3060 systemd[1184]: newton-daemon.service: Failed with result 'exit-code'.
Oct 08 18:45:02 optiplex3060 systemd[1184]: Failed to start newton-daemon.service - Newton Chain Telemetry (one block per run).
Oct 08 19:00:10 optiplex3060 systemd[1184]: Starting newton-daemon.service - Newton Chain Telemetry (one block per run)...
Oct 08 19:00:10 optiplex3060 python3[2897914]: /usr/bin/python3: can't open file '/home/jesse/openroot/bin/newton_daemon.py': [Errno 2] No such file or directory
Oct 08 19:00:10 optiplex3060 systemd[1184]: newton-daemon.service: Main process exited, code=exited, status=2/INVALIDARGUMENT
Oct 08 19:00:10 optiplex3060 systemd[1184]: newton-daemon.service: Failed with result 'exit-code'.
Oct 08 19:00:10 optiplex3060 systemd[1184]: Failed to start newton-daemon.service - Newton Chain Telemetry (one block per run).
Oct 08 19:15:10 optiplex3060 systemd[1184]: Starting newton-daemon.service - Newton Chain Telemetry (one block per run)...
Oct 08 19:15:10 optiplex3060 python3[2898801]: /usr/bin/python3: can't open file '/home/jesse/openroot/bin/newton_daemon.py': [Errno 2] No such file or directory
Oct 08 19:15:10 optiplex3060 systemd[1184]: newton-daemon.service: Main process exited, code=exited, status=2/INVALIDARGUMENT
Oct 08 19:15:10 optiplex3060 systemd[1184]: newton-daemon.service: Failed with result 'exit-code'.
Oct 08 19:15:10 optiplex3060 systemd[1184]: Failed to start newton-daemon.service - Newton Chain Telemetry (one block per run).
Oct 08 19:30:00 optiplex3060 systemd[1184]: Starting newton-daemon.service - Newton Chain Telemetry (one block per run)...
Oct 08 19:30:00 optiplex3060 python3[2899702]: /usr/bin/python3: can't open file '/home/jesse/openroot/bin/newton_daemon.py': [Errno 2] No such file or directory
Oct 08 19:30:00 optiplex3060 systemd[1184]: newton-daemon.service: Main process exited, code=exited, status=2/INVALIDARGUMENT
Oct 08 19:30:00 optiplex3060 systemd[1184]: newton-daemon.service: Failed with result 'exit-code'.
Oct 08 19:30:00 optiplex3060 systemd[1184]: Failed to start newton-daemon.service - Newton Chain Telemetry (one block per run).


===== 6. PROCESSES & LIVE SCRIPT PATHS =====
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
jesse       1166  0.1 27.6 8658908 4475608 ?     Ssl  Sep27  17:27 /usr/local/bin/llama-server -m /opt/models/qwen2.5-coder-7b-instruct-q4_k_m.gguf -c 8192 -ngl 0 -t 4 --host 0.0.0.0 --port 8080 --parallel 1 --alias qwen2.5-coder-7b
jesse       1573  0.3  1.1 2773748 178712 ?      Ssl  Sep27  56:47 /usr/bin/node /home/jesse/.npm-global/lib/node_modules/openclaw/dist/index.js gateway --port 18789
root     2340669  0.0  0.3  91484 49196 ?        S<s  Oct07   0:13 /usr/lib/systemd/systemd-journald
root     2375223  0.1  0.2 1290604 42576 ?       Ssl  Oct07   2:07 /usr/sbin/tailscaled --state=/var/lib/tailscale/tailscaled.state --socket=/run/tailscale/tailscaled.sock --port=41641
jesse       1220  0.0  0.1 2280308 30188 ?       SNl  Sep27  15:33 /usr/bin/syncthing serve --no-browser --no-restart --logflags=0
root        1163  0.0  0.1 607808 28716 ?        Ssl  Sep27  12:44 /usr/bin/python3 /usr/bin/fail2ban-server -xf start
root        3618  0.0  0.1 582792 25284 ?        Ssl  Sep27   0:55 /usr/libexec/fwupd/fwupd
jesse    2392412  0.0  0.1 106892 20252 ?        Ss   Oct07   0:12 /usr/bin/python3 /home/jesse/openroot-edge/scripts/dashboard.py 8766
root     1331947  0.0  0.1 2224440 20164 ?       Ssl  Sep30   1:15 /snap/snapd/current/usr/lib/snapd/snapd
jesse    2392455  0.0  0.0  26696 15824 ?        S    Oct07   0:11 python3 /home/jesse/openroot-edge/scripts/node_daemon.py
ollama   2373804  0.0  0.0 2179956 14788 ?       Ssl  Oct07   0:07 /usr/local/bin/ollama serve
jesse    2075258  0.0  0.0 392228 13532 ?        Ss   Oct04   0:56 /usr/bin/python3 /home/jesse/openroot/bin/openai_relay_9999.py
cups-br+ 2400554  0.0  0.0 269400 13040 ?        Ssl  00:00   0:00 /usr/sbin/cups-browsed
1163 /usr/bin/python3 /usr/bin/fail2ban-server -xf start
1176 /usr/bin/python3 /usr/share/unattended-upgrades/unattended-upgrade-shutdown --wait-for-signal
1967 python3 /home/jesse/openroot/bin/bot_loop_v1.py
18546 /usr/bin/python3 /home/jesse/openroot/bin/openroot_rapl_sampler_v1.py --interval 5
2075258 /usr/bin/python3 /home/jesse/openroot/bin/openai_relay_9999.py
2079554 python3 /home/jesse/openroot/bin/1349_bottom_tier.py --role SCOUT --input night-sky radiative cooling Stirling H-003 --mode live --provider local,groq
2392412 /usr/bin/python3 /home/jesse/openroot-edge/scripts/dashboard.py 8766
2392445 bash /home/jesse/openroot-edge/scripts/agape-keeper.sh python3 /home/jesse/openroot-edge/scripts/node_daemon.py
2392455 python3 /home/jesse/openroot-edge/scripts/node_daemon.py
2900085 bash -c pgrep -af python | head -15
1573 /usr/bin/node /home/jesse/.npm-global/lib/node_modules/openclaw/dist/index.js gateway --port 18789
1967 python3 /home/jesse/openroot/bin/bot_loop_v1.py
2900090 bash -c pgrep -af "bot_loop|handoff|launch_ladder|newton|lumo|a1_core|tinycrew|governor|context_bridge|openclaw" | head -20
bot_loop.pid -> 1967
    PID     ELAPSED CMD
   1967 11-04:48:28 python3 /home/jesse/openroot/bin/bot_loop_v1.py


===== 7. NETWORK LISTENERS & LOCAL LLAMA =====
State  Recv-Q Send-Q                          Local Address:Port  Peer Address:PortProcess                                    
LISTEN 0      5                                     0.0.0.0:9999       0.0.0.0:*    users:(("python3",pid=2075258,fd=3))      
LISTEN 0      4096                                127.0.0.1:9050       0.0.0.0:*                                              
LISTEN 0      5                                     0.0.0.0:8766       0.0.0.0:*    users:(("python3",pid=2392412,fd=3))      
LISTEN 0      4096                                127.0.0.1:631        0.0.0.0:*                                              
LISTEN 0      4096                                  0.0.0.0:22         0.0.0.0:*                                              
LISTEN 0      4096                                127.0.0.1:8384       0.0.0.0:*    users:(("syncthing",pid=1220,fd=16))      
LISTEN 0      4096                            127.0.0.53%lo:53         0.0.0.0:*                                              
LISTEN 0      511                                 127.0.0.1:18789      0.0.0.0:*    users:(("node-MainThread",pid=1573,fd=33))
LISTEN 0      4096                                127.0.0.1:5037       0.0.0.0:*    users:(("adb",pid=2096674,fd=9))          
LISTEN 0      512                                   0.0.0.0:8080       0.0.0.0:*    users:(("llama-server",pid=1166,fd=3))    
LISTEN 0      32                              192.168.122.1:53         0.0.0.0:*                                              
LISTEN 0      4096                               127.0.0.54:53         0.0.0.0:*                                              
LISTEN 0      4096                100.122.169.43%tailscale0:51828      0.0.0.0:*                                              
LISTEN 0      4096   [fd7a:115c:a1e0::1a01:a9d5]%tailscale0:37598         [::]:*                                              
LISTEN 0      4096                                     [::]:22            [::]:*                                              
LISTEN 0      4096                                        *:11434            *:*                                              
LISTEN 0      4096                                    [::1]:631           [::]:*                                              
LISTEN 0      4096                                        *:22000            *:*    users:(("syncthing",pid=1220,fd=13))      
LISTEN 0      511                                     [::1]:18789         [::]:*    users:(("node-MainThread",pid=1573,fd=34))
{"error":{"message":"File Not Found","type":"not_found_error","code":404}}

NO RESPONSE on :11434

NAME                         ID              SIZE      MODIFIED    
nomic-embed-text:latest      0a109f422b47    274 MB    3 days ago     
openroot-instruct:7b         4e732ee3ca45    4.7 GB    4 days ago     
qwen2.5:7b-instruct          845dbda0ea48    4.7 GB    4 days ago     
phi4-mini:latest             78fad5d182a7    2.5 GB    10 days ago    
llama3.2:3b                  a80c4f17acd5    2.0 GB    10 days ago    
qwen2.5-coder:7b             dae161e27b0e    4.7 GB    10 days ago    
deepseek-r1:1.5b             e0979632db5a    1.1 GB    2 weeks ago    
llama3.2:1b                  baf6a787fdff    1.3 GB    2 weeks ago    
openroot-coder:latest        27df8bec37d6    4.7 GB    3 weeks ago    


===== 8. OPENROOT GIT STATE (jesseray718/openroot) =====
## main
 M data/superlinear/rapl_samples.jsonl
 M data_bot_state.json
 M logs/cron_thermal.log
 M logs/local_task_watch_v1.log
porcelain entries: 59
 M data/superlinear/rapl_samples.jsonl
 M data_bot_state.json
 M logs/cron_thermal.log
 M logs/local_task_watch_v1.log
 M logs/lumo_ingest.log
 M logs/superloop.log
 M reports/reasoning_kernel_audit_20260929T050213Z/sources/__pycache__/bin_0012_newton_chain.cpython-312.pyc
 M reports/reasoning_kernel_audit_20260929T050213Z/sources/__pycache__/bin_0054_agape_ledger_chain.cpython-312.pyc
 M reports/reasoning_kernel_audit_20260929T050213Z/sources/__pycache__/bin_0107_agape_mesh_oracle.cpython-312.pyc
 M reports/reasoning_kernel_audit_20260929T050213Z/sources/__pycache__/bin_0534_feed_oracle.cpython-312.pyc
 M reports/reasoning_kernel_audit_20260929T050213Z/sources/__pycache__/bin_0677_physics_ledger_v1.cpython-312.pyc
 M reports/reasoning_kernel_audit_20260929T050213Z/sources/__pycache__/bin_0678_physics_ledger_v2.cpython-312.pyc
 M reports/reasoning_kernel_audit_20260929T050213Z/sources/__pycache__/bin_0768_agape_cooperation_theorem.cpython-312.pyc
 M reports/reasoning_kernel_audit_20260929T050213Z/sources/__pycache__/bin_0773_proof_builder.cpython-312.pyc
 M reports/reasoning_kernel_audit_20260929T050213Z/sources/__pycache__/bin_0775_sacred_language_theorem.cpython-312.pyc
 M reports/reasoning_kernel_audit_20260929T050213Z/sources/__pycache__/bin_0776_sacred_merkle_system.cpython-312.pyc
 M reports/reasoning_kernel_audit_20260929T050213Z/sources/__pycache__/bin_0778_theorem_generator.cpython-312.pyc
 M reports/reasoning_kernel_audit_20260929T050213Z/sources/__pycache__/bin_0779_theorem_generator_batch2.cpython-312.pyc
 M reports/reasoning_kernel_audit_20260929T050213Z/sources/__pycache__/bin_0780_theorem_generator_batch3.cpython-312.pyc
 M reports/reasoning_kernel_audit_20260929T050213Z/sources/__pycache__/bin_0781_theorem_generator_batch4.cpython-312.pyc
 M reports/reasoning_kernel_audit_20260929T050213Z/sources/__pycache__/bin_0782_theorem_generator_batch5.cpython-312.pyc
 M reports/reasoning_kernel_audit_20260929T050213Z/sources/__pycache__/bin_0783_theorems_extend.cpython-312.pyc
 M reports/reasoning_kernel_audit_20260929T050213Z/sources/__pycache__/bin_0798_agape_oracle.cpython-312.pyc
 M reports/reasoning_kernel_audit_20260929T050213Z/sources/__pycache__/bin_cache_pathway_orchestrator_v1.cpython-312.pyc
 M reports/reasoning_kernel_audit_20260929T050213Z/sources/__pycache__/bin_popw_ledger.cpython-312.pyc
Reh1t	https://github.com/Reh1t/openroot.git (fetch)
Reh1t	https://github.com/Reh1t/openroot.git (push)
origin	git@github.com:jesseray718/openroot.git (fetch)
origin	git@github.com:jesseray718/openroot.git (push)
upstream	https://github.com/jesseray718/openroot.git (fetch)
upstream	https://github.com/jesseray718/openroot.git (push)
0e12793 (HEAD -> main) inventory: clean flat history baseline for openroot
* main 0e12793 inventory: clean flat history baseline for openroot
fatal: no upstream configured for branch 'main'
warning: garbage found: .git/objects/pack/tmp_pack_RZHqO2
warning: garbage found: .git/objects/pack/tmp_pack_yA5Ost
warning: garbage found: .git/objects/90/tmp_obj_pI9NyT
count: 49787
size: 1.12 GiB
in-pack: 3690
packs: 2
size-pack: 162.20 MiB
prune-packable: 0
garbage: 3
size-garbage: 4.50 GiB
--- .gitignore ---
consolidation-backups/
venv/
node_modules/
*.db
data/operator_holds/
data/sdcard-sync/
lumo_inbox/
quarantine_tooling_repair_backups_*/
IGNORED     : knowledge_index.db
IGNORED     : openroot_vector.db
IGNORED     : node_modules
IGNORED     : data/fts_index.db
NOT IGNORED : reports
github.com
  ✓ Logged in to github.com account jesseray718 (/home/jesse/.config/gh/hosts.yml)
  - Active account: true
  - Git operations protocol: https
  - Token: ghp_************************************
  - Token scopes: 'admin:enterprise', 'admin:gpg_key', 'admin:org', 'admin:org_hook', 'admin:public_key', 'admin:repo_hook', 'admin:ssh_signing_key', 'audit_log', 'codespace', 'copilot', 'delete:packages', 'delete_repo', 'gist', 'notifications', 'project', 'repo', 'user', 'workflow', 'write:discussion', 'write:network_configurations', 'write:packages'
{"defaultBranchRef":{"name":"main"},"diskUsage":192727,"name":"openroot","pushedAt":"2026-10-08T21:21:35Z"}


===== 9. REPO SPRAWL MAP (git metadata; sizes in section 3) =====
openroot | branch=main | last=2026-10-08 18:17:26 -0500 | origin=git@github.com:jesseray718/openroot.git
openroot-edge | branch=master | last=2026-10-07 23:28:55 -0500 | origin=none
openroot-history-backup.git | branch=master | last=2026-09-17 06:19:56 -0500 | origin=/home/jesse/openroot
jesseray718 | branch=main | last=2026-09-09 22:42:58 -0500 | origin=https://github.com/jesseray718/jesseray718.git
jesseray718.github.io | branch=main | last=2026-09-10 00:23:56 -0500 | origin=https://github.com/jesseray718/jesseray718.github.io.git


===== 10. SENSITIVE FILE POSTURE (flagged only — contents never read) =====
-rw-------  278 bytes  /home/jesse/.api_keys
-rw-------  72 bytes  /home/jesse/.git-credentials
-rw-------  206 bytes  /home/jesse/github-recovery-codes.txt
-rw-rw-r--  76 bytes  /home/jesse/openroot/.env.local
-rwxr-xr-x  458228 bytes  /home/jesse/kai-settings.json
-rw-------  74164 bytes  /home/jesse/.bash_history
-rw-r--r--  757 bytes  /home/jesse/how-user jesse -p Linger
total 68
drwx------   2 jesse jesse  4096 Sep 21 22:28 .
drwxr-x--- 137 jesse jesse 20480 Oct  8 18:43 ..
-rw-------   1 jesse jesse   102 Oct  4 10:53 authorized_keys
-rw-------   1 jesse jesse   444 Sep 21 22:28 black-locust-rmh
-rw-r--r--   1 jesse jesse   120 Sep 21 22:28 black-locust-rmh.pub
-rw-------   1 jesse jesse   226 Oct  2 20:41 config
-rw-------   1 jesse jesse   411 Aug  1 15:49 id_ed25519
-rw-------   1 jesse jesse   411 Aug  2 06:53 id_ed25519_optiplex
-rw-r--r--   1 jesse jesse   100 Aug  2 06:53 id_ed25519_optiplex.pub
-rw-r--r--   1 jesse jesse    99 Aug  1 15:49 id_ed25519.pub
-rw-------   1 jesse jesse  2666 Oct  3 00:09 known_hosts
Rule: anything secret above with group/world read bits needs chmod 600.


===== 11. LIVE-STATE FILES (recent mtimes = active automation) =====
-rw-rw-r-- 1 jesse jesse       4 Sep 27 14:45 /home/jesse/openroot/bot_loop.pid
-rw-rw-r-- 1 jesse jesse     286 Oct  8 19:33 /home/jesse/openroot/data_bot_state.json
-rw-rw-r-- 1 jesse jesse 5936708 Oct  8 19:31 /home/jesse/.openroot_tap.tsv
20260925_050350	0	git push 
20260925_050401	0	cd openroot 
20260925_050411	1	gh stack checkout 61 
20260925_050434	1	gh stack rebase 
20260925_050442	1	gh stack push 


===== 12. DATABASE FILES ON DISK =====
total 4489088
drwx------  13 jesse jesse      12288 Oct  8 18:32 .
drwx------  33 jesse jesse      12288 Oct  8 18:15 ..
-rw-rw-r--   1 jesse jesse        238 Sep 26 16:51 a1_config.json.pre_bounded_roots.20260926T215133Z.bak
-rw-r--r--   1 jesse jesse      36864 Oct  2 18:55 agapenet_kb.db
-rw-r--r--   1 jesse jesse   16875520 Oct  2 19:51 agapenet_kb_v2.db
-rw-r--r--   1 jesse jesse      12288 Sep 13 19:12 api_keys.db
-rw-rw-r--   1 jesse jesse        122 Sep 21 04:02 bridge_state.json
-rw-r--r--   1 jesse jesse      28672 Sep 13 21:21 capability_exchange.db
-rw-r--r--   1 jesse jesse      40960 Sep 28 16:12 code_pathways.db
-rw-r--r--   1 jesse jesse      32768 Sep 26 15:53 compost_v1.db
-rw-rw-r--   1 jesse jesse     170257 Oct  4 22:15 cost_ledger.jsonl
-rw-r--r--   1 jesse jesse      20480 Sep 21 23:04 cycle_state.db
-rw-rw-r--   1 jesse jesse      14313 Oct  4 04:00 debate_ledger.jsonl
-rw-r--r--   1 jesse jesse   12656640 Sep 27 23:47 dedup_ledger.db
-rw-r--r--   1 jesse jesse     929792 Sep 21 04:00 doc_index.db
-rw-rw-r--   1 jesse jesse     148405 Oct  4 22:15 drift_alerts.jsonl
-rw-r--r--   1 jesse jesse    9936896 Oct  8 06:44 ecosystem_v2.db
-rw-r--r--   1 jesse jesse      77824 Sep 24 03:28 embed_cache.db
drwxrwxr-x   2 jesse jesse       4096 Oct  7 17:52 embeddings
-rw-r--r--   1 jesse jesse  137601024 Sep 27 22:49 embeddings.db
-rw-r--r--   1 jesse jesse      32768 Oct  3 00:12 embeddings.db-shm
-rw-r--r--   1 jesse jesse          0 Oct  3 00:12 embeddings.db-wal
-rw-------   1 jesse jesse        128 Sep 21 03:41 .env
-rw-r--r--   1 jesse jesse      28672 Sep 28 03:30 expertise_fp5s.db
-rw-rw-r--   1 jesse jesse       8092 Oct  8 06:44 failure_queue_20261008.md
-rw-r--r--   1 jesse jesse  410906624 Oct  8 04:02 file_ledger.db
-rw-r--r--   1 jesse jesse 2116853760 Oct  8 18:32 fts_index.db
-rw-r--r--   1 jesse jesse      20480 Sep 16 01:51 goals_ledger.db
-rw-r--r--   1 jesse jesse      16384 Sep 28 05:22 gov_smoke.db
-rw-r--r-- 1 jesse jesse    45056 Sep 24 00:01 /home/jesse/openroot/knowledge_base.db
-rw-r--r-- 1 jesse jesse 22319104 Oct  5 06:41 /home/jesse/openroot/knowledge_index.db
-rw-r--r-- 1 jesse jesse 91697152 Oct  4 23:13 /home/jesse/openroot/openroot_vector.db
-rw-r--r-- 1 jesse jesse   217088 Oct  8 05:09 /home/jesse/openroot/provenance.db
-rw-r--r-- 1 jesse jesse    12824 Oct  8 05:09 /home/jesse/openroot/provenance.db-journal
-rw-r--r-- 1 jesse jesse    16384 Oct  5 03:15 /home/jesse/openroot/sqlite.db
3.45.1 2024-01-30 16:01:20 e876e51a0ed5c5b3126f52e532044363a014bc594cfefa87ffb5b82257ccalt1 (64-bit)

===== 13. SQLITE / FTS5 CAPABILITY (this python) =====
sqlite 3.45.1 | FTS5 compiled in: True

===== 14. DATABASE INVENTORY UNDER ~/openroot (read-only) =====
found 155 db files; profiling top 25 by size

- openroot/data/fts_index.db  (2116.9 MB, mtime 2026-10-08 18:32)
  * objects (4): table:compost_ledger, table:knowledge_fts, table:sqlite_sequence, table:workspace_lattice
  * row counts: compost_ledger=0; knowledge_fts=111862; sqlite_sequence=0; workspace_lattice=37250

- openroot/data/qa_corpus.db  (1510.4 MB, mtime 2026-09-20 21:16)
  * objects (8): table:answers, table:chunks, table:chunks_fts, table:chunks_fts_config, table:chunks_fts_content, table:chunks_fts_data, table:chunks_fts_docsize, table:chunks_fts_idx
  * FTS virtual tables: chunks_fts
  * row counts: answers=0; chunks=511705; chunks_fts=511705

- openroot/data/file_ledger.db  (410.9 MB, mtime 2026-10-08 04:02)
  * objects (1): table:files
  * row counts: files=888262

- openroot/data/hash_manifest_optiplex.db  (371.1 MB, mtime 2026-09-30 12:53)
  * objects (2): table:hash_manifest, table:manifest
  * row counts: hash_manifest=0; manifest=512755

- openroot/data/embeddings.db  (137.6 MB, mtime 2026-09-27 22:49)
  * SIDECAR: embeddings.db-wal  -> possible hot journal / live writer
  * SIDECAR: embeddings.db-shm  -> possible hot journal / live writer
  * objects (5): table:chunks, table:documents, table:embeddings, table:index_metadata, table:sqlite_sequence
  * row counts: chunks=11110; documents=1; embeddings=1; index_metadata=4; sqlite_sequence=2

- openroot/database/canonical_index.db  (109.4 MB, mtime 2026-10-04 22:56)
  * objects (3): table:canonical_files, table:file_embeddings, table:sqlite_sequence
  * row counts: canonical_files=74281; file_embeddings=0; sqlite_sequence=1

- openroot/openroot_vector.db  (91.7 MB, mtime 2026-10-04 23:13)
  * objects (3): table:canonical_files, table:file_embeddings, table:sqlite_sequence
  * row counts: canonical_files=62166; file_embeddings=41; sqlite_sequence=2

- openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/universal_index_1789712158.db  (28.1 MB, mtime 2026-09-18 02:27)
  * objects (4): table:audit_log, table:content_classes, table:files, table:qa_templates
  * row counts: audit_log=72; content_classes=6; files=40194; qa_templates=4

- openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/snap/firefox/common/.mozilla/firefox/vnvnlq1y.default/suggest.sqlite  (23.8 MB, mtime 2026-08-14 15:55)
  * SIDECAR: suggest.sqlite-wal  -> possible hot journal / live writer
  * SIDECAR: suggest.sqlite-shm  -> possible hot journal / live writer
  * objects (28): table:amo_custom_details, table:amp_custom_details, table:amp_fts, table:amp_fts_config, table:amp_fts_data, table:amp_fts_docsize, table:amp_fts_idx, table:dismissed_dynamic_suggestions, table:dismissed_suggestions, table:dynamic_custom_details, table:full_keywords, table:geonames, table:geonames_alternates, table:geonames_metrics, table:icons, table:ingested_records, table:keywords, table:keywords_i18n ...
  * FTS virtual tables: amp_fts
  * row counts: amo_custom_details=6; amp_custom_details=4570; amp_fts=0; dismissed_dynamic_suggestions=0; dismissed_suggestions=0; dynamic_custom_details=39; full_keywords=4570; geonames=2924; geonames_alternates=ERR(OperationalError); geonames_metrics=0; icons=204; ingested_records=306; keywords=110992; keywords_i18n=ERR(OperationalError); keywords_metrics=56; mdn_custom_details=20; meta=2; prefix_keywords=45

- openroot/knowledge_index.db  (22.3 MB, mtime 2026-10-05 06:41)
  * objects (7): table:ledger, table:ledger_fts, table:ledger_fts_config, table:ledger_fts_content, table:ledger_fts_data, table:ledger_fts_docsize, table:ledger_fts_idx
  * FTS virtual tables: ledger_fts
  * row counts: ledger=2934; ledger_fts=2934

- openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/snap/firefox/common/.mozilla/firefox/vnvnlq1y.default/storage/permanent/chrome/idb/3870112724rsegmnoittet-es.sqlite  (19.8 MB, mtime 2026-08-14 19:48)
  * SIDECAR: 3870112724rsegmnoittet-es.sqlite-wal  -> possible hot journal / live writer
  * SIDECAR: 3870112724rsegmnoittet-es.sqlite-shm  -> possible hot journal / live writer
  * objects (7): table:database, table:file, table:index_data, table:object_data, table:object_store, table:object_store_index, table:unique_index_data
  * row counts: database=1; file=21; object_store=4; object_store_index=2

- openroot/data/agapenet_kb_v2.db  (16.9 MB, mtime 2026-10-02 19:51)
  * objects (10): table:jobs, table:ledger, table:sqlite_sequence, table:tidbits, table:tidbits_config, table:tidbits_content, table:tidbits_data, table:tidbits_docsize, table:tidbits_idx, table:vectors
  * FTS virtual tables: tidbits
  * row counts: jobs=2; ledger=0; sqlite_sequence=1; tidbits=1534; vectors=0

- openroot/data/dedup_ledger.db  (12.7 MB, mtime 2026-09-27 23:47)
  * objects (1): table:files
  * row counts: files=23047

- openroot/data/ecosystem_v2.db  (9.9 MB, mtime 2026-10-08 06:44)
  * objects (2): table:gates, table:repairs
  * row counts: gates=30998; repairs=0

- openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/snap/firefox/common/.mozilla/firefox/vnvnlq1y.default/domain_to_categories.sqlite  (8.7 MB, mtime 2026-08-14 20:35)
  * SIDECAR: domain_to_categories.sqlite-journal  -> possible hot journal / live writer
  * objects (2): table:domain_to_categories, table:moz_meta
  * row counts: domain_to_categories=72939; moz_meta=1

- openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/snap/firefox/common/.mozilla/firefox/vnvnlq1y.default/places.sqlite  (5.2 MB, mtime 2026-08-14 20:40)
  * SIDECAR: places.sqlite-wal  -> possible hot journal / live writer
  * SIDECAR: places.sqlite-shm  -> possible hot journal / live writer
  * objects (21): table:moz_anno_attributes, table:moz_annos, table:moz_bookmarks, table:moz_bookmarks_deleted, table:moz_historyvisits, table:moz_historyvisits_extra, table:moz_inputhistory, table:moz_items_annos, table:moz_keywords, table:moz_meta, table:moz_newtab_shortcuts_interaction, table:moz_newtab_story_click, table:moz_newtab_story_impression, table:moz_origins, table:moz_places, table:moz_places_extra, table:moz_places_metadata, table:moz_places_metadata_search_queries ...
  * row counts: moz_anno_attributes=2; moz_annos=2; moz_bookmarks=12; moz_bookmarks_deleted=0; moz_historyvisits=614; moz_historyvisits_extra=0; moz_inputhistory=3; moz_items_annos=0; moz_keywords=0; moz_meta=1; moz_newtab_shortcuts_interaction=259; moz_newtab_story_click=0; moz_newtab_story_impression=653; moz_origins=41; moz_places=423; moz_places_extra=0; moz_places_metadata=532; moz_places_metadata_search_queries=0

- openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/snap/firefox/common/.mozilla/firefox/vnvnlq1y.default/favicons.sqlite  (5.2 MB, mtime 2026-08-14 20:40)
  * SIDECAR: favicons.sqlite-wal  -> possible hot journal / live writer
  * SIDECAR: favicons.sqlite-shm  -> possible hot journal / live writer
  * objects (4): table:moz_icons, table:moz_icons_to_pages, table:moz_pages_w_icons, table:sqlite_stat1
  * row counts: moz_icons=49; moz_icons_to_pages=663; moz_pages_w_icons=341; sqlite_stat1=3

- openroot/consolidation-backups/untracked_collision_20260919-072429/data/termux-home-rescue/data/mesh_index.db  (2.8 MB, mtime 2026-09-13 12:28)
  * objects (1): table:files
  * row counts: files=7564

- openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/snap/firefox/common/.mozilla/firefox/vnvnlq1y.default/storage/default/https+++lumo.proton.me/idb/1066234074LDu3m%oADEBh_CdLC4I49.sqlite  (2.5 MB, mtime 2026-08-14 19:44)
  * SIDECAR: 1066234074LDu3m%oADEBh_CdLC4I49.sqlite-wal  -> possible hot journal / live writer
  * SIDECAR: 1066234074LDu3m%oADEBh_CdLC4I49.sqlite-shm  -> possible hot journal / live writer
  * objects (7): table:database, table:file, table:index_data, table:object_data, table:object_store, table:object_store_index, table:unique_index_data
  * row counts: database=1; file=0; object_store=7; object_store_index=5

- openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/agape_rag.db  (1.8 MB, mtime 2026-09-18 01:36)
  * objects (7): table:chunks, table:chunks_fts, table:chunks_fts_config, table:chunks_fts_content, table:chunks_fts_data, table:chunks_fts_docsize, table:chunks_fts_idx
  * FTS virtual tables: chunks_fts
  * row counts: chunks=267; chunks_fts=267

- openroot/data/newton_chain.db  (1.3 MB, mtime 2026-09-30 16:56)
  * objects (14): table:artifacts, table:audit_log, table:chain, table:edges, table:meta, table:node_fts, table:node_fts_config, table:node_fts_content, table:node_fts_data, table:node_fts_docsize, table:node_fts_idx, table:nodes, table:receipts, table:sqlite_sequence
  * FTS virtual tables: node_fts
  * row counts: artifacts=120; audit_log=369; chain=3; edges=233; meta=2; node_fts=135; nodes=135; receipts=1; sqlite_sequence=1

- openroot/context_bridge/lumo_inbox/ingested.sqlite  (1.0 MB, mtime 2026-09-30 02:09)
  * objects (6): table:msgs, table:msgs_fts, table:msgs_fts_config, table:msgs_fts_data, table:msgs_fts_docsize, table:msgs_fts_idx
  * FTS virtual tables: msgs_fts
  * row counts: msgs=579; msgs_fts=579

- openroot/consolidation-backups/untracked_collision_20260919-072429/logs/terminal_rag.sqlite  (0.9 MB, mtime 2026-09-12 05:31)
  * objects (1): table:chunks
  * row counts: chunks=50

- openroot/data/doc_index.db  (0.9 MB, mtime 2026-09-21 04:00)
  * objects (6): table:fts_docs, table:fts_docs_config, table:fts_docs_content, table:fts_docs_data, table:fts_docs_docsize, table:fts_docs_idx
  * FTS virtual tables: fts_docs
  * row counts: fts_docs=64

- openroot/data/sdcard-sync/kit/chunk_index.sqlite  (0.9 MB, mtime 2026-09-12 20:57)
  * objects (3): table:chunks, table:files, table:sqlite_sequence
  * row counts: chunks=1522; files=1342; sqlite_sequence=2

===== 15. NEWTON CHAIN LEDGER =====

- archives/openroot (1)/agape_kb/newton_chain.jsonl  (0.0 MB, mtime 2026-08-05 13:54)
  * lines=1  valid_json=1  malformed=0
  * key union (8): axiom, derived_from, eta_value, id, layer, statement, timestamp, verified
  * timestamps: first-seen=2026-08-05T18:54:56.398903+00:00  last-seen=2026-08-05T18:54:56.398903+00:00
  * NOTE: no explicit unit/energy keys in key union — schema may lack units.
  * first entry (trunc): {"id": "G00_be5fe075", "axiom": "LAYER1_GATE", "statement": "IF (DERIVATION) AND (R=1.0) THEN execute derivation at layer 1, targeting lowest η node", "layer": 1, "eta_value": 1.0, "verified": true, "derived_from": ["A1", "A2"], "timestamp"

- openroot/data/newton_chain.jsonl  (0.0 MB, mtime 2026-10-05 06:41)
  * lines=3  valid_json=3  malformed=0
  * key union (5): current_hash, index, payload, previous_hash, timestamp
  * timestamps: first-seen=2026-10-05T11:11:31.834243+00:00  last-seen=2026-10-05T11:41:27.903766+00:00
  * NOTE: no explicit unit/energy keys in key union — schema may lack units.
  * first entry (trunc): {"index": 0, "timestamp": "2026-10-05T11:11:31.834243+00:00", "payload": {"event": "GENESIS", "description": "Newton Chain Thermodynamic Ledger Initialized"}, "previous_hash": "000000000000000000000000000000000000000000000000000000000000000
  * last entry (trunc): {"index": 2, "timestamp": "2026-10-05T11:41:27.903766+00:00", "payload": {"work_type": "AERO_DISC_RUN", "joules_recorded": 1420.5, "node_id": "optiplex3060", "status": "VERIFIED"}, "previous_hash": "31bbc00f9c0ba1ccbdb7bae8322e3e84da99605d6

- snap/openroot (1)/agape_kb/newton_chain.jsonl  (0.0 MB, mtime 2026-08-05 13:54)
  * lines=1  valid_json=1  malformed=0
  * key union (8): axiom, derived_from, eta_value, id, layer, statement, timestamp, verified
  * timestamps: first-seen=2026-08-05T18:54:56.398903+00:00  last-seen=2026-08-05T18:54:56.398903+00:00
  * NOTE: no explicit unit/energy keys in key union — schema may lack units.
  * first entry (trunc): {"id": "G00_be5fe075", "axiom": "LAYER1_GATE", "statement": "IF (DERIVATION) AND (R=1.0) THEN execute derivation at layer 1, targeting lowest η node", "layer": 1, "eta_value": 1.0, "verified": true, "derived_from": ["A1", "A2"], "timestamp"

===== 16. ACRE-0001 / PoPW RECORD =====
- /home/jesse/archives/openroot (1)/acre/claims/ACRE-0001-seed-core-aero-disc.json (1088 bytes, mtime 2026-08-01 16:23)
  head: {   "claim_id": "ACRE-0001",   "type": "PoPW_contextual_absorption",   "timestamp": "2026-08-01T16:19:00-05:00",   "actor": "jesse@openroot.earth",   "work_description": "Absorption of Aero-Disc volumetric exchanger primitive + complete Seed Core (16 foundational optimization seeds) into durable inter-session lattice",   "physical_component": "Aero-Disc Path A cardboard disc design + porous_exchan
- /home/jesse/archives/openroot (1)/absorbed/github_clone_temp_openroot_library_kai-sandbox_skills_openroot_tokens_ACRE_SPECIFICATION.md (17772 bytes, mtime 2026-07-25 09:16)
  head: # ACRE Token Specification ## Real-Value Currency Minted for Verified Innovation  **Status:** Pre-launch specification (token awaits 3 validated nodes + legal opinion)   **Launch Target:** After Node Zero + 2 independent replications validated   **Blockchain Integration:** Solana (IPFS memo field linking to OpenRoot commons)   **Core Mechanic:** ACRE minted only when software/hardware improves, de
- /home/jesse/archives/openroot (1)/absorbed/github_clone_temp_openroot_library_kai-sandbox_github-repos_openroot_tokens_ACRE_SPECIFICATION.md (17772 bytes, mtime 2026-07-25 09:15)
  head: # ACRE Token Specification ## Real-Value Currency Minted for Verified Innovation  **Status:** Pre-launch specification (token awaits 3 validated nodes + legal opinion)   **Launch Target:** After Node Zero + 2 independent replications validated   **Blockchain Integration:** Solana (IPFS memo field linking to OpenRoot commons)   **Core Mechanic:** ACRE minted only when software/hardware improves, de
- /home/jesse/archives/openroot (1)/absorbed/github_clone_temp_openroot_library_kai-sandbox_openroot_tokens_ACRE_SPECIFICATION.md (17772 bytes, mtime 2026-07-25 09:16)
  head: # ACRE Token Specification ## Real-Value Currency Minted for Verified Innovation  **Status:** Pre-launch specification (token awaits 3 validated nodes + legal opinion)   **Launch Target:** After Node Zero + 2 independent replications validated   **Blockchain Integration:** Solana (IPFS memo field linking to OpenRoot commons)   **Core Mechanic:** ACRE minted only when software/hardware improves, de
- /home/jesse/archives/openroot (1)/absorbed/github_clone_temp_openroot_library_kai-sandbox_openroot-ecosystem_openroot_tokens_ACRE_SPECIFICATION.md (17772 bytes, mtime 2026-07-25 09:15)
  head: # ACRE Token Specification ## Real-Value Currency Minted for Verified Innovation  **Status:** Pre-launch specification (token awaits 3 validated nodes + legal opinion)   **Launch Target:** After Node Zero + 2 independent replications validated   **Blockchain Integration:** Solana (IPFS memo field linking to OpenRoot commons)   **Core Mechanic:** ACRE minted only when software/hardware improves, de
- /home/jesse/archives/openroot (1)/absorbed/github_clone_temp_openroot_tokens_ACRE_SPECIFICATION.md (17772 bytes, mtime 2026-07-25 09:16)
  head: # ACRE Token Specification ## Real-Value Currency Minted for Verified Innovation  **Status:** Pre-launch specification (token awaits 3 validated nodes + legal opinion)   **Launch Target:** After Node Zero + 2 independent replications validated   **Blockchain Integration:** Solana (IPFS memo field linking to OpenRoot commons)   **Core Mechanic:** ACRE minted only when software/hardware improves, de
- /home/jesse/archives/openroot (1)/tokens/ACRE_SPECIFICATION.md (17772 bytes, mtime 2026-07-17 05:39)
  head: # ACRE Token Specification ## Real-Value Currency Minted for Verified Innovation  **Status:** Pre-launch specification (token awaits 3 validated nodes + legal opinion)   **Launch Target:** After Node Zero + 2 independent replications validated   **Blockchain Integration:** Solana (IPFS memo field linking to OpenRoot commons)   **Core Mechanic:** ACRE minted only when software/hardware improves, de
- /home/jesse/archives/openroot-lattice/openroot/tokens/ACRE_SPECIFICATION.md (17772 bytes, mtime 2026-08-14 00:21)
  head: # ACRE Token Specification ## Real-Value Currency Minted for Verified Innovation  **Status:** Pre-launch specification (token awaits 3 validated nodes + legal opinion)   **Launch Target:** After Node Zero + 2 independent replications validated   **Blockchain Integration:** Solana (IPFS memo field linking to OpenRoot commons)   **Core Mechanic:** ACRE minted only when software/hardware improves, de

===== 17. LARGE FILES & DUPLICATE CANDIDATES (>= 20 MB) =====
Skipped reinstallable caches (.cache/.ollama/.npm/snap/.local/node_modules/venv/.git).
Top 40 largest files:
  140737471.6 MB  ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/core
   14537.1 MB  ~/archives/termux-full-backup-20260809-2143.tar.gz
   12978.4 MB  ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/archive.zip
    5477.2 MB  ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/home_full_20260819_221848.tar.xz
    5477.2 MB  ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/3bb82b451306285c/home_full_20260819_221848.tar.xz
    5476.5 MB  ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/pack-56a7ee30d407cebe9a7faf3b2256968ea276a91a.pack
    5476.5 MB  ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/3bb82b451306285c/pack-56a7ee30d407cebe9a7faf3b2256968ea276a91a.pack
    5200.6 MB  ~/wisdom-scaffold/data/optiplex_public.db
    5200.6 MB  ~/wisdom-recovery/20260904-024705/wisdom-scaffold/data/optiplex_public.db
    4920.7 MB  ~/optiplex-archive/New-folder/Alarms/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
    4920.7 MB  ~/optiplex-archive/New-folder/Alarms/Download/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
    4295.0 MB  ~/archives/critical.tar.gz
    3996.7 MB  ~/optiplex-archive/New-folder/agape_recovery/critical_files/termux_backup_20260702_221906.tar.gz
    3996.7 MB  ~/optiplex-archive/New-folder/Alarms/termux_backup_20260702_221906.tar.gz
    3996.7 MB  ~/archives/termux_backup_20260702_221906.tar.gz
    3619.5 MB  ~/optiplex-archive/New-folder/Alarms/home_backup_20260724.tar.gz
    3619.5 MB  ~/archives/home_backup_20260724.tar.gz
    3186.2 MB  ~/optiplex-archive/New-folder/agape_recovery/critical_files/alchemy_archive_20260724_024327.tar.gz
    3186.2 MB  ~/optiplex-archive/New-folder/Alarms/openroot_usb_stage/openroot/alchemy_archive/alchemy_archive_20260724_024327.tar.gz
    3186.2 MB  ~/optiplex-archive/New-folder/Alarms/openroot (2)/alchemy_archive/alchemy_archive_20260724_024327.tar.gz
    2796.8 MB  ~/archives/home_backup_20260724.tar (1).gz
    2393.2 MB  ~/optiplex-archive/New-folder/Kai_Termux_Shared/phi-3-mini-q4.gguf
    2116.9 MB  ~/openroot/data/fts_index.db
    1890.3 MB  ~/archives/OpenRootArchives/20260810/openroot-pre-consolidation-backup-2148.tar.xz
    1758.9 MB  ~/kai_recovery/openroot/lumo_inbox/incoming/kai_extract_20260928_015017.tar.gz
    1758.9 MB  ~/harvest_hold/kai_import_20260928_015017.tar.gz
    1697.9 MB  ~/openroot/lumo_inbox/expanded/kai_extract_20260928_015017.bca6fe9a/kai_extract_20260928_015017/stage/Download/warm-20260906/termux-home-20260906.tar.zst
    1697.9 MB  ~/kai_recovery/extracted/kai_extract_20260928_015017/stage/Download/warm-20260906/termux-home-20260906.tar.zst
    1697.9 MB  ~/harvest_hold/kai_deep_harvest_20260928_024955/nested/kai_extract_20260928_015017/stage/Download/warm-20260906/termux-home-20260906.tar.zst
    1510.4 MB  ~/openroot/data/qa_corpus.db
    1317.8 MB  ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/home_full_20260821_160013.tar.xz
    1317.8 MB  ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/3bb82b451306285c/home_full_20260821_160013.tar.xz
    1312.5 MB  ~/harvest_hold/a15_backup/termux_20260928_191232/data/data/com.termux/files/home/wisdom-scaffold/all_notes_repos.db
    1312.5 MB  ~/harvest_hold/a15_backup/termux_20260928_190708/data/data/com.termux/files/home/wisdom-scaffold/all_notes_repos.db
    1223.0 MB  ~/archives/OpenRootArchives/20260810/backups-2203.tar.xz
    1209.8 MB  ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/storage/emulated/0/Documents/old-downloads.tar.gz
    1209.8 MB  ~/archives/old-downloads.tar.gz
    1209.2 MB  ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/bc7527e5dc6cf30d/data/data/com.termux/files/home/downloads/termux_backup_20260702_221906.tar.gz
    1127.6 MB  ~/optiplex-archive/New-folder/Alarms/phone_backup/termux/termux_backup.tar.gz
    1118.9 MB  ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/auto_20260721_200420.log

Same-size duplicate groups (verify before deleting anything):
    5477.2 MB x2:
      ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/home_full_20260819_221848.tar.xz
      ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/3bb82b451306285c/home_full_20260819_221848.tar.xz
    5476.5 MB x2:
      ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/pack-56a7ee30d407cebe9a7faf3b2256968ea276a91a.pack
      ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/3bb82b451306285c/pack-56a7ee30d407cebe9a7faf3b2256968ea276a91a.pack
    5200.6 MB x2:
      ~/wisdom-scaffold/data/optiplex_public.db
      ~/wisdom-recovery/20260904-024705/wisdom-scaffold/data/optiplex_public.db
    4920.7 MB x2:
      ~/optiplex-archive/New-folder/Alarms/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
      ~/optiplex-archive/New-folder/Alarms/Download/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
    3996.7 MB x3:
      ~/optiplex-archive/New-folder/agape_recovery/critical_files/termux_backup_20260702_221906.tar.gz
      ~/optiplex-archive/New-folder/Alarms/termux_backup_20260702_221906.tar.gz
      ~/archives/termux_backup_20260702_221906.tar.gz
    3619.5 MB x2:
      ~/optiplex-archive/New-folder/Alarms/home_backup_20260724.tar.gz
      ~/archives/home_backup_20260724.tar.gz
    3186.2 MB x3:
      ~/optiplex-archive/New-folder/agape_recovery/critical_files/alchemy_archive_20260724_024327.tar.gz
      ~/optiplex-archive/New-folder/Alarms/openroot_usb_stage/openroot/alchemy_archive/alchemy_archive_20260724_024327.tar.gz
      ~/optiplex-archive/New-folder/Alarms/openroot (2)/alchemy_archive/alchemy_archive_20260724_024327.tar.gz
    1758.9 MB x2:
      ~/kai_recovery/openroot/lumo_inbox/incoming/kai_extract_20260928_015017.tar.gz
      ~/harvest_hold/kai_import_20260928_015017.tar.gz
    1697.9 MB x3:
      ~/openroot/lumo_inbox/expanded/kai_extract_20260928_015017.bca6fe9a/kai_extract_20260928_015017/stage/Download/warm-20260906/termux-home-20260906.tar.zst
      ~/kai_recovery/extracted/kai_extract_20260928_015017/stage/Download/warm-20260906/termux-home-20260906.tar.zst
      ~/harvest_hold/kai_deep_harvest_20260928_024955/nested/kai_extract_20260928_015017/stage/Download/warm-20260906/termux-home-20260906.tar.zst
    1317.8 MB x2:
      ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/home_full_20260821_160013.tar.xz
      ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/3bb82b451306285c/home_full_20260821_160013.tar.xz
    1312.5 MB x2:
      ~/harvest_hold/a15_backup/termux_20260928_191232/data/data/com.termux/files/home/wisdom-scaffold/all_notes_repos.db
      ~/harvest_hold/a15_backup/termux_20260928_190708/data/data/com.termux/files/home/wisdom-scaffold/all_notes_repos.db
    1209.8 MB x2:
      ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/storage/emulated/0/Documents/old-downloads.tar.gz
      ~/archives/old-downloads.tar.gz
    1118.9 MB x3:
      ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/usb128-import-20260913/auto_20260721_200420.log
      ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/storage/emulated/0/Documents/terminal-logs/auto_20260721_200420.log
      ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/3bb82b451306285c/auto_20260721_200420.log
    1117.3 MB x2:
      ~/optiplex-archive/New-folder/Alarms/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf
      ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/5ed3729d0c9f1d85/models/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf
    1117.3 MB x4:
      ~/optiplex-archive/New-folder/Kai_Termux_Shared/models/qwen2.5-1.5b-instruct-q4_k_m.gguf
      ~/optiplex-archive/New-folder/Alarms/qwen2.5-1.5b-instruct-q4_k_m.gguf
      ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/5ed3729d0c9f1d85/models/qwen2.5-1.5b-instruct-q4_k_m.gguf
      ~/openroot/consolidation-backups/untracked_collision_20260919-072429/data/universal_index/unpacked/5ed3729d0c9f1d85/models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf

===== 18. SHELL-ESCAPE ARTIFACT FILENAMES (junk from unquoted heredocs) =====
Found 39 candidates (first 60). Some may be legit files; nothing is deleted:
  ' \\){DATA}'
  ' \\){ROOT}'
  ' \\){WISDOM}'
  'Android (1)'
  'Perplexity-AI-4.0.0-Linux(1).AppImage'
  'THEORETICAL_CLAIMS (1).jsonl'
  '[2600:6c40:2a3f:c289:dbf3:38bb:38ce:2787]:22000:'
  '[fd00:e4c0:e268:80ea:1cf3:192d:e6ab:e86c]:22000:'
  '[fd00:e4c0:e268:80ea:2cad:5610:355b:8c1a]:22000:'
  '[fd00:e4c0:e268:80ea:34d4:feff:fe16:a624]:22000:'
  '\\( HOME'
  '\\( {RAG}'
  '\\( {ROOT}'
  '\\( {WISDOM}'
  'archives/Download (1)'
  'archives/USB storage 1 (1).zip'
  'archives/USB storage 1 (2).zip'
  'archives/USB storage 1 (3).zip'
  'archives/USB storage 1 (4).zip'
  'archives/USB storage 1 (5).zip'
  'archives/USB storage 1 (6).zip'
  'archives/home_backup_20260724.tar (1).gz'
  'archives/kai9000-export-20260801_183632.tar (1).zip'
  'archives/kai9000-export-20260801_183632.tar (2).zip'
  'archives/kai9000-export-20260801_183632.tar (3).zip'
  'archives/kai9000-export-20260801_183632.tar (4).zip'
  'archives/kai9000-export-20260801_183632.tar (5).zip'
  'archives/openroot (1)'
  'archives/pack-b860d9de5ec23a303c96036761cffebcbd5c8292 (1).zip'
  'crowdfund-campaign (1)'
  'kai-settings (1).json'
  'snap/Download (1)'
  'snap/crowdfund-campaign (1)'
  'snap/openroot (1)'
  'une-push/{'
  'une-push/}'
  'une/{'
  'une/}'
  '{'

===== 19. BACKUP-FILE CHURN =====
20 backup files in ~/openroot/bin (iterative-repair history):
  a1_core_v1.py.pre_ledger_scan_repair.20260926T214957Z.bak
  a1_core_v1.py.pre_ledger_scan_repair.20260926T214851Z.bak
  handoff_manager.py.pre_session_id_collision_fix.20260926T220915Z.bak
  handoff_manager.py.pre_start_idempotency_fix.20260926T220804Z.bak
  bot_loop_v1.py.backup_20260923
  launch_ladder_v1.py.pre_mistake_runner_fix.20260926T210256Z.bak
  handoff_manager.py.pre_session_id_format_fix.20260926T221628Z.bak
  handoff_manager.py.pre_session_id_format_fix.20260926T221515Z.bak
  a1_core_v1.py.pre_bounded_roots.20260926T215133Z.bak
  handoff_manager.py.pre_session_id_collision_fix.20260926T220956Z.bak
  launch_ladder_v1.py.pre_registration_fix_v2.20260926T201522Z.bak
  handoff_manager.py.pre_single_session_repair.20260926T220226Z.bak
  handoff_manager.py.pre_end_session_tuple_fix.20260926T220321Z.bak
  launch_ladder_v1.py.pre_mistake_runner_fix_v2.20260926T210713Z.bak
  handoff_manager.py.pre_secrets_import.20260926T221131Z.bak
Recommendation: move .bak history into git history instead of sibling files.

===== 20. ACTIVE BOT STATE SNAPSHOT =====
- data_bot_state.json (mtime 2026-10-08 19:38):
  {
  "snapshots": {
    "/sdcard/openroot/thermo_ledger/eta_moves.jsonl": "missing",
    "/sdcard/openroot/parallel_analysis/ledger/ideas.jsonl": "missing",
    "/sdcard/openroot/ledger/experiments/linux_command_persistence.jsonl": "missing"
  },
  "cycles": 3223,
  "last_ts": 1791506286.2410588
}

- ~/.openroot_tap.tsv (mtime 2026-10-08 19:31), first 5 lines:
  20260925_050350	0	git push
  20260925_050401	0	cd openroot
  20260925_050411	1	gh stack checkout 61
  20260925_050434	1	gh stack rebase
  20260925_050442	1	gh stack push
