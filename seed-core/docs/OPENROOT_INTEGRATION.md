# Integration with the Larger OpenRoot Project

Seed Core sits above the physical and computational primitives (Aero-Disc, UNE, PoPW, local LLM hierarchy). Seeds are how the system remembers the why and the how of optimization so every new session begins at a higher baseline.

Absorption path remains:
1. Write or update seed
2. Place as /sdcard/openroot/session_seeds/current_seed.json
3. Run extract / bridge
4. Future sessions inherit the raised capability
