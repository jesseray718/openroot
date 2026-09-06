# SPEC: Nanobot Swarm Topology (Computational Permaculture)
**Path:** `research/epistemology/NANOBOT-SWARM-SPEC-01.md`
**Version:** 1.0
**Status:** CONCEPTUAL / IMPLEMENTATION-READY
**Framework:** Good/Input Formula $\frac{Benefit \times Urgency \times (1-Slump)}{Cost \times Effort \times Verification\_Overhead}$

---

## 1. System Objective
To maximize the "yield" of high-fidelity technical artifacts per unit of human interaction. The swarm converts raw human intent into verified, structured documentation by distributing cognitive loads across specialized LLM instances (nanobots), treating human input as the "seed" and AI-clusters as the "soil/nutrients."

## 2. The Good/Input Optimization Strategy
To minimize the denominator (Cost, Effort, Verification Overhead) and maximize the numerator (Benefit, Urgency):

- **Benefit ↑**: Shift from "chatting" to "artifact production."
- **Urgency ↑**: Focus swarm on Stage 1 Roadmap (Stranger-reproducibility).
- **Slump ↓**: Automate the "blank page" problem; nanobots generate the first 80% of any draft.
- **Cost ↓**: Use local models (llama.cpp) for drafting; cloud models (Groq/Claude) for synthesis/critique.
- **Effort ↓**: Human acts as *Governor/Editor*, not *Writer*.
- **Verification Overhead ↓**: Implement "Cross-Model Consensus" (Advisory) → "Human Physical Attestation" (Evidence).

---

## 3. Swarm Topology & Domain Mapping

The swarm operates as a **Directed Acyclic Graph **(DAG). Each node (Nanobot) has a specific instruction set and input/output contract.

### A. The Specialized Nodes
| Nanobot ID | Designation | Domain | Toolset | Primary Function |
| :--- | :--- | :--- | :--- | :--- |
| **SCOUT** | Intelligence | Search/Discovery | `web_search`, `fetch_url` | Gather latest papers, API docs, and competitor failure modes. |
| **ARCHITECT** | Synthesis | System Mapping | Theory → Structure | Convert raw ideas into markdown specs/schemas. |
| **SKEPTIC** | Verification | Red-Teaming | Convergence Analysis | Identify "theoretical" gaps, bus-factor risks, and logical fallacies. |
| **SCRIBE** | Production | Drafting | GitHub/Markdown/GPL/CC | Format based on OpenRoot naming conventions. |
| **GOVERNOR** | Routing | Orchestration | `aiq`, `bash`, `lumo` | Route output from SCOUT → ARCHITECT → SKEPTIC → SCRIBE. |

---

## 4. Execution Routing (The Assembly Line)

Human input enters as a **Seed Intent** (e.g., *"I need a test protocol for WBTE-01"*).

1. **Sourcing Phase **(SCOUT):
   - Inputs: Seed Intent.
   - Output: Raw data (Technical papers on dew-point cooling, hardware requirements).
2. **Structural Phase **(ARCHITECT):
   - Inputs: Scout Data + OpenRoot Context Bridge.
   - Output: A skeletal draft (headers, logic flow, required variables).
3. **Stress-Test Phase **(SKEPTIC):
   - Inputs: Architect Draft.
   - Output: A "Critique List" (e.g., *"Missing safety warning on pressure valves," "Claim X is not yet verified physically"*).
4. **Refinement Phase **(ARCHITECT ↔ SKEPTIC):
   - Iterative loop until the SKEPTIC's "Criticality Score" drops below a threshold.
5. **Production Phase **(SCRIBE):
   - Inputs: Refined Draft.
   - Output: Paste-ready `.md` file with correct licensing (CC-BY-SA 4.0/GPL v3).
6. **Final Gate **(HUMAN):
   - Action: Review → `gcp` (git add/commit/push).

---

## 5. Epistemic Safeguards
Following the Convergence Analysis, the swarm adheres to the **Physicality Boundary**:

- **LLM Consensus ≠ Truth**: If SCOUT, ARCHITECT, and SKEPTIC all agree a thermal claim is "likely," the SCRIBE *must* still label it `[THEORETICAL]`.
- **The Attestation Trigger**: Swarm output remains "Draft" status until a physical person (Stranger/Academic) provides a verified observation (VERIFY-01).
- **Verification Overhead Reduction**: The SKEPTIC is tasked with creating the *simplest possible* test it can imagine to prove the theory wrong (Falsification over Verification).

## 6. Implementation Path (Termux/aiq)
- **Local/Cloud Hybrid**:
  - `Local (Qwen2.5)` → High-volume drafting/formatting.
  - `Groq (Llama3/Mixtral)` → High-speed routing and synthesis.
  - `Claude/GPT-4` → High-complexity convergence and strategic audit.
- **Automation**: Use `~/bin/epi` to chain these prompts via shell scripts, piping the output of one AI provider into the prompt of the next.

---
**Permaculture Principle Applied**: *Integrate rather than segregate.* (The swarm turns fragmented AI capabilities into a singular, productive organism).
