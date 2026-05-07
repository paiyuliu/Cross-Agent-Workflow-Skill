#!/usr/bin/env python3
"""
Batch Document Extractor
========================

Extracts content from multiple document files (PDF, XLSX, DOCX, PPTX)
and produces structured output in JSON or Markdown format.

Usage:
    python batch_extractor.py --files "*.pdf" "*.xlsx" --output extracted/
    python batch_extractor.py --files "report.pdf" "data.xlsx" --format json --max-chars 50000
    python batch_extractor.py --batch-config extraction_manifest.json --output results/
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional


class BatchExtractor:
    """Extract content from multiple document types."""
    
    def __init__(self, output_dir: str = "extracted", format: str = "markdown"):
        self.output_dir = Path(output_dir)
        self.format = format
        self.format = format
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = []
        
    def check_dependencies(self) -> Dict[str, bool]:
        """Check which extraction libraries are available."""
        import importlib
        deps = {
            'openpyxl': 'Excel extraction',
            'pdfplumber': 'PDF extraction (primary)',
            'pypdf': 'PDF extraction (fallback)',
            'python-docx': 'DOCX extraction',
            'python-pptx': 'PPTX extraction',
        }
        available = {}
        for lib, desc in deps.items():
            module_name = lib.replace('-', '_')
            try:
                if importlib.util.find_spec(module_name):
                    available[lib] = True
                else:
                    available[lib] = False
            except Exception:
                available[lib] = False
        return available
    
    def extract_excel(self, file_path: str, max_chars: Optional[int] = None) -> Dict[str, Any]:
        """Extract content from XLSX file."""
        try:
            from openpyxl import load_workbook
        except ImportError:
            return {
                'file': file_path,
                'type': 'xlsx',
                'error': 'openpyxl not installed',
                'status': 'failed'
            }
        
        result = {
            'file': file_path,
            'type': 'xlsx',
            'sheets': {},
            'status': 'success'
        }
        
        try:
            wb = load_workbook(file_path, data_only=True)
            for sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
                rows = []
                char_count = 0
                
                for row in ws.iter_rows(values_only=True):
                    cells = [str(cell) if cell is not None else "" for cell in row]
                    if any(c.strip() for c in cells):
                        row_str = " | ".join(cells)
                        if max_chars and char_count + len(row_str) > max_chars:
                            break
                        rows.append(row_str)
                        char_count += len(row_str)
                
                result['sheets'][sheet_name] = rows
        except Exception as e:
            result['error'] = str(e)
            result['status'] = 'failed'
        
        return result
    
    def extract_pdf(self, file_path: str, max_chars: Optional[int] = None, engine: str = 'pdfplumber') -> Dict[str, Any]:
        """Extract content from PDF file."""
        result = {
            'file': file_path,
            'type': 'pdf',
            'pages': [],
            'status': 'success',
            'engine': engine
        }
        
        if engine == 'pdfplumber':
            try:
                import pdfplumber
            except ImportError:
                result['error'] = 'pdfplumber not installed'
                result['status'] = 'failed'
                return result
            
            try:
                with pdfplumber.open(file_path) as pdf:
                    char_count = 0
                    for page_num, page in enumerate(pdf.pages, 1):
                        text = page.extract_text() or ""
                        if max_chars and char_count + len(text) > max_chars:
                            text = text[:max(0, max_chars - char_count)]
                        
                        result['pages'].append({
                            'page': page_num,
                            'text': text[:1000] if text else ""
                        })
                        char_count += len(text)
                        if max_chars and char_count >= max_chars:
                            break
            except Exception as e:
                result['error'] = str(e)
                result['status'] = 'failed'
        else:
            try:
                import pypdf
            except ImportError:
                result['error'] = 'pypdf not installed'
                result['status'] = 'failed'
                return result
            
            try:
                with open(file_path, 'rb') as f:
                    pdf_reader = pypdf.PdfReader(f)
                    char_count = 0
                    for page_num, page in enumerate(pdf_reader.pages, 1):
                        text = page.extract_text() or ""
                        if max_chars and char_count + len(text) > max_chars:
                            text = text[:max(0, max_chars - char_count)]
                        
                        result['pages'].append({
                            'page': page_num,
                            'text': text[:1000] if text else ""
                        })
                        char_count += len(text)
                        if max_chars and char_count >= max_chars:
                            break
            except Exception as e:
                result['error'] = str(e)
                result['status'] = 'failed'
        
        return result
    
    def extract_docx(self, file_path: str) -> Dict[str, Any]:
        """Extract content from DOCX file."""
        try:
            from docx import Document
        except ImportError:
            return {
                'file': file_path,
                'type': 'docx',
                'error': 'python-docx not installed',
                'status': 'failed'
            }
        
        result = {
            'file': file_path,
            'type': 'docx',
            'paragraphs': [],
            'status': 'success'
        }
        
        try:
            doc = Document(file_path)
            for para in doc.paragraphs:
                if para.text.strip():
                    result['paragraphs'].append(para.text)
        except Exception as e:
            result['error'] = str(e)
            result['status'] = 'failed'
        
        return result
    
    def extract_file(self, file_path: str, max_chars: Optional[int] = None) -> Dict[str, Any]:
        """Extract content based on file type."""
        file_path = str(file_path)
        ext = Path(file_path).suffix.lower()
        
        if ext == '.xlsx':
            return self.extract_excel(file_path, max_chars)
        elif ext == '.pdf':
            return self.extract_pdf(file_path, max_chars, engine='pdfplumber')
        elif ext == '.docx':
            return self.extract_docx(file_path)
        else:
            return {
                'file': file_path,
                'error': f'Unsupported file type: {ext}',
                'status': 'failed'
            }
    
    def process_files(self, file_list: List[str], max_chars: Optional[int] = None) -> List[Dict[str, Any]]:
        """Process multiple files and return results."""
        results = []
        for file_path in file_list:
            if Path(file_path).exists():
                print(f"Extracting: {file_path}")
                result = self.extract_file(file_path, max_chars)
                results.append(result)
            else:
                print(f"File not found: {file_path}")
                results.append({
                    'file': file_path,
                    'error': 'File not found',
                    'status': 'failed'
                })
        
        self.results = results
        return results
    
    def save_results(self, output_file: Optional[str] = None) -> str:
        """Save extraction results to file."""
        if not output_file:
            output_file = self.output_dir / f"extraction_results.{self.format}"
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
        elif self.format == 'markdown':
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("# Batch Extraction Results\n\n")
                for result in self.results:
                    f.write(f"## {result.get('file', 'Unknown')}\n\n")
                    f.write(f"**Type:** {result.get('type', 'Unknown')}\n\n")
                    f.write(f"**Status:** {result.get('status', 'Unknown')}\n\n")
                    
                    if result.get('status') == 'failed':
                        f.write(f"**Error:** {result.get('error', 'Unknown error')}\n\n")
                    elif result.get('type') == 'xlsx':
                        for sheet, rows in result.get('sheets', {}).items():
                            f.write(f"### Sheet: {sheet}\n\n")
                            f.write("```\n")
                            for row in rows[:50]:
                                f.write(f"{row}\n")
                            if len(rows) > 50:
                                f.write(f"... ({len(rows) - 50} more rows)\n")
                            f.write("```\n\n")
                    elif result.get('type') == 'pdf':
                        for page in result.get('pages', [])[:5]:
                            f.write(f"### Page {page['page']}\n\n")
                            f.write(f"{page['text'][:500]}\n\n")
        
        return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Batch extract content from multiple document files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python batch_extractor.py --files "*.pdf" "*.xlsx" --output extracted/
    python batch_extractor.py --files report.pdf data.xlsx --format json
    python batch_extractor.py --check-deps
        """
    )
    
    parser.add_argument('--files', nargs='+', help='Files to extract (supports wildcards)')
    parser.add_argument('--output', default='extracted', help='Output directory')
    parser.add_argument('--format', choices=['json', 'markdown'], default='markdown', help='Output format')
    parser.add_argument('--max-chars', type=int, help='Maximum characters to extract per file')
    parser.add_argument('--check-deps', action='store_true', help='Check dependencies and exit')
    
    args = parser.parse_args()
    
    extractor = BatchExtractor(output_dir=args.output, format=args.format)
    
    if args.check_deps:
        print("Dependency Check:")
        deps = extractor.check_dependencies()
        for lib, available in deps.items():
            status = "✓" if available else "✗"
            print(f"  {status} {lib}")
        return 0
    
    if not args.files:
        parser.print_help()
        return 1
    
    # Expand wildcards
    from glob import glob
    file_list = []
    for pattern in args.files:
        file_list.extend(glob(pattern))
    
    if not file_list:
        print(f"No files found matching: {args.files}")
        return 1
    
    print(f"Processing {len(file_list)} file(s)...")
    extractor.process_files(file_list, max_chars=args.max_chars)
    
    output_file = extractor.save_results()
    print(f"Results saved to: {output_file}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
