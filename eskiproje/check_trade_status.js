/**
 * 🔍 TRADE STATUS CHECKER
 * 
 * Checks current market status and recent trades
 */

const axios = require('axios');

async function checkTradeStatus() {
  try {
    console.log('🔍 COMPREHENSIVE TRADE STATUS CHECK');
    console.log('═══════════════════════════════════════════════════════════════════════════════');
    
    // 1. Check account status
    console.log('\n💰 1. ACCOUNT STATUS:');
    const accountResponse = await axios.get('http://localhost:8081/api/account_info');
    const account = accountResponse.data;
    
    console.log(`   Login: ${account.login}`);
    console.log(`   Balance: $${account.balance.toLocaleString()}`);
    console.log(`   Equity: $${account.equity.toLocaleString()}`);
    console.log(`   Free Margin: $${account.margin_free.toLocaleString()}`);
    console.log(`   Margin Level: ${account.margin_level.toFixed(2)}%`);
    console.log(`   Trade Allowed: ${account.trade_allowed ? '✅ YES' : '❌ NO'}`);
    
    // 2. Check current positions
    console.log('\n📊 2. CURRENT POSITIONS:');
    const positionsResponse = await axios.get('http://localhost:8081/api/positions');
    const positions = positionsResponse.data;
    
    console.log(`   Total Positions: ${positions.length}`);
    
    if (positions.length > 0) {
      // Group by symbol
      const symbolCounts = {};
      let totalProfit = 0;
      
      positions.forEach(pos => {
        symbolCounts[pos.symbol] = (symbolCounts[pos.symbol] || 0) + 1;
        totalProfit += pos.profit;
      });
      
      console.log(`   Total P&L: $${totalProfit.toFixed(2)} ${totalProfit >= 0 ? '📈' : '📉'}`);
      console.log(`   Symbols breakdown:`);
      
      Object.entries(symbolCounts).forEach(([symbol, count]) => {
        const symbolPositions = positions.filter(p => p.symbol === symbol);
        const symbolProfit = symbolPositions.reduce((sum, p) => sum + p.profit, 0);
        console.log(`     ${symbol}: ${count} positions, P&L: $${symbolProfit.toFixed(2)}`);
      });
      
      // Show recent positions (last 5)
      console.log(`\n   📋 Recent Positions (Last 5):`);
      positions.slice(-5).forEach((pos, index) => {
        console.log(`     ${index + 1}. ${pos.symbol} ${pos.type === 0 ? 'BUY' : 'SELL'} ${pos.volume} lots`);
        console.log(`        Entry: ${pos.price_open} | Current: ${pos.price_current} | P&L: $${pos.profit.toFixed(2)}`);
        console.log(`        Time: ${new Date(pos.time * 1000).toLocaleString()}`);
      });
    } else {
      console.log(`   ⚠️ No open positions found`);
    }
    
    // 3. Check market data availability
    console.log('\n📈 3. MARKET DATA STATUS:');
    const symbols = ['BTCUSD', 'ETHUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD'];
    
    for (const symbol of symbols) {
      try {
        const marketResponse = await axios.get(`http://localhost:8081/api/market_data/${symbol}`);
        const data = marketResponse.data;
        
        const spread = data.ask - data.bid;
        const spreadPct = ((spread / data.bid) * 100).toFixed(4);
        
        console.log(`   ${symbol}: $${data.bid} / $${data.ask} (Spread: ${spread.toFixed(2)} / ${spreadPct}%) ✅`);
      } catch (error) {
        console.log(`   ${symbol}: ❌ Not available`);
      }
    }
    
    // 4. Test a small trade request
    console.log('\n🧪 4. TRADE EXECUTION TEST:');
    console.log('   Testing with minimal EURUSD order...');
    
    try {
      const testTradeResponse = await axios.post('http://localhost:8081/api/trade', {
        symbol: 'EURUSD',
        action: 'buy',
        volume: 0.01,
        comment: 'Test_Trade_Phase2'
      }, {
        headers: { 'Content-Type': 'application/json' },
        timeout: 10000
      });
      
      console.log(`   ✅ Trade API Response:`, JSON.stringify(testTradeResponse.data, null, 2));
      
    } catch (error) {
      console.log(`   ❌ Trade Test Failed: ${error.message}`);
      if (error.response) {
        console.log(`   Error Details:`, JSON.stringify(error.response.data, null, 2));
      }
    }
    
    // 5. Market hours check
    console.log('\n🕐 5. MARKET HOURS ANALYSIS:');
    const now = new Date();
    const utcHour = now.getUTCHours();
    const utcDay = now.getUTCDay(); // 0 = Sunday, 6 = Saturday
    
    console.log(`   Current UTC Time: ${now.toISOString()}`);
    console.log(`   UTC Hour: ${utcHour}`);
    console.log(`   UTC Day: ${utcDay} (${['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][utcDay]})`);
    
    // Forex market hours (approximate)
    let marketStatus = '';
    if (utcDay === 0 || utcDay === 6) {
      marketStatus = '🔴 WEEKEND - Forex Closed (Crypto 24/7)';
    } else if (utcDay === 1 && utcHour < 22) {
      marketStatus = '🔴 MONDAY OPENING - Forex Opening Soon';
    } else if (utcDay === 5 && utcHour > 21) {
      marketStatus = '🔴 FRIDAY CLOSING - Forex Closing Soon';
    } else if (utcHour >= 22 || utcHour < 22) {
      marketStatus = '🟢 FOREX OPEN';
    } else {
      marketStatus = '🟡 TRANSITION PERIOD';
    }
    
    console.log(`   Forex Status: ${marketStatus}`);
    console.log(`   Crypto Status: 🟢 24/7 OPEN`);
    
    // 6. Recommendations
    console.log('\n💡 6. RECOMMENDATIONS:');
    
    if (marketStatus.includes('🔴')) {
      console.log(`   ⚠️ Forex markets may be closed`);
      console.log(`   ✅ Crypto trading (BTC, ETH) should work 24/7`);
      console.log(`   💡 Try crypto symbols for testing`);
    } else {
      console.log(`   ✅ Forex markets should be open`);
      console.log(`   ✅ All symbols should be tradeable`);
    }
    
    console.log(`   🔧 If trades fail: Check MT5 Expert Advisor is running`);
    console.log(`   🔧 If no response: Restart backend services`);
    
  } catch (error) {
    console.error('❌ Status check failed:', error.message);
  }
}

// Run the check
checkTradeStatus(); 