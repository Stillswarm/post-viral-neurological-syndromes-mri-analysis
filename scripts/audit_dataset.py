#!/usr/bin/env python3
"""Create a privacy-preserving structural audit of the Dryad workbook."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


def normalized(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())


def is_empty(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def audit_sheet(sheet: Any) -> dict[str, Any]:
    rows = [tuple(row) for row in sheet.iter_rows(values_only=True)]
    populated = [row for row in rows if any(not is_empty(value) for value in row)]
    if not populated:
        return {"sheet": sheet.title, "data_rows": 0, "columns": []}

    header = populated[0]
    headers = [str(value).strip() if not is_empty(value) else f"unnamed_{i + 1}"
               for i, value in enumerate(header)]
    records = populated[1:]
    width = max(len(headers), max((len(row) for row in records), default=0))
    headers.extend(f"unnamed_{i + 1}" for i in range(len(headers), width))
    padded = [tuple(row) + (None,) * (width - len(row)) for row in records]

    fields = []
    for index, name in enumerate(headers):
        values = [row[index] for row in padded]
        present = [value for value in values if not is_empty(value)]
        numeric = [float(value) for value in present
                   if isinstance(value, (int, float)) and not isinstance(value, bool)
                   and math.isfinite(float(value))]
        field = {
            "name": name,
            "nonempty": len(present),
            "missing": len(values) - len(present),
            "missing_fraction": round((len(values) - len(present)) / len(values), 4)
            if values else None,
            "unique_nonempty": len({str(value) for value in present}),
            "numeric_count": len(numeric),
        }
        if numeric:
            field["numeric_min"] = min(numeric)
            field["numeric_max"] = max(numeric)

        key = normalized(name)
        if "moca" in key:
            scores = [float(value) for value in present
                      if isinstance(value, (int, float)) and not isinstance(value, bool)]
            field["moca_below_26_count"] = sum(score < 26 for score in scores)
            field["moca_at_least_26_count"] = sum(score >= 26 for score in scores)
            field["moca_numeric_count"] = len(scores)
        if any(token in key for token in ("group", "cohort")):
            field["category_counts"] = dict(sorted(Counter(str(v) for v in present).items()))
        if any(token in key for token in ("subjectid", "participantid", "patientid", "recordid")):
            field["duplicate_nonempty_count"] = len(present) - len({str(v) for v in present})
        fields.append(field)

    populated_records = [row for row in padded if any(not is_empty(v) for v in row)]
    duplicate_rows = len(populated_records) - len({tuple(map(str, row)) for row in populated_records})
    return {
        "sheet": sheet.title,
        "data_rows": len(populated_records),
        "columns": fields,
        "duplicate_full_rows": duplicate_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path, help="Local Dryad_final.xlsx path")
    parser.add_argument(
        "--output", type=Path,
        default=Path("reports/generated/dataset_audit.json"),
        help="Output JSON path (default: reports/generated/dataset_audit.json)",
    )
    args = parser.parse_args()
    if not args.workbook.is_file():
        parser.error(f"Workbook not found: {args.workbook}")

    workbook = load_workbook(args.workbook, read_only=True, data_only=True)
    report = {
        "source_doi": "10.5061/dryad.kkwh70s9g",
        "workbook_name": args.workbook.name,
        "file_size_bytes": args.workbook.stat().st_size,
        "sha256": sha256(args.workbook),
        "sheets": [audit_sheet(sheet) for sheet in workbook.worksheets],
        "privacy_note": "Aggregate schema/statistics only; no participant-level values are written.",
    }
    workbook.close()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(f"Audited {len(report['sheets'])} sheets; report: {args.output}")
    for sheet in report["sheets"]:
        print(f"- {sheet['sheet']}: {sheet['data_rows']} data rows, {len(sheet['columns'])} columns")


if __name__ == "__main__":
    main()
