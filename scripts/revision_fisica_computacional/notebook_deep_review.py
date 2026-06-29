from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

MARKER = "MARIO_FISICA_COMPUTACIONAL_DEEP_NOTEBOOK_REVIEW_V1"
RESOURCE_ID = "MCP_SCIKI_N8N_MARIO_COMPUTACIONAL_REVIEW_RESOURCE_V1"
ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "build" / "revision_fisica_computacional"

NOTEBOOK_PATHS = [
    "trabajos/laboratorio/COMPU_SISTEMA_SOLAR.ipynb",
    "trabajos/laboratorio/ISING.ipynb",
    "trabajos/laboratorio/Jup_voluntario_hopfield_mariohc.ipynb",
    "trabajos/laboratorio/Jup_voluntario_shrodinger_mariohc.ipynb",
]

IMPORT_RE = re.compile(r"^\s*(import\s+\S+|from\s+\S+\s+import\s+)")
SHELL_RE = re.compile(r"^\s*!|subprocess|os\.system")
FILE_IO_RE = re.compile(
    r"\.(dat|txt|csv|png|gif|mp4|cpp|npy)|open\(|loadtxt|read_csv|savetxt|savefig|imread|Video|Image"
)
EXTERNAL_DEP_RE = re.compile(r"pip install|apt-get|conda install|wget|curl")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+")
RICH_OUTPUT_KEYS = {
    "image/png",
    "image/jpeg",
    "video/mp4",
    "text/html",
    "application/vnd.jupyter.widget-view+json",
    "application/javascript",
}


def cell_source(cell: dict[str, Any]) -> str:
    source = cell.get("source", "")
    if isinstance(source, list):
        return "".join(str(part) for part in source)
    return str(source)


def unique_first(values: list[str], limit: int) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
        if len(result) >= limit:
            break
    return result


def output_has_rich_data(output: dict[str, Any]) -> bool:
    data = output.get("data", {})
    if isinstance(data, dict) and any(key in data for key in RICH_OUTPUT_KEYS):
        return True
    return output.get("output_type") == "display_data"


def summarize_notebook(path_text: str) -> dict[str, Any]:
    path = ROOT / path_text
    if not path.exists():
        return {
            "path": path_text,
            "status": "missing_file",
            "review_state": "BLOCKED",
            "risks": ["missing notebook file"],
        }

    raw = path.read_bytes()
    if not raw.strip():
        return {
            "path": path_text,
            "status": "empty_file",
            "review_state": "BLOCKED",
            "bytes": 0,
            "cells": 0,
            "markdown_cells": 0,
            "code_cells": 0,
            "headings": [],
            "imports": [],
            "error_outputs": 0,
            "executed_code_cells": 0,
            "empty_code_cells": 0,
            "long_code_cells": [],
            "rich_output_cells": 0,
            "shell_commands": [],
            "file_io_mentions": [],
            "external_deps": [],
            "source_hash": None,
            "risks": ["empty notebook file"],
        }

    try:
        notebook = json.loads(raw.decode("utf-8"))
    except Exception as exc:  # pragma: no cover - CI diagnostic path.
        return {
            "path": path_text,
            "status": "parse_error",
            "review_state": "BLOCKED",
            "bytes": len(raw),
            "error": str(exc),
            "risks": ["notebook json parse error"],
        }

    cells = list(notebook.get("cells", []))
    markdown_cells = [cell for cell in cells if cell.get("cell_type") == "markdown"]
    code_cells = [cell for cell in cells if cell.get("cell_type") == "code"]

    headings: list[str] = []
    imports: list[str] = []
    shell_commands: list[str] = []
    file_io_mentions: list[str] = []
    external_deps: list[str] = []
    error_outputs = 0
    executed_code_cells = 0
    empty_code_cells = 0
    rich_output_cells = 0
    max_source_lines = 0
    long_code_cells: list[int] = []
    source_digest_parts: list[str] = []

    for cell_index, cell in enumerate(cells, start=1):
        source = cell_source(cell)
        source_digest_parts.append(f"{cell.get('cell_type')}\0{source}")
        line_count = len(source.splitlines())
        max_source_lines = max(max_source_lines, line_count)

        if cell.get("cell_type") == "markdown":
            for line in source.splitlines():
                if HEADING_RE.match(line):
                    headings.append(line.strip())
            continue

        if cell.get("cell_type") != "code":
            continue

        if not source.strip():
            empty_code_cells += 1
        if line_count > 80:
            long_code_cells.append(cell_index)
        if cell.get("execution_count") is not None:
            executed_code_cells += 1

        for line in source.splitlines():
            text = line.strip()
            if IMPORT_RE.match(text):
                imports.append(text)
            if SHELL_RE.search(text):
                shell_commands.append(text)
            if FILE_IO_RE.search(text):
                file_io_mentions.append(text)
            if EXTERNAL_DEP_RE.search(text):
                external_deps.append(text)

        cell_has_rich_output = False
        for output in cell.get("outputs", []):
            if output.get("output_type") == "error":
                error_outputs += 1
            if output_has_rich_data(output):
                cell_has_rich_output = True
        if cell_has_rich_output:
            rich_output_cells += 1

    risks: list[str] = []
    if len(raw) > 25_000_000:
        risks.append("very large notebook likely contains embedded outputs")
    if error_outputs:
        risks.append("saved error outputs present")
    if empty_code_cells:
        risks.append("empty code cells present")
    if long_code_cells:
        risks.append("long code cells should be split or moved to scripts")
    if executed_code_cells != len(code_cells):
        risks.append("not all code cells have execution_count")
    if shell_commands:
        risks.append("requires local shell execution")
    if file_io_mentions:
        risks.append("depends on generated files or media artifacts")
    if external_deps:
        risks.append("runtime dependency installation commands present")
    if rich_output_cells and len(raw) > 10_000_000:
        risks.append("rich outputs should be cleared or externalized before final archival")

    return {
        "path": path_text,
        "status": "parsed",
        "review_state": "NEEDS_REVISION" if risks else "READY_FOR_CONTENT_REVIEW",
        "bytes": len(raw),
        "cells": len(cells),
        "markdown_cells": len(markdown_cells),
        "code_cells": len(code_cells),
        "headings": unique_first(headings, 20),
        "imports": unique_first(imports, 25),
        "error_outputs": error_outputs,
        "executed_code_cells": executed_code_cells,
        "empty_code_cells": empty_code_cells,
        "long_code_cells": long_code_cells,
        "max_source_lines": max_source_lines,
        "rich_output_cells": rich_output_cells,
        "shell_commands": unique_first(shell_commands, 20),
        "file_io_mentions": unique_first(file_io_mentions, 30),
        "external_deps": unique_first(external_deps, 20),
        "source_hash": hashlib.sha256("".join(source_digest_parts).encode("utf-8")).hexdigest(),
        "risks": risks,
    }


def build_witness(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    blocked = [item for item in summaries if item.get("review_state") == "BLOCKED"]
    needs_revision = [item for item in summaries if item.get("review_state") == "NEEDS_REVISION"]
    ready = [item for item in summaries if item.get("review_state") == "READY_FOR_CONTENT_REVIEW"]
    return {
        "marker": MARKER,
        "resource_id": RESOURCE_ID,
        "resource_active": True,
        "upstream_repo": "marioehercue/Computacional_Mario",
        "contribution_repo": "jbermejovega/Computacional_Mario",
        "scope": "mario_fisica_computacional_notebook_by_notebook",
        "workflow": ".github/workflows/fisica-computacional-notebook-review.yml",
        "review_mode": "read_only_static_notebook_json_review",
        "code_execution_allowed": False,
        "notebook_count": len(summaries),
        "blocked_count": len(blocked),
        "needs_revision_count": len(needs_revision),
        "ready_count": len(ready),
        "invariants": {
            "mcp_resource_active": True,
            "sciki_map_active": True,
            "n8n_workflow_exported": True,
            "notebook_by_notebook": True,
            "no_notebook_code_execution": True,
            "replay_safe": True,
            "contents_read_only": True,
        },
        "notebooks": summaries,
    }


def write_markdown(witness: dict[str, Any]) -> None:
    lines = [
        f"# {MARKER}",
        "",
        "Generated witness for the MCP/SCIKI/N8N invariant review workflow.",
        "Notebook code is not executed by this script.",
        "",
        "| Notebook | State | Size MB | Cells | Markdown | Code | Risks |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in witness["notebooks"]:
        risks = "; ".join(item.get("risks", [])) or "none"
        risks = risks.replace("|", "/")
        lines.append(
            "| `{path}` | {state} | {size:.2f} | {cells} | {md} | {code} | {risks} |".format(
                path=item["path"],
                state=item.get("review_state", item.get("status")),
                size=item.get("bytes", 0) / 1_000_000,
                cells=item.get("cells", 0),
                md=item.get("markdown_cells", 0),
                code=item.get("code_cells", 0),
                risks=risks,
            )
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- blocked_count: {witness['blocked_count']}",
            f"- needs_revision_count: {witness['needs_revision_count']}",
            f"- ready_count: {witness['ready_count']}",
            "- resource_active: true",
            "- replay_safe: true",
        ]
    )
    (OUTPUT_DIR / "notebook-review-witness.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summaries = [summarize_notebook(path) for path in NOTEBOOK_PATHS]
    witness = build_witness(summaries)
    (OUTPUT_DIR / "notebook-review-witness.json").write_text(
        json.dumps(witness, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_markdown(witness)
    print(json.dumps(witness, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
