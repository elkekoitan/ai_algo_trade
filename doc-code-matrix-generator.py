#!/usr/bin/env python3
"""
Documentation-to-Code Cross-Reference Matrix Generator
Creates an Excel file mapping documented features to actual codebase implementation
"""

import os
import json
import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
import ast
import glob

class DocCodeMatrixGenerator:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.docs_dir = self.project_root / "docs"
        
        # Initialize data structures
        self.documented_features = []
        self.backend_endpoints = {}
        self.frontend_components = {}
        self.matrix_data = []
        
    def analyze_documentation(self) -> None:
        """Extract documented features from documentation files"""
        print("📚 Analyzing documentation files...")
        
        # Read documentation index if available
        doc_index_file = self.project_root / "documentation_index.json"
        if doc_index_file.exists():
            with open(doc_index_file, 'r', encoding='utf-8') as f:
                doc_index = json.load(f)
                
            for doc in doc_index:
                if doc.get('type') in ['api', 'tech-spec', 'user-guide']:
                    self.documented_features.extend(self._extract_features_from_doc(doc))
        
        # Parse MODULES.md for module documentation
        modules_md = self.docs_dir / "MODULES.md"
        if modules_md.exists():
            self._parse_modules_md(modules_md)
            
        # Parse architecture documentation
        arch_files = list(self.docs_dir.glob("**/ARCHITECTURE.md")) + list(self.docs_dir.glob("**/architecture/*.md"))
        for arch_file in arch_files:
            self._parse_architecture_doc(arch_file)
        
        print(f"📝 Found {len(self.documented_features)} documented features")
    
    def analyze_backend(self) -> None:
        """Analyze backend FastAPI routes and modules"""
        print("🔧 Analyzing backend codebase...")
        
        # Analyze API routes
        api_dir = self.backend_dir / "api" / "v1"
        if api_dir.exists():
            for py_file in api_dir.glob("*.py"):
                if py_file.name != "__init__.py":
                    self._analyze_api_file(py_file)
        
        # Analyze modules
        modules_dir = self.backend_dir / "modules"
        if modules_dir.exists():
            for module_dir in modules_dir.iterdir():
                if module_dir.is_dir() and not module_dir.name.startswith('__'):
                    self._analyze_module_dir(module_dir)
        
        print(f"🔗 Found {len(self.backend_endpoints)} backend endpoints")
    
    def analyze_frontend(self) -> None:
        """Analyze frontend components and pages"""
        print("🎨 Analyzing frontend codebase...")
        
        # Analyze pages
        app_dir = self.frontend_dir / "app"
        if app_dir.exists():
            for page_dir in app_dir.iterdir():
                if page_dir.is_dir():
                    page_file = page_dir / "page.tsx"
                    if page_file.exists():
                        self._analyze_frontend_page(page_file)
        
        # Analyze components
        components_dir = self.frontend_dir / "components"
        if components_dir.exists():
            for component_file in components_dir.rglob("*.tsx"):
                self._analyze_frontend_component(component_file)
        
        print(f"🎭 Found {len(self.frontend_components)} frontend components")
    
    def generate_matrix(self) -> None:
        """Generate the cross-reference matrix"""
        print("📊 Generating cross-reference matrix...")
        
        for feature in self.documented_features:
            matrix_entry = {
                'Feature/Module': feature['name'],
                'Type': feature['type'],
                'Documented_In': feature['source'],
                'Description': feature.get('description', ''),
                'Backend_Present': 'Absent',
                'Backend_Details': '',
                'Frontend_Present': 'Absent', 
                'Frontend_Details': '',
                'API_Endpoint': '',
                'Status': 'Not Implemented',
                'Mismatch_Details': '',
                'Implementation_Notes': ''
            }
            
            # Check backend presence
            backend_match = self._find_backend_match(feature)
            if backend_match:
                matrix_entry['Backend_Present'] = 'Present'
                matrix_entry['Backend_Details'] = backend_match['details']
                matrix_entry['API_Endpoint'] = backend_match.get('endpoint', '')
            
            # Check frontend presence
            frontend_match = self._find_frontend_match(feature)
            if frontend_match:
                matrix_entry['Frontend_Present'] = 'Present'
                matrix_entry['Frontend_Details'] = frontend_match['details']
            
            # Determine overall status
            matrix_entry['Status'] = self._determine_status(matrix_entry)
            
            # Check for mismatches
            mismatch = self._check_for_mismatch(feature, backend_match, frontend_match)
            if mismatch:
                matrix_entry['Mismatch_Details'] = mismatch
                matrix_entry['Status'] = 'Mismatch'
            
            self.matrix_data.append(matrix_entry)
    
    def export_to_excel(self, output_path: str = "doc-code-matrix.xlsx") -> None:
        """Export the matrix to Excel file"""
        print(f"📤 Exporting matrix to {output_path}...")
        
        df = pd.DataFrame(self.matrix_data)
        
        try:
            # Try to create Excel file with openpyxl
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Main matrix sheet
                df.to_excel(writer, sheet_name='Doc-Code Matrix', index=False)
                
                # Summary sheet
                summary_data = self._generate_summary()
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Backend endpoints sheet
                backend_df = pd.DataFrame([
                    {
                        'Module': module,
                        'Endpoint': endpoint,
                        'Method': details.get('method', 'GET') if isinstance(details, dict) else 'Unknown',
                        'Description': details.get('description', '') if isinstance(details, dict) else str(details),
                        'File': details.get('file', '') if isinstance(details, dict) else ''
                    }
                    for module, endpoints in self.backend_endpoints.items()
                    if isinstance(endpoints, dict)
                    for endpoint, details in endpoints.items()
                ])
                backend_df.to_excel(writer, sheet_name='Backend Endpoints', index=False)
                
                # Frontend components sheet
                frontend_df = pd.DataFrame([
                    {
                        'Component': component,
                        'Type': details.get('type', 'Component'),
                        'File': details.get('file', ''),
                        'Description': details.get('description', '')
                    }
                    for component, details in self.frontend_components.items()
                ])
                frontend_df.to_excel(writer, sheet_name='Frontend Components', index=False)
            
            print(f"✅ Matrix exported successfully to {output_path}")
            
        except ImportError:
            # Fallback to CSV if Excel libraries not available
            print("⚠️ Excel library not available, exporting to CSV instead...")
            csv_path = output_path.replace('.xlsx', '.csv')
            df.to_csv(csv_path, index=False)
            
            # Export additional sheets as separate CSV files
            summary_data = self._generate_summary()
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_csv(csv_path.replace('.csv', '_summary.csv'), index=False)
            
            backend_df = pd.DataFrame([
                {
                    'Module': module,
                    'Endpoint': endpoint,
                    'Method': details.get('method', 'GET') if isinstance(details, dict) else 'Unknown',
                    'Description': details.get('description', '') if isinstance(details, dict) else str(details),
                    'File': details.get('file', '') if isinstance(details, dict) else ''
                }
                for module, endpoints in self.backend_endpoints.items()
                if isinstance(endpoints, dict)
                for endpoint, details in endpoints.items()
            ])
            backend_df.to_csv(csv_path.replace('.csv', '_backend.csv'), index=False)
            
            frontend_df = pd.DataFrame([
                {
                    'Component': component,
                    'Type': details.get('type', 'Component'),
                    'File': details.get('file', ''),
                    'Description': details.get('description', '')
                }
                for component, details in self.frontend_components.items()
            ])
            frontend_df.to_csv(csv_path.replace('.csv', '_frontend.csv'), index=False)
            
            print(f"✅ Matrix exported to CSV files: {csv_path} (and related files)")
    
    def _extract_features_from_doc(self, doc: Dict) -> List[Dict]:
        """Extract features from a documentation entry"""
        features = []
        
        # Read the actual file if path exists
        doc_path = self.project_root / doc['path']
        if doc_path.exists():
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract headers, API endpoints, class names, etc.
            features.extend(self._extract_from_markdown(content, doc['path']))
        
        return features
    
    def _extract_from_markdown(self, content: str, source: str) -> List[Dict]:
        """Extract features from markdown content"""
        features = []
        
        # Extract headers
        header_pattern = r'^#{1,6}\s+(.+)$'
        for match in re.finditer(header_pattern, content, re.MULTILINE):
            header_text = match.group(1).strip()
            if any(keyword in header_text.lower() for keyword in ['api', 'endpoint', 'component', 'module', 'service']):
                features.append({
                    'name': header_text,
                    'type': 'Documentation Section',
                    'source': source,
                    'description': header_text
                })
        
        # Extract API endpoints from documentation
        api_pattern = r'(/api/v1/[^\s\)]+)'
        for match in re.finditer(api_pattern, content):
            endpoint = match.group(1)
            features.append({
                'name': endpoint,
                'type': 'API Endpoint',
                'source': source,
                'description': f'API endpoint documented in {source}'
            })
        
        # Extract code blocks that might reference components
        code_pattern = r'```[\w]*\n(.*?)\n```'
        for match in re.finditer(code_pattern, content, re.DOTALL):
            code_block = match.group(1)
            if 'class ' in code_block or 'def ' in code_block or 'function ' in code_block:
                features.append({
                    'name': 'Code Block',
                    'type': 'Code Reference',
                    'source': source,
                    'description': 'Code block in documentation'
                })
        
        return features
    
    def _parse_modules_md(self, modules_file: Path) -> None:
        """Parse MODULES.md to extract module information"""
        with open(modules_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse module sections
        module_pattern = r'^## (.+)$'
        for match in re.finditer(module_pattern, content, re.MULTILINE):
            module_name = match.group(1).strip()
            
            # Find the section content
            start = match.end()
            next_match = re.search(r'^##', content[start:], re.MULTILINE)
            end = start + next_match.start() if next_match else len(content)
            section_content = content[start:end]
            
            # Extract file path
            file_pattern = r'\*\*File:\*\* `(.+)`'
            file_match = re.search(file_pattern, section_content)
            file_path = file_match.group(1) if file_match else ''
            
            # Extract description
            desc_pattern = r'### Description\n(.+?)(?=\n###|\n\n|\Z)'
            desc_match = re.search(desc_pattern, section_content, re.DOTALL)
            description = desc_match.group(1).strip() if desc_match else ''
            
            # Extract classes
            class_pattern = r'- `([^`]+)`: (.+)'
            classes = []
            for class_match in re.finditer(class_pattern, section_content):
                classes.append({
                    'name': class_match.group(1),
                    'description': class_match.group(2)
                })
            
            self.documented_features.append({
                'name': module_name,
                'type': 'Module',
                'source': 'MODULES.md',
                'description': description,
                'file_path': file_path,
                'classes': classes
            })
    
    def _parse_architecture_doc(self, arch_file: Path) -> None:
        """Parse architecture documentation"""
        with open(arch_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract system components
        component_pattern = r'### (\d+\.\s+)?(.+?)\s*(?:\(([^)]+)\))?$'
        for match in re.finditer(component_pattern, content, re.MULTILINE):
            component_name = match.group(2).strip()
            tech_stack = match.group(3) if match.group(3) else ''
            
            self.documented_features.append({
                'name': component_name,
                'type': 'System Component',
                'source': str(arch_file.relative_to(self.project_root)),
                'description': f'System component: {component_name}',
                'tech_stack': tech_stack
            })
    
    def _analyze_api_file(self, api_file: Path) -> None:
        """Analyze a FastAPI route file"""
        try:
            with open(api_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            module_name = api_file.stem
            endpoints = {}
            
            # Parse AST to extract route decorators
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        for decorator in node.decorator_list:
                            if isinstance(decorator, ast.Attribute):
                                if decorator.attr in ['get', 'post', 'put', 'delete', 'patch']:
                                    # Extract endpoint path
                                    endpoint_path = ''
                                    if hasattr(decorator, 'args') and decorator.args:
                                        if isinstance(decorator.args[0], ast.Str):
                                            endpoint_path = decorator.args[0].s
                                    
                                    # Extract docstring
                                    docstring = ast.get_docstring(node) or ''
                                    
                                    endpoints[endpoint_path or node.name] = {
                                        'method': decorator.attr.upper(),
                                        'function': node.name,
                                        'description': docstring,
                                        'file': str(api_file.relative_to(self.project_root))
                                    }
            except SyntaxError:
                # Fallback to regex parsing if AST fails
                self._parse_api_file_regex(content, api_file, endpoints)
            
            if endpoints:
                self.backend_endpoints[module_name] = endpoints
                
        except Exception as e:
            print(f"Warning: Could not parse {api_file}: {e}")
    
    def _parse_api_file_regex(self, content: str, api_file: Path, endpoints: Dict) -> None:
        """Fallback regex parsing for API files"""
        # Extract router decorators
        route_pattern = r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'
        for match in re.finditer(route_pattern, content):
            method = match.group(1).upper()
            path = match.group(2)
            
            # Find the function definition that follows
            func_pattern = r'async def (\w+)\('
            func_match = re.search(func_pattern, content[match.end():])
            func_name = func_match.group(1) if func_match else 'unknown'
            
            endpoints[path] = {
                'method': method,
                'function': func_name,
                'description': f'{method} {path}',
                'file': str(api_file.relative_to(self.project_root))
            }
    
    def _analyze_module_dir(self, module_dir: Path) -> None:
        """Analyze a backend module directory"""
        for py_file in module_dir.rglob("*.py"):
            if py_file.name != "__init__.py":
                self._analyze_python_file(py_file)
    
    def _analyze_python_file(self, py_file: Path) -> None:
        """Analyze a Python file for classes and functions"""
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract classes and functions
            class_pattern = r'class\s+(\w+)(?:\([^)]*\))?:'
            for match in re.finditer(class_pattern, content):
                class_name = match.group(1)
                module_path = str(py_file.relative_to(self.backend_dir))
                
                if 'classes' not in self.backend_endpoints:
                    self.backend_endpoints['classes'] = {}
                
                self.backend_endpoints['classes'][class_name] = {
                    'file': module_path,
                    'type': 'Class',
                    'description': f'Class {class_name} in {module_path}'
                }
                
        except Exception as e:
            print(f"Warning: Could not parse {py_file}: {e}")
    
    def _analyze_frontend_page(self, page_file: Path) -> None:
        """Analyze a frontend page file"""
        try:
            with open(page_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            page_name = page_file.parent.name
            
            # Extract component name from default export
            export_pattern = r'export default function (\w+)\('
            match = re.search(export_pattern, content)
            component_name = match.group(1) if match else f"{page_name}Page"
            
            # Extract imports and API calls
            api_calls = re.findall(r'fetch\(["\']([^"\']+)["\']', content)
            
            self.frontend_components[component_name] = {
                'type': 'Page',
                'file': str(page_file.relative_to(self.project_root)),
                'description': f'Frontend page: {page_name}',
                'api_calls': api_calls,
                'route': f'/{page_name}'
            }
            
        except Exception as e:
            print(f"Warning: Could not parse {page_file}: {e}")
    
    def _analyze_frontend_component(self, component_file: Path) -> None:
        """Analyze a frontend component file"""
        try:
            with open(component_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract component name
            export_pattern = r'export default function (\w+)\('
            match = re.search(export_pattern, content)
            if not match:
                export_pattern = r'export\s+(?:default\s+)?(?:function\s+)?(\w+)'
                match = re.search(export_pattern, content)
            
            component_name = match.group(1) if match else component_file.stem
            
            # Extract props interface if exists
            props_pattern = r'interface\s+(\w*Props?\w*)\s*{'
            props_match = re.search(props_pattern, content)
            props_interface = props_match.group(1) if props_match else None
            
            self.frontend_components[component_name] = {
                'type': 'Component',
                'file': str(component_file.relative_to(self.project_root)),
                'description': f'React component: {component_name}',
                'props_interface': props_interface
            }
            
        except Exception as e:
            print(f"Warning: Could not parse {component_file}: {e}")
    
    def _find_backend_match(self, feature: Dict) -> Dict[str, Any] | None:
        """Find matching backend implementation for a documented feature"""
        feature_name = feature['name'].lower()
        
        # Check API endpoints
        for module, endpoints in self.backend_endpoints.items():
            if isinstance(endpoints, dict):
                for endpoint, details in endpoints.items():
                    if (feature_name in endpoint.lower() or 
                        feature_name in details.get('function', '').lower() or
                        feature_name.replace('-', '_') in details.get('function', '').lower()):
                        return {
                            'details': f"Found in {module}: {endpoint}",
                            'endpoint': endpoint,
                            'module': module,
                            'type': 'API Endpoint'
                        }
        
        # Check classes
        if 'classes' in self.backend_endpoints:
            for class_name, details in self.backend_endpoints['classes'].items():
                if (feature_name in class_name.lower() or
                    feature_name.replace('-', '_') in class_name.lower()):
                    return {
                        'details': f"Found class: {class_name}",
                        'class': class_name,
                        'type': 'Class'
                    }
        
        # Check by file path if available
        if 'file_path' in feature and feature['file_path']:
            file_path = feature['file_path'].replace('\\', '/')
            backend_file = self.backend_dir / file_path
            if backend_file.exists():
                return {
                    'details': f"File exists: {file_path}",
                    'file': file_path,
                    'type': 'File'
                }
        
        return None
    
    def _find_frontend_match(self, feature: Dict) -> Dict[str, Any] | None:
        """Find matching frontend implementation for a documented feature"""
        feature_name = feature['name'].lower()
        
        for component_name, details in self.frontend_components.items():
            if (feature_name in component_name.lower() or
                feature_name.replace('-', '_') in component_name.lower() or
                feature_name.replace(' ', '') in component_name.lower()):
                return {
                    'details': f"Found component: {component_name}",
                    'component': component_name,
                    'type': details['type']
                }
        
        return None
    
    def _determine_status(self, matrix_entry: Dict) -> str:
        """Determine the implementation status"""
        backend_present = matrix_entry['Backend_Present'] == 'Present'
        frontend_present = matrix_entry['Frontend_Present'] == 'Present'
        
        if backend_present and frontend_present:
            return 'Fully Implemented'
        elif backend_present:
            return 'Backend Only'
        elif frontend_present:
            return 'Frontend Only'
        else:
            return 'Not Implemented'
    
    def _check_for_mismatch(self, feature: Dict, backend_match: Dict, frontend_match: Dict) -> str:
        """Check for mismatches between documentation and implementation"""
        mismatches = []
        
        # Check API endpoint mismatches
        if feature['type'] == 'API Endpoint':
            if backend_match and 'endpoint' in backend_match:
                doc_endpoint = feature['name']
                impl_endpoint = backend_match['endpoint']
                if doc_endpoint != impl_endpoint and doc_endpoint not in impl_endpoint:
                    mismatches.append(f"Endpoint mismatch: documented '{doc_endpoint}' vs implemented '{impl_endpoint}'")
        
        # Check component name mismatches
        if feature['type'] in ['Component', 'Page']:
            if frontend_match and 'component' in frontend_match:
                doc_name = feature['name']
                impl_name = frontend_match['component']
                if doc_name.lower() != impl_name.lower():
                    mismatches.append(f"Component name mismatch: documented '{doc_name}' vs implemented '{impl_name}'")
        
        return '; '.join(mismatches)
    
    def _generate_summary(self) -> List[Dict]:
        """Generate summary statistics"""
        total_features = len(self.matrix_data)
        fully_implemented = len([m for m in self.matrix_data if m['Status'] == 'Fully Implemented'])
        backend_only = len([m for m in self.matrix_data if m['Status'] == 'Backend Only'])
        frontend_only = len([m for m in self.matrix_data if m['Status'] == 'Frontend Only'])
        not_implemented = len([m for m in self.matrix_data if m['Status'] == 'Not Implemented'])
        mismatches = len([m for m in self.matrix_data if m['Status'] == 'Mismatch'])
        
        return [
            {'Metric': 'Total Documented Features', 'Count': total_features, 'Percentage': '100%'},
            {'Metric': 'Fully Implemented', 'Count': fully_implemented, 'Percentage': f'{fully_implemented/total_features*100:.1f}%'},
            {'Metric': 'Backend Only', 'Count': backend_only, 'Percentage': f'{backend_only/total_features*100:.1f}%'},
            {'Metric': 'Frontend Only', 'Count': frontend_only, 'Percentage': f'{frontend_only/total_features*100:.1f}%'},
            {'Metric': 'Not Implemented', 'Count': not_implemented, 'Percentage': f'{not_implemented/total_features*100:.1f}%'},
            {'Metric': 'Mismatches', 'Count': mismatches, 'Percentage': f'{mismatches/total_features*100:.1f}%'},
            {'Metric': 'Backend Endpoints Found', 'Count': sum(len(eps) for eps in self.backend_endpoints.values() if isinstance(eps, dict)), 'Percentage': '-'},
            {'Metric': 'Frontend Components Found', 'Count': len(self.frontend_components), 'Percentage': '-'}
        ]
    
    def _format_excel(self, writer) -> None:
        """Format the Excel file with colors and styling"""
        workbook = writer.book
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        
        present_format = workbook.add_format({
            'fg_color': '#C6EFCE',
            'border': 1
        })
        
        absent_format = workbook.add_format({
            'fg_color': '#FFC7CE',
            'border': 1
        })
        
        mismatch_format = workbook.add_format({
            'fg_color': '#FFEB9C',
            'border': 1
        })
        
        # Format main sheet
        worksheet = writer.sheets['Doc-Code Matrix']
        
        # Set column widths
        worksheet.set_column('A:A', 30)  # Feature/Module
        worksheet.set_column('B:B', 15)  # Type
        worksheet.set_column('C:C', 25)  # Documented_In
        worksheet.set_column('D:D', 40)  # Description
        worksheet.set_column('E:E', 15)  # Backend_Present
        worksheet.set_column('F:F', 30)  # Backend_Details
        worksheet.set_column('G:G', 15)  # Frontend_Present
        worksheet.set_column('H:H', 30)  # Frontend_Details
        worksheet.set_column('I:I', 25)  # API_Endpoint
        worksheet.set_column('J:J', 20)  # Status
        worksheet.set_column('K:K', 30)  # Mismatch_Details
        worksheet.set_column('L:L', 30)  # Implementation_Notes
        
        # Apply conditional formatting
        worksheet.conditional_format('E:E', {
            'type': 'text',
            'criteria': 'containing',
            'value': 'Present',
            'format': present_format
        })
        
        worksheet.conditional_format('E:E', {
            'type': 'text',
            'criteria': 'containing',
            'value': 'Absent',
            'format': absent_format
        })
        
        worksheet.conditional_format('G:G', {
            'type': 'text',
            'criteria': 'containing',
            'value': 'Present',
            'format': present_format
        })
        
        worksheet.conditional_format('G:G', {
            'type': 'text',
            'criteria': 'containing',
            'value': 'Absent',
            'format': absent_format
        })
        
        worksheet.conditional_format('J:J', {
            'type': 'text',
            'criteria': 'containing',
            'value': 'Mismatch',
            'format': mismatch_format
        })

def main():
    """Main execution function"""
    print("🚀 Starting Documentation-to-Code Cross-Reference Analysis")
    print("=" * 60)
    
    # Initialize generator
    project_root = os.path.dirname(os.path.abspath(__file__))
    generator = DocCodeMatrixGenerator(project_root)
    
    # Run analysis
    try:
        generator.analyze_documentation()
        generator.analyze_backend()
        generator.analyze_frontend()
        generator.generate_matrix()
        generator.export_to_excel()
        
        print("\n" + "=" * 60)
        print("✅ Analysis completed successfully!")
        print(f"📊 Matrix exported to: doc-code-matrix.xlsx")
        print("📈 Summary statistics available in the Summary sheet")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
