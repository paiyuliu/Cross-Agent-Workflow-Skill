# Document Extraction Guide

Comprehensive reference for extracting content from Office and PDF documents using the cross-agent workflow framework.

## Overview

This guide covers three extraction approaches:
1. **Quick inspection** - Get document structure and summary
2. **Content extraction** - Extract full text, tables, and metadata
3. **Batch processing** - Process multiple files with consistent output

## File Type Support Matrix

| Format | Inspect | Extract | Tables | Metadata | Edit |
|--------|---------|---------|--------|----------|------|
| `.pdf` | ✓ | ✓ | ✓ | ✓ | Limited |
| `.xlsx` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `.docx` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `.pptx` | ✓ | ✓ | ✗ | ✓ | ✓ |

## Quick Inspection

Use `doc_inspect.py` for a fast overview before extracting:

```bash
# Get markdown summary (fastest)
python SKILL/scripts/doc_inspect.py "report.pdf" --format markdown

# Get JSON structure
python SKILL/scripts/doc_inspect.py "data.xlsx" --format json

# Get summary of a presentation
python SKILL/scripts/doc_inspect.py "slides.pptx" --format markdown
```

**Output characteristics:**
- Markdown: Human-readable, section headers, key statistics
- JSON: Structured, scriptable, contains metadata

**When to use:**
- Understand file structure before extracting
- Quick page/sheet/slide count
- Check if file is readable
- Verify extraction method needed

## Content Extraction

Use `doc_extract.py` for complete content extraction:

```bash
# Full PDF extraction with tables
python SKILL/scripts/doc_extract.py "document.pdf" --format markdown --max-chars 50000

# Excel with all rows and columns
python SKILL/scripts/doc_extract.py "spreadsheet.xlsx" --format json

# Word document with formatting preserved
python SKILL/scripts/doc_extract.py "report.docx" --format markdown

# Extract only specific worksheet
python SKILL/scripts/doc_extract.py "data.xlsx" --sheet "Sales_Q1" --format csv
```

**Common parameters:**
- `--format` - Output format (markdown, json, csv)
- `--max-chars` - Limit output size (useful for large PDFs)
- `--sheet` - For XLSX, specify which sheet to extract
- `--slides` - For PPTX, extract specific slides (e.g., "1,2,3")

## Advanced PDF Operations

Use `pdf_skill.py` for layout-aware and table-aware extraction:

```bash
# Automatic engine selection with table detection
python SKILL/scripts/pdf_skill.py "report.pdf" --format json

# Force pdfplumber for layout preservation
python SKILL/scripts/pdf_skill.py "form.pdf" --format markdown --engine pdfplumber

# Use pypdf for faster extraction
python SKILL/scripts/pdf_skill.py "large.pdf" --format json --engine pypdf --no-tables

# Detailed page analysis
python SKILL/scripts/pdf_skill.py "document.pdf" --analyze
```

**Engine comparison:**
- `pdfplumber` - Best for layout, tables, and form extraction; slower on large files
- `pypdf` - Faster for text extraction; less layout awareness
- `auto` - Recommended; uses pdfplumber if available, falls back to pypdf

**Use pdfplumber when:**
- Extracting from forms or structured layouts
- Tables are important
- Preserving column alignment matters
- Page-specific analysis needed

**Use pypdf when:**
- Speed is important
- File is very large (>500 pages)
- Simple text extraction suffices
- Tables are not critical

## Batch Processing

Use `batch_extractor.py` to process multiple documents with consistent output:

```bash
# Extract all PDFs and Excel files
python SKILL/scripts/batch_extractor.py --files "*.pdf" "*.xlsx" --output extracted/

# Process specific files with JSON output
python SKILL/scripts/batch_extractor.py --files report.pdf data.xlsx summary.docx --format json

# Extract with character limit per file
python SKILL/scripts/batch_extractor.py --files "reports/*.pdf" --max-chars 30000 --output results/

# Check dependencies before batch processing
python SKILL/scripts/batch_extractor.py --check-deps
```

**Batch features:**
- Automatic format detection by file extension
- Consistent JSON or Markdown output
- Character limit per file to manage output size
- Error handling and status reporting
- Extensible for custom processing logic

