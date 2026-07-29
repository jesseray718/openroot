import datetime, json, os
log_file = f"/storage/emulated/0/Documents/openroot-data/{datetime.date.today()}.jsonl"
def log(t_in, t_out, hum):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, "a") as f: f.write(json.dumps({"ts": datetime.datetime.now().isoformat(), "ΔT": t_in-t_out, "hum": hum})+"\n")
