@echo off
chcp 65001 > nul
cls
echo ====================================================
echo       AI ALGO TRADE - PROJE BAŞLATICI
echo ====================================================
echo.

:: Python kontrolü
echo [1/4] Python kontrol ediliyor...
python --version > nul 2>&1
if errorlevel 1 (
    echo HATA: Python bulunamadı! Lütfen Python 3.8+ yükleyin
    pause
    exit /b 1
)
python --version

:: MT5 kontrolü
echo.
echo [2/4] MetaTrader5 paketi kontrol ediliyor...
python -c "import MetaTrader5; print(f'MT5 Versiyonu: {MetaTrader5.__version__}')" 2> nul
if errorlevel 1 (
    echo MT5 paketi yüklü değil, yükleniyor...
    pip install MetaTrader5
)

:: Backend başlatma
echo.
echo [3/4] Backend başlatılıyor (Port 8002)...
start "AI Algo Trade - Backend" cmd /k "cd backend && python simple_start.py"

:: Frontend başlatma
echo.
echo [4/4] Frontend başlatılıyor (Port 3000)...
start "AI Algo Trade - Frontend" cmd /k "cd frontend && npm run dev"

:: Final mesaj
echo.
echo ====================================================
echo     ✅ PROJE BAŞARIYLA BAŞLATILDI!
echo ====================================================
echo.
echo Backend:  http://localhost:8002
echo Frontend: http://localhost:3000
echo.
echo Tarayıcınızda http://localhost:3000 adresini açın
echo.
echo Kapatmak için bu pencereyi kapatın
pause > nul 