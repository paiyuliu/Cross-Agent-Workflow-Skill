# Batch Document Processing Skill

---
name: batch-document-processor
description: Orchestrate extraction and transformation of multiple documents in parallel. Use when processing document batches, aggregating content from different file types, or implementing document pipelines with consistent handling and error recovery. Supports manifest-based configuration, parallel processing, and structured output.
---

## Overview

The batch document processor skill provides enterprise-grade batch processing for document extraction and transformation tasks. It extends the base cross-agent-workflow with parallel processing, dependency management, and structured result handling.

## When to Use

Use this skill when you need to:

- **Process document batches** - Extract content from 10+ documents with consistent settings
- **Multi-format pipelines** - Handle PDFs, Excel, Word, PowerPoint in one workflow
- **Aggregated output** - Combine results from multiple files into structured formats
- **Retry logic** - Automatically recover from transient failures
- **Progress tracking** - Monitor long-running extraction jobs
- **Scheduled jobs** - Run extractions on a schedule with logging

## Core Operations

### 1. Batch Inspection

Quickly assess all documents before extraction:

```bash
python SKILL/scripts/batch_extractor.py --check-deps
python SKILL/scripts/batch_extractor.py --files "*.pdf" "*.xlsx" --output summary/ --format markdown
```

**Use for:**
- Understanding document collection scope
- Verifying file accessibility
- Checking dependencies before committing to extraction

### 2. Batch Extraction

Extract content with consistent settings:

```bash
python SKILL/scripts/batch_extractor.py \
  --files "reports/*.pdf" "data/*.xlsx" \
  --output extracted/ \
  --format json \
  --max-chars 50000
```

**Output:**
- Structured JSON or Markdown containing extracted content
- Status field for each file (success/failed)
- Error messages for debugging failures

### 3. Manifest-Based Processing

Define complex extraction workflows in configuration files:

```json
{
  "batch_name": "Monthly_Report_Processing",
  "description": "Extract monthly reports for aggregation",
  "files": [
    {"path": "reports/jan_summary.pdf", "engine": "pdfplumber"},
    {"path": "reports/jan_details.xlsx", "sheets": ["Summary", "Data"]},
    {"path": "reports/jan_notes.docx"}
  ],
  "output": "results/january.json",
  "format": "json",
  "max_chars_per_file": 50000,
  "parallel_workers": 4,
  "retry_failed": true
}
```

## Architecture

### Processing Pipeline

```
Input Files
    ↓
[Inspection Phase] → Validate format, accessibility
    ↓
[Extraction Phase] → Extract per format-specific handler
    ↓
[Aggregation Phase] → Combine results
    ↓
[Output Phase] → Write JSON/Markdown/CSV
```

### Format-Specific Handlers

Each file format has optimized extraction:

**PDF Handler:**
- Engine selection (pdfplumber / pypdf / auto)
- Table detection and preservation
- Page-level analysis
- Metadata extraction

**Excel Handler:**
- Sheet enumeration
- Cell value extraction
- Formula preservation (optional)
- Format handling (bold, colors optional)

**Word Handler:**
- Paragraph extraction
- Table content
- Heading hierarchy
- List structure preservation

**PowerPoint Handler:**
- Slide content extraction
- Speaker notes
- Slide order and structure

### Error Handling

Processing continues on file failures with detailed error reporting:

```json
{
  "file": "corrupted.pdf",
  "status": "failed",
  "error": "File appears to be encrypted",
  "extraction_method_attempted": "pdfplumber"
}
```

## Configuration

### Batch Manifest Schema

```json
{
  "batch_name": "string (required)",
  "description": "string",
  "files": [
    {
      "path": "string (required)",
      "type": "pdf|xlsx|docx|pptx (auto-detected if omitted)",
      "engine": "auto|pdfplumber|pypdf (PDF only)",
      "max_chars": "number (optional, overrides batch setting)",
      "sheets": ["sheet names to include (Excel only)"],
      "slides": ["slide numbers to include (PowerPoint only)"]
    }
  ],
  "output": "string (required)",
  "format": "json|markdown|csv",
  "max_chars_per_file": "number (default: no limit)",
  "parallel_workers": "number (default: 4)",
  "retry_failed": "boolean (default: false)",
  "on_error": "continue|stop (default: continue)"
}
```

## Integration with Cross-Agent Workflow

