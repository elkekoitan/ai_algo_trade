@echo off
echo ====================================================
echo       AI ALGO TRADE - PROJECT STARTUP
echo ====================================================
echo.

:: Check Python
echo [1/5] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

:: Check MetaTrader5
echo.
echo [2/5] Checking MetaTrader5 package...
python -c "import MetaTrader5; print(f'MT5 Version: {MetaTrader5.__version__}')"
if errorlevel 1 (
    echo ERROR: MetaTrader5 not found! Installing...
    pip install MetaTrader5
)

:: Test MT5 Connection
echo [1/3] Testing MT5 Connection...
python test_mt5_connection.py
if errorlevel 1 (
    echo ERROR: MT5 connection failed!
    pause
    exit /b 1
)

:: Start Backend
echo.
echo [2/3] Starting Backend (Port 8002)...
start "AI Algo Trade - Backend" cmd /k "cd backend && python main.py"

:: Wait for backend to start
echo Waiting for backend to initialize...
ping -n 10 127.0.0.1 > nul

:: Start Frontend
echo.
echo [3/3] Starting Frontend (Port 3000)...
start "AI Algo Trade - Frontend" cmd /k "cd frontend && npm run dev"

:: Final message
echo.
echo ====================================================
echo       PROJECT STARTED SUCCESSFULLY!
echo ====================================================
echo.
echo Backend:  http://localhost:8002
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8002/docs
echo.
echo Press any key to exit this window...
pause > nul 