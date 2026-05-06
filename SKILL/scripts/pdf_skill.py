#!/usr/bin/env python3
"""Dedicated PDF skill for advanced text extraction, table detection, and metadata analysis."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from log_action import append_action
except Exception:  # pragma: no cover
    append_action = None


def missing(module: str, package: str) -> dict[str, Any]:
    return {
        "ok": False,
        "missing_dependency": module,
        "install": f"Install {package} from SKILL/requirements.txt.",
    }


def extract_with_pypdf(path: Path, include_metadata: bool = True) -> dict[str, Any]:
    """Extract text and metadata using pypdf."""
    try:
        from pypdf import PdfReader
    except ImportError:
        return missing("pypdf", "pypdf")

    try:
        reader = PdfReader(str(path))
    except Exception as e:
        return {"ok": False, "error": "pdf_read_error", "details": str(e)}

    pages_data = []
    full_text = []

    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        full_text.append(text)
        pages_data.append({
            "page": page_num,
            "text": text,
            "text_length": len(text),
        })

    result = {
        "ok": True,
        "engine": "pypdf",
        "pages": len(reader.pages),
        "pages_data": pages_data,
        "full_text": "\n".join(full_text),
    }

    if include_metadata and reader.metadata:
        result["metadata"] = {str(k): str(v) for k, v in reader.metadata.items()}

    return result


def extract_with_pdfplumber(path: Path, extract_tables: bool = True) -> dict[str, Any]:
    """Extract text and tables using pdfplumber for layout-aware extraction."""
    try:
        import pdfplumber
    except ImportError:
        return missing("pdfplumber", "pdfplumber")

    try:
        pdf = pdfplumber.open(str(path))
    except Exception as e:
        return {"ok": False, "error": "pdf_read_error", "details": str(e)}

    pages_data = []
    full_text = []

    for page_num, page in enumerate(pdf.pages, start=1):
        text = page.extract_text() or ""
        full_text.append(text)
        page_info = {
            "page": page_num,
            "text": text,
            "text_length": len(text),
            "width": page.width,
            "height": page.height,
        }

        if extract_tables:
            try:
                tables = page.extract_tables()
                if tables:
                    page_info["tables"] = [
                        {"rows": len(t), "columns": len(t[0]) if t else 0, "data": t[:5]}
                        for t in tables
                    ]
            except Exception:
                pass

        pages_data.append(page_info)

    pdf.close()

    result = {
        "ok": True,
        "engine": "pdfplumber",
        "pages": len(pdf.pages),
        "pages_data": pages_data,
        "full_text": "\n".join(full_text),
    }

    return result


def analyze_pdf(path: Path) -> dict[str, Any]:
    """Comprehensive PDF analysis using best available engine."""
    if not path.exists():
        return {"ok": False, "error": "file_not_found", "path": str(path)}

    # Try pdfplumber first for layout-aware extraction
    result = extract_with_pdfplumber(path, extract_tables=True)
    if result.get("ok"):
        result["path"] = str(path)
        return result

    # Fall back to pypdf
    if result.get("missing_dependency") == "pdfplumber":
        result = extract_with_pypdf(path, include_metadata=True)
        if result.get("ok"):
            result["path"] = str(path)
            return result

    # Both failed
    return {"ok": False, "error": "no_pdf_engine", "details": "Install pypdf or pdfplumber"}


def to_markdown(result: dict[str, Any]) -> str:
    """Convert result to markdown format."""
    lines = [f"# PDF Analysis: {result.get('path', '')}", ""]

    # Metadata
    if "metadata" in result:
        lines.extend(["## Metadata", ""])
        for key, value in result["metadata"].items():
            lines.append(f"- {key}: {value}")
        lines.append("")

    # Summary
    lines.extend([
        "## Summary",
        f"- Engine: {result.get('engine', 'unknown')}",
        f"- Pages: {result.get('pages', 0)}",
        "",
    ])

    # Pages overview
    if "pages_data" in result:
        lines.extend(["## Pages Overview", ""])
        for page_info in result["pages_data"][:10]:
            lines.append(f"### Page {page_info['page']}")
            lines.append(f"- Text length: {page_info.get('text_length', 0)} characters")
            if "tables" in page_info:
                lines.append(f"- Tables: {len(page_info['tables'])}")
            if "width" in page_info:
                lines.append(f"- Size: {page_info['width']} x {page_info['height']}")
            lines.append("")

    # Full text (truncated for markdown)
    if "full_text" in result:
        lines.extend(["## Extracted Text (first 5000 chars)", ""])
        lines.append("```")
        lines.append(result["full_text"][:5000])
        lines.append("```")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Advanced PDF extraction and analysis.")
    parser.add_argument("path")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    parser.add_argument("--engine", choices=["auto", "pypdf", "pdfplumber"], default="auto")
    parser.add_argument("--no-tables", action="store_true", help="Skip table extraction")
    parser.add_argument("--no-log", action="store_true")
    args = parser.parse_args()

    path = Path(args.path)

    if args.engine == "pypdf":
        result = extract_with_pypdf(path, include_metadata=True)
    elif args.engine == "pdfplumber":
        result = extract_with_pdfplumber(path, extract_tables=not args.no_tables)
    else:
        result = analyze_pdf(path)

    result["path"] = str(path)

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    else:
        print(to_markdown(result))

    if append_action and not args.no_log:
        append_action("agent", "pdf-skill", f"{args.path}: ok={result.get('ok')}")

    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
