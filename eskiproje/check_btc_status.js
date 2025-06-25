const axios = require('axios');

async function checkBTCStatus() {
    try {
        console.log('🔍 BTC/USD İŞLEM DURUMU KONTROLÜ');
        console.log('=' .repeat(50));
        
        // 1. Güncel BTC fiyatı
        const marketData = await axios.get('http://localhost:8081/api/market_data/BTCUSD');
        console.log('📊 Güncel BTC/USD:');
        console.log(`   💰 Bid: $${marketData.data.bid}`);
        console.log(`   💰 Ask: $${marketData.data.ask}`);
        console.log(`   📈 Spread: $${(marketData.data.ask - marketData.data.bid).toFixed(2)}`);
        
        // 2. Hesap durumu
        const accountData = await axios.get('http://localhost:8081/api/account_info');
        console.log('\n💰 Hesap Durumu:');
        console.log(`   💵 Balance: $${accountData.data.balance?.toLocaleString()}`);
        console.log(`   💎 Equity: $${accountData.data.equity?.toLocaleString()}`);
        console.log(`   📊 Profit: $${accountData.data.profit?.toLocaleString()}`);
        console.log(`   🏦 Margin Level: ${accountData.data.margin_level?.toFixed(2)}%`);
        
        // 3. Pozisyon kontrolü
        const positions = await axios.get('http://localhost:8081/api/positions');
        console.log(`\n📋 Toplam Pozisyon: ${positions.data.length}`);
        
        // BTC pozisyonlarını ara
        const btcPositions = positions.data.filter(pos => 
            pos.symbol === 'BTCUSD' || pos.symbol.includes('BTC')
        );
        
        if (btcPositions.length > 0) {
            console.log('🎯 BTC POZİSYONLARI:');
            btcPositions.forEach((pos, index) => {
                console.log(`   ${index + 1}. ${pos.symbol} - ${pos.type === 0 ? 'BUY' : 'SELL'}`);
                console.log(`      📊 Lot: ${pos.volume}`);
                console.log(`      💰 Açılış: $${pos.price_open}`);
                console.log(`      💎 Güncel: $${pos.price_current}`);
                console.log(`      📈 P&L: $${pos.profit?.toFixed(2)}`);
                console.log(`      🕒 Zaman: ${new Date(pos.time * 1000).toLocaleString()}`);
            });
        } else {
            console.log('⚠️  BTC pozisyonu bulunamadı');
        }
        
        // 4. Son 3 pozisyon
        console.log('\n📋 SON 3 POZİSYON:');
        const lastPositions = positions.data.slice(-3);
        lastPositions.forEach((pos, index) => {
            console.log(`   ${index + 1}. ${pos.symbol} - ${pos.type === 0 ? 'BUY' : 'SELL'} - P&L: $${pos.profit?.toFixed(2)}`);
        });
        
        // 5. İşlem analizi
        console.log('\n🎯 İŞLEM ANALİZİ:');
        console.log(`   📊 Giriş Fiyatımız: $105,317.42`);
        console.log(`   💰 Güncel Ask: $${marketData.data.ask}`);
        console.log(`   📈 Fark: $${(marketData.data.ask - 105317.42).toFixed(2)}`);
        console.log(`   🎯 Take Profit: $111,636.47`);
        console.log(`   🛑 Stop Loss: $103,211.07`);
        
        if (marketData.data.ask > 105317.42) {
            console.log('   ✅ Pozisyon KAR EDİYOR!');
        } else {
            console.log('   ⚠️  Pozisyon zarar ediyor');
        }
        
    } catch (error) {
        console.error('❌ Hata:', error.message);
    }
}

checkBTCStatus(); 