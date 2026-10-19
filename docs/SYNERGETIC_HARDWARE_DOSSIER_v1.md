# The Synergetic Hardware Dossier — OpenRoot Physical Organism v1.0

## 7 Layers of Physical Sovereignty
Layer 6: AI SYNTHESIS (OptiPlex + Cloud Router)
Layer 5: GOVERNANCE (OpenRoot receipts, pods, synergetic calculus)
Layer 4: APPLICATION (LXMF messaging, ACRE minting, TODO routing)
Layer 3: TRANSPORT (Reticulum multi-radio overlay network)
Layer 2: MESH FIRMWARE (MeshCore, Meshtastic, RNode firmware)
Layer 1: RADIO HARDWARE (LoRa SX1262, ESP32 WiFi/BT, AM transmitter)
Layer 0: PHYSICAL SUBSTRATE (sensors, actuators, solar, aerocement)

## ESP32 (The Atomic Node) — $3-5 each
Dual-core 240MHz, 520KB SRAM, WiFi + Bluetooth.
Signs readings with Ed25519 hardware crypto. 1 ESP32 = 1 zone in expert mesh.
Sensors: DS18B20 temp ($2), BME280 climate ($3), INA219 energy ($2), HX711 weight ($2), INMP441 audio ($3), PN532 NFC ($3), LoRa SX1262 ($8).
Stacking: 1 ESP32 + BME280 + INA219 + HX711 + LoRa = 4 functions, $15. Synergy = phi^4 = 6.85x.

## LoRa Meshtastic (Ground Mesh) — $30-55/node
SX1262 radio, 915MHz US, 10km range. Self-healing mesh, no infrastructure.
10 nodes = 10 sensors + 10 relays + 1 mesh = 21 functions. Synergy = phi^21 x (1 + ln(10)/phi) = 2930x.

## MeshCore (C++ Mesh Firmware)
Open-source, runs on ESP32/nRF52840. Diversity: if Meshtastic jammed, MeshCore works.
Supports 50+ boards. Built-in Ed25519 crypto.

## Reticulum (RNS — Universal Transport)
Python-based, multi-transport, self-healing, encrypted (X25519 + Ed25519).
Connects LoRa, WiFi, Serial, TCP, AX.25 ham radio. DTN store-and-forward.
RNS destination hash = zone ID. RNS path = routing trail.

## RNode (Open Hardware Radio) — $50-120
Open-source, SX1276/1262, USB serial. LoRa node + KISS modem + packet radio.
 $50 RNode + $0 OptiPlex = mesh gateway. Commercial equivalent $500+. eta = 120x.

## LXMF (Reticulum Messaging)
Asynchronous store-and-forward over RNS. Like Signal but for mesh.
Delivery receipts = signed confirmation. Closed-loop: OptiPlex sends command, ESP32 executes, measures joules, signs receipt, sends back.

## Cloud 9 Mini Aerostat (Elevated Relay) — $200-400
Ground-tethered aerostat, heated envelope via thermal cascade.
Lift + communication + energy storage + observation = 4 functions.
LoRa range 10km to 50-100km at altitude. Thermal cascade heats envelope = FREE lift.
Synergy = phi^4 x (1 + ln(3)/phi) = 9.18x.

## AM Radio Broadcasting (Uncensorable Layer) — $45 total
Technician license: $15 FCC fee + pass 35-question test. Baofeng UV-5R: $25.
Unlocks: AX.25 packet radio, APRS, Winlink (email over radio), repeater networks (500km+).
1 transmitter = unlimited receivers. Cannot be jammed. Legally protected FCC Part 97.
eta = $500 commercial / $45 DIY x 12 months = 133x.

## Thermal Cascade (Energy Sovereignty)
Aerocement solar absorber + geothermal labyrinth + desiccant dehumidification.
Captures solar energy, stores in thermal mass, dispatches as heat/cooling/mechanical.
Measured AND unmetered: RAPL joules + delta-T sensors. No fuel, no supply chain.

## Routing Cascade (Compute Sovereignty)
Per-pod keyword routing (deterministic, no AI) + minimal dossier (4000 chars) + cloud router cascade (OpenRouter Llama 3.3 70B + local qwen2.5:3b fallback) + clarifying loop.
Receipt cache = free recompute. Rolling-window token replenishment.

## Monetary Leverage Cascade (Capital Sovereignty)
Synergetic TODO router routes capital through decision engine.
Formula: synergy = base x phi^stack x (1 + ln(beneficiaries)/phi).
Agape gate: eta(A+B) > max(eta(A), eta(B)). Connect only if measurably better.
 $1 OpenRouter credit routes to highest-synergy TODO. SARE grants pod = 250000x ROI.

## Priority Build Order
1. Technician license + Baofeng ($45, 133x ROI, principles 2,5,9,11)
2. 5x ESP32 + DS18B20 + LoRa ($50, 67x ROI, principles 1,2,3,7,9)
3. RNode on OptiPlex ($50, 120x ROI, principles 5,7,9,11)
4. RNS instance on OptiPlex ($0, infinite ROI, principles 7,8,9,12)
5. Cloud 9 mini prototype ($200, 9x ROI, principles 2,3,5,9,11)
6. SARE grants pod ($0, 15000x ROI, principles 3,6,7,8)

## Synergetic Compounding Formula
eta_system = (sum of useful outputs) / (sum of human inputs)
synergy = 1 x phi^functions x (1 + ln(beneficiaries)/phi)
Cooperation compounds exponentially. Extraction stays linear.
