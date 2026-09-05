# Offline-first 7B coder — user manual (Jesse hardware)

Hierarchy is locked. Do not invert it.

1. A15 Termux = governor, client, file bus. 3.5 GB usable. No 7B weights.
2. OptiPlex 3060 = heavy spoke. llama-server + Q4 GGUF in /home/jesse/models
3. Cloud = burst only after local 7B fails the task.

Phone IP 192.168.1.233. Box IP 192.168.1.193. SSH user jesse. Key on phone:
/data/data/com.termux/files/home/.ssh/id_ed25519_optiplex

## What "offline-first" means here

- Weights never leave /home/jesse/models
- API is LAN only: 127.0.0.1:8080 on the box, 192.168.1.193:8080 from the phone
- No OpenRouter key required for daily code edits
- If Spectrum drops, SSH over USB/ethernet still works if the NIC is up
- GitHub is optional publish, not the inference path

## SSH pane — start the server

Pick one GGUF. Example name only if that file exists after you list the dir.

```
ls -lh /home/jesse/models
```

If the dir is empty, download ON THE BOX, not the phone. Prefer Q4_K_M 7B-class coder:

- Qwen2.5-Coder-7B-Instruct Q4_K_M
- or DeepSeek-Coder-6.7B-Instruct Q4_K_M

Need llama-server from llama.cpp. If missing:

```
sudo apt update
sudo apt install -y build-essential cmake git
```

Then build llama.cpp on the box into /home/jesse/src/llama.cpp and install the binary you actually have. Do not copy a Termux build onto Ubuntu.

Start (adjust filename after ls):

```
/home/jesse/src/llama.cpp/llama-server \
  -m /home/jesse/models/REPLACE_AFTER_LS.gguf \
  --host 0.0.0.0 \
  --port 8080 \
  -c 4096 \
  -ngl 0
```

OptiPlex 3060 is CPU-first. -ngl 0 is honest. If you later have a GPU, raise ngl. Do not pretend you have one.

Health:

```
curl -s http://127.0.0.1:8080/v1/models
```

## A15 pane — talk to it

```
python3 /data/data/com.termux/files/home/code/openroot/kit/bin/coder_client.py status
python3 /data/data/com.termux/files/home/code/openroot/kit/bin/coder_client.py ask write a pathlib probe that prints cwd
```

If status says connection refused: server is down, or box firewall, or IP changed. Check on SSH:

```
ip -br addr
ss -lptn | grep 8080
```

If IP is no longer 192.168.1.193, stop and update the two URLs in coder_client.py. Do not invent 192.168.1.x.

## SSH tunnel alternative (when LAN HTTP is blocked)

From A15:

```
ssh -i /data/data/com.termux/files/home/.ssh/id_ed25519_optiplex \
  -o BatchMode=yes \
  -L 8080:127.0.0.1:8080 \
  jesse@192.168.1.193
```

Then on the phone use 127.0.0.1:8080 only inside that session. Still no GGUF on the phone.

## What to send the 7B

Good: one file, one function, absolute paths, "do not use tilde", "Termux python 3.14 stdlib".
Bad: whole openroot tree, thesis restatement, "become AGI", ACRE mint while canon is false.

## One-hot RAM on A15

Never: llama-server + embedder + Markor OCR + gh clone at once.
Allowed: gh, python3 kit scripts, SSH, Fork idle.

## Failure table

| Symptom | Cause | Move |
|---|---|---|
| OOM on phone | you loaded a model | kill it; model stays on box |
| curl localhost on A15 | wrong host | 192.168.1.193 |
| empty models dir | never downloaded | download on box only |
| 8080 closed | server not started | SSH start command |
| garbage code with tildes | weak system prompt | keep the system line in coder_client.py |
| thermal fan scream | context 32k on CPU | stay at -c 4096 |

## After it works

Log jobs are in sqlite coder_job. That is the hang trail. Do not also invent a second logger.
