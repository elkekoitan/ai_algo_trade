//+------------------------------------------------------------------+
//|                                        Sanal_SupurgeV1_Functions.mqh |
//|                        Helper functions for Sanal Süpürge V1    |
//+------------------------------------------------------------------+

//+------------------------------------------------------------------+
//| Find Total Position                                              |
//+------------------------------------------------------------------+
void FindTotalPosition()
{
   TotalBuy=0;
   TotalSell=0;
   TotalBuyPoz=0;
   TotalSellPoz=0;

   for(int yy=0; yy<OrdersTotal(); yy++)
   {
      if(OrderSelect(yy,SELECT_BY_POS))
      {
         if(OrderSymbol()==symbol)
            if(OrderComment()==PositionComment)
            {
               if(OrderType()==ORDER_TYPE_BUY)
               {
                  TotalBuy=TotalBuy+1;
                  TotalBuyPoz=TotalBuyPoz+1;
               }

               if(OrderType()==ORDER_TYPE_SELL)
               {
                  TotalSell=TotalSell+1;
                  TotalSellPoz=TotalSellPoz+1;
               }
            }
      }
   }
}

//+------------------------------------------------------------------+
//| Order Time Check                                                 |
//+------------------------------------------------------------------+
void OrderTime()
{
   OrderTimeOk=false;

   int hour=Hour();
   int minute=Minute();

   if(hour<DoNotOpenAfterHour&&hour>DoNotOpenBeforeHour)
      OrderTimeOk=true;

   if(hour==DoNotOpenAfterHour&&hour>DoNotOpenBeforeHour)
      if(minute<DoNotOpenAfterMinutes)
         OrderTimeOk=true;

   if(hour==DoNotOpenBeforeHour&&hour<DoNotOpenAfterHour)
      if(minute>DoNotOpenBeforeMinutes)
         OrderTimeOk=true;

   if(OrderTimeOk)
      if(UseTimeLimitBreak)
      {
         if(hour>DoNotOpenAfterHourBreak&&hour<DoNotOpenBeforeHourBreak)
            OrderTimeOk=false;

         if(hour==DoNotOpenAfterHourBreak)
            if(minute>DoNotOpenAfterMinutes)
               OrderTimeOk=false;

         if(hour==DoNotOpenBeforeHourBreak)
            if(minute<DoNotOpenBeforeMinutesBreak)
               OrderTimeOk=false;
      }

   if(UseTimeLimit==false)
      OrderTimeOk=true;
}

//+------------------------------------------------------------------+
//| Find Last TP                                                     |
//+------------------------------------------------------------------+
void FindLastTp()
{
   for(int y=0; y<OrdersTotal(); y++)
   {
      if(OrderSelect(y,SELECT_BY_POS))
      {
         if(OrderSymbol()==symbol)
            if(OrderComment()==PositionComment)
            {
               if(OrderType()==ORDER_TYPE_BUY)
               {
                  LastPositionBuyTp=OrderTakeProfit();
                  LastPositionBuySl=OrderStopLoss();
               }

               if(OrderType()==ORDER_TYPE_SELL)
               {
                  LastPositionSellTp=OrderTakeProfit();
                  LastPositionSellSl=OrderStopLoss();
               }
            }
      }
   }
}

//+------------------------------------------------------------------+
//| TP Modify                                                        |
//+------------------------------------------------------------------+
void TpModify()
{
   for(int aaaaa =OrdersTotal()-1; aaaaa>=0; aaaaa--)
   {
      OrderSelect(aaaaa,SELECT_BY_POS,MODE_TRADES);
      if(OrderSymbol()==symbol)
         if(OrderComment()==PositionComment)
         {
            if(OrderType()==ORDER_TYPE_BUY)
            {
               if(LastPositionBuyTp!=0)
                  if(LastPositionBuySl!=0)
                     if(OrderTakeProfit()!=LastPositionBuyTp)
                        if(OrderStopLoss()!=LastPositionBuySl)
                        {
                           OrderModify(OrderTicket(),OrderOpenPrice(),LastPositionBuySl,LastPositionBuyTp,0,clrNONE);
                        }
            }

            if(OrderType()==ORDER_TYPE_SELL)
            {
               if(LastPositionSellTp!=0)
                  if(LastPositionSellSl!=0)
                     if(OrderTakeProfit()!=LastPositionSellTp)
                        if(OrderStopLoss()!=LastPositionSellSl)
                        {
                           OrderModify(OrderTicket(),OrderOpenPrice(),LastPositionSellSl,LastPositionSellTp,0,clrNONE);
                        }
            }
         }
   }
}

