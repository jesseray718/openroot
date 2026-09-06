# Vesica Piscis — Phased Global Rollout (DV.MSH.VP.PHN01)
LoRa physical limit: 2-5 km typical, 10-15 km max rural line-of-sight.
The original 12-node coordinates (7,000–13,000 km apart) cannot be direct radio neighbors.

**Correct architecture:** 12 nodes = global coordination hubs synced via IPFS/Zenodo/internet. LoRa only used for local clusters (<10 km).

## Phase 1: Sikeston Seed (Next 30-90 days)
VP-01 at kiosk (36.88, -89.59) as gateway (LoRa + WiFi/4G backhaul).
Deploy 3 more nodes within 5 km (neighbors/house/shop/farm).
Test evidence packet flow: work → LoRa → IPFS hash → Zenodo → Solana memo.

## Phase 2: Regional (3-12 months)
Expand to 7-10 nodes in SE Missouri / southern Illinois / western Kentucky triangle.
Add fiber/DSL backhaul at 2-3 hubs.

## Phase 3+: National then Global
National backbone hubs in major cities. The 12 symbolic coordinates become internet-synced verification hubs (not radio-linked). All evidence packets sync via IPFS polling across the 12 hubs.

Full details, cost model, and packet routing in committed version.
