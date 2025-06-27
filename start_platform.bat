@echo off
CHCP 65001 > nul
SETLOCAL ENABLEDELAYEDEXPANSION

TITLE AI Algo Trade - Platform Launcher

ECHO 🚀 AI Algo Trade Platform v2.0.0 Baslatiliyor...
ECHO =================================================

ECHO.
ECHO ▶️ 1. Backend Sunucusu Hazirlaniyor...
cd backend
IF %ERRORLEVEL% NEQ 0 (
    ECHO ❌ HATA: 'backend' dizini bulunamadi.
    GOTO END
)

:: Python sanal ortami
IF NOT EXIST venv (
    ECHO 🐍 Python sanal ortami (venv) olusturuluyor... Bu islem biraz surebilir.
    python -m venv venv >nul 2>&1
    IF %ERRORLEVEL% NEQ 0 (
        ECHO ❌ HATA: Sanal ortam olusturulamadi. Python'un PATH'de oldugundan emin olun.
        GOTO END
    )
)

:: Bagimliliklari yukle
ECHO 📦 Backend bagimliliklari (requirements.txt) yukleniyor... Bu islem biraz surebilir.
call venv\Scripts\activate
pip install -r requirements.txt >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO ❌ HATA: Backend bagimliliklari yuklenemedi.
    GOTO END
)
ECHO ✅ Backend bagimliliklari yuklendi.

:: Backend sunucusunu yeni bir pencerede baslat
ECHO 🔥 Backend sunucusu (main.py) http://localhost:8000 adresinde baslatiliyor...
start "AI Algo Trade Backend" cmd /c "venv\Scripts\python.exe main.py"
cd ..

ECHO.
ECHO ▶️ 2. Frontend Sunucusu Hazirlaniyor...
timeout /t 5 >nul
cd frontend
IF %ERRORLEVEL% NEQ 0 (
    ECHO ❌ HATA: 'frontend' dizini bulunamadi.
    GOTO END
)

:: Node.js bagimliliklari
IF NOT EXIST node_modules (
    ECHO 📦 Frontend bagimliliklari (npm) yukleniyor... Bu islem biraz surebilir.
    call npm install >nul 2>&1
    IF %ERRORLEVEL% NEQ 0 (
        ECHO ❌ HATA: Frontend bagimliliklari yuklenemedi. Node.js ve npm'in PATH'de oldugundan emin olun.
        GOTO END
    )
)
ECHO ✅ Frontend bagimliliklari yuklendi.

:: Frontend sunucusunu baslat
ECHO 🌐 Frontend (Next.js) sunucusu http://localhost:3000 adresinde baslatiliyor...
start "AI Algo Trade Frontend" cmd /c "npm run dev"
cd ..

ECHO.
ECHO 🎉 AI Algo Trade Platformu Basariyla Baslatildi!
ECHO =================================================
ECHO   📊 Backend API: http://localhost:8000
ECHO   🌐 Frontend UI: http://localhost:3000
ECHO   📖 API Dokumanlari: http://localhost:8000/docs
ECHO -------------------------------------------------
ECHO Backend ve Frontend ayri pencerelerde calisiyor.
ECHO Durdurmak icin pencereleri kapatabilirsiniz.
ECHO.

:END
pause 