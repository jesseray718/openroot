# Termux → Tailscale → OptiPlex → Ollama

## Known connection

Phone: Android running native Termux.
Remote account: jesse
OptiPlex Tailscale address observed: 100.122.169.43
Remote Ollama endpoint: 127.0.0.1:11434
Phone forwarded endpoint: 127.0.0.1:11434

Tailscale must be connected on both devices and the OptiPlex must be awake.
The observed address can change; verify it in Tailscale if connectivity fails.

## Start the tunnel in native Termux

```bash
ssh -NT \
  -o ConnectTimeout=10 \
  -o ExitOnForwardFailure=yes \
  -o ServerAliveInterval=30 \
  -o ServerAliveCountMax=3 \
  -L 127.0.0.1:11434:127.0.0.1:11434 \
  jesse@100.122.169.43
```

A quiet foreground SSH session is expected.
Leave it running. Ctrl+C stops that tunnel.

## Quick test in a SECOND Termux session

```bash
curl --connect-timeout 5 --max-time 10 http://127.0.0.1:11434/api/tags
```

A successful response contains a JSON `models` array.
This checks model-list access, not successful inference.
Local access alone does not prove which process serves the port.

## Save a Termux:Widget launcher

Run this on the PHONE, not inside the OptiPlex SSH shell.

```bash
mkdir -p "$HOME/.shortcuts"
chmod 700 "$HOME/.shortcuts"

cat > "$HOME/.shortcuts/OpenRoot-Tunnel" <<'SCRIPT'
#!/data/data/com.termux/files/usr/bin/bash

if curl --fail --silent \
  --connect-timeout 2 --max-time 4 \
  http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    echo "The local model API already responds."
    read -r -p "Press Enter to close."
    exit 0
fi

echo "Starting OptiPlex tunnel. Keep Tailscale connected."
echo "Leave this session running. Ctrl+C stops the tunnel."

ssh -NT \
  -o ConnectTimeout=10 \
  -o ExitOnForwardFailure=yes \
  -o ServerAliveInterval=30 \
  -o ServerAliveCountMax=3 \
  -L 127.0.0.1:11434:127.0.0.1:11434 \
  jesse@100.122.169.43

status=$?
echo "Tunnel stopped. SSH exit status: $status"
read -r -p "Press Enter to close."
exit "$status"
SCRIPT

chmod 700 "$HOME/.shortcuts/OpenRoot-Tunnel"
bash -n "$HOME/.shortcuts/OpenRoot-Tunnel"
```

Install the compatible Termux:Widget companion app, add its Android
home-screen widget, refresh its list, and select OpenRoot-Tunnel.

Direct launch:
```bash
"$HOME/.shortcuts/OpenRoot-Tunnel"
```

## Diagnose in order

1. Phone Tailscale connected?
2. OptiPlex online and address correct?
3. SSH reachable?
4. Ollama reachable on the PC?
5. Local forwarding reachable?
6. Only then test inference.

SSH test:
```bash
ssh -o ConnectTimeout=10 jesse@100.122.169.43 'echo CONNECTION_OK'
```

PC-side Ollama test:
```bash
ssh -o ConnectTimeout=10 jesse@100.122.169.43 \
  'curl --connect-timeout 5 --max-time 10 http://127.0.0.1:11434/api/tags'
```

An SSH connection timeout is not fixed by changing curl API paths.
Do not expose Ollama publicly or change its bind address to repair
a failed Tailscale/SSH connection.

## Observed 2026-10-24 model-list response

The user reported successful local /api/tags access after earlier timeouts.

Models included:
- nomic-embed-text:latest
- qwen2.5-coder:1.5b
- qwen2.5-coder:3b
- qwen2.5-coder:7b
- qwen2.5:1.5b
- qwen2.5:3b
- qwen2.5:7b-instruct
- qwen3:0.6b
- qwen3:1.7b
- phi4-router:latest
- phi4-mini:latest
- openroot-coder:latest
- openroot-instruct:7b
- openroot-assistant:latest
- smollm2:1.7b
- gemma3:1b
- granite3.3:2b
- llama3.2:1b
- llama3.2:3b
- deepseek-r1:1.5b

phi4-router is an installed generative model. Its name does not establish
that it is the original trained non-generative router.

## Copy/paste rule

Copy only fenced command contents.
Do not paste shell prompts, `>` continuation prompts, welcome banners,
Markdown link notation, or previous output as commands.
