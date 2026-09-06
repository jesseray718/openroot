# Handbook — Leveling Cooperative

## 1. Get a working terminal (Termux)

1. Install Termux from F-Droid (not Play Store).
2. Open Termux and run:

pkg update -y && pkg install git python -y

3. Clone OpenRoot if needed:

cd /data/data/com.termux/files/home
git clone https://github.com/jesseray718/openroot.git

## 2. Enter the cooperative

cd /data/data/com.termux/files/home/openroot/leveling-cooperative
bash handbook/GET-TERMINAL-AND-RUN.sh

## 3. Commands

bash zero-dep-app/pool.sh status
bash zero-dep-app/pool.sh invest 25.00 "weekly seed"
bash zero-dep-app/pool.sh ledger
bash zero-dep-app/pool.sh dividend
bash zero-dep-app/pool.sh handup

## 4. Rules

- Capital only. Never put SSN or full credit file in.
- Fixed automatic hand-up percentage of every surplus.
- No owners. No corporate cut.
- Everything is local and auditable.
