# Spoke Node Quickstart — OpenRoot Mesh

**Purpose**  
Deploy a local Tier 3 spoke node (Vesica Piscis unit) that joins the growing fractal mesh seeded from Sikeston kiosk (Tier 3 Node 1). One element, multiple yields: local comms + relay + future ACRE rewards for uptime + verified physical work.

**Hardware (minimum viable)**  
- ESP32 + SX1262 LoRa module (or Meshtastic board) \~$25-40  
- 5-10 dBi antenna + pigtail  
- 5V solar panel + 18650/TP4056 + 3.7V Li-ion (or USB-C from kiosk)  
- Optional: small enclosure or AE-GFRC housing later

**Software (one-command on Linux/Termux)**  
1. Flash latest Meshtastic firmware (or use stock ESP-IDF + our future firmware).  
2. Clone spoke template:  
   git clone https://github.com/jesseray718/openroot-spoke-template.git spoke-node  
   cd spoke-node  
3. Edit config.yaml (or web UI):  
   - Long name: your location (e.g. "Sikeston-Node-02")  
   - Short name: unique 4-char (e.g. "SK02")  
   - Frequency: 915 MHz (US) or regional ISM  
   - Role: CLIENT or ROUTER  
   - Connect to nearest known node (Sikeston kiosk coordinates or public Meshtastic map)  
4. Flash + power. Node appears on mesh map within minutes.  
5. Verify: send text message to neighbor; check position packets; confirm routing.

**Integration with OpenRoot stack**  
- Name the node via UNE (once implemented).  
- Uptime + relay work units logged for future ACRE mint (two-approval via Kingdom Engine).  
- Power via Thermal Cascade / solar when AE-GFRC housing is ready.  
- Report status to Bounty Board for verified physical work credit.

**Next steps after first node online**  
- Add second node 5-10 km away (golden ratio spacing).  
- Elevate one node (water tower / hill) for Tier 2 relay.  
- Join regional Flower of Life cluster.  
- Document build in community/ for ACRE claim.

**Troubleshooting**  
- No neighbors: check antenna orientation, frequency match, height.  
- High packet loss: reduce power or add relay.  
- Termux/Android node: use Meshtastic Android app + USB OTG or Bluetooth.

**License & standing**  
CC-BY-SA 4.0 docs. One Human Family. Value the marginal — your first $40 node is structurally identical to the 12 master icosahedron nodes.

Run this, get your first spoke live, then report back. Next block (outreach drafts) only after confirmation.
