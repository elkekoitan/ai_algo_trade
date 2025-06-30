#!/usr/bin/env python3
"""
Backend Startup Script with proper Python path configuration
"""
import sys
import os
from pathlib import Path

# Add project root and backend to Python path
project_root = Path(__file__).parent.parent.absolute()
backend_root = Path(__file__).parent.absolute()

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_root))

print(f"Python Path configured:")
print(f"  - Project root: {project_root}")
print(f"  - Backend root: {backend_root}")

# Now import and run the unified main
try:
    from unified_main import app
    import uvicorn
    
    print("\n✅ Starting Unified Trading Engine on http://localhost:8002")
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=True)
    
except ImportError as e:
    print(f"\n❌ Import error: {e}")
    print("\nTrying to fix imports...")
    
    # Try alternative import
    try:
        import unified_main
        import uvicorn
        
        print("\n✅ Starting server with alternative import...")
        uvicorn.run(unified_main.app, host="0.0.0.0", port=8002, reload=True)
        
    except Exception as e2:
        print(f"\n❌ Failed to start: {e2}")
        sys.exit(1)
        
except Exception as e:
    print(f"\n❌ Startup error: {e}")
    sys.exit(1) 