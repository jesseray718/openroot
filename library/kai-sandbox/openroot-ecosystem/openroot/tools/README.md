# OpenRoot Tools Integration Layer

Master index and 3-stage rollout for high-leverage OSAT mapped into OpenRoot.

## Purpose
Curates immediately usable tools for Node Zero, AEGIS MESH, thermal systems, Stirling mechanical work, ACRE PoPW accounting, sensors, and offline hardware documentation. All Stage 1 components execute on Galaxy A15 Termux with zero grid, zero server, zero persistent network.

## 3-Stage Rollout Plan
Stage 1 (now): Termux-native (python + sqlite3 + built-ins) — ACRE ledger, basic sensor logging, F-Droid kit.  
Stage 2: pip-installable in Termux (pvlib, CoolProp, Reticulum, meshtastic).  
Stage 3: Hardware-in-the-loop validation scripts + bounty-linked verification for ACRE minting.

## Directory Map
- mesh/ — Reticulum + Meshtastic (AEGIS MESH backbone)  
- thermal/ — pvlib + CoolProp + desiccant psychrometrics (exact Thermal Loop)  
- stirling/ — Urieli scripts + AzelioOpenLibrary (engine sizing)  
- acre-ledger/ — ledger.py (SQLite PoPW, 80-line, no deps)  
- onsat-bridge/ — sentinelhub-py + OpenEO (Copernicus/GIS successor)  
- sensors/ — KnowFlow AWM + phyphox + DS18B20 (Node Zero cure monitoring)  
- hardware-docs/ — GitBuilding pipeline  
- fdroid-kit/ — curated F-Droid apps for Stages 1+2

See subfolder READMEs for install commands and pillar alignment.
