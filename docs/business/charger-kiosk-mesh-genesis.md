# Charger Kiosk + Mesh Genesis: Business Model and Node Deployment Plan

**Project:** OpenRoot / One Human Family
**Location:** Sikeston, MO (I-55 / I-57 interchange)
**Date:** 2026-07-08
**Author:** Jesse McMillen / One Human Family

## Part 1: The 25W USB-C Charger Supply Chain

### Wholesale vs Retail Price Discovery

| Source | Price/Unit | Min Order | Notes |
|--------|-----------|-----------|-------|
| Amazon (TT&C 2-pack) | $4.99 | 1 (2-pack) | Free ship over $35, 6ft cable included |
| Amazon (Samsung OEM) | $17.99 | 1 | Official Samsung brand |
| Walmart (generic+cable) | $11.88-$15.59 | 1 | In-store pickup |
| Walmart (Samsung OEM) | $14.29-$19.49 | 1 | Official Samsung |
| Walmart (2-pack generic) | $6.50/ea | 1 (2-pack) | Decent middle ground |
| Rite Distribution (charger only) | $3.89 | 1+ | No cable included |
| Alibaba (100W cable only) | $2.10 | 200 | Cable only, no charger |
| Bulk combo (Rite+Alibaba) | $6.00 | 200 | Cheapest bulk if 200+ needed |

**Conclusion:** Amazon's $4.99/kit (TT&C 2-pack) beats wholesale for orders under 200 units. Amazon IS the bulk supplier at this scale.

### 25W vs 15W Charging Performance (Samsung Galaxy)

| Metric | 15W Charger | 25W Charger | Difference |
|--------|-------------|-------------|------------|
| 0-30 min charge | ~30% | ~45-50% | +15-20% |
| Full charge (0-100%) | ~90 min | ~60-70 min | 20-30 min saved |
| First hour | ~55-60% | ~80-85% | +20-25% |

The difference is most pronounced in the first 30 minutes -- morning rushes, emergency top-ups, multi-device stations. For overnight charging, 15W works equally well.

## Part 2: The Billboard + Vending Machine Funnel

### The Concept

Interstate Billboard: "DEAD PHONE? Next Exit -> Charger Kiosk"
- Traveler pulls off to gas station / truck stop parking lot
- Vending machine kiosk: select phone, buy optimized charger + cable
- Result: $15-20 sale, $5 cost = $10-15 profit per transaction

### Upfront Costs

| Component | Low End | High End |
|-----------|---------|----------|
| Smart vending kiosk (card reader, touchscreen) | $3,600 | $9,500 |
| Billboard (rural Missouri, monthly) | $250/mo | $1,000/mo |
| Billboard design/install | $300 one-time | $2,000 one-time |
| Kiosk location rent (gas station lot) | $0 (rev share) | $200/mo |
| Initial charger inventory (50 kits) | $250 | $500 |
| Power hookup | $0 | $500 |
| **Total to launch** | **~$4,400** | **~$13,500** |

### Revenue Projection

| Metric | Conservative | Optimistic |
|--------|-------------|------------|
| Daily sales | 3 kits/day | 10 kits/day |
| Sale price per kit | $15 | $20 |
| Cost per kit | $5 | $5 |
| Daily profit | $30 | $150 |
| Monthly profit (before overhead) | $900 | $4,500 |
| Minus billboard | -$250 | -$500 |
| Minus location rent | $0 | -$200 |
| **Net monthly profit** | **$650** | **$3,800** |

Payback on kiosk investment: 7 months (conservative) to 1.5 months (optimistic)

### Strategic Location Note

Sikeston sits at the I-55 / I-57 interchange. Major north-south trucking corridor: Memphis to Chicago, St. Louis to the Gulf. Lambert's Cafe ("Throwed Rolls") already pulls travelers off the highway. The kiosk should be placed at a gas station right off the Sikeston exit.

## Part 3: Phased Rollout

### Phase 0 -- Proof of Demand ($500)
- Buy 20 charger kits from Amazon ($100)
- Folding table at Sikeston gas station on a Saturday
- Sell at $15 each
- If sold out in one day: billboard+kiosk model validated

### Phase 1 -- Mini Kiosk ($5,000)
- Lease HonestWaves-style vending kiosk ($3,600)
- Partner with truck stop for free placement (10% rev share)
- Rent one rural billboard at $250/mo on I-55
- Run for 90 days, track numbers

### Phase 2 -- Scale ($15,000+)
- Second kiosk at opposite exit
- Second billboard
- Add screen protectors, cases, power banks
- This becomes the storefront without a storefront lease

### Phase 3 -- Computer/Electronics Shop Front
- Physical storefront for selling optimized hardware + recycled devices
- Repair services ($30-60/hr labor + parts margin)
- Becomes community tech hub

## Part 4: Mesh Node Genesis -- The Kiosk IS Node Zero

The charger kiosk is not just a retail business. It is Tier 3, Node 1, the Vesica Piscis seed of the global fractal mesh.

- Charger kiosk (Sikeston, I-55)
- 1x LoRa node ($50) attached to kiosk
- Acts as: Tier 3, Node 1
- Range: 10km radius
- Covers: Sikeston + surrounding rural area
- The kiosk powers the node, the node powers the network

The kiosk does dual duty:
- Revenue: selling chargers to travelers (cash flow)
- Infrastructure: first mesh node (network growth)
- Permaculture principle: one element serves multiple functions

### Cost: Adding Mesh to the Kiosk

| Component | Cost |
|-----------|------|
| LoRa node (ESP32 + SX1262) | $50 |
| Solar panel + battery | $20 |
| Antenna + cabling | $20 |
| **Total mesh addition** | **$90** |

For $90 on top of the kiosk investment, the retail business becomes the seed of a global communication infrastructure.

## Part 5: Revenue to Infrastructure Pipeline

1. Charger Kiosk Revenue ($650-3,800/mo net)
2. Fund Phase 1: 50 LoRa nodes ($3,500)
3. Mesh network attracts members
4. Membership fees / ACRE tokens / donations
5. Fund Phase 2: Regional relay ($5,000-50,000)
6. Electronics recycling feeds recycled hardware into Tier 3/4
7. Recycled hardware = $0 cost nodes
8. Network grows without capital expenditure
9. 501(c)(3) receives grants for digital inclusion
10. Grants fund Phase 3+ scaling

Copyright (c) One Human Family. Licensed CC-BY-SA 4.0 (documentation), GPL v3 (code).
