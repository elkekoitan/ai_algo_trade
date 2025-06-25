# 🚀 ICT ULTRA PLATFORM - BAŞLATMA REHBERİ

## ⚡ HIZLI BAŞLATMA YÖNTEMLERİ

### **Windows Command Prompt (CMD) İçin:**
```bash
start_ict_platform.bat
```

### **Git Bash / PowerShell / Linux Terminal İçin:**
```bash
cd ICT_Ultra_Platform
node scripts/robust-start.js
```

### **Manuel Başlatma (Backup):**
```bash
# 1. Backend
cd backend && python production_api_server.py &

# 2. Proxy  
cd ICT_Ultra_Platform && node api-server-8081.js &

# 3. Frontend
cd ICT_Ultra_Platform/apps/web && rm -rf .next && pnpm dev
```

## 🔍 SİSTEM DURUMU KONTROLÜ

### **Health Check:**
```bash
health_check.bat        # Windows CMD
# VEYA
curl http://localhost:8001/status   # Terminal
```

### **Port Kontrolü:**
```bash
netstat -ano | findstr ":3000"
netstat -ano | findstr ":8001"  
netstat -ano | findstr ":8081"
```

## 🛑 GÜVENLİ KAPATMA

### **Otomatik Kapatma:**
```bash
stop_ict_platform.bat
```

### **Manuel Kapatma:**
```bash
taskkill /F /IM node.exe
taskkill /F /IM python.exe
```

## ⚠️ SORUN GİDERME

### **Eğer "command not found" hatası alırsanız:**
- ✅ Windows CMD kullanın (Git Bash değil)
- ✅ VEYA: `node scripts/robust-start.js` kullanın

### **Eğer port conflict varsa:**
- ✅ `stop_ict_platform.bat` çalıştırın
- ✅ 10 saniye bekleyin
- ✅ Tekrar başlatın

### **Eğer frontend compile edilmezse:**
- ✅ `rm -rf .next` komutu çalıştırın
- ✅ `pnpm install` yapın
- ✅ Tekrar başlatın

## 🎯 BAŞARI KONTROL LİSTESİ

- [ ] Backend: http://localhost:8001/status → `{"is_connected":true}`
- [ ] Proxy: http://localhost:8081/api/status → `{"is_connected":true}`  
- [ ] Frontend: http://localhost:3000 → ICT Dashboard görünür
- [ ] Dashboard: http://localhost:3000/dashboard → Trading interface aktif

## 📞 EMERGENCY RESTART

```bash
# TOTAL RESET (Son çare)
taskkill /F /IM node.exe
taskkill /F /IM python.exe
timeout /t 5
start_ict_platform.bat
```

---
**💡 TİP:** Sistem bir kez başladıktan sonra stabil çalışır. İlk başlatmada 30-45 saniye bekleyin. 