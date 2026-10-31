# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
"""OpenRoot Synergetic TODO Router v1

Dynamic TODO list with:
- Full coefficient accounting (cost, effort, time, reward, tool, resonance)
- 12 permaculture principles as routing gates (each routes to all other 11)
- Synergetic calculus: stacking functions compound exponentially
- Agape cooperation: benefit measured at recipient, not giver
- Both human and AI can append
- Routes capital ($1, $15 tokens) through the decision engine

Formula (synergetic):
  synergy_score = base_value × φ^stack_count × (1 + ln(beneficiaries)/φ)
  where φ = 1.618 (golden ratio), stack_count = functions served

Formula (agape gate):
  connection_permitted = η(A+B) > max(η(A), η(B))
  benefit measured at recipient only, not at giver
"""
import argparse, hashlib, json, math, os, sqlite3, sys, time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(os.environ.get("OPENROOT_REPO", "/home/jesse/openroot"))
DB_PATH = REPO / "data" / "synergetic_todo.db"
PHI = 1.6180339887498947

# 12 Permaculture Principles — each routes to all other 11
PERMACULTURE = {
    1: {"name": "Observe & Interact", "gate": "passive_monitoring_days >= 7 before mutation",
        "routes_to": [2,3,4,5,6,7,8,9,10,11,12],
        "metric": "observation_depth"},
    2: {"name": "Catch & Store Energy", "gate": "stored_joules >= captured_joules * 0.5",
        "routes_to": [1,3,4,5,6,7,8,9,10,11,12],
        "metric": "energy_storage_efficiency"},
    3: {"name": "Obtain a Yield", "gate": "output_value >= input_cost * 1.5",
        "routes_to": [1,2,4,5,6,7,8,9,10,11,12],
        "metric": "roi_ratio"},
    4: {"name": "Apply Self-Regulation", "gate": "if scar_count >= 3 for class X, auto_disable(X)",
        "routes_to": [1,2,3,5,6,7,8,9,10,11,12],
        "metric": "feedback_latency"},
    5: {"name": "Use Renewable Resources", "gate": "renewable_fraction >= 0.8",
        "routes_to": [1,2,3,4,6,7,8,9,10,11,12],
        "metric": "renewable_fraction"},
    6: {"name": "Produce No Waste", "gate": "compost_rate >= 0.95",
        "routes_to": [1,2,3,4,5,7,8,9,10,11,12],
        "metric": "waste_composted_pct"},
    7: {"name": "Design Patterns to Details", "gate": "schema_first then implementation",
        "routes_to": [1,2,3,4,5,6,8,9,10,11,12],
        "metric": "schema_to_impl_drift"},
    8: {"name": "Integrate Don't Segregate", "gate": "cross_zone_proposals >= 1 per beat",
        "routes_to": [1,2,3,4,5,6,7,9,10,11,12],
        "metric": "integration_density"},
    9: {"name": "Use Small Slow Solutions", "gate": "if small_model_works, never_use_large",
        "routes_to": [1,2,3,4,5,6,7,8,10,11,12],
        "metric": "solution_size_vs_need"},
    10: {"name": "Value Diversity", "gate": "unique_approaches >= 3",
         "routes_to": [1,2,3,4,5,6,7,8,9,11,12],
         "metric": "diversity_index"},
    11: {"name": "Use Edges & Marginal", "gate": "edge_utilization >= core_utilization",
         "routes_to": [1,2,3,4,5,6,7,8,9,10,12],
         "metric": "edge_to_core_ratio"},
    12: {"name": "Creatively Respond to Change", "gate": "adaptation_rate >= 0.5",
         "routes_to": [1,2,3,4,5,6,7,8,9,10,11],
         "metric": "adaptation_velocity"},
}

