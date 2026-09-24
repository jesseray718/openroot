#!/data/data/com.termux/files/usr/bin/env python3
"""
dag_orchestrator.py — OpenRoot fractal DAG mold
Zero-dep topological runner. Nodes are bottom_tier leaves.
Self-similar: a DAG can contain sub-DAGs (recursive).
Integrates H-003 thermal cascade thinking, UNE naming, ACRE accounting.
"""
import json, os, time
from pathlib import Path
from collections import defaultdict, deque

GOV = Path(os.environ.get("GOVERNOR_HOME", str(Path.home() / ".governor")))
DAGS, QUEUE, DONE, OUT = GOV / "dags", GOV / "queue", GOV / "done", GOV / "output"

def topo_sort(nodes: dict, edges: list) -> list:
    """Kahn's algorithm. nodes = {id: task_dict}, edges = [(src, dst), ...]"""
    graph = defaultdict(list)
    indeg = {n: 0 for n in nodes}
    for src, dst in edges:
        graph[src].append(dst)
        indeg[dst] = indeg.get(dst, 0) + 1
    q = deque([n for n in nodes if indeg[n] == 0])
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in graph[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    if len(order) != len(nodes):
        raise ValueError("cycle detected in DAG")
    return order

def run_dag(dag_path: Path):
    dag = json.loads(dag_path.read_text())
    nodes = {n["id"]: n for n in dag["nodes"]}
    edges = dag.get("edges", [])
    order = topo_sort(nodes, edges)
    print(json.dumps({"dag": dag_path.stem, "order": order, "node": "N0_dag_orchestrator"}), flush=True)

    results = {}
    for nid in order:
        task = nodes[nid]
        # inject upstream outputs as context (fractal memory)
        if "depends_on" in task:
            ctx = "\n".join(f"[{d}]: {results.get(d,{}).get('content','')[:120]}" for d in task["depends_on"])
            task["prompt"] = f"Context:\n{ctx}\n\nTask: {task['prompt']}"
        # enqueue as leaf
        qfile = QUEUE / f"{nid}.json"
        qfile.write_text(json.dumps(task))
        # wait for bottom_tier to finish (poll)
        deadline = time.time() + 180
        while time.time() < deadline:
            donef = DONE / f"{nid}.json"
            if donef.exists():
                results[nid] = json.loads(donef.read_text())
                break
            time.sleep(0.8)
        else:
            results[nid] = {"tid": nid, "status": "timeout"}
            print(json.dumps({"nid": nid, "status": "timeout"}), flush=True)

    summary = {"dag": dag_path.stem, "results": {k: {"status": v.get("status"), "tokens": v.get("tokens"), "conf": v.get("confidence")} for k,v in results.items()}}
    (OUT / f"dag_{dag_path.stem}.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary), flush=True)
    return summary

def main():
    print(json.dumps({"node": "N0_dag_orchestrator", "status": "alive", "mold": "fractal-dag"}), flush=True)
    while True:
        for dpath in sorted(DAGS.glob("*.json")):
            try:
                run_dag(dpath)
                dpath.rename(dpath.with_suffix(".done"))
            except Exception as e:
                print(json.dumps({"err": str(e), "dag": dpath.name}), flush=True)
        time.sleep(2)

if __name__ == "__main__":
    main()
