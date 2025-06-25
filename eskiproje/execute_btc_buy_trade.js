const axios = require('axios');

// BTC/USD ALIŞ İŞLEMİ - GERÇEK TİCARET
async function executeBTCBuyTrade() {
    try {
        console.log('🚀 BTC/USD ALIŞ İŞLEMİ BAŞLATIYOR...');
        
        // 1. Güncel piyasa verilerini al
        const marketResponse = await axios.get('http://localhost:8081/api/market_data/BTCUSD');
        const marketData = marketResponse.data;
        
        console.log('📊 Güncel BTC/USD Verileri:');
        console.log(`   💰 Bid: $${marketData.bid}`);
        console.log(`   💰 Ask: $${marketData.ask}`);
        console.log(`   📈 Spread: $${(marketData.ask - marketData.bid).toFixed(2)}`);
        
        // 2. Hesap bilgilerini kontrol et
        const accountResponse = await axios.get('http://localhost:8081/api/account_info');
        const accountData = accountResponse.data;
        
        console.log('🏦 Demo Hesap Durumu:');
        console.log(`   💵 Balance: $${accountData.balance?.toLocaleString()}`);
        console.log(`   💎 Equity: $${accountData.equity?.toLocaleString()}`);
        console.log(`   🏢 Broker: ${accountData.company}`);
        
        // 3. İşlem parametrelerini hesapla
        const currentPrice = marketData.ask; // Alış için ask fiyatı
        const lotSize = 0.01; // Güvenli mikro lot
        const riskPercent = 1; // %1 risk
        const rewardRatio = 3; // 1:3 risk/reward
        
        // Stop Loss ve Take Profit hesaplama
        const stopLossDistance = currentPrice * 0.02; // %2 stop loss
        const stopLoss = currentPrice - stopLossDistance;
        const takeProfit = currentPrice + (stopLossDistance * rewardRatio);
        
        const tradeData = {
            symbol: 'BTCUSD',
            action: 'BUY',
            volume: lotSize,
            price: currentPrice,
            sl: stopLoss,
            tp: takeProfit,
            comment: 'ICT_ULTRA_BTC_BUY',
            magic: 12345
        };
        
        console.log('📋 İŞLEM PARAMETRELERİ:');
        console.log(`   🎯 Sembol: ${tradeData.symbol}`);
        console.log(`   📈 Yön: ${tradeData.action}`);
        console.log(`   📊 Lot: ${tradeData.volume}`);
        console.log(`   💰 Giriş: $${tradeData.price.toFixed(2)}`);
        console.log(`   🛑 Stop Loss: $${tradeData.sl.toFixed(2)}`);
        console.log(`   🎯 Take Profit: $${tradeData.tp.toFixed(2)}`);
        console.log(`   📊 Risk/Reward: 1:${rewardRatio}`);
        
        // Risk hesaplama
        const riskAmount = (accountData.balance * riskPercent) / 100;
        const potentialReward = riskAmount * rewardRatio;
        
        console.log('⚡ RİSK ANALİZİ:');
        console.log(`   🔥 Risk Miktarı: $${riskAmount.toFixed(2)} (%${riskPercent})`);
        console.log(`   💎 Potansiyel Kazanç: $${potentialReward.toFixed(2)}`);
        console.log(`   📊 Risk/Reward Oranı: 1:${rewardRatio}`);
        
        // 4. İşlemi gönder
        console.log('\n🚀 İŞLEM GÖNDERİLİYOR...');
        
        const tradeResponse = await axios.post('http://localhost:8081/api/trade', tradeData, {
            headers: {
                'Content-Type': 'application/json'
            },
            timeout: 10000
        });
        
        console.log('✅ İŞLEM SONUCU:');
        console.log(JSON.stringify(tradeResponse.data, null, 2));
        
        // 5. İşlem doğrulama
        setTimeout(async () => {
            try {
                console.log('\n🔍 İŞLEM DOĞRULAMA...');
                const positionsResponse = await axios.get('http://localhost:8081/api/positions');
                const positions = positionsResponse.data;
                
                console.log(`📊 Toplam Pozisyon Sayısı: ${positions.length}`);
                
                // BTC pozisyonlarını ara
                const btcPositions = positions.filter(pos => 
                    pos.symbol === 'BTCUSD' || pos.symbol.includes('BTC')
                );
                
                if (btcPositions.length > 0) {
                    console.log('🎯 BTC POZİSYONLARI BULUNDU:');
                    btcPositions.forEach((pos, index) => {
                        console.log(`   ${index + 1}. ${pos.symbol} - ${pos.type} - Lot: ${pos.volume} - P&L: $${pos.profit}`);
                    });
                } else {
                    console.log('⚠️  BTC pozisyonu bulunamadı. İşlem beklemede olabilir.');
                }
                
                // Son 5 pozisyonu göster
                console.log('\n📋 SON POZİSYONLAR:');
                positions.slice(-5).forEach((pos, index) => {
                    console.log(`   ${index + 1}. ${pos.symbol} - ${pos.type} - P&L: $${pos.profit?.toFixed(2)}`);
                });
                
            } catch (verifyError) {
                console.error('❌ Doğrulama hatası:', verifyError.message);
            }
        }, 3000);
        
    } catch (error) {
        console.error('❌ İŞLEM HATASI:', error.message);
        if (error.response) {
            console.error('📋 Hata Detayları:', error.response.data);
        }
    }
}

// İşlemi başlat
executeBTCBuyTrade(); 