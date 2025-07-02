@echo off
echo ========================================
echo AI Algo Trade - Documentation Automation
echo ========================================
echo.

cd /d "%~dp0"
cd ..\..

echo 🚀 Major Development Sonrasi Dokumantasyon Analizi
echo.
echo Bulundugunuz dizin: %CD%
echo.

echo 📋 Analiz baslatiliyor...
node docs\automation\master-doc-sync.js major

echo.
echo ✅ Analiz tamamlandi!
echo.
echo 📊 Raporlar: docs\automation\reports\
echo 📖 API Reference: docs\API_REFERENCE.md
echo 🎨 Components: docs\COMPONENTS_REFERENCE.md
echo.

pause 