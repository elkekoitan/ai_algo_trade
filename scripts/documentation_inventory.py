#!/usr/bin/env python3
"""
Documentation Inventory & Categorization Script
Creates a structured index of all project documentation with metadata and link analysis.
"""

import os
import re
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple
import argparse

class DocumentationAnalyzer:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.docs_pattern = re.compile(r'.*\.md$', re.IGNORECASE)
        self.link_patterns = {
            'markdown_link': re.compile(r'\[([^\]]+)\]\(([^)]+)\)'),
            'html_link': re.compile(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>', re.IGNORECASE),
            'url_link': re.compile(r'https?://[^\s\)]+'),
            'relative_link': re.compile(r'\]\((\./[^)]+|\.\./[^)]+|[^http][^)]*\.md[^)]*)\)'),
            'file_reference': re.compile(r'`([^`]*\.(?:md|py|js|ts|json|yaml|yml))`'),
        }
        
        # Document type classification patterns
        self.type_patterns = {
            'user-guide': [
                r'guide', r'tutorial', r'how-?to', r'quick-?start', r'getting-?started',
                r'setup', r'installation', r'kullanim', r'kilavuz'
            ],
            'api': [
                r'api', r'endpoint', r'swagger', r'openapi', r'rest', r'graphql'
            ],
            'tech-spec': [
                r'architecture', r'technical', r'spec', r'design', r'security',
                r'schema', r'database', r'system', r'integration'
            ],
            'status': [
                r'status', r'roadmap', r'implementation', r'progress', r'development',
                r'tasks', r'todo', r'changelog', r'summary'
            ],
            'diagram': [
                r'diagram', r'flow', r'architecture', r'schema', r'overview'
            ],
            'readme': [
                r'^readme', r'index', r'overview', r'main'
            ]
        }
        
        self.documentation_index = []

    def find_documentation_files(self) -> List[Path]:
        """Find all documentation files in the project."""
        doc_files = []
        
        # Find all .md files excluding node_modules
        for file_path in self.root_path.rglob("*.md"):
            if 'node_modules' not in str(file_path):
                doc_files.append(file_path)
        
        return sorted(doc_files)

    def classify_document_type(self, file_path: Path, content: str) -> str:
        """Classify document type based on filename and content."""
        file_name = file_path.name.lower()
        relative_path = str(file_path.relative_to(self.root_path)).lower()
        content_lower = content.lower()
        
        # Check patterns in order of specificity
        for doc_type, patterns in self.type_patterns.items():
            for pattern in patterns:
                if (re.search(pattern, file_name) or 
                    re.search(pattern, relative_path) or
                    re.search(pattern, content_lower[:500])):  # Check first 500 chars
                    return doc_type
        
        # Special cases based on directory structure
        path_parts = file_path.parts
        if 'user-guides' in path_parts:
            return 'user-guide'
        elif 'technical' in path_parts:
            return 'tech-spec'
        elif 'diagrams' in path_parts:
            return 'diagram'
        elif 'roadmaps' in path_parts or 'status' in path_parts:
            return 'status'
        elif 'architecture' in path_parts:
            return 'tech-spec'
        
        return 'general'

    def extract_links(self, content: str, file_path: Path) -> Dict[str, List[str]]:
        """Extract all types of links from document content."""
        links = {
            'internal_links': [],
            'external_links': [],
            'file_references': [],
            'broken_links': []
        }
        
        # Extract markdown links
        for match in self.link_patterns['markdown_link'].finditer(content):
            link_text, link_url = match.groups()
            self._categorize_link(link_url, link_text, links, file_path)
        
        # Extract HTML links
        for match in self.link_patterns['html_link'].finditer(content):
            link_url, link_text = match.groups()
            self._categorize_link(link_url, link_text, links, file_path)
        
        # Extract standalone URLs
        for match in self.link_patterns['url_link'].finditer(content):
            link_url = match.group(0)
            self._categorize_link(link_url, '', links, file_path)
        
        # Extract file references in backticks
        for match in self.link_patterns['file_reference'].finditer(content):
            file_ref = match.group(1)
            links['file_references'].append(file_ref)
        
        return links

    def _categorize_link(self, url: str, text: str, links: Dict, file_path: Path):
        """Categorize a link as internal, external, or broken."""
        if url.startswith(('http://', 'https://')):
            links['external_links'].append({'url': url, 'text': text})
        elif url.startswith(('mailto:', 'tel:')):
            links['external_links'].append({'url': url, 'text': text})
        else:
            # Internal link - check if it exists
            target_path = self._resolve_internal_link(url, file_path)
            link_info = {'url': url, 'text': text, 'resolved_path': str(target_path) if target_path else None}
            
            if target_path and target_path.exists():
                links['internal_links'].append(link_info)
            else:
                links['broken_links'].append(link_info)

    def _resolve_internal_link(self, url: str, source_file: Path) -> Path:
        """Resolve internal link to absolute path."""
        try:
            # Remove anchors
            url = url.split('#')[0]
            if not url:
                return source_file
            
            # Resolve relative to source file
            if url.startswith('./'):
                return (source_file.parent / url[2:]).resolve()
            elif url.startswith('../'):
                return (source_file.parent / url).resolve()
            else:
                # Try relative to source file first, then root
                candidate1 = (source_file.parent / url).resolve()
                candidate2 = (self.root_path / url).resolve()
                
                if candidate1.exists():
                    return candidate1
                elif candidate2.exists():
                    return candidate2
                else:
                    return candidate1  # Return best guess
        except Exception:
            return None

    def analyze_document(self, file_path: Path) -> Dict:
        """Analyze a single document and extract metadata."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
        
        # Get file stats
        stat = file_path.stat()
        last_modified = datetime.fromtimestamp(stat.st_mtime)
        
        # Extract basic metadata
        relative_path = str(file_path.relative_to(self.root_path))
        doc_type = self.classify_document_type(file_path, content)
        links = self.extract_links(content, file_path)
        
        # Extract title (first heading)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else file_path.stem
        
        # Count content metrics
        word_count = len(content.split())
        line_count = len(content.splitlines())
        
        return {
            'path': relative_path,
            'absolute_path': str(file_path),
            'filename': file_path.name,
            'title': title,
            'type': doc_type,
            'last_modified': last_modified.isoformat(),
            'size_bytes': stat.st_size,
            'word_count': word_count,
            'line_count': line_count,
            'internal_links': links['internal_links'],
            'external_links': links['external_links'],
            'file_references': links['file_references'],
            'broken_links': links['broken_links'],
            'total_links': (len(links['internal_links']) + 
                          len(links['external_links']) + 
                          len(links['broken_links']))
        }

    def generate_inventory(self) -> List[Dict]:
        """Generate complete documentation inventory."""
        doc_files = self.find_documentation_files()
        
        print(f"Found {len(doc_files)} documentation files")
        
        for file_path in doc_files:
            print(f"Analyzing: {file_path.relative_to(self.root_path)}")
            doc_info = self.analyze_document(file_path)
            if doc_info:
                self.documentation_index.append(doc_info)
        
        return self.documentation_index

    def save_to_json(self, output_path: str = "documentation_index.json"):
        """Save inventory to JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.documentation_index, f, indent=2, ensure_ascii=False)
        print(f"JSON inventory saved to: {output_path}")

    def save_to_csv(self, output_path: str = "documentation_index.csv"):
        """Save inventory to CSV file."""
        if not self.documentation_index:
            return
        
        # Flatten the data for CSV
        flattened_data = []
        for doc in self.documentation_index:
            row = {
                'path': doc['path'],
                'filename': doc['filename'],
                'title': doc['title'],
                'type': doc['type'],
                'last_modified': doc['last_modified'],
                'size_bytes': doc['size_bytes'],
                'word_count': doc['word_count'],
                'line_count': doc['line_count'],
                'total_links': doc['total_links'],
                'internal_links_count': len(doc['internal_links']),
                'external_links_count': len(doc['external_links']),
                'broken_links_count': len(doc['broken_links']),
                'internal_links': ' | '.join([f"{link['text']}({link['url']})" for link in doc['internal_links']]),
                'external_links': ' | '.join([f"{link['text']}({link['url']})" for link in doc['external_links']]),
                'broken_links': ' | '.join([f"{link['text']}({link['url']})" for link in doc['broken_links']]),
                'file_references': ' | '.join(doc['file_references'])
            }
            flattened_data.append(row)
        
        # Write CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = flattened_data[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flattened_data)
        
        print(f"CSV inventory saved to: {output_path}")

    def generate_summary_report(self) -> str:
        """Generate a summary report of the documentation inventory."""
        if not self.documentation_index:
            return "No documentation found."
        
        # Calculate statistics
        total_docs = len(self.documentation_index)
        type_counts = {}
        total_words = 0
        total_links = 0
        broken_links_count = 0
        
        for doc in self.documentation_index:
            doc_type = doc['type']
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
            total_words += doc['word_count']
            total_links += doc['total_links']
            broken_links_count += len(doc['broken_links'])
        
        # Most recent updates
        recent_docs = sorted(self.documentation_index, 
                           key=lambda x: x['last_modified'], 
                           reverse=True)[:5]
        
        # Generate report
        report = f"""
# Documentation Inventory Summary Report
Generated: {datetime.now().isoformat()}

## Overview
- **Total Documents**: {total_docs}
- **Total Words**: {total_words:,}
- **Total Links**: {total_links}
- **Broken Links**: {broken_links_count}

## Document Types
"""
        for doc_type, count in sorted(type_counts.items()):
            report += f"- **{doc_type.title()}**: {count} documents\n"
        
        report += f"""
## Recently Updated Documents
"""
        for doc in recent_docs:
            report += f"- [{doc['title']}]({doc['path']}) - {doc['last_modified'][:10]}\n"
        
        report += f"""
## Link Health
- **Total Links**: {total_links}
- **Broken Links**: {broken_links_count}
- **Link Health**: {((total_links - broken_links_count) / max(total_links, 1) * 100):.1f}%

## Recommendations
"""
        if broken_links_count > 0:
            report += f"- Fix {broken_links_count} broken internal links\n"
        
        if type_counts.get('general', 0) > total_docs * 0.2:
            report += "- Consider improving document categorization for 'general' type documents\n"
        
        return report

def main():
    parser = argparse.ArgumentParser(description='Analyze project documentation and create structured index')
    parser.add_argument('--root', default='.', help='Root directory to analyze (default: current directory)')
    parser.add_argument('--output-json', default='documentation_index.json', help='JSON output file')
    parser.add_argument('--output-csv', default='documentation_index.csv', help='CSV output file')
    parser.add_argument('--summary', default='documentation_summary.md', help='Summary report file')
    
    args = parser.parse_args()
    
    analyzer = DocumentationAnalyzer(args.root)
    
    print("Starting documentation inventory...")
    inventory = analyzer.generate_inventory()
    
    if inventory:
        analyzer.save_to_json(args.output_json)
        analyzer.save_to_csv(args.output_csv)
        
        # Generate and save summary report
        summary = analyzer.generate_summary_report()
        with open(args.summary, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"Summary report saved to: {args.summary}")
        print(f"\nInventory complete! Found {len(inventory)} documentation files.")
    else:
        print("No documentation files found.")

if __name__ == "__main__":
    main()
