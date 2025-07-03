#!/usr/bin/env python3
"""
Enhanced Documentation-to-Code Analysis
Provides detailed analysis of specific documented features vs actual implementation
"""

import os
import json
import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple

class DetailedDocAnalysis:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.docs_dir = self.project_root / "docs"
        
        # Core documented modules (based on analysis)
        self.documented_modules = {
            'God Mode': {
                'endpoints': [
                    '/api/v1/god-mode/activate',
                    '/api/v1/god-mode/deactivate', 
                    '/api/v1/god-mode/status',
                    '/api/v1/god-mode/predictions',
                    '/api/v1/god-mode/signals',
                    '/api/v1/god-mode/alerts'
                ],
                'components': ['GodModePage', 'GodModeControl', 'PredictionsPanel'],
                'backend_files': ['backend/api/v1/god_mode.py', 'backend/modules/god_mode/core_service.py'],
                'frontend_files': ['frontend/app/god-mode/page.tsx', 'frontend/components/god-mode/']
            },
            'Shadow Mode': {
                'endpoints': [
                    '/api/v1/shadow-mode/activate',
                    '/api/v1/shadow-mode/deactivate',
                    '/api/v1/shadow-mode/status',
                    '/api/v1/shadow-mode/whales',
                    '/api/v1/shadow-mode/dark-pools',
                    '/api/v1/shadow-mode/analytics'
                ],
                'components': ['ShadowModePage', 'ShadowControlPanel', 'WhaleTracker', 'DarkPoolMonitor'],
                'backend_files': ['backend/api/v1/shadow_mode.py', 'backend/modules/shadow_mode/shadow_service.py'],
                'frontend_files': ['frontend/app/shadow/page.tsx', 'frontend/components/shadow-mode/']
            },
            'Adaptive Trade Manager': {
                'endpoints': [
                    '/api/v1/adaptive-trade-manager/status',
                    '/api/v1/adaptive-trade-manager/positions', 
                    '/api/v1/adaptive-trade-manager/alerts',
                    '/api/v1/adaptive-trade-manager/risk-metrics'
                ],
                'components': ['AdaptiveTradeManagerPage', 'AdaptiveControls', 'RiskDashboard', 'TradeMonitor'],
                'backend_files': ['backend/api/v1/adaptive_trade_manager.py', 'backend/modules/adaptive_trade_manager/'],
                'frontend_files': ['frontend/app/adaptive-trade-manager/page.tsx', 'frontend/components/adaptive-trade-manager/']
            },
            'Trading Core': {
                'endpoints': [
                    '/api/v1/trading/place_order',
                    '/api/v1/trading/positions',
                    '/api/v1/trading/account_info',
                    '/api/v1/trading/history'
                ],
                'components': ['TradingPage', 'OrderPanel', 'PositionsTable', 'AccountInfo'],
                'backend_files': ['backend/api/v1/trading.py', 'backend/modules/mt5_integration/'],
                'frontend_files': ['frontend/app/trading/page.tsx', 'frontend/components/trading/']
            },
            'Strategy Whisperer': {
                'endpoints': [
                    '/api/v1/strategy-whisperer/generate',
                    '/api/v1/strategy-whisperer/backtest',
                    '/api/v1/strategy-whisperer/deploy'
                ],
                'components': ['StrategyWhispererPage', 'NaturalLanguageInput', 'CodePreview', 'BacktestResults'],
                'backend_files': ['backend/api/v1/strategy_whisperer.py', 'backend/modules/strategy_whisperer/'],
                'frontend_files': ['frontend/app/strategy-whisperer/page.tsx', 'frontend/components/strategy-whisperer/']
            },
            'Market Narrator': {
                'endpoints': [
                    '/api/v1/market-narrator/stories',
                    '/api/v1/market-narrator/analysis',
                    '/api/v1/market-narrator/influence-map'
                ],
                'components': ['MarketNarratorPage', 'StoryFeed', 'InfluenceMap'],
                'backend_files': ['backend/api/v1/market_narrator.py', 'backend/modules/market_narrator/'],
                'frontend_files': ['frontend/app/market-narrator/page.tsx', 'frontend/components/market-narrator/']
            }
        }
        
        self.actual_implementation = {
            'backend_endpoints': {},
            'frontend_components': {},
            'backend_files': set(),
            'frontend_files': set()
        }
        
        self.analysis_results = []
    
    def analyze_implementation(self):
        """Analyze actual implementation"""
        print("🔍 Analyzing actual implementation...")
        
        # Scan backend files
        self._scan_backend_implementation()
        
        # Scan frontend files  
        self._scan_frontend_implementation()
        
        print(f"📝 Found {len(self.actual_implementation['backend_endpoints'])} backend endpoints")
        print(f"🎨 Found {len(self.actual_implementation['frontend_components'])} frontend components")
    
    def _scan_backend_implementation(self):
        """Scan backend for actual implementation"""
        # Scan API routes
        api_dir = self.backend_dir / "api" / "v1"
        if api_dir.exists():
            for py_file in api_dir.glob("*.py"):
                if py_file.name != "__init__.py":
                    self._analyze_api_routes(py_file)
        
        # Scan module directories
        modules_dir = self.backend_dir / "modules"
        if modules_dir.exists():
            for item in modules_dir.rglob("*.py"):
                if item.name != "__init__.py":
                    self.actual_implementation['backend_files'].add(str(item.relative_to(self.project_root)))
    
    def _scan_frontend_implementation(self):
        """Scan frontend for actual implementation"""
        # Scan pages
        app_dir = self.frontend_dir / "app"
        if app_dir.exists():
            for page_dir in app_dir.iterdir():
                if page_dir.is_dir():
                    page_file = page_dir / "page.tsx"
                    if page_file.exists():
                        self._analyze_frontend_page(page_file)
                        self.actual_implementation['frontend_files'].add(str(page_file.relative_to(self.project_root)))
        
        # Scan components
        components_dir = self.frontend_dir / "components"
        if components_dir.exists():
            for component_file in components_dir.rglob("*.tsx"):
                self._analyze_frontend_component(component_file)
                self.actual_implementation['frontend_files'].add(str(component_file.relative_to(self.project_root)))
    
    def _analyze_api_routes(self, api_file: Path):
        """Extract API routes from FastAPI file"""
        try:
            with open(api_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract router prefix if defined
            prefix_pattern = r'router\s*=\s*APIRouter\([^)]*prefix\s*=\s*["\']([^"\']+)["\']'
            prefix_match = re.search(prefix_pattern, content)
            prefix = prefix_match.group(1) if prefix_match else ''
            
            # Extract route decorators
            route_pattern = r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'
            for match in re.finditer(route_pattern, content):
                method = match.group(1).upper()
                path = match.group(2)
                full_path = f"/api/v1{prefix}{path}" if prefix else f"/api/v1{path}"
                
                # Find associated function
                func_start = match.end()
                func_pattern = r'async def (\w+)\('
                func_match = re.search(func_pattern, content[func_start:])
                func_name = func_match.group(1) if func_match else 'unknown'
                
                self.actual_implementation['backend_endpoints'][full_path] = {
                    'method': method,
                    'function': func_name,
                    'file': str(api_file.relative_to(self.project_root)),
                    'module': api_file.stem
                }
        
        except Exception as e:
            print(f"Warning: Could not parse {api_file}: {e}")
    
    def _analyze_frontend_page(self, page_file: Path):
        """Analyze frontend page"""
        try:
            with open(page_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            page_name = page_file.parent.name
            
            # Extract default export function name
            export_pattern = r'export default function (\w+)\('
            match = re.search(export_pattern, content)
            component_name = match.group(1) if match else f"{page_name.replace('-', '').title()}Page"
            
            # Extract API calls
            api_calls = re.findall(r'fetch\(["\']([^"\']+)["\']', content)
            
            self.actual_implementation['frontend_components'][component_name] = {
                'type': 'Page',
                'file': str(page_file.relative_to(self.project_root)),
                'route': f'/{page_name}',
                'api_calls': api_calls
            }
            
        except Exception as e:
            print(f"Warning: Could not parse {page_file}: {e}")
    
    def _analyze_frontend_component(self, component_file: Path):
        """Analyze frontend component"""
        try:
            with open(component_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract component name from export
            export_pattern = r'export default (?:function\s+)?(\w+)'
            match = re.search(export_pattern, content)
            component_name = match.group(1) if match else component_file.stem
            
            self.actual_implementation['frontend_components'][component_name] = {
                'type': 'Component',
                'file': str(component_file.relative_to(self.project_root)),
                'directory': str(component_file.parent.relative_to(self.project_root))
            }
            
        except Exception as e:
            print(f"Warning: Could not parse {component_file}: {e}")
    
    def cross_reference_analysis(self):
        """Perform detailed cross-reference analysis"""
        print("🔄 Performing cross-reference analysis...")
        
        for module_name, module_info in self.documented_modules.items():
            print(f"\n📋 Analyzing {module_name}:")
            
            module_analysis = {
                'module': module_name,
                'endpoints_status': {},
                'components_status': {},
                'files_status': {},
                'overall_status': 'Unknown'
            }
            
            # Check endpoints
            for endpoint in module_info['endpoints']:
                if endpoint in self.actual_implementation['backend_endpoints']:
                    impl = self.actual_implementation['backend_endpoints'][endpoint]
                    module_analysis['endpoints_status'][endpoint] = {
                        'status': 'Present',
                        'method': impl['method'],
                        'function': impl['function'],
                        'file': impl['file']
                    }
                    print(f"  ✅ {endpoint} -> {impl['function']} in {impl['file']}")
                else:
                    module_analysis['endpoints_status'][endpoint] = {
                        'status': 'Missing',
                        'method': 'Unknown',
                        'function': 'Not Found',
                        'file': 'Not Found'
                    }
                    print(f"  ❌ {endpoint} -> NOT FOUND")
            
            # Check frontend components
            for component in module_info['components']:
                if component in self.actual_implementation['frontend_components']:
                    impl = self.actual_implementation['frontend_components'][component]
                    module_analysis['components_status'][component] = {
                        'status': 'Present',
                        'type': impl['type'],
                        'file': impl['file']
                    }
                    print(f"  ✅ {component} -> {impl['file']}")
                else:
                    module_analysis['components_status'][component] = {
                        'status': 'Missing',
                        'type': 'Unknown',
                        'file': 'Not Found'
                    }
                    print(f"  ❌ {component} -> NOT FOUND")
            
            # Check backend files
            backend_files_present = 0
            for file_path in module_info['backend_files']:
                if any(file_path in actual_file for actual_file in self.actual_implementation['backend_files']):
                    module_analysis['files_status'][file_path] = 'Present'
                    backend_files_present += 1
                    print(f"  📁 ✅ {file_path}")
                else:
                    module_analysis['files_status'][file_path] = 'Missing'
                    print(f"  📁 ❌ {file_path}")
            
            # Check frontend files
            frontend_files_present = 0
            for file_path in module_info['frontend_files']:
                if any(file_path in actual_file for actual_file in self.actual_implementation['frontend_files']):
                    module_analysis['files_status'][file_path] = 'Present'
                    frontend_files_present += 1
                    print(f"  📁 ✅ {file_path}")
                else:
                    module_analysis['files_status'][file_path] = 'Missing'
                    print(f"  📁 ❌ {file_path}")
            
            # Calculate overall status
            total_endpoints = len(module_info['endpoints'])
            present_endpoints = len([s for s in module_analysis['endpoints_status'].values() if s['status'] == 'Present'])
            
            total_components = len(module_info['components'])
            present_components = len([s for s in module_analysis['components_status'].values() if s['status'] == 'Present'])
            
            if present_endpoints == total_endpoints and present_components == total_components:
                module_analysis['overall_status'] = 'Fully Implemented'
            elif present_endpoints > 0 or present_components > 0:
                module_analysis['overall_status'] = 'Partially Implemented'
            else:
                module_analysis['overall_status'] = 'Not Implemented'
            
            module_analysis['completion_percentage'] = {
                'endpoints': (present_endpoints / total_endpoints * 100) if total_endpoints > 0 else 0,
                'components': (present_components / total_components * 100) if total_components > 0 else 0,
                'overall': ((present_endpoints + present_components) / (total_endpoints + total_components) * 100) if (total_endpoints + total_components) > 0 else 0
            }
            
            print(f"  📊 Overall: {module_analysis['overall_status']} ({module_analysis['completion_percentage']['overall']:.1f}% complete)")
            
            self.analysis_results.append(module_analysis)
    
    def generate_detailed_matrix(self):
        """Generate detailed Excel matrix"""
        print("📊 Generating detailed matrix...")
        
        # Create detailed matrix data
        matrix_data = []
        
        for result in self.analysis_results:
            module_name = result['module']
            
            # Add endpoint rows
            for endpoint, status in result['endpoints_status'].items():
                matrix_data.append({
                    'Module': module_name,
                    'Feature_Type': 'API Endpoint',
                    'Feature_Name': endpoint,
                    'Status': status['status'],
                    'Method': status.get('method', ''),
                    'Implementation_Function': status.get('function', ''),
                    'Implementation_File': status.get('file', ''),
                    'Frontend_Component': '',
                    'Completion_%': result['completion_percentage']['endpoints']
                })
            
            # Add component rows
            for component, status in result['components_status'].items():
                matrix_data.append({
                    'Module': module_name,
                    'Feature_Type': 'Frontend Component',
                    'Feature_Name': component,
                    'Status': status['status'],
                    'Method': '',
                    'Implementation_Function': '',
                    'Implementation_File': status.get('file', ''),
                    'Frontend_Component': component,
                    'Completion_%': result['completion_percentage']['components']
                })
        
        # Create summary data
        summary_data = []
        for result in self.analysis_results:
            summary_data.append({
                'Module': result['module'],
                'Overall_Status': result['overall_status'],
                'Endpoints_Complete_%': result['completion_percentage']['endpoints'],
                'Components_Complete_%': result['completion_percentage']['components'],
                'Overall_Complete_%': result['completion_percentage']['overall'],
                'Total_Endpoints': len(result['endpoints_status']),
                'Present_Endpoints': len([s for s in result['endpoints_status'].values() if s['status'] == 'Present']),
                'Total_Components': len(result['components_status']),
                'Present_Components': len([s for s in result['components_status'].values() if s['status'] == 'Present'])
            })
        
        # Export to Excel
        try:
            with pd.ExcelWriter('doc-code-matrix-detailed.xlsx', engine='openpyxl') as writer:
                # Main matrix
                df_matrix = pd.DataFrame(matrix_data)
                df_matrix.to_excel(writer, sheet_name='Detailed Matrix', index=False)
                
                # Summary
                df_summary = pd.DataFrame(summary_data)
                df_summary.to_excel(writer, sheet_name='Module Summary', index=False)
                
                # Implementation status
                implementation_data = []
                for module_name, module_info in self.documented_modules.items():
                    for endpoint in module_info['endpoints']:
                        implementation_data.append({
                            'Module': module_name,
                            'Type': 'Backend Endpoint',
                            'Feature': endpoint,
                            'Expected': 'Required',
                            'Actual': 'Present' if endpoint in self.actual_implementation['backend_endpoints'] else 'Missing',
                            'File': self.actual_implementation['backend_endpoints'].get(endpoint, {}).get('file', 'N/A')
                        })
                    
                    for component in module_info['components']:
                        implementation_data.append({
                            'Module': module_name,
                            'Type': 'Frontend Component',
                            'Feature': component,
                            'Expected': 'Required',
                            'Actual': 'Present' if component in self.actual_implementation['frontend_components'] else 'Missing',
                            'File': self.actual_implementation['frontend_components'].get(component, {}).get('file', 'N/A')
                        })
                
                df_implementation = pd.DataFrame(implementation_data)
                df_implementation.to_excel(writer, sheet_name='Implementation Status', index=False)
            
            print("✅ Detailed matrix exported to: doc-code-matrix-detailed.xlsx")
            
        except ImportError:
            # Fallback to CSV
            df_matrix = pd.DataFrame(matrix_data)
            df_matrix.to_csv('doc-code-matrix-detailed.csv', index=False)
            
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_csv('doc-code-matrix-summary.csv', index=False)
            
            print("✅ Detailed matrix exported to CSV files")
    
    def print_summary_report(self):
        """Print summary report to console"""
        print("\n" + "="*80)
        print("📊 DOCUMENTATION-TO-CODE CROSS-REFERENCE SUMMARY")
        print("="*80)
        
        total_modules = len(self.analysis_results)
        fully_implemented = len([r for r in self.analysis_results if r['overall_status'] == 'Fully Implemented'])
        partially_implemented = len([r for r in self.analysis_results if r['overall_status'] == 'Partially Implemented'])
        not_implemented = len([r for r in self.analysis_results if r['overall_status'] == 'Not Implemented'])
        
        print(f"\n📈 OVERALL STATISTICS:")
        print(f"  Total Modules Analyzed: {total_modules}")
        print(f"  Fully Implemented: {fully_implemented} ({fully_implemented/total_modules*100:.1f}%)")
        print(f"  Partially Implemented: {partially_implemented} ({partially_implemented/total_modules*100:.1f}%)")
        print(f"  Not Implemented: {not_implemented} ({not_implemented/total_modules*100:.1f}%)")
        
        print(f"\n📋 MODULE BREAKDOWN:")
        for result in self.analysis_results:
            status_emoji = "✅" if result['overall_status'] == 'Fully Implemented' else "🟡" if result['overall_status'] == 'Partially Implemented' else "❌"
            print(f"  {status_emoji} {result['module']}: {result['overall_status']} ({result['completion_percentage']['overall']:.1f}% complete)")
            
            # Show specific missing items
            missing_endpoints = [ep for ep, status in result['endpoints_status'].items() if status['status'] == 'Missing']
            missing_components = [comp for comp, status in result['components_status'].items() if status['status'] == 'Missing']
            
            if missing_endpoints:
                print(f"    Missing Endpoints: {', '.join(missing_endpoints[:3])}{'...' if len(missing_endpoints) > 3 else ''}")
            if missing_components:
                print(f"    Missing Components: {', '.join(missing_components[:3])}{'...' if len(missing_components) > 3 else ''}")
        
        print(f"\n🔍 DETAILED FINDINGS:")
        total_endpoints = sum(len(self.documented_modules[m]['endpoints']) for m in self.documented_modules)
        present_endpoints = sum(len([s for s in r['endpoints_status'].values() if s['status'] == 'Present']) for r in self.analysis_results)
        
        total_components = sum(len(self.documented_modules[m]['components']) for m in self.documented_modules)
        present_components = sum(len([s for s in r['components_status'].values() if s['status'] == 'Present']) for r in self.analysis_results)
        
        print(f"  Backend API Endpoints: {present_endpoints}/{total_endpoints} implemented ({present_endpoints/total_endpoints*100:.1f}%)")
        print(f"  Frontend Components: {present_components}/{total_components} implemented ({present_components/total_components*100:.1f}%)")
        
        print(f"\n📁 FILE ANALYSIS:")
        print(f"  Total Backend Files Found: {len(self.actual_implementation['backend_files'])}")
        print(f"  Total Frontend Files Found: {len(self.actual_implementation['frontend_files'])}")
        
        print("\n" + "="*80)

def main():
    """Main execution function"""
    print("🚀 Starting Enhanced Documentation-to-Code Analysis")
    print("="*80)
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    analyzer = DetailedDocAnalysis(project_root)
    
    try:
        analyzer.analyze_implementation()
        analyzer.cross_reference_analysis()
        analyzer.generate_detailed_matrix()
        analyzer.print_summary_report()
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
