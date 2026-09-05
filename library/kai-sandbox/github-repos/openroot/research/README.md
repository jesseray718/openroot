# OpenRoot Research Commons
Open trials. Public data. Community validation.
Every build log is a data point.
Every sensor reading is peer-reviewable evidence.

This is how you build accreditation that means something —
not by paying an institution, but by publishing verifiable
data that anyone can replicate.

## Active Research

### Node Zero — Sikeston, Missouri (Hot/Humid)
Status: Panel pour imminent, June 2026
Builder: Jesse McMillen
Data: Published to build-log/node-zero/ after Day 21

## Climate Validation Needed

- [ ] Hot/dry (Arizona, Morocco, Saudi Arabia)
- [ ] Hot/humid (Florida, Bangladesh, SE Asia)
- [x] Hot/humid continental (SE Missouri — in progress)
- [ ] Temperate (Pacific Northwest, Northern Europe)
- [ ] Tropical (Central Africa, Brazil, Indonesia)
- [ ] Cold (Canada, Scandinavia, Russia)

## How to Submit Research

1. Build a node
2. Log sensor data (scripts/sensor_log.sh)
3. Publish data to IPFS
4. Open a PR with your data and build log
5. Community validates your methodology
6. Your data enters the permanent commons

## Data Format
See scripts/sensor_log.sh for the canonical CSV schema.
All data must include: timestamp, location, sensor IDs,
raw readings, calculated delta-T.
