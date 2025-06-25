//+------------------------------------------------------------------+
//|                                             ICT_OrderBlock_EA.mq5 |
//|                                          ICT Ultra v2: Algo Forge |
//|                                     https://github.com/ict-ultra |
//+------------------------------------------------------------------+
#property copyright "ICT Ultra v2: Algo Forge"
#property link      "https://github.com/ict-ultra"
#property version   "1.0"
#property description "ICT Order Block trading strategy"
#property strict

// Include necessary libraries
#include <Trade/Trade.mqh>
#include <Arrays/ArrayObj.mqh>

// Input parameters
input string Symbol_Settings = "===== Symbol Settings ====="; // Symbol Settings
input string Symbol_List = "EURUSD,GBPUSD,USDJPY,XAUUSD"; // Symbol List (comma separated)
input ENUM_TIMEFRAMES Timeframe = PERIOD_H1; // Timeframe

input string OB_Settings = "===== Order Block Settings ====="; // Order Block Settings
input double MinBodySizeFactor = 0.6; // Minimum body size factor
input double MinMoveAfterFactor = 1.5; // Minimum move after factor
input int ConfirmationCandles = 3; // Confirmation candles
input int LookbackPeriod = 100; // Lookback period
input double StrengthThreshold = 0.7; // Strength threshold

input string Trade_Settings = "===== Trade Settings ====="; // Trade Settings
input double LotSize = 0.01; // Lot size
input double RiskPercent = 1.0; // Risk percent per trade
input int StopLoss = 50; // Stop loss in points (0 = no SL)
input int TakeProfit = 100; // Take profit in points
input int MaxTrades = 5; // Maximum simultaneous trades
input int MagicNumber = 222001; // Magic number

// Global variables
CTrade Trade;
int OnInit_Counter = 0;
datetime LastSignalCheck = 0;
string SymbolArray[];
int SymbolCount = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   // Set magic number for trade identification
   Trade.SetExpertMagicNumber(MagicNumber);
   
   // Parse symbol list
   SymbolCount = StringSplit(Symbol_List, ',', SymbolArray);
   if(SymbolCount == 0)
   {
      Print("Error: No symbols specified");
      return INIT_PARAMETERS_INCORRECT;
   }
   
   // Check if all symbols are available
   for(int i = 0; i < SymbolCount; i++)
   {
      string symbol = StringTrim(SymbolArray[i]);
      if(!SymbolSelect(symbol, true))
      {
         Print("Error: Symbol not found: ", symbol);
         return INIT_PARAMETERS_INCORRECT;
      }
   }
   
   // Success
   Print("ICT Order Block EA initialized successfully");
   Print("Monitoring ", SymbolCount, " symbols on ", EnumToString(Timeframe), " timeframe");
   
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   // Clean up
   Print("ICT Order Block EA deinitialized");
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   // Check signals every 60 seconds
   if(TimeCurrent() - LastSignalCheck < 60)
      return;
   
   LastSignalCheck = TimeCurrent();
   
   // Check for order blocks on each symbol
   for(int i = 0; i < SymbolCount; i++)
   {
      string symbol = StringTrim(SymbolArray[i]);
      CheckOrderBlocks(symbol);
   }
}

