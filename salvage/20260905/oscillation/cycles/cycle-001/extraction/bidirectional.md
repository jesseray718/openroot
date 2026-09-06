# Cycle-001 Bidirectional Analysis — TinyGS

## What TinyGS already does extremely well
- Turns \~$20 of hardware (ESP32 + LoRa) into a real satellite ground station
- Joins a live global network of citizen stations
- Supports multiple LoRa modules (SX126x / SX127x and expanding)
- Fully open source, already running at planetary scale
- Extremely low barrier for the lowest node

## How OpenRoot can improve TinyGS (OpenRoot → them)
1. Lowest-node physical mounting & antenna guidance
   - Chicken-wire / scrap / passive structures that still work
   - Simple sky-facing or ground-plane designs that cost almost nothing
2. Clearer “start with almost nothing” BOM path
3. Documentation written for people who have never touched PlatformIO or LoRa before
4. Optional passive thermal / weather protection ideas that fit the same low-cost philosophy

## How TinyGS improves OpenRoot (them → OpenRoot)
1. Immediate real space-age capability that can sit on or beside Node-001
2. Proven global network the lowest node can join tonight
3. Working LoRa satellite reception stack that is already modular
4. Concrete example of the exact pattern: low-tech physical node + high-tech signal

## Smallest useful first contribution (proposed)
Create a single short document inside the TinyGS fork:
“Lowest-Node Antenna & Mounting Notes”
- Materials that cost almost nothing
- How to get a usable antenna with scrap / chicken wire / simple wire
- How to place the station so it can still see the sky
- Link back to OpenRoot Node-001 as a complementary physical unit

This contribution is small, high-signal, and directly raises α_A for the people with the least.