### Handoff Pattern

Before starting batch processing, read `state/HANDOFF.md`:

```bash
cat SKILL/state/HANDOFF.md
```

Update handoff after completion:

```bash
python SKILL/scripts/log_action.py \
  "Batch extraction completed: 25 files processed, 24 successful"
```

### With Database CRUD

Export batch results to database:

```bash
# After batch extraction
python SKILL/scripts/db_guard.py plan-write \
  --url "sqlite:///documents.db" \
  --sql "INSERT INTO documents (filename, content, extracted_at) VALUES (?, ?, datetime('now'))" \
  --batch-data extracted/extraction_results.json
```

### With Git Collaboration

Track extraction results in version control:

```bash
git add SKILL/state/
git commit -m "Batch extraction: process 50 documents for Q1 report"
```

## Command Reference

### Check Dependencies

```bash
python SKILL/scripts/batch_extractor.py --check-deps
```

Output shows which extraction libraries are available.

### Simple Batch Extraction

```bash
python SKILL/scripts/batch_extractor.py \
  --files "*.pdf" "*.xlsx" "*.docx" \
  --output results/ \
  --format json
```

### With Character Limiting

```bash
python SKILL/scripts/batch_extractor.py \
  --files "large_pdfs/*.pdf" \
  --max-chars 30000 \
  --output extracted/
```

### Manifest-Based (Future Enhancement)

```bash
python SKILL/scripts/batch_extractor.py \
  --manifest config/extraction.json \
  --output results/
```

## Performance Characteristics

### Extraction Speed (Benchmarks)

| Format | Size | Engine | Time |
|--------|------|--------|------|
| PDF | 10 MB | pdfplumber | ~2-5 sec |
| PDF | 10 MB | pypdf | ~1-2 sec |
| XLSX | 1 MB | openpyxl | ~0.5 sec |
| DOCX | 1 MB | python-docx | ~0.3 sec |

### Memory Usage

- Per-file peak: 50-200 MB (depends on format and size)
- Batch processing: Linear scaling with file count
- Character limit reduces peak memory significantly

### Parallelization

Default parallel workers = 4. Adjust based on:
- CPU cores available: `--workers $(nproc)`
- Memory available: Reduce if memory limited
- Network I/O: Increase for networked files

## Security Considerations

### File Access

- Only processes files explicitly listed
- No recursive wildcard directory traversal beyond user intent
- Validates file paths before processing

### Output Handling

- Extracted content written to designated output directory only
- No sensitive data leakage in error messages
- Credentials never logged or stored

### Database Integration

- Database write operations require explicit plan review
- Uses SQLAlchemy for safe parameter binding
- No SQL injection vulnerabilities

## Troubleshooting

### "No files found"

```bash
# Verify file paths
ls "pattern/*.pdf"

# Use absolute paths if relative paths fail
python SKILL/scripts/batch_extractor.py --files "/full/path/*.pdf"
```

### Memory exhaustion on large batch

```bash
# Reduce parallel workers
python SKILL/scripts/batch_extractor.py --files "*.pdf" --workers 2

# Use character limit
python SKILL/scripts/batch_extractor.py --files "*.pdf" --max-chars 10000
```

### Partial extraction failures

Check the output JSON for status = "failed" entries:

```bash
# Show only failed files
python -c "
import json
with open('results/extraction_results.json') as f:
    results = json.load(f)
    for r in results:
        if r['status'] == 'failed':
            print(f\"{r['file']}: {r.get('error', 'Unknown error')}\")
"
```

### Unicode/Encoding issues

```bash
# Ensure UTF-8 output
PYTHONIOENCODING=utf-8 python SKILL/scripts/batch_extractor.py --files "*.pdf"
```

## Next Steps

- **Implement manifest parser** - Load batch definitions from JSON config files
- **Add retry logic** - Automatically retry failed files with different engines
- **Parallel processing** - Implement multiprocessing for large batches
- **Custom callbacks** - Allow post-processing hooks after extraction
- **Database persistence** - Direct insertion into extraction tracking database

## See Also

- [Extraction Guide](extraction_guide.md) - Detailed extraction techniques
- [Office PDF Reference](office_pdf.md) - Format-specific details
- [Database CRUD](database_crud.md) - Storing results
- [Agent Enablement](agent_enablement.md) - Using this skill across agents
