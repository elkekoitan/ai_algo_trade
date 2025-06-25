/**
 * 🚀 LIVE CRYPTO TRADE EXECUTOR
 * 
 * Executes real BTC trade on MT5 Demo Account
 * Account: 25201110 @ Tickmill-Demo
 */

const axios = require('axios');

class CryptoTradeExecutor {
  constructor() {
    this.baseUrl = 'http://localhost:8081/api';
    this.symbol = 'BTCUSD';
    this.lotSize = 0.01; // Micro lot for safety
  }

  async executeRealCryptoTrade() {
    try {
      console.log('🚀 STARTING LIVE CRYPTO TRADE EXECUTION');
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

      // 1. Get current BTC market data
      console.log('📊 Step 1: Getting BTC market data...');
      const marketResponse = await axios.get(`${this.baseUrl}/market_data/${this.symbol}`);
      const marketData = marketResponse.data;
      
      console.log(`📈 BTC Market Data:`);
      console.log(`   Symbol: ${marketData.symbol}`);
      console.log(`   Bid: $${marketData.bid.toLocaleString()}`);
      console.log(`   Ask: $${marketData.ask.toLocaleString()}`);
      console.log(`   Spread: $${(marketData.ask - marketData.bid).toFixed(2)}`);
      console.log(`   Timestamp: ${marketData.timestamp}`);

      // 2. Get account info
      console.log('\n💰 Step 2: Checking account status...');
      const accountResponse = await axios.get(`${this.baseUrl}/account_info`);
      const accountData = accountResponse.data;
      
      console.log(`🏦 Account Info:`);
      console.log(`   Login: ${accountData.login}`);
      console.log(`   Server: ${accountData.server}`);
      console.log(`   Balance: $${accountData.balance.toLocaleString()}`);
      console.log(`   Equity: $${accountData.equity.toLocaleString()}`);
      console.log(`   Free Margin: $${accountData.margin_free.toLocaleString()}`);
      console.log(`   Leverage: 1:${accountData.leverage}`);

      // 3. Calculate trade parameters
      console.log('\n🎯 Step 3: Calculating trade parameters...');
      const currentPrice = marketData.ask; // For BUY order
      const entryPrice = currentPrice;
      
      // Calculate SL and TP (2% risk, 3:1 R:R)
      const riskPercentage = 0.02; // 2%
      const stopLossDistance = currentPrice * riskPercentage;
      const stopLoss = entryPrice - stopLossDistance;
      const takeProfit = entryPrice + (stopLossDistance * 3); // 3:1 R:R
      
      console.log(`📋 Trade Parameters:`);
      console.log(`   Entry Price: $${entryPrice.toLocaleString()}`);
      console.log(`   Stop Loss: $${stopLoss.toLocaleString()}`);
      console.log(`   Take Profit: $${takeProfit.toLocaleString()}`);
      console.log(`   Risk Distance: $${stopLossDistance.toLocaleString()}`);
      console.log(`   Risk:Reward: 1:3`);
      console.log(`   Lot Size: ${this.lotSize}`);

      // 4. Execute the trade
      console.log('\n🚀 Step 4: Executing BTC BUY trade...');
      
      const tradePayload = {
        symbol: this.symbol,
        action: 'buy',
        volume: this.lotSize,
        price: entryPrice,
        sl: stopLoss,
        tp: takeProfit,
        comment: 'Live_BTC_Trade_Phase2_Test'
      };

      console.log(`📤 Sending trade order:`, JSON.stringify(tradePayload, null, 2));

      const tradeResponse = await axios.post(`${this.baseUrl}/trade`, tradePayload, {
        headers: { 'Content-Type': 'application/json' },
        timeout: 15000
      });

      console.log('\n✅ TRADE EXECUTION RESULT:');
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      
      if (tradeResponse.data.success) {
        console.log(`🎉 TRADE SUCCESSFUL!`);
        console.log(`   Order ID: ${tradeResponse.data.order_id || tradeResponse.data.ticket}`);
        console.log(`   Symbol: ${this.symbol}`);
        console.log(`   Action: BUY`);
        console.log(`   Volume: ${this.lotSize} lots`);
        console.log(`   Entry: $${entryPrice.toLocaleString()}`);
        console.log(`   Stop Loss: $${stopLoss.toLocaleString()}`);
        console.log(`   Take Profit: $${takeProfit.toLocaleString()}`);
        console.log(`   Status: EXECUTED ✅`);
        
        // 5. Verify the position
        await this.verifyPosition();
        
      } else {
        console.log(`❌ TRADE FAILED!`);
        console.log(`   Error: ${tradeResponse.data.error || 'Unknown error'}`);
        console.log(`   Details: ${JSON.stringify(tradeResponse.data)}`);
      }

    } catch (error) {
      console.error('\n💥 TRADE EXECUTION ERROR:');
      console.error('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      console.error(`Error: ${error.message}`);
      
      if (error.response) {
        console.error(`Status: ${error.response.status}`);
        console.error(`Data: ${JSON.stringify(error.response.data)}`);
      }
    }
  }

  async verifyPosition() {
    try {
      console.log('\n🔍 Step 5: Verifying opened position...');
      
      const positionsResponse = await axios.get(`${this.baseUrl}/positions`);
      const positions = positionsResponse.data;
      
      // Find our BTC position
      const btcPositions = positions.filter(pos => pos.symbol === this.symbol);
      
      if (btcPositions.length > 0) {
        console.log(`✅ Found ${btcPositions.length} BTC position(s):`);
        
        btcPositions.forEach((pos, index) => {
          console.log(`\n   Position ${index + 1}:`);
          console.log(`     Ticket: ${pos.ticket}`);
          console.log(`     Symbol: ${pos.symbol}`);
          console.log(`     Type: ${pos.type === 0 ? 'BUY' : 'SELL'}`);
          console.log(`     Volume: ${pos.volume} lots`);
          console.log(`     Open Price: $${pos.price_open.toLocaleString()}`);
          console.log(`     Current Price: $${pos.price_current.toLocaleString()}`);
          console.log(`     Profit: $${pos.profit.toFixed(2)} ${pos.profit >= 0 ? '📈' : '📉'}`);
          console.log(`     Swap: $${pos.swap.toFixed(2)}`);
          console.log(`     Stop Loss: $${pos.sl.toLocaleString()}`);
          console.log(`     Take Profit: $${pos.tp.toLocaleString()}`);
        });
      } else {
        console.log(`⚠️ No BTC positions found. Trade may have been rejected.`);
      }
      
    } catch (error) {
      console.error(`❌ Position verification error: ${error.message}`);
    }
  }

  async showMarketStatus() {
    try {
      console.log('\n📊 CURRENT MARKET STATUS:');
      console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
      
      const symbols = ['BTCUSD', 'EURUSD', 'GBPUSD'];
      
      for (const symbol of symbols) {
        try {
          const response = await axios.get(`${this.baseUrl}/market_data/${symbol}`);
          const data = response.data;
          
          console.log(`${symbol}: Bid: ${data.bid} | Ask: ${data.ask} | Spread: ${(data.ask - data.bid).toFixed(data.symbol.includes('USD') && !data.symbol.includes('JPY') ? 5 : 2)}`);
        } catch (err) {
          console.log(`${symbol}: ❌ Not available`);
        }
      }
      
    } catch (error) {
      console.error(`Market status error: ${error.message}`);
    }
  }
}

// 🚀 EXECUTE THE TRADE
async function main() {
  const executor = new CryptoTradeExecutor();
  
  console.log('🎯 LIVE CRYPTO TRADING SESSION STARTED');
  console.log('═══════════════════════════════════════════════════════════════════════════════');
  console.log('📅 Date:', new Date().toISOString());
  console.log('🏦 Account: 25201110 @ Tickmill-Demo');
  console.log('💰 Target: BTC/USD Crypto Trade');
  console.log('⚠️  Note: This is a REAL demo trade - will execute on live demo account!');
  console.log('═══════════════════════════════════════════════════════════════════════════════');
  
  // Show market status first
  await executor.showMarketStatus();
  
  // Execute the trade
  await executor.executeRealCryptoTrade();
  
  console.log('\n🏁 TRADING SESSION COMPLETED');
  console.log('═══════════════════════════════════════════════════════════════════════════════');
}

// Run if called directly
if (require.main === module) {
  main().catch(console.error);
}

module.exports = CryptoTradeExecutor; 