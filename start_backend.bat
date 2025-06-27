@echo off
echo Starting ICT Ultra v2 Backend Service...

cd backend
echo Installing dependencies...
pip install fastapi uvicorn python-multipart

echo Starting simple backend on port 8001...
python simple_main.py

pause 