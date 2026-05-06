# Office and PDF Reference

Use this reference when inspecting, extracting, creating, or modifying `.docx`, `.pptx`, `.xlsx`, or `.pdf` files.

## Tooling

- `.docx`: use `python-docx` for paragraphs, tables, styles, and safe copy-based edits.
- `.pptx`: use `python-pptx` for slide text, shapes, tables, speaker notes where supported, and safe copy-based edits.
- `.xlsx`: use `openpyxl` for worksheets, cells, formulas, styles, and workbook metadata.
- `.pdf`: use `pypdf` first for simple text and metadata; use `pdfplumber` when layout-sensitive extraction is needed. Use `scripts/pdf_skill.py` for advanced operations including page-level analysis, table detection, and engine selection.

## Operating Rules

- Inspect before editing; produce a concise structure summary first.
- Preserve original files by writing changed files to a new path unless the user explicitly approves overwrite.
- For Office files, prefer library APIs over raw OOXML unless the library cannot represent the required change.
- For PDF, default to read/extract. Treat editing, redaction, or conversion as separate tasks requiring explicit validation.
- When extraction is incomplete, report missing pages/slides/sheets and the extraction method used.

## Common Commands

```bash
# Quick inspection
python SKILL/scripts/doc_inspect.py "file.docx" --format markdown
python SKILL/scripts/doc_inspect.py "file.pdf" --format markdown

# Fuller extraction
python SKILL/scripts/doc_extract.py "file.pptx" --format json --max-chars 50000
python SKILL/scripts/doc_extract.py "file.xlsx" --format markdown
python SKILL/scripts/doc_extract.py "file.pdf" --format markdown --max-chars 30000

# Advanced PDF operations (layout-aware, table detection, page analysis)
python SKILL/scripts/pdf_skill.py "file.pdf" --format json
python SKILL/scripts/pdf_skill.py "file.pdf" --format markdown --engine pdfplumber
python SKILL/scripts/pdf_skill.py "file.pdf" --format json --engine pypdf --no-tables
```

## Expected Failure Handling

- Missing dependency: install `requirements.txt` or only use formats backed by installed libraries.
- Encrypted or corrupted file: stop and report the exact file and library error.
- Scanned PDF: report that OCR is required; do not invent text.
- Huge workbook or deck: summarize structure first, then ask for target sheets/slides if needed.
