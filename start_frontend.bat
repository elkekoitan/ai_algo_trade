@echo off
echo === AI Algo Trade Frontend Starting ===

:: Navigate to frontend directory
cd frontend

:: Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
)

:: Start frontend
echo.
echo Starting Next.js frontend on port 3000...
echo.
npm run dev

pause 