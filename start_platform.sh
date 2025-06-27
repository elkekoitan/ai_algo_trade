#!/bin/bash

# ICT Ultra v2 Platform - Gelişmiş Başlatma Betiği
# Bu betik, hem backend hem de frontend sunucularını başlatır,
# sanal ortamları ve bağımlılıkları yönetir.

echo "🚀 ICT Ultra v2 Platformu Başlatılıyor..."
echo "-------------------------------------------------"

# Hata durumunda çıkış yap
set -e

# Backend'i başlatma fonksiyonu
start_backend() {
    echo "▶️ Backend sunucusu hazırlanıyor..."
    cd backend || { echo "HATA: 'backend' dizini bulunamadı."; exit 1; }

    # Python sanal ortamını kontrol et ve oluştur
    if [ ! -d "venv" ]; then
        echo "🐍 Python sanal ortamı oluşturuluyor..."
        python -m venv venv
    fi

    # Sanal ortamı aktive et
    echo "激活 Sanal ortam aktive ediliyor..."
    source venv/Scripts/activate

    # Bağımlılıkları yükle
    echo "📦 Backend bağımlılıkları (requirements.txt) yükleniyor..."
    pip install -r requirements.txt

    # Sunucuyu başlat
    echo "🔥 Backend sunucusu (simple_main.py) http://localhost:8001 adresinde başlatılıyor..."
    python simple_main.py &
    BACKEND_PID=$!
    echo "✅ Backend PID: $BACKEND_PID"
    cd ..
}

# Frontend'i başlatma fonksiyonu
start_frontend() {
    echo "-------------------------------------------------"
    echo "▶️ Frontend sunucusu hazırlanıyor..."
    cd frontend || { echo "HATA: 'frontend' dizini bulunamadı."; exit 1; }

    # Node.js bağımlılıklarını kontrol et
    if [ ! -d "node_modules" ]; then
        echo "📦 Frontend bağımlılıkları (npm) yükleniyor..."
        npm install
    fi

    # Frontend geliştirme sunucusunu başlat
    echo "🌐 Frontend (Next.js) sunucusu http://localhost:3000 adresinde başlatılıyor..."
    # 'next' komutunu doğrudan node_modules içinden çalıştırarak PATH sorununu çöz
    ./node_modules/.bin/next dev &
    FRONTEND_PID=$!
    echo "✅ Frontend PID: $FRONTEND_PID"
    cd ..
}

# Ana çalıştırma bloğu
start_backend
start_frontend

echo ""
echo "🎉 ICT Ultra v2 Platformu Başarıyla Başlatıldı!"
echo "-------------------------------------------------"
echo "   Backend API: http://localhost:8001"
echo "   Frontend UI: http://localhost:3000"
echo "   API Dokümanları: http://localhost:8001/docs"
echo "-------------------------------------------------"
echo "PID'ler: Backend ($BACKEND_PID), Frontend ($FRONTEND_PID)"
echo "Platformu durdurmak için terminalleri kapatın."
echo ""

# Betiğin açık kalmasını sağla
wait $BACKEND_PID $FRONTEND_PID 