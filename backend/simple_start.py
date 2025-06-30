import sys
import os
from pathlib import Path

# Add paths
project_root = Path(__file__).parent.parent
backend_root = Path(__file__).parent

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_root))

# Set environment variables
os.environ['MT5_LOGIN'] = '25201110'
os.environ['MT5_PASSWORD'] = 'e|([rXU1IsiM'
os.environ['MT5_SERVER'] = 'Tickmill-Demo'

print("Starting backend with paths:")
print(f"  Project: {project_root}")
print(f"  Backend: {backend_root}")

# Import and run
try:
    import uvicorn
    uvicorn.run("unified_main:app", host="0.0.0.0", port=8002, reload=False)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc() 