//+------------------------------------------------------------------+
//| Check for order blocks on a symbol                               |
//+------------------------------------------------------------------+
void CheckOrderBlocks(string symbol)
{
   // Get current price
   double ask = SymbolInfoDouble(symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(symbol, SYMBOL_BID);
   
   // Get candle data
   MqlRates rates[];
   if(CopyRates(symbol, Timeframe, 0, LookbackPeriod + ConfirmationCandles + 10, rates) <= 0)
   {
      Print("Error getting rates for ", symbol);
      return;
   }
   
   // Calculate average body size
   double totalBodySize = 0;
   for(int i = 0; i < ArraySize(rates); i++)
   {
      totalBodySize += MathAbs(rates[i].close - rates[i].open);
   }
   double avgBodySize = totalBodySize / ArraySize(rates);
   
   // Find bullish order blocks (bearish candles before bullish moves)
   for(int i = 0; i < ArraySize(rates) - ConfirmationCandles - 1; i++)
   {
      // Check if we've gone beyond the lookback period
      if(i >= LookbackPeriod)
         break;
      
      // Check if this is a bearish candle (potential bullish order block)
      bool isBearish = rates[i].close < rates[i].open;
      if(!isBearish)
         continue;
      
      // Check if body size is significant
      double bodySize = MathAbs(rates[i].close - rates[i].open);
      if(bodySize < MinBodySizeFactor * avgBodySize)
         continue;
      
      // Check if the next candles show a bullish move
      double maxClose = rates[i].close;
      for(int j = 1; j <= ConfirmationCandles; j++)
      {
         if(i + j >= ArraySize(rates))
            break;
         
         maxClose = MathMax(maxClose, rates[i + j].close);
      }
      
      // Calculate the move after the potential order block
      double moveSize = maxClose - rates[i].close;
      
      // Check if the move is significant
      if(moveSize < MinMoveAfterFactor * avgBodySize)
         continue;
      
      // Calculate strength
      double strength = MathMin(1.0, (bodySize / avgBodySize) * (moveSize / (MinMoveAfterFactor * avgBodySize)));
      
      if(strength < StrengthThreshold)
         continue;
      
      // This is a valid bullish order block
      // Check if price is near the order block
      if(bid > rates[i].low * 0.995 && bid < rates[i].low * 1.005)
      {
         // Check if we already have a trade for this order block
         if(!HasOpenTrade(symbol, rates[i].time, "bullish"))
         {
            // Open a buy trade
            OpenBuyTrade(symbol, rates[i].low, rates[i].high, strength);
         }
      }
   }
   
   // Find bearish order blocks (bullish candles before bearish moves)
   for(int i = 0; i < ArraySize(rates) - ConfirmationCandles - 1; i++)
   {
      // Check if we've gone beyond the lookback period
      if(i >= LookbackPeriod)
         break;
      
      // Check if this is a bullish candle (potential bearish order block)
      bool isBullish = rates[i].close > rates[i].open;
      if(!isBullish)
         continue;
      
      // Check if body size is significant
      double bodySize = MathAbs(rates[i].close - rates[i].open);
      if(bodySize < MinBodySizeFactor * avgBodySize)
         continue;
      
      // Check if the next candles show a bearish move
      double minClose = rates[i].close;
      for(int j = 1; j <= ConfirmationCandles; j++)
      {
         if(i + j >= ArraySize(rates))
            break;
         
         minClose = MathMin(minClose, rates[i + j].close);
      }
      
      // Calculate the move after the potential order block
      double moveSize = rates[i].close - minClose;
      
      // Check if the move is significant
      if(moveSize < MinMoveAfterFactor * avgBodySize)
         continue;
      
      // Calculate strength
      double strength = MathMin(1.0, (bodySize / avgBodySize) * (moveSize / (MinMoveAfterFactor * avgBodySize)));
      
      if(strength < StrengthThreshold)
         continue;
      
      // This is a valid bearish order block
      // Check if price is near the order block
      if(ask > rates[i].high * 0.995 && ask < rates[i].high * 1.005)
      {
         // Check if we already have a trade for this order block
         if(!HasOpenTrade(symbol, rates[i].time, "bearish"))
         {
            // Open a sell trade
            OpenSellTrade(symbol, rates[i].low, rates[i].high, strength);
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Check if we already have a trade for this order block            |
//+------------------------------------------------------------------+
bool HasOpenTrade(string symbol, datetime time, string type)
{
   for(int i = 0; i < OrdersTotal(); i++)
   {
      if(OrderSelect(i, SELECT_BY_POS, MODE_TRADES))
      {
         if(OrderMagicNumber() == MagicNumber && OrderSymbol() == symbol)
         {
            // Check if this is the same order block
            // We use the order comment to store the order block time and type
            string comment = OrderComment();
            if(StringFind(comment, "OB_" + type + "_" + TimeToString(time)) >= 0)
            {
               return true;
            }
         }
      }
   }
   
   return false;
}

//+------------------------------------------------------------------+
//| Open a buy trade based on a bullish order block                  |
//+------------------------------------------------------------------+
void OpenBuyTrade(string symbol, double obLow, double obHigh, double strength)
{
   // Check if we have reached the maximum number of trades
   if(GetOpenTradesCount() >= MaxTrades)
      return;
   
   // Calculate lot size based on risk
   double lot = LotSize;
   if(RiskPercent > 0 && StopLoss > 0)
   {
      double riskAmount = AccountBalance() * RiskPercent / 100;
      double tickValue = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
      double tickSize = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
      double pointValue = tickValue / tickSize;
      
      if(pointValue > 0)
      {
         lot = NormalizeDouble(riskAmount / (StopLoss * pointValue), 2);
         lot = MathMax(lot, SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN));
         lot = MathMin(lot, SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX));
      }
   }
   
   // Calculate stop loss and take profit
   double sl = StopLoss > 0 ? NormalizeDouble(obLow - StopLoss * SymbolInfoDouble(symbol, SYMBOL_POINT), SymbolInfoInteger(symbol, SYMBOL_DIGITS)) : 0;
   double tp = TakeProfit > 0 ? NormalizeDouble(SymbolInfoDouble(symbol, SYMBOL_ASK) + TakeProfit * SymbolInfoDouble(symbol, SYMBOL_POINT), SymbolInfoInteger(symbol, SYMBOL_DIGITS)) : 0;
   
   // Open the trade
   string comment = "ICT_OB_bullish_" + DoubleToString(strength, 2);
   Trade.Buy(lot, symbol, 0, sl, tp, comment);
   
   Print("Opened buy trade on ", symbol, " based on bullish order block with strength ", strength);
}

//+------------------------------------------------------------------+
//| Open a sell trade based on a bearish order block                 |
//+------------------------------------------------------------------+
void OpenSellTrade(string symbol, double obLow, double obHigh, double strength)
{
   // Check if we have reached the maximum number of trades
   if(GetOpenTradesCount() >= MaxTrades)
      return;
   
   // Calculate lot size based on risk
   double lot = LotSize;
   if(RiskPercent > 0 && StopLoss > 0)
   {
      double riskAmount = AccountBalance() * RiskPercent / 100;
      double tickValue = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
      double tickSize = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
      double pointValue = tickValue / tickSize;
      
      if(pointValue > 0)
      {
         lot = NormalizeDouble(riskAmount / (StopLoss * pointValue), 2);
         lot = MathMax(lot, SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN));
         lot = MathMin(lot, SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX));
      }
   }
   
   // Calculate stop loss and take profit
   double sl = StopLoss > 0 ? NormalizeDouble(obHigh + StopLoss * SymbolInfoDouble(symbol, SYMBOL_POINT), SymbolInfoInteger(symbol, SYMBOL_DIGITS)) : 0;
   double tp = TakeProfit > 0 ? NormalizeDouble(SymbolInfoDouble(symbol, SYMBOL_BID) - TakeProfit * SymbolInfoDouble(symbol, SYMBOL_POINT), SymbolInfoInteger(symbol, SYMBOL_DIGITS)) : 0;
   
   // Open the trade
   string comment = "ICT_OB_bearish_" + DoubleToString(strength, 2);
   Trade.Sell(lot, symbol, 0, sl, tp, comment);
   
   Print("Opened sell trade on ", symbol, " based on bearish order block with strength ", strength);
}

//+------------------------------------------------------------------+
//| Get the number of open trades with our magic number              |
//+------------------------------------------------------------------+
int GetOpenTradesCount()
{
   int count = 0;
   
   for(int i = 0; i < OrdersTotal(); i++)
   {
      if(OrderSelect(i, SELECT_BY_POS, MODE_TRADES))
      {
         if(OrderMagicNumber() == MagicNumber)
         {
            count++;
         }
      }
   }
   
   return count;
} 