"""
Hard-Constraint Pre-Submission Feasibility Gating (G = 1 Enforcement & PE Auditor)
Audits candidate deliverables against statutory schemas, NaN propagation, and register integrity.
"""
import re
import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple

from core.mcp_snapshot import WorkspaceSnapshot

class FeasibilityAuditReport:
    def __init__(self, passed: bool, errors: List[str], warnings: List[str]):
        self.passed = passed
        self.errors = errors
        self.warnings = warnings

    @property
    def G_value(self) -> int:
        return 1 if self.passed else 0

class PreSubmissionFeasibilityGate:
    def __init__(self, workdir: Path, instruction: str):
        self.workdir = Path(workdir)
        self.instruction = instruction

    def audit(self) -> FeasibilityAuditReport:
        errors = []
        warnings = []

        # 1. Inspect all created/modified deliverables
        deliverables = WorkspaceSnapshot.get_created_deliverables(self.workdir)
        if not deliverables:
            errors.append("[FATAL] Zero deliverables generated. $G$ forfeited to 0.")
            return FeasibilityAuditReport(passed=False, errors=errors, warnings=warnings)

        # 2. Check for 0-Byte or Corrupted Writes
        for d in deliverables:
            if d.stat().st_size == 0:
                errors.append(f"[F2 Corruption] Deliverable is 0-bytes: {d.name}")

        # 3. Deep Schema & Content Integrity Checks
        for d in deliverables:
            suffix = d.suffix.lower()

            # CSV / Tabular checks (NaN / Inf / Row completeness)
            if suffix in ['.csv', '.tsv']:
                try:
                    with open(d, 'r', encoding='utf-8', errors='ignore') as f:
                        reader = csv.reader(f)
                        rows = list(reader)
                        if len(rows) < 2:
                            errors.append(f"[F2 Register] Tabular file has fewer than 2 rows (missing data): {d.name}")
                        for r_idx, row in enumerate(rows):
                            for c in row:
                                if c.strip().lower() in ['nan', 'inf', '-inf', '#null!', '#value!']:
                                    errors.append(f"[F3 Numeric] Unresolved {c} cell in {d.name} at row {r_idx}")
                except Exception as ex:
                    errors.append(f"[F2 Format] CSV Read Failure on {d.name}: {str(ex)}")

            # BIM / IFC4 Header Check
            elif suffix == '.ifc':
                content_prefix = d.read_text(encoding='utf-8', errors='ignore')[:300]
                if "ISO-10303-21;" not in content_prefix or "FILE_SCHEMA(('IFC4'));" not in content_prefix:
                    errors.append(f"[F1 Schema] Invalid IFC4 Header structure in {d.name}")

            # PDF Header Check
            elif suffix == '.pdf':
                with open(d, 'rb') as f:
                    header = f.read(5)
                    if header != b'%PDF-':
                        errors.append(f"[F2 Schema] Invalid PDF Magic Bytes in {d.name}")

        # 4. Mandatory Deliverable Mapping from Instruction
        lower_inst = self.instruction.lower()
        if "register" in lower_inst or "schedule" in lower_inst:
            has_table = any(d.suffix.lower() in ['.csv', '.xlsx', '.tsv'] for d in deliverables)
            if not has_table:
                errors.append("[F2 Missing] Task requested a register/schedule, but no tabular deliverable found.")

        if "memo" in lower_inst or "report" in lower_inst or "summary" in lower_inst:
            has_doc = any(d.suffix.lower() in ['.md', '.docx', '.pdf', '.txt'] for d in deliverables)
            if not has_doc:
                errors.append("[F2 Missing] Task requested a memo/report, but no textual document found.")

        passed = (len(errors) == 0)
        return FeasibilityAuditReport(passed=passed, errors=errors, warnings=warnings)
