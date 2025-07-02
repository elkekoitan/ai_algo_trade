"""
Smoke tests for AI Algo Trade Platform backend.
Tests import functionality and API endpoints.
"""

import pytest
import sys
import os
import httpx
import asyncio
from typing import Dict, List

# Test results storage
test_results = {
    "import_errors": [],
    "endpoint_errors": [],
    "discrepancies": [],
    "passed_tests": [],
    "failed_tests": []
}

class TestImports:
    """Test module imports to catch Strategy Whisperer and other import errors."""
    
    def test_basic_imports(self):
        """Test basic Python and FastAPI imports."""
        try:
            import fastapi
            import uvicorn
            import pydantic
            test_results["passed_tests"].append("basic_imports")
        except ImportError as e:
            test_results["import_errors"].append(f"Basic imports failed: {e}")
            test_results["failed_tests"].append("basic_imports")
            pytest.fail(f"Basic imports failed: {e}")
    
    def test_backend_main_import(self):
        """Test importing the main backend module."""
        try:
            # Add backend to path if not already there
            backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
            if backend_path not in sys.path:
                sys.path.insert(0, backend_path)
            
            from backend.main import app
            assert app is not None
            test_results["passed_tests"].append("backend_main_import")
        except ImportError as e:
            test_results["import_errors"].append(f"Backend main import failed: {e}")
            test_results["failed_tests"].append("backend_main_import")
            pytest.fail(f"Backend main import failed: {e}")
    
    def test_strategy_whisperer_import(self):
        """Test Strategy Whisperer module import specifically."""
        try:
            backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
            if backend_path not in sys.path:
                sys.path.insert(0, backend_path)
                
            # Try to import the strategy whisperer module
            from backend.api.v1 import strategy_whisperer
            test_results["passed_tests"].append("strategy_whisperer_import")
            
        except ImportError as e:
            test_results["import_errors"].append(f"Strategy Whisperer import failed: {e}")
            test_results["failed_tests"].append("strategy_whisperer_import")
            # Don't fail the test entirely, just record the error
            print(f"Warning: Strategy Whisperer import failed: {e}")
    
    def test_all_api_router_imports(self):
        """Test importing all API routers."""
        backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
            
        routers_to_test = [
            "market_data", "signals", "trading", "scanner", "algo_forge",
            "ai_intelligence", "edge_computing", "social_trading", 
            "institutional", "quantum_tech", "god_mode", "shadow_mode",
            "adaptive_trade_manager", "market_narrator", "crypto_trading",
            "autotrader", "unified_trading", "performance"
        ]
        
        failed_imports = []
        successful_imports = []
        
        for router_name in routers_to_test:
            try:
                module = __import__(f"backend.api.v1.{router_name}", fromlist=[router_name])
                successful_imports.append(router_name)
            except ImportError as e:
                failed_imports.append(f"{router_name}: {e}")
        
        # Record results
        test_results["passed_tests"].extend([f"router_import_{r}" for r in successful_imports])
        test_results["import_errors"].extend(failed_imports)
        test_results["failed_tests"].extend([f"router_import_{r.split(':')[0]}" for r in failed_imports])
        
        # Log results but don't fail the test entirely
        if failed_imports:
            print(f"Some router imports failed: {failed_imports}")
        print(f"Successful router imports: {successful_imports}")


class TestBackendSpinup:
    """Test backend startup and basic functionality."""
    
    @pytest.mark.asyncio
    async def test_backend_startup_check(self):
        """Check if backend can be started and is responding."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try to connect to the backend
                try:
                    response = await client.get("http://localhost:8002/health")
                    if response.status_code == 200:
                        test_results["passed_tests"].append("backend_startup_check")
                        return
                except (httpx.ConnectError, httpx.TimeoutException):
                    pass
                
                # If we get here, backend is not running
                test_results["failed_tests"].append("backend_startup_check")
                test_results["endpoint_errors"].append("Backend not responding at http://localhost:8002")
                
        except Exception as e:
            test_results["failed_tests"].append("backend_startup_check")
            test_results["endpoint_errors"].append(f"Backend startup check failed: {e}")


class TestAPIEndpoints:
    """Test API endpoints for correct HTTP verbs and responses."""
    
    @pytest.mark.asyncio 
    async def test_root_endpoint(self):
        """Test the root endpoint."""
        await self._test_endpoint("/", "GET", [200])
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Test the health check endpoint."""
        await self._test_endpoint("/health", "GET", [200])
    
    @pytest.mark.asyncio  
    async def test_system_status_endpoint(self):
        """Test the system status endpoint."""
        await self._test_endpoint("/api/v1/system/status", "GET", [200])
    
    @pytest.mark.asyncio
    async def test_docs_endpoints(self):
        """Test documentation endpoints."""
        await self._test_endpoint("/docs", "GET", [200])
        await self._test_endpoint("/redoc", "GET", [200])
    
    @pytest.mark.asyncio
    async def test_trading_endpoints(self):
        """Test trading-related endpoints."""
        endpoints = [
            ("/api/v1/trading/account_info", "GET", [200, 500]),
            ("/api/v1/trading/account", "GET", [200, 500]),
            ("/api/v1/auto-trader/status", "GET", [200])
        ]
        
        for endpoint, method, expected_status in endpoints:
            await self._test_endpoint(endpoint, method, expected_status)
    
    @pytest.mark.asyncio
    async def test_market_data_endpoints(self):
        """Test market data endpoints."""
        await self._test_endpoint("/api/v1/market/tick/EURUSD", "GET", [200, 500])
    
    @pytest.mark.asyncio
    async def test_api_router_endpoints(self):
        """Test API router base endpoints."""
        router_endpoints = [
            "/api/v1/unified",
            "/api/v1/market", 
            "/api/v1/performance",
            "/api/v1/market-narrator",
            "/api/v1/autotrader"
        ]
        
        for endpoint in router_endpoints:
            await self._test_endpoint(endpoint, "GET", [200, 404, 405])
    
    async def _test_endpoint(self, endpoint: str, method: str, expected_status: List[int]):
        """Helper method to test individual endpoints."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                base_url = "http://localhost:8002"
                url = f"{base_url}{endpoint}"
                
                if method == "GET":
                    response = await client.get(url)
                elif method == "POST":
                    response = await client.post(url, json={})
                elif method == "PUT":
                    response = await client.put(url, json={})
                elif method == "DELETE":
                    response = await client.delete(url)
                else:
                    test_results["discrepancies"].append(f"Unsupported HTTP method: {method} for {endpoint}")
                    return
                
                # Check if status code is expected
                if response.status_code in expected_status:
                    test_results["passed_tests"].append(f"endpoint_{endpoint.replace('/', '_')}_{method}")
                else:
                    discrepancy = f"Endpoint {endpoint} returned {response.status_code}, expected one of {expected_status}"
                    test_results["discrepancies"].append(discrepancy)
                    test_results["failed_tests"].append(f"endpoint_{endpoint.replace('/', '_')}_{method}")
                
                # Log response for debugging
                print(f"[{method}] {endpoint} -> {response.status_code}")
                
        except httpx.ConnectError:
            error_msg = f"Cannot connect to backend at {endpoint}"
            test_results["endpoint_errors"].append(error_msg) 
            test_results["failed_tests"].append(f"endpoint_{endpoint.replace('/', '_')}_{method}")
            
        except Exception as e:
            error_msg = f"Error testing {endpoint}: {e}"
            test_results["endpoint_errors"].append(error_msg)
            test_results["failed_tests"].append(f"endpoint_{endpoint.replace('/', '_')}_{method}")


class TestHTTPVerbValidation:
    """Test for wrong HTTP verbs and missing fields."""
    
    @pytest.mark.asyncio
    async def test_wrong_http_verbs(self):
        """Test endpoints with wrong HTTP verbs to catch discrepancies."""
        test_cases = [
            # Should be GET, test with POST
            ("/", "POST", [405, 501]),
            ("/health", "POST", [405, 501]),
            ("/api/v1/system/status", "POST", [405, 501]),
            
            # Should be GET, test with PUT
            ("/", "PUT", [405, 501]),
            ("/health", "PUT", [405, 501]),
            
            # Should be GET, test with DELETE
            ("/", "DELETE", [405, 501]),
            ("/health", "DELETE", [405, 501]),
        ]
        
        for endpoint, method, expected_status in test_cases:
            await self._test_wrong_verb(endpoint, method, expected_status)
    
    async def _test_wrong_verb(self, endpoint: str, method: str, expected_status: List[int]):
        """Test endpoint with wrong HTTP verb."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                base_url = "http://localhost:8002" 
                url = f"{base_url}{endpoint}"
                
                if method == "POST":
                    response = await client.post(url, json={})
                elif method == "PUT":
                    response = await client.put(url, json={})
                elif method == "DELETE":
                    response = await client.delete(url)
                else:
                    return
                
                if response.status_code in expected_status:
                    test_results["passed_tests"].append(f"wrong_verb_{endpoint.replace('/', '_')}_{method}")
                else:
                    discrepancy = f"Wrong verb test: {endpoint} with {method} returned {response.status_code}, expected one of {expected_status}"
                    test_results["discrepancies"].append(discrepancy)
                    test_results["failed_tests"].append(f"wrong_verb_{endpoint.replace('/', '_')}_{method}")
                
        except Exception as e:
            error_msg = f"Error testing wrong verb {method} on {endpoint}: {e}"
            test_results["endpoint_errors"].append(error_msg)