//+------------------------------------------------------------------+
//| Control True False                                               |
//+------------------------------------------------------------------+
void KontrolTrueFalse()
{
   if(BuyIslemiAc==false)
   {
      OrderBuy1Sended=true;
      OrderBuy2Sended=true;
      OrderBuy3Sended=true;
      OrderBuy4Sended=true;
      OrderBuy5Sended=true;
      OrderBuy6Sended=true;
      OrderBuy7Sended=true;
      OrderBuy8Sended=true;
      OrderBuy9Sended=true;
      OrderBuy10Sended=true;
      OrderBuy11Sended=true;
      OrderBuy12Sended=true;
      OrderBuy13Sended=true;
      OrderBuy14Sended=true;
   }

   if(SellIslemiAc==false)
   {
      OrderSell1Sended=true;
      OrderSell2Sended=true;
      OrderSell3Sended=true;
      OrderSell4Sended=true;
      OrderSell5Sended=true;
      OrderSell6Sended=true;
      OrderSell7Sended=true;
      OrderSell8Sended=true;
      OrderSell9Sended=true;
      OrderSell10Sended=true;
      OrderSell11Sended=true;
      OrderSell12Sended=true;
      OrderSell13Sended=true;
      OrderSell14Sended=true;
   }
}

//+------------------------------------------------------------------+
//| Close All Buy                                                    |
//+------------------------------------------------------------------+
void CloseAllBuy()
{
   reflevelbuy=0;
   BuyTpLevel=0;
   BuySlLevel=0;

   OrderBuy1Sended=false;
   OrderBuy2Sended=false;
   OrderBuy3Sended=false;
   OrderBuy4Sended=false;
   OrderBuy5Sended=false;
   OrderBuy6Sended=false;
   OrderBuy7Sended=false;
   OrderBuy8Sended=false;
   OrderBuy9Sended=false;
   OrderBuy10Sended=false;
   OrderBuy11Sended=false;
   OrderBuy12Sended=false;
   OrderBuy13Sended=false;
   OrderBuy14Sended=false;

   OrderBuy1Ok=false;
   OrderBuy2Ok=false;
   OrderBuy3Ok=false;
   OrderBuy4Ok=false;
   OrderBuy5Ok=false;
   OrderBuy6Ok=false;
   OrderBuy7Ok=false;
   OrderBuy8Ok=false;
   OrderBuy9Ok=false;
   OrderBuy10Ok=false;
   OrderBuy11Ok=false;
   OrderBuy12Ok=false;
   OrderBuy13Ok=false;
   OrderBuy14Ok=false;

   for(int i=1; i<=14; i++)
   {
      ObjectDelete(_Symbol,"objecbuy"+IntegerToString(i));
   }
}

//+------------------------------------------------------------------+
//| Close All Sell                                                   |
//+------------------------------------------------------------------+
void CloseAllSell()
{
   reflevelsell=0;
   SellTpLevel=0;
   SellSlLevel=0;

   OrderSell1Sended=false;
   OrderSell2Sended=false;
   OrderSell3Sended=false;
   OrderSell4Sended=false;
   OrderSell5Sended=false;
   OrderSell6Sended=false;
   OrderSell7Sended=false;
   OrderSell8Sended=false;
   OrderSell9Sended=false;
   OrderSell10Sended=false;
   OrderSell11Sended=false;
   OrderSell12Sended=false;
   OrderSell13Sended=false;
   OrderSell14Sended=false;

   OrderSell1Ok=false;
   OrderSell2Ok=false;
   OrderSell3Ok=false;
   OrderSell4Ok=false;
   OrderSell5Ok=false;
   OrderSell6Ok=false;
   OrderSell7Ok=false;
   OrderSell8Ok=false;
   OrderSell9Ok=false;
   OrderSell10Ok=false;
   OrderSell11Ok=false;
   OrderSell12Ok=false;
   OrderSell13Ok=false;
   OrderSell14Ok=false;

   for(int i=1; i<=14; i++)
   {
      ObjectDelete(_Symbol,"objecsell"+IntegerToString(i));
   }
} 