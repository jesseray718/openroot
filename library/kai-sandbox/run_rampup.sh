#!/data/data/com.termux/files/usr/bin/bash
set -uo pipefail
LOG="$HOME/.lumo_rampup_$(date +%Y%m%d_%H%M%S).log"
techo(){ echo "$1" | tee -a "$LOG"; }
techo "[+] Ramp-up starting -> $LOG"
LLDIR=""
for d in "$HOME/llama.cpp-fix" "$HOME/skills/llama.cpp" "$HOME/llama.cpp"; do
  [ -d "$d" ] && LLDIR="$d" && break
done
if [ -z "$LLDIR" ]; then
  techo "[FAIL] no llama.cpp dir found (checked ~/llama.cpp-fix, ~/skills/llama.cpp, ~/llama.cpp)"
  exit 1
fi
techo "[+] using llama.cpp at $LLDIR"
cd "$LLDIR" || exit 1
if [ ! -f build/CMakeCache.txt ]; then
  techo "[+] generating build (default CPU backend)"
  cmake -B build -DCMAKE_BUILD_TYPE=Release 2>&1 | tail -5 | tee -a "$LOG"
fi
techo "[+] compiling llama-server target only"
cmake --build build --config Release -j"$(nproc)" --target llama-server 2>&1 | tail -25 | tee -a "$LOG"
BIN="$LLDIR/build/bin/llama-server"
if [ -x "$BIN" ]; then
  mkdir -p "$HOME/bin"
  cp "$BIN" "$HOME/bin/llama-server"
  techo "[OK] llama-server -> $HOME/bin/llama-server"
else
  techo "[FAIL] binary missing, check compile errors above"
fi
techo "[+] cleanup: cargo src cache"
rm -rf "$HOME/.cargo/registry/src"
techo "[+] cleanup: python __pycache__"
find "$HOME" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
techo "[+] cleanup: unused Ollama"
rm -rf "$HOME/.ollama"
techo "[+] listing real models in ~/models"
ls -lh "$HOME"/models/*.gguf 2>/dev/null | tee -a "$LOG"
techo "[+] detecting qwen duplicates..."
A="$HOME/models/qwen2.5-1.5b-instruct-q4_k_m.gguf"
B="$HOME/models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"
if [ -f "$A" ] && [ -f "$B" ]; then
  HA=$(md5sum "$A" | awk '{print $1}')
  HB=$(md5sum "$B" | awk '{print $1}')
  if [ "$HA" = "$HB" ]; then
    techo "[DUP] identical (${HB}). Reclaim with: rm -f '$B'"
  else
    techo "[DIFF] hashes differ - keep both"
  fi
else
  techo "[+] no duplicate pair found; verify filenames above"
fi
echo "=== RAMP-UP DONE ===" | tee -a "$LOG"
echo "Log: $LOG" | tee -a "$LOG"
du -sh "$HOME" 2>/dev/null | tee -a "$LOG"
