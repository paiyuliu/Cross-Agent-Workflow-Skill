# Document Extraction & Batch Processing Skills

---
name: doc-extraction-advanced
description: Advanced document extraction with format-specific handlers for PDF, Excel, Word, and PowerPoint. Use when extracting content from single or multiple documents, requiring layout-aware PDF extraction, table detection, or batch processing. Provides three extraction levels: quick inspection, full content extraction, and batch processing with consistent output.
---

---
name: batch-document-processor
description: Enterprise batch processing for document extraction and transformation. Use when processing 10+ documents, implementing document pipelines, or aggregating content from mixed file types. Supports manifest-based configuration, parallel processing, automatic retry, error recovery, and structured JSON/Markdown output.
---

## Core Capabilities

### Document Extraction

Three-tier extraction approach for different use cases:

**Tier 1: Quick Inspection**
- Purpose: Understand document structure before extraction
- Speed: <1 second per file
- Tools: `doc_inspect.py`
- Output: Markdown or JSON summary

**Tier 2: Content Extraction**
- Purpose: Extract full content with formatting
- Speed: 1-10 seconds per file (depends on size)
- Tools: `doc_extract.py`, `pdf_skill.py`
- Output: Markdown, JSON, or CSV

**Tier 3: Batch Processing**
- Purpose: Process multiple files with consistent settings
- Speed: Parallel processing, 1-5 seconds per file
- Tools: `batch_extractor.py`
- Output: JSON manifest with all results

### Format Support

| Format | Inspection | Extraction | Tables | Metadata | Edit |
|--------|-----------|-----------|--------|----------|------|
| **PDF** | ✓ | ✓ | ✓ | ✓ | Limited |
| **XLSX** | ✓ | ✓ | ✓ | ✓ | ✓ |
| **DOCX** | ✓ | ✓ | ✓ | ✓ | ✓ |
| **PPTX** | ✓ | ✓ | ✗ | ✓ | ✓ |

## PDF Extraction Features

### Engine Selection

**pdfplumber (layout-aware):**
- Best for: Forms, tables, position-sensitive extraction
- Advantages: Preserves layout, detects tables, page-specific analysis
- Tradeoff: Slower on large files (>500 pages)
- Use when: Structure and layout matter

**pypdf (fast):**
- Best for: Text extraction, large files
- Advantages: Fast, simple API, minimal dependencies
- Tradeoff: No layout preservation, limited table detection
- Use when: Speed and simplicity matter

**Automatic:**
- Uses pdfplumber if available
- Falls back to pypdf if needed
- Recommended for unknown files

### Table Detection

- Automatic table identification in pdfplumber mode
- Table extraction to JSON structure
- Handles multi-cell merges and complex layouts
- Fallback to text extraction if tables not detected

### Page Analysis

```bash
# Analyze page structure
python SKILL/scripts/pdf_skill.py document.pdf --analyze
```

Returns:
- Page count and dimensions
- Text blocks per page
- Table locations
- Image count
- Text orientation

## Batch Processing Pipeline

```
Input Files (*.pdf, *.xlsx, *.docx, *.pptx)
    ↓
[1. Dependency Check] ← Install missing libraries
    ↓
[2. File Validation] ← Verify accessibility
    ↓
[3. Format Detection] ← Determine extraction handler
    ↓
[4. Extraction] ← Extract per format (serial or parallel)
    ↓
[5. Error Handling] ← Log failures, continue on next
    ↓
[6. Aggregation] ← Combine all results
    ↓
Output (JSON or Markdown)
```

### Configuration

Manifest-based batch operations:

```json
{
  "batch_name": "Q1_Report_Extract",
  "description": "Extract quarterly reports",
  "files": [
    {
      "path": "reports/summary.pdf",
      "type": "pdf",
      "engine": "pdfplumber",
      "max_pages": 10
    },
    {
      "path": "reports/data.xlsx",
      "type": "xlsx",
      "sheets": ["Summary", "Details"]
    },
    {
      "path": "reports/notes.docx"
    }
  ],
  "output": "results/extracted.json",
  "format": "json",
  "max_chars_per_file": 50000,
  "parallel_workers": 4,
  "retry_failed": true
}
```

## Dependency Model

### Minimal (Core)
```bash
pip install openpyxl pypdf pdfplumber
```
Provides: PDF, Excel extraction (no Word, PowerPoint)

### Standard (Recommended)
```bash
pip install -r SKILL/requirements.txt
```
Provides: All formats + database support

### Full (All Extras)
```bash
pip install -r SKILL/requirements.txt -r SKILL/requirements-db.txt
```
Provides: All formats + all database drivers

## Usage Examples

### Single PDF Inspection
```bash
python SKILL/scripts/doc_inspect.py "report.pdf" --format markdown
```

### Excel Extraction with Sheet Filter
```bash
python SKILL/scripts/doc_extract.py "data.xlsx" --sheet "Sales_Q1" --format json
```

### Layout-Aware PDF Extraction
```bash
python SKILL/scripts/pdf_skill.py "form.pdf" --format markdown --engine pdfplumber
```

### Batch Extract All Files
```bash
python SKILL/scripts/batch_extractor.py \
  --files "*.pdf" "*.xlsx" "*.docx" \
  --output extracted/ \
  --format json \
  --max-chars 30000
```

### Dependency Check Before Batch
```bash
python SKILL/scripts/batch_extractor.py --check-deps
```

## Integration Points

### With Cross-Agent Workflow

1. **Handoff logging:**
```bash
python SKILL/scripts/log_action.py \
  "Extracted 25 documents: success rate 96%"
```

2. **State management:**
```bash
cat SKILL/state/HANDOFF.md  # Check current status
```

### With Database CRUD

```bash
# Extract then load into database
python SKILL/scripts/batch_extractor.py --files "*.pdf" --output results/

# Then use db_guard to insert
python SKILL/scripts/db_guard.py plan-write \
  --url "sqlite:///docs.db" \
  --sql "INSERT INTO documents (filename, content) VALUES (?, ?)"
```

### With Version Control

```bash
# Track extraction results
git add SKILL/state/ACTION_LOG.md
git commit -m "Batch extraction: 50 files processed for archival"
```

## Performance Notes

### Extraction Speed (Typical)
- PDF (pdfplumber): 2-5 sec / 10 MB
- PDF (pypdf): 1-2 sec / 10 MB
- Excel: 0.5 sec / 1 MB
- Word: 0.3 sec / 1 MB

### Memory Profile
- Per-file peak: 50-200 MB
- Batch parallel: Linear with worker count
- Mitigation: Use `--max-chars` to cap output size

### Scaling
- Parallel workers: Default 4 (adjust via config)
- Recommended: workers = min(cpu_count, 8)
- For memory-constrained: workers = 1-2

## Troubleshooting

**"Module not found"**
→ Install: `pip install -r SKILL/requirements.txt`

**"No text extracted from PDF"**
→ PDF is scanned/image-based; OCR needed (not supported)

**"Timeout on large batch"**
→ Use pypdf engine or reduce `--max-chars`

**"Character encoding issues"**
→ Run with: `PYTHONIOENCODING=utf-8 python script.py`

## See Also

- [Extraction Guide](extraction_guide.md) - Detailed extraction techniques
- [Batch Processing](batch_processing.md) - Enterprise batch patterns
- [Office PDF Reference](office_pdf.md) - Format-specific deep dives
- [Database CRUD](database_crud.md) - Storing extracted content