def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT DEFAULT 'general',
            status TEXT DEFAULT 'pending',
            
            -- Coefficient variables (plain-term accounting)
            cost_usd REAL DEFAULT 0,
            effort_hours REAL DEFAULT 0,
            time_to_yield_days REAL DEFAULT 0,
            reward_usd REAL DEFAULT 0,
            tool_required TEXT DEFAULT '',
            resonance REAL DEFAULT 0.5,
            
            -- Synergetic calculus
            functions_stacked INTEGER DEFAULT 1,
            beneficiaries INTEGER DEFAULT 1,
            synergy_score REAL DEFAULT 0,
            agape_coefficient REAL DEFAULT 0.5,
            
            -- Permaculture routing
            principles_matched TEXT DEFAULT '[]',
            principle_scores TEXT DEFAULT '{}',
            
            -- Metadata
            created_by TEXT DEFAULT 'human',
            created_at TEXT,
            updated_at TEXT,
            completed_at TEXT,
            receipt_hash TEXT,
            notes TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS capital_routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount_usd REAL NOT NULL,
            source TEXT NOT NULL,
            todo_id INTEGER,
            route_path TEXT,
            yield_usd REAL DEFAULT 0,
            status TEXT DEFAULT 'pending',
            created_at TEXT,
            FOREIGN KEY (todo_id) REFERENCES todos(id)
        );
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,
            value_usd REAL DEFAULT 0,
            location TEXT,
            status TEXT DEFAULT 'active',
            linked_todos TEXT DEFAULT '[]',
            created_at TEXT
        );
    """)
    return conn

def now_utc():
    return datetime.now(timezone.utc).isoformat()

def calc_synergy(functions_stacked, beneficiaries, base_value=1.0):
    """Synergetic calculus: reward = base × φ^stack × (1 + ln(cooperators)/φ)"""
    if functions_stacked < 1: functions_stacked = 1
    if beneficiaries < 1: beneficiaries = 1
    return base_value * (PHI ** min(functions_stacked, 50)) * (1 + math.log(beneficiaries) / PHI)

def calc_agape_gate(eta_a, eta_b, eta_combined):
    """Agape composition rule: connect only if η(A+B) > max(η(A), η(B))"""
    return eta_combined > max(eta_a, eta_b)

def calc_eta(cost, effort, reward, time_to_yield, resonance, functions_stacked, beneficiaries):
    """η = useful output / human input, weighted by synergy and resonance"""
    if cost + effort <= 0: return 0
    input_cost = cost + (effort * 15)  # effort valued at $15/hr
    output_value = reward * calc_synergy(functions_stacked, beneficiaries)
    if input_cost <= 0: return output_value
    time_penalty = max(0.1, 1.0 / (1.0 + time_to_yield / 30))
    return (output_value / input_cost) * resonance * time_penalty

def score_principles(todo):
    """Score each permaculture principle 0-1, return matched + scores"""
    scores = {}
    matched = []
    
    # Principle 1: Observe (passive monitoring)
    scores[1] = 0.8 if todo.get('category') in ['research','observation','audit'] else 0.3
    
    # Principle 2: Catch & Store Energy
    scores[2] = 0.9 if todo.get('category') in ['energy','thermal','solar','battery'] else 0.3
    
    # Principle 3: Obtain a Yield
    roi = (todo.get('reward_usd',0) - todo.get('cost_usd',0)) / max(todo.get('cost_usd',1), 1)
    scores[3] = min(1.0, max(0.0, roi / 2))
    
    # Principle 4: Self-Regulation
    scores[4] = 0.7 if todo.get('category') in ['fix','repair','maintain'] else 0.4
    
    # Principle 5: Renewable Resources
    scores[5] = 0.9 if todo.get('tool_required','').lower() in ['solar','esp32','scrap','recycled'] else 0.4
    
    # Principle 6: Produce No Waste
    scores[6] = 0.9 if todo.get('category') in ['compost','recycle','salvage','e-scrap'] else 0.4
    
    # Principle 7: Design Patterns to Details
    scores[7] = 0.8 if todo.get('category') in ['architecture','schema','design','plan'] else 0.4
    
    # Principle 8: Integrate Don't Segregate
    scores[8] = min(1.0, todo.get('beneficiaries',1) / 5)
    
    # Principle 9: Small Slow Solutions
    scores[9] = 0.9 if todo.get('cost_usd',0) < 50 and todo.get('effort_hours',0) < 4 else 0.3
    
    # Principle 10: Value Diversity
    scores[10] = 0.7 if todo.get('functions_stacked',1) >= 3 else 0.3
    
    # Principle 11: Use Edges
    scores[11] = 0.8 if todo.get('category') in ['mesh','edge','rural','marginal'] else 0.4
    
    # Principle 12: Creatively Respond to Change
    scores[12] = 0.7 if todo.get('category') in ['adapt','pivot','experiment'] else 0.4
    
    for pid, score in scores.items():
        if score >= 0.6:
            matched.append(pid)
    
    return matched, scores

def add_todo(conn, args):
    """Add a TODO item with full coefficient accounting"""
    todo = {
        'title': args.title,
        'description': args.description or '',
        'category': args.category or 'general',
        'cost_usd': args.cost or 0,
        'effort_hours': args.effort or 0,
        'time_to_yield_days': args.time_to_yield or 0,
        'reward_usd': args.reward or 0,
        'tool_required': args.tool or '',
        'resonance': args.resonance or 0.5,
        'functions_stacked': args.stacked or 1,
        'beneficiaries': args.beneficiaries or 1,
        'created_by': args.created_by or 'human',
        'created_at': now_utc(),
        'updated_at': now_utc(),
    }
    
    # Calculate synergy score
    base_value = max(todo['reward_usd'], 1)
    todo['synergy_score'] = calc_synergy(todo['functions_stacked'], todo['beneficiaries'], base_value)
    
    # Calculate agape coefficient (η)
    todo['agape_coefficient'] = calc_eta(
        todo['cost_usd'], todo['effort_hours'], todo['reward_usd'],
        todo['time_to_yield_days'], todo['resonance'],
        todo['functions_stacked'], todo['beneficiaries']
    )
    
    # Score permaculture principles
    matched, scores = score_principles(todo)
    todo['principles_matched'] = json.dumps(matched)
    todo['principle_scores'] = json.dumps(scores)
    
    # Insert
    cols = ', '.join(todo.keys())
    placeholders = ', '.join(['?'] * len(todo))
    cur = conn.execute(f"INSERT INTO todos ({cols}) VALUES ({placeholders})", list(todo.values()))
    conn.commit()
    todo_id = cur.lastrowid
    
    # Receipt hash
    receipt_data = json.dumps(todo, sort_keys=True)
    receipt_hash = hashlib.sha256(receipt_data.encode()).hexdigest()
    conn.execute("UPDATE todos SET receipt_hash=? WHERE id=?", [receipt_hash, todo_id])
    conn.commit()
    
    print(f"[banked] TODO #{todo_id} added: {todo['title']}")
    print(f"  synergy_score: {todo['synergy_score']:.2f}")
    print(f"  agape_coefficient (η): {todo['agape_coefficient']:.4f}")
    print(f"  principles matched: {len(matched)}/12 — {[PERMACULTURE[p]['name'] for p in matched]}")
    print(f"  receipt: {receipt_hash[:16]}...")
    return todo_id

def list_todos(conn, args):
    """List TODOs sorted by synergetic priority"""
    status = args.status or 'pending'
    order = args.sort or 'priority'
    
    if order == 'priority':
        order_clause = "ORDER BY synergy_score DESC, agape_coefficient DESC"
    elif order == 'eta':
        order_clause = "ORDER BY agape_coefficient DESC"
    elif order == 'cost':
        order_clause = "ORDER BY cost_usd ASC"
    elif order == 'time':
        order_clause = "ORDER BY time_to_yield_days ASC"
    else:
        order_clause = "ORDER BY id DESC"
    
    rows = conn.execute(f"SELECT * FROM todos WHERE status=? {order_clause}", [status]).fetchall()
    cols = [d[0] for d in conn.execute("SELECT * FROM todos LIMIT 0").description]
    
    if not rows:
        print(f"[held] no {status} todos")
        return
    
    print(f"\n{'ID':>3} {'Title':40s} {'Cost':>7} {'Reward':>7} {'η':>6} {'Syn':>6} {'Princ':>5} {'Stack':>5} {'Tool'}")
    print("-" * 110)
    for row in rows:
        todo = dict(zip(cols, row))
        principles = json.loads(todo.get('principles_matched','[]'))
        print(f"{todo['id']:>3} {todo['title'][:40]:40s} "
              f"${todo['cost_usd']:>5.0f} ${todo['reward_usd']:>5.0f} "
              f"{todo['agape_coefficient']:>5.2f} {todo['synergy_score']:>5.1f} "
              f"{len(principles):>4}/12 {todo['functions_stacked']:>4} "
              f"{todo['tool_required'][:15]}")
    print(f"\n  total: {len(rows)} {status} todos")

def route_capital(conn, args):
    """Route capital through the decision engine — finds highest synergetic TODO"""
    amount = args.amount
    rows = conn.execute(
        "SELECT * FROM todos WHERE status='pending' AND cost_usd <= ? ORDER BY synergy_score DESC, agape_coefficient DESC LIMIT 10",
        [amount]
    ).fetchall()
    cols = [d[0] for d in conn.execute("SELECT * FROM todos LIMIT 0").description]
    
    if not rows:
        print(f"[held] no pending todos under ${amount}")
        return
    
    print(f"\n=== CAPITAL ROUTE: ${amount} ===")
    print(f"{'ID':>3} {'Title':40s} {'Cost':>7} {'Reward':>7} {'η':>6} {'Syn':>6} {'ROI':>6} {'Stack'}")
    print("-" * 90)
    
    best = None
    best_score = 0
    for row in rows:
        todo = dict(zip(cols, row))
        roi = (todo['reward_usd'] - todo['cost_usd']) / max(todo['cost_usd'], 1)
        total_score = todo['synergy_score'] * todo['agape_coefficient'] * (1 + roi)
        if total_score > best_score:
            best_score = total_score
            best = todo
        principles = json.loads(todo.get('principles_matched','[]'))
        print(f"{todo['id']:>3} {todo['title'][:40]:40s} "
              f"${todo['cost_usd']:>5.0f} ${todo['reward_usd']:>5.0f} "
              f"{todo['agape_coefficient']:>5.2f} {todo['synergy_score']:>5.1f} "
              f"{roi:>5.1f}x {todo['functions_stacked']}")
    
    if best:
        print(f"\n>>> RECOMMENDED ROUTE: #{best['id']} — {best['title']}")
        print(f"    Cost: ${best['cost_usd']:.2f} | Reward: ${best['reward_usd']:.2f}")
        print(f"    η (agape): {best['agape_coefficient']:.4f}")
        print(f"    Synergy: {best['synergy_score']:.2f} ({best['functions_stacked']} functions, {best['beneficiaries']} beneficiaries)")
        principles = json.loads(best.get('principles_matched','[]'))
        print(f"    Permaculture: {len(principles)}/12 principles matched")
        print(f"    Tool: {best['tool_required']}")
        
        # Record the route
        conn.execute(
            "INSERT INTO capital_routes (amount_usd, source, todo_id, route_path, status, created_at) VALUES (?,?,?,?,?,?)",
            [amount, args.source or 'general', best['id'], json.dumps({
                'todo_id': best['id'], 'eta': best['agape_coefficient'],
                'synergy': best['synergy_score'], 'principles': principles
            }), 'routed', now_utc()]
        )
        conn.commit()
        print(f"    [banked] capital route recorded")

def show_started_unfinished(conn):
    """Show items started but not finished"""
    rows = conn.execute("SELECT * FROM todos WHERE status='in_progress' ORDER BY updated_at DESC").fetchall()
    cols = [d[0] for d in conn.execute("SELECT * FROM todos LIMIT 0").description]
    
    if not rows:
        print("[banked] no unfinished items")
        return
    
    print(f"\n=== STARTED BUT NOT FINISHED ({len(rows)}) ===")
    for row in rows:
        todo = dict(zip(cols, row))
        principles = json.loads(todo.get('principles_matched','[]'))
        print(f"  #{todo['id']} {todo['title'][:50]}")
        print(f"    cost: ${todo['cost_usd']:.0f} | effort: {todo['effort_hours']:.1f}h | η: {todo['agape_coefficient']:.2f}")
        print(f"    started: {todo.get('updated_at','?')[:19]} | principles: {len(principles)}/12")

def show_assets(conn):
    """Show registered assets"""
    rows = conn.execute("SELECT * FROM assets WHERE status='active' ORDER BY value_usd DESC").fetchall()
    if not rows:
        print("[held] no assets registered — use 'add-asset' to register")
        return
    
    print(f"\n=== ASSETS ({len(rows)}) ===")
    for row in rows:
        print(f"  {row[1]:30s} type={row[2] or '?':10s} value=${row[3]:>8.0f} location={row[4] or '?'}")

def mark_status(conn, args):
    """Update status of a TODO"""
    conn.execute("UPDATE todos SET status=?, updated_at=? WHERE id=?", [args.status, now_utc(), args.id])
    if args.status == 'completed':
        conn.execute("UPDATE todos SET completed_at=? WHERE id=?", [now_utc(), args.id])
    conn.commit()
    print(f"[banked] TODO #{args.id} marked {args.status}")

def add_asset(conn, args):
    """Register an asset"""
    conn.execute(
        "INSERT INTO assets (name, type, value_usd, location, status, linked_todos, created_at) VALUES (?,?,?,?,?,?,?)",
        [args.name, args.type, args.value, args.location, 'active', '[]', now_utc()]
    )
    conn.commit()
    print(f"[banked] asset registered: {args.name} (${args.value})")

def show_boundary_map(conn):
    """Show the permaculture routing map — how principles connect"""
    print("\n=== PERMACULTURE ROUTING MAP (12 → 11 each) ===")
    for pid, p in PERMACULTURE.items():
        routes = p['routes_to']
        names = [PERMACULTURE[r]['name'][:15] for r in routes[:4]]
        print(f"  {pid:2d}. {p['name']:30s} → routes to {len(routes)} others (sample: {', '.join(names)}...)")
    print(f"\n  Total routing edges: {sum(len(p['routes_to']) for p in PERMACULTURE.values())}")

def main():
    ap = argparse.ArgumentParser(description="OpenRoot Synergetic TODO Router v1")
    sub = ap.add_subparsers(dest='cmd', required=True)
    
    # Add TODO
    ap_add = sub.add_parser('add', help='Add a TODO with full coefficient accounting')
    ap_add.add_argument('--title', required=True)
    ap_add.add_argument('--description', default='')
    ap_add.add_argument('--category', default='general')
    ap_add.add_argument('--cost', type=float, default=0, help='Cost in USD')
    ap_add.add_argument('--effort', type=float, default=0, help='Effort in hours')
    ap_add.add_argument('--time-to-yield', type=float, default=0, help='Days to yield')
    ap_add.add_argument('--reward', type=float, default=0, help='Expected reward in USD')
    ap_add.add_argument('--tool', default='', help='Tool required')
    ap_add.add_argument('--resonance', type=float, default=0.5, help='Resonance 0-1 (agape alignment)')
    ap_add.add_argument('--stacked', type=int, default=1, help='Number of functions stacked')
    ap_add.add_argument('--beneficiaries', type=int, default=1, help='Number of beneficiaries')
    ap_add.add_argument('--created-by', default='human')
    
    # List
    ap_list = sub.add_parser('list', help='List TODOs')
    ap_list.add_argument('--status', default='pending')
    ap_list.add_argument('--sort', default='priority', choices=['priority','eta','cost','time','id'])
    
    # Route capital
    ap_route = sub.add_parser('route', help='Route capital through decision engine')
    ap_route.add_argument('--amount', type=float, required=True, help='Amount to route in USD')
    ap_route.add_argument('--source', default='general')
    
    # Status update
    ap_mark = sub.add_parser('mark', help='Update TODO status')
    ap_mark.add_argument('id', type=int)
    ap_mark.add_argument('status', choices=['pending','in_progress','completed','blocked'])
    
    # Started but not finished
    sub.add_parser('unfinished', help='Show started but not finished')
    
    # Assets
    ap_asset = sub.add_parser('add-asset', help='Register an asset')
    ap_asset.add_argument('--name', required=True)
    ap_asset.add_argument('--type', default='')
    ap_asset.add_argument('--value', type=float, default=0)
    ap_asset.add_argument('--location', default='')
    
    sub.add_parser('assets', help='Show registered assets')
    
    # Boundary map
    sub.add_parser('map', help='Show permaculture routing map')
    
    args = ap.parse_args()
    conn = init_db()
    
    if args.cmd == 'add':
        add_todo(conn, args)
    elif args.cmd == 'list':
        list_todos(conn, args)
    elif args.cmd == 'route':
        route_capital(conn, args)
    elif args.cmd == 'mark':
        mark_status(conn, args)
    elif args.cmd == 'unfinished':
        show_started_unfinished(conn)
    elif args.cmd == 'add-asset':
        add_asset(conn, args)
    elif args.cmd == 'assets':
        show_assets(conn)
    elif args.cmd == 'map':
        show_boundary_map(conn)
    
    conn.close()

if __name__ == "__main__":
    main()