**Output structure (JSON):**
```json
[
  {
    "file": "report.pdf",
    "type": "pdf",
    "status": "success",
    "pages": [
      {"page": 1, "text": "...content..."},
      {"page": 2, "text": "...content..."}
    ]
  },
  {
    "file": "data.xlsx",
    "type": "xlsx",
    "status": "success",
    "sheets": {
      "Sheet1": ["Row 1 | content", "Row 2 | content"],
      "Sheet2": [...]
    }
  }
]
```

## Dependency Management

### Minimal Installation (Core)
```bash
pip install python-docx python-pptx openpyxl pypdf pdfplumber
```

### Full Installation (All features)
```bash
pip install -r SKILL/requirements.txt
```

### Checking Available Libraries
```bash
python SKILL/scripts/batch_extractor.py --check-deps
```

### Per-Format Installation
- PDF only: `pip install pypdf pdfplumber`
- Excel only: `pip install openpyxl`
- Word only: `pip install python-docx`
- PowerPoint only: `pip install python-pptx`

## Troubleshooting

### "Module not found" errors
**Problem:** Script reports missing extraction library
**Solution:** Install via `pip install -r SKILL/requirements.txt` or install format-specific library

### PDF extracts no text
**Problem:** Scanned PDF or image-based PDF
**Cause:** OCR not supported in basic extraction
**Solution:** Use `pdf_skill.py` with `--engine pdfplumber` and check if text is embedded

### Excel extraction incomplete
**Problem:** Only first few rows extracted
**Cause:** Using `--max-chars` limit
**Solution:** Remove `--max-chars` or increase value; or extract specific sheets

### Large file timeout
**Problem:** Script times out on large PDFs
**Solution:** Use `--engine pypdf` instead of pdfplumber; or split file first

### Encoding issues with special characters
**Problem:** Characters show as squares or garbage
**Cause:** File encoding mismatch
**Solution:** Ensure Python runs with UTF-8: `PYTHONIOENCODING=utf-8 python script.py`

## Integration with Batch Workflow

### Step 1: Inspect all documents
```bash
python SKILL/scripts/doc_inspect.py "file1.pdf" --format markdown
python SKILL/scripts/doc_inspect.py "file2.xlsx" --format markdown
```

### Step 2: Check extraction compatibility
```bash
python SKILL/scripts/batch_extractor.py --files "*.pdf" "*.xlsx" --check-deps
```

### Step 3: Extract with appropriate settings
```bash
python SKILL/scripts/batch_extractor.py \
  --files "*.pdf" "*.xlsx" \
  --format json \
  --output extracted/ \
  --max-chars 50000
```

### Step 4: Process results programmatically
Load the JSON output and process per your requirements:
```python
import json
with open('extracted/extraction_results.json') as f:
    results = json.load(f)
    for item in results:
        if item['status'] == 'success':
            # Process extracted content
            print(f"Successfully extracted {item['file']}")
```

## Best Practices

1. **Always inspect before extracting** - Use `doc_inspect.py` first to understand structure
2. **Use appropriate engine** - Match PDF engine to file characteristics
3. **Respect character limits** - Use `--max-chars` for large batch jobs to manage output size
4. **Validate output** - Check extraction completeness before downstream processing
5. **Preserve originals** - Save extracts to new files; never modify source documents
6. **Handle failures gracefully** - Batch processing continues on file errors; check status field
7. **Version control** - Store extraction manifests and configurations in version control

## Advanced: Custom Batch Processing

Create a manifest file for complex batch operations:

```json
{
  "batch_name": "Q1_Report_Extraction",
  "description": "Extract all Q1 reports for processing",
  "files": [
    {
      "path": "reports/quarterly_q1.pdf",
      "type": "pdf",
      "engine": "pdfplumber",
      "max_pages": 10
    },
    {
      "path": "data/financial_q1.xlsx",
      "type": "xlsx",
      "sheets": ["Summary", "Details"],
      "max_chars": 50000
    }
  ],
  "output": "results/q1_extracted.json",
  "format": "json"
}
```

Then process with a custom script that reads the manifest and calls batch_extractor programmatically.
