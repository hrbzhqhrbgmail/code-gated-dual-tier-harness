# Code-Gated Dual-Tier Agent Harness for Physical-Engineering's Last Exam (PLE)

[![Competition](https://img.shields.io/badge/Kaggle-Google%20PLE%20Challenge-blue.svg)](https://www.kaggle.com/competitions/physical-engineerings-last-exam)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Protocol](https://img.shields.io/badge/Protocol-PLE%20v1%20WebSocket-orange.svg)](docs/protocol.md)

An autonomous, deterministic agent harness engineered for **Physical-Engineering's Last Exam (PLE)**, uniting frontier reasoning (Google-sponsored `google-cloud/gemini-4-argon` / `gemini-3.8-flash`) with strict engineering discipline.

---

## 1. Architectural Highlights

Our architecture decouples host orchestration from container execution through a four-stage state machine:

$$\mathcal{S} = \{\text{Stage 0: Snapshot \& MCP}\} \xrightarrow{\tau_0} \{\text{Stage 1: Planner}\} \xrightarrow{\tau_1} \{\text{Stage 2: Worker}\} \xrightarrow{\tau_2} \{\text{Stage 3: Deterministic PE Audit}\}$$

1. **Stage 0 — Baseline Snapshot & Dynamic `MCPRegistry`**:
   - Takes a cryptographic baseline snapshot of the workspace to monitor deliverable provenance.
   - Auto-discovers local container Model Context Protocol (`MCP`) servers on `http://127.0.0.1:8000/mcp/`.

2. **Stage 1 — Read-Only Principal Planner & Revision Graph DAG (`PLAN_MAX_SEC = 420s`)**:
   - Ingests and disambiguates multi-modal project archives (PDF, DWG/DXF, XLSX, IFC4).
   - Formulates a Directed Acyclic Graph (DAG) that automatically prunes `SUPERSEDED` revisions and outdated addenda.

3. **Stage 2 — Deterministic Container Worker (`WORKER_MAX_SEC = 5400s`)**:
   - Emits self-contained scripts via bounded execution tools, enforced with a **3-strike error loop breaker**.

4. **Stage 3 — Pre-Submission Feasibility Gate ($G = 1$ Enforcement)**:
   - Audits deliverables against statutory schemas, 0-byte write corruptions, table row dropouts, and `NaN`/`Inf` numerical drifts.
   - Mathematically enforces $G = 1$ in the composite objective $s = 0.4p + 0.6G \cdot O'$, completely preventing zero-score forfeits.

---

## 2. Multi-Disciplinary Closed-Form Engineering Solvers

Embedded Python verification engines ensure zero-token, exact IEEE-754 precision compliance:
- **Structural (AISC 360-16 & ASCE 7-16)**: Compact W-beam flexural capacity ($\phi M_n$) and Velocity Wind Pressure ($q_z$).
- **Electrical (NFPA 70 / NEC 2023)**: Balanced 3-phase feeder voltage drop ($\le 3.0\%$) and ampacity de-rating (Table 310.15).
- **Geotechnical (Terzaghi 1D)**: Piecewise primary consolidation settlement across normally and overconsolidated clay strata.
- **Mechanical / Hydraulics (Darcy-Weisbach & ASHRAE)**: Pipe head-loss and chilled-water velocity boundary compliance ($2.0 \sim 10.0\text{ fps}$).
- **Computational Geometry (3D AABB)**: Zero-clash spatial interference guarantees.

---

## 3. Repository Structure

```
.
├── submission.yaml               # PLE Benchmark official submission configuration
├── serve.py                      # PLE Protocol v1 WebSocket server
├── core/
│   ├── revision_graph.py         # Multi-Modal Revision Graph DAG Parser
│   ├── engineering_solvers.py    # Closed-form physics and code-clause solvers
│   ├── mcp_snapshot.py           # Baseline snapshot and dynamic MCP tool registry
│   └── feasibility_gate.py       # Hard-constraint feasibility gate (G = 1)
└── artifacts/                    # Evaluation artifacts directory
```

---

## 4. Local Verification & Reproducibility

```bash
# 1. Install Harbor and kit
uv tool install harbor==0.20.0 --with websockets

# 2. Run kit smoke test and protocol validation
uv run python -m kit check .

# 3. Evaluate dev tasks
uv run python eval/run.py . --tasks data-center-site-model
```

---

## 5. License
Licensed under the Apache License, Version 2.0.