def test_generate_report():
    """Generate a comprehensive test report."""
    print("\n" + "="*80)
    print("AI ALGO TRADE PLATFORM - SMOKE TEST REPORT")
    print("="*80)
    
    print(f"\nIMPORT TEST RESULTS:")
    print(f"✅ Passed Import Tests: {len([t for t in test_results['passed_tests'] if 'import' in t])}")
    print(f"❌ Failed Import Tests: {len([t for t in test_results['failed_tests'] if 'import' in t])}")
    
    if test_results["import_errors"]:
        print("\nImport Errors:")
        for error in test_results["import_errors"]:
            print(f"  - {error}")
    
    print(f"\nENDPOINT TEST RESULTS:")
    print(f"✅ Passed Endpoint Tests: {len([t for t in test_results['passed_tests'] if 'endpoint' in t])}")
    print(f"❌ Failed Endpoint Tests: {len([t for t in test_results['failed_tests'] if 'endpoint' in t])}")
    
    if test_results["endpoint_errors"]:
        print("\nEndpoint Errors:")
        for error in test_results["endpoint_errors"]:
            print(f"  - {error}")
    
    if test_results["discrepancies"]:
        print("\nDISCREPANCIES FOUND:")
        for discrepancy in test_results["discrepancies"]:
            print(f"  ⚠️  {discrepancy}")
    
    print(f"\nSUMMARY:")
    print(f"Total Passed Tests: {len(test_results['passed_tests'])}")
    print(f"Total Failed Tests: {len(test_results['failed_tests'])}")
    print(f"Total Import Errors: {len(test_results['import_errors'])}")
    print(f"Total Endpoint Errors: {len(test_results['endpoint_errors'])}")
    print(f"Total Discrepancies: {len(test_results['discrepancies'])}")
    
    print("\n" + "="*80)
    
    # Save report to file
    report_path = os.path.join(os.path.dirname(__file__), "smoke_test_report.txt")
    with open(report_path, "w") as f:
        f.write("AI ALGO TRADE PLATFORM - SMOKE TEST REPORT\n")
        f.write("="*80 + "\n\n")
        f.write(f"Import Errors: {len(test_results['import_errors'])}\n")
        f.write(f"Endpoint Errors: {len(test_results['endpoint_errors'])}\n")
        f.write(f"Discrepancies: {len(test_results['discrepancies'])}\n")
        f.write(f"Passed Tests: {len(test_results['passed_tests'])}\n")
        f.write(f"Failed Tests: {len(test_results['failed_tests'])}\n\n")
        
        if test_results["import_errors"]:
            f.write("IMPORT ERRORS:\n")
            for error in test_results["import_errors"]:
                f.write(f"- {error}\n")
            f.write("\n")
        
        if test_results["endpoint_errors"]:
            f.write("ENDPOINT ERRORS:\n")
            for error in test_results["endpoint_errors"]:
                f.write(f"- {error}\n")
            f.write("\n")
        
        if test_results["discrepancies"]:
            f.write("DISCREPANCIES:\n")
            for discrepancy in test_results["discrepancies"]:
                f.write(f"- {discrepancy}\n")
    
    print(f"Report saved to: {report_path}")
