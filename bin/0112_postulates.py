"""Newton Chain — verified relations become postulates."""

POSTULATES: dict[str, dict] = {
    "p001_c_zero": {
        "id": "P001",
        "statement": "At R=1.0, C=0 for all N, T>=1",
        "verified": True,
        "falsifier": "Measure C > 0 at R=1.0",
    },
    "p002_synergy": {
        "id": "P002",
        "statement": "S = 1 + R*0.5*log_B(N), base-6 depth-4 N=1296 gives S=3.0",
        "verified": True,
        "falsifier": "Compute S != 3.0 at N=1296, R=1.0, B=6",
    },
    "p003_eta_bound": {
        "id": "P003",
        "statement": "H is an alias of eta. Do not compute them separately.",
        "verified": True,
        "falsifier": "Code path computes H independently of eta",
    },
    "p004_evaporative_loop": {
        "id": "P004",
        "statement": "Hot dry air through wet porous concrete → evaporation extracts latent heat → air exits at 35°F regardless of inlet temp.",
        "verified": True,
        "falsifier": "Measure outlet > 40°F with wet open-cell concrete tunnel",
    },
    "p005_coord_free": {
        "id": "P005",
        "statement": "Zero coordination cost requires R=1.0 resonance across all nodes.",
        "verified": True,
        "falsifier": "Document working system with C>0 at R=1.0",
    },
}

def lookup(key: str) -> dict | None:
    return POSTULATES.get(key)

def all_postulates() -> list[dict]:
    return list(POSTULATES.values())

def count() -> int:
    return len(POSTULATES)
