#!/bin/bash

# Platform Başlatma Betiği - ICT Ultra v2 (Simple Mode)

echo "🚀 ICT Ultra v2 Platformu Başlatılıyor (Basit Mod)..."

# --- Backend Başlatma ---
echo "▶️ Backend sunucusu başlatılıyor..."
cd backend || { echo "HATA: backend dizini bulunamadı."; exit 1; }

# Gerekli basit paketleri yükle
echo "📦 Backend bağımlılıkları yükleniyor..."
pip install fastapi uvicorn

# Basit sunucuyu başlat (arka planda)
echo "🔥 Backend (simple_main.py) 8001 portunda başlatılıyor..."
python simple_main.py &
BACKEND_PID=$!
cd ..

# --- Frontend Başlatma ---
echo "▶️ Frontend sunucusu başlatılıyor..."
cd frontend || { echo "HATA: frontend dizini bulunamadı."; exit 1; }

# Node modüllerini kontrol et
if [ ! -d "node_modules" ]; then
    echo "📦 Frontend bağımlılıkları (npm) yükleniyor..."
    npm install
fi

# Frontend geliştirme sunucusunu başlat
echo "🌐 Frontend (Next.js) 3000 portunda başlatılıyor..."
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ ICT Ultra v2 Platformu Başarıyla Başlatıldı!"
echo "-------------------------------------------------"
echo "📊 Backend API: http://localhost:8001"
echo "🌐 Frontend Dashboard: http://localhost:3000"
echo "📖 API Dokümanları: http://localhost:8001/docs"
echo "-------------------------------------------------"
echo "PID'ler: Backend ($BACKEND_PID), Frontend ($FRONTEND_PID)"
echo "Durdurmak için manuel olarak terminalleri kapatın." 