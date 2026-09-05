# Scenario Resolver Logic (for later automation)
Input: observed conditions + available resources + people present
Process:
1. Match against trigger conditions
2. Surface immediate life-safety actions first
3. Rank subsequent actions by (impact on lowest node) × (feasibility with present resources)
4. Pull cross-references from permies-high-value, hackaday-oshw, and ancient-wisdom seeds
5. Output a short, ordered action list + what to measure next

This logic is deliberately simple so it can run offline on a phone or mesh node with no large model required.
