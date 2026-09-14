# API Monetization Pipeline — spec v0.1
Existing assets: thermal_product_server (OptiPlex), thermal cascade + psychrometric models,
acre ledger. Pipeline: FastAPI gateway -> API-key auth (sqlite) -> metered joules per request
(from lever joule_events pattern) -> tier pricing -> Stripe/LemonSqueezy webhook -> billing rows.
Grade: STUB until one paid-tier smoke test. Sell-to: HVAC sizing, greenhouse cooling, DePIN
node planning, permies/homestead audience via the existing README channels.
