//+------------------------------------------------------------------+
//|                                              Sanal_SupurgeV1.mq4 |
//|                        Copyright 2021, MetaQuotes Software Corp. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2021, MetaQuotes Software Corp."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict

#include "Sanal_SupurgeV1_Functions.mqh"

//+------------------------------------------------------------------+
//| Global Variables                                                 |
//+------------------------------------------------------------------+
bool OrderTimeOk=false;
float BuyTpLevel, SellTpLevel, BuySlLevel, SellSlLevel;
double NewPositionAddLevel2Point, NewPositionAddLevel3Point, NewPositionAddLevel4Point;
double NewPositionAddLevel5Point, NewPositionAddLevel6Point, NewPositionAddLevel7Point;
double NewPositionAddLevel8Point, NewPositionAddLevel9Point, NewPositionAddLevel10Point;
double NewPositionAddLevel11Point, NewPositionAddLevel12Point, NewPositionAddLevel13Point, NewPositionAddLevel14Point;

double BuyPositionsOpenLevel1, BuyPositionsOpenLevel2, BuyPositionsOpenLevel3, BuyPositionsOpenLevel4;
double BuyPositionsOpenLevel5, BuyPositionsOpenLevel6, BuyPositionsOpenLevel7, BuyPositionsOpenLevel8;
double BuyPositionsOpenLevel9, BuyPositionsOpenLevel10, BuyPositionsOpenLevel11, BuyPositionsOpenLevel12;
double BuyPositionsOpenLevel13, BuyPositionsOpenLevel14;

double SellPositionsOpenLevel1, SellPositionsOpenLevel2, SellPositionsOpenLevel3, SellPositionsOpenLevel4;
double SellPositionsOpenLevel5, SellPositionsOpenLevel6, SellPositionsOpenLevel7, SellPositionsOpenLevel8;
double SellPositionsOpenLevel9, SellPositionsOpenLevel10, SellPositionsOpenLevel11, SellPositionsOpenLevel12;
double SellPositionsOpenLevel13, SellPositionsOpenLevel14;

bool OrderBuy1Sended=false, OrderBuy2Sended=false, OrderBuy3Sended=false, OrderBuy4Sended=false;
bool OrderBuy5Sended=false, OrderBuy6Sended=false, OrderBuy7Sended=false, OrderBuy8Sended=false;
bool OrderBuy9Sended=false, OrderBuy10Sended=false, OrderBuy11Sended=false, OrderBuy12Sended=false;
bool OrderBuy13Sended=false, OrderBuy14Sended=false;

bool OrderSell1Sended=false, OrderSell2Sended=false, OrderSell3Sended=false, OrderSell4Sended=false;
bool OrderSell5Sended=false, OrderSell6Sended=false, OrderSell7Sended=false, OrderSell8Sended=false;
bool OrderSell9Sended=false, OrderSell10Sended=false, OrderSell11Sended=false, OrderSell12Sended=false;
bool OrderSell13Sended=false, OrderSell14Sended=false;

bool OrderBuy1Ok=false, OrderBuy2Ok=false, OrderBuy3Ok=false, OrderBuy4Ok=false;
bool OrderBuy5Ok=false, OrderBuy6Ok=false, OrderBuy7Ok=false, OrderBuy8Ok=false;
bool OrderBuy9Ok=false, OrderBuy10Ok=false, OrderBuy11Ok=false, OrderBuy12Ok=false;
bool OrderBuy13Ok=false, OrderBuy14Ok=false;

bool OrderSell1Ok=false, OrderSell2Ok=false, OrderSell3Ok=false, OrderSell4Ok=false;
bool OrderSell5Ok=false, OrderSell6Ok=false, OrderSell7Ok=false, OrderSell8Ok=false;
bool OrderSell9Ok=false, OrderSell10Ok=false, OrderSell11Ok=false, OrderSell12Ok=false;
bool OrderSell13Ok=false, OrderSell14Ok=false;

double tp1point, tp2point, tp3point, tp4point, tp5point, tp6point, tp7point;
double tp8point, tp9point, tp10point, tp11point, tp12point, tp13point, tp14point;

double sl1point, sl2point, sl3point, sl4point, sl5point, sl6point, sl7point;
double sl8point, sl9point, sl10point, sl11point, sl12point, sl13point, sl14point;

int digit;
string symbol;
double ask, bid;
double reflevelbuy=0, reflevelsell=0;
int Total=1, TotalBuy=0, TotalSell=0;
double LastPositionBuyTp=0, LastPositionSellTp=0;
double LastPositionBuySl=0, LastPositionSellSl=0;
int obje=1000;
bool PivotOk=false;
int TotalBuyPoz=0, TotalSellPoz=0;

//+------------------------------------------------------------------+
//| Expert parameters                                                |
//+------------------------------------------------------------------+
extern bool BuyIslemiAc=true;
extern bool SellIslemiAc=true;

extern string PositionComment="HayaletSüpürge";
extern double PivotUst=1.8;
extern double PivotAlt=1.01;

// Order Parameters
extern bool SendOrder1=true; //1. işlemi Ac
extern double LotSize1=0.01; //1. işlem Lot
extern int tp1=1000; //1. işlem TP
extern int sl1=100; //1. işlem SL

extern bool SendOrder2=true; //2. işlemi Ac
extern double LotSize2=0.02; //2. işlem Lot
extern int NewPositionAddLevel2=100; //2 İşlem Mesafe
extern int tp2=1000; //2. işlem TP
extern int sl2=100; //2. işlem SL

extern bool SendOrder3=true; //3. işlemi Ac
extern double LotSize3=0.03; //3. işlem Lot
extern int NewPositionAddLevel3=100; //3 İşlem Mesafe
extern int tp3=1000; //3. işlem TP
extern int sl3=100; //3. işlem SL

extern bool SendOrder4=true; //4. işlemi Ac
extern double LotSize4=0.04; //4. işlem Lot
extern int NewPositionAddLevel4=100; //4 İşlem Mesafe
extern int tp4=1000; //4. işlem TP
extern int sl4=100; //4. işlem SL

extern bool SendOrder5=true; //5. işlemi Ac
extern double LotSize5=0.05; //5. işlem Lot
extern int NewPositionAddLevel5=100; //5 İşlem Mesafe
extern int tp5=1000; //5. işlem TP
extern int sl5=100; //5. işlem SL

extern bool SendOrder6=true; //6. işlemi Ac
extern double LotSize6=0.06; //6. işlem Lot
extern int NewPositionAddLevel6=100; //6 İşlem Mesafe
extern int tp6=1000; //6. işlem TP
extern int sl6=100; //6. işlem SL

extern bool SendOrder7=true; //7. işlemi Ac
extern double LotSize7=0.07; //7. işlem Lot
extern int NewPositionAddLevel7=100; //7 İşlem Mesafe
extern int tp7=1000; //7. işlem TP
extern int sl7=100; //7. işlem SL

extern bool SendOrder8=true; //8. işlemi Ac
extern double LotSize8=0.08; //8. işlem Lot
extern int NewPositionAddLevel8=100; //8 İşlem Mesafe
extern int tp8=1000; //8. işlem TP
extern int sl8=100; //8. işlem SL

extern bool SendOrder9=true; //9. işlemi Ac
extern double LotSize9=0.09; //9. işlem Lot
extern int NewPositionAddLevel9=100; //9 İşlem Mesafe
extern int tp9=1000; //9. işlem TP
extern int sl9=100; //9. işlem SL

extern bool SendOrder10=true; //10. işlemi Ac
extern double LotSize10=0.1; //10. işlem Lot
extern int NewPositionAddLevel10=100; //10 İşlem Mesafe
extern int tp10=2500; //10. işlem TP
extern int sl10=100; //10. işlem Sl

extern bool SendOrder11=true; //11. işlemi Ac
extern double LotSize11=0.1; //11. işlem Lot
extern int NewPositionAddLevel11=100; //11 İşlem Mesafe
extern int tp11=2500; //11. işlem TP
extern int sl11=100; //11. işlem Sl

extern bool SendOrder12=true; //12. işlemi Ac
extern double LotSize12=0.1; //12. işlem Lot
extern int NewPositionAddLevel12=100; //12 İşlem Mesafe
extern int tp12=2500; //12. işlem TP
extern int sl12=100; //12. işlem Sl

extern bool SendOrder13=true; //13. işlemi Ac
extern double LotSize13=0.1; //13. işlem Lot
extern int NewPositionAddLevel13=100; //13 İşlem Mesafe
extern int tp13=2500; //13. işlem TP
extern int sl13=100; //13. işlem Sl

extern bool SendOrder14=true; //14. işlemi Ac
extern double LotSize14=0.1; //14. işlem Lot
extern int NewPositionAddLevel14=100; //14 İşlem Mesafe
extern int tp14=2500; //14. işlem TP
extern int sl14=100; //14. işlem Sl

// Alert Settings
extern bool Alert3=true;
extern bool Alert4=true;
extern bool Alert5=true;

// Time Filter Settings
extern bool UseTimeLimit=false; //Zaman Filtresini Kullan
extern int DoNotOpenAfterHour=20; //Bitiş Saati
extern int DoNotOpenAfterMinutes=30; //Bitiş Dakikası
extern int DoNotOpenBeforeHour=02; //Bbaslangıç Saati
extern int DoNotOpenBeforeMinutes=30; //başlangıç Dakikası
extern bool UseTimeLimitBreak=true; //Ara Zaman Kullan
extern int DoNotOpenAfterHourBreak=12; //Ara Başlangıç Saati
extern int DoNotOpenAfterMinutesBreak=30; //Ara Başlangıç Dakikası
extern int DoNotOpenBeforeHourBreak=13; //Ara Bitiş Saati
extern int DoNotOpenBeforeMinutesBreak=30; //Ara Bitiş Dakikası

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   if(TimeCurrent()>D'02.04.2025'||AccountNumber()!=25201110) // Updated for our master account
   {
      Alert("Yazılımcınız ile irtibata geçiniz. Lisans süreniz dolmuştur");
      ExpertRemove();
      return(INIT_FAILED);
   }

   digit=Digits();
   symbol=Symbol();
   
   // Calculate position addition levels
   NewPositionAddLevel2Point=NormalizeDouble((NewPositionAddLevel2)*_Point,digit);
   NewPositionAddLevel3Point=NewPositionAddLevel2Point+NormalizeDouble((NewPositionAddLevel3)*_Point,digit);
   NewPositionAddLevel4Point=NewPositionAddLevel3Point+NormalizeDouble((NewPositionAddLevel4)*_Point,digit);
   NewPositionAddLevel5Point=NewPositionAddLevel4Point+NormalizeDouble((NewPositionAddLevel5)*_Point,digit);
   NewPositionAddLevel6Point=NewPositionAddLevel5Point+NormalizeDouble((NewPositionAddLevel6)*_Point,digit);
   NewPositionAddLevel7Point=NewPositionAddLevel6Point+NormalizeDouble((NewPositionAddLevel7)*_Point,digit);
   NewPositionAddLevel8Point=NewPositionAddLevel7Point+NormalizeDouble((NewPositionAddLevel8)*_Point,digit);
   NewPositionAddLevel9Point=NewPositionAddLevel8Point+NormalizeDouble((NewPositionAddLevel9)*_Point,digit);
   NewPositionAddLevel10Point=NewPositionAddLevel9Point+NormalizeDouble((NewPositionAddLevel10)*_Point,digit);
   NewPositionAddLevel11Point=NewPositionAddLevel10Point+NormalizeDouble((NewPositionAddLevel11)*_Point,digit);
   NewPositionAddLevel12Point=NewPositionAddLevel11Point+NormalizeDouble((NewPositionAddLevel12)*_Point,digit);
   NewPositionAddLevel13Point=NewPositionAddLevel12Point+NormalizeDouble((NewPositionAddLevel13)*_Point,digit);
   NewPositionAddLevel14Point=NewPositionAddLevel13Point+NormalizeDouble((NewPositionAddLevel14)*_Point,digit);

   // Calculate TP and SL points
   tp1point=NormalizeDouble((tp1*_Point),digit);
   tp2point=NormalizeDouble((tp2*_Point),digit);
   tp3point=NormalizeDouble((tp3*_Point),digit);
   tp4point=NormalizeDouble((tp4*_Point),digit);
   tp5point=NormalizeDouble((tp5*_Point),digit);
   tp6point=NormalizeDouble((tp6*_Point),digit);
   tp7point=NormalizeDouble((tp7*_Point),digit);
   tp8point=NormalizeDouble((tp8*_Point),digit);
   tp9point=NormalizeDouble((tp9*_Point),digit);
   tp10point=NormalizeDouble((tp10*_Point),digit);
   tp11point=NormalizeDouble((tp11*_Point),digit);
   tp12point=NormalizeDouble((tp12*_Point),digit);
   tp13point=NormalizeDouble((tp13*_Point),digit);
   tp14point=NormalizeDouble((tp14*_Point),digit);

   sl1point=NormalizeDouble((sl1*_Point),digit);
   sl2point=NormalizeDouble((sl2*_Point),digit);
   sl3point=NormalizeDouble((sl3*_Point),digit);
   sl4point=NormalizeDouble((sl4*_Point),digit);
   sl5point=NormalizeDouble((sl5*_Point),digit);
   sl6point=NormalizeDouble((sl6*_Point),digit);
   sl7point=NormalizeDouble((sl7*_Point),digit);
   sl8point=NormalizeDouble((sl8*_Point),digit);
   sl9point=NormalizeDouble((sl9*_Point),digit);
   sl10point=NormalizeDouble((sl10*_Point),digit);
   sl11point=NormalizeDouble((sl11*_Point),digit);
   sl12point=NormalizeDouble((sl12*_Point),digit);
   sl13point=NormalizeDouble((sl13*_Point),digit);
   sl14point=NormalizeDouble((sl14*_Point),digit);

   ObjectsDeleteAll(0,-1,-1);
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   ObjectsDeleteAll(0,-1,-1);
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   bid=SymbolInfoDouble(NULL,SYMBOL_BID);
   ask=SymbolInfoDouble(NULL,SYMBOL_ASK);

   FindTotalPosition();
   OrderTime();
   FindLastTp();
   CloseOrder();
   FindOrderLevel();
   TpModify();
   CalculateLine();

   PivotOk=false;
   if((TotalBuyPoz+TotalSellPoz)>0)
      PivotOk=true;

   if((TotalBuyPoz+TotalSellPoz)==0)
      if(ask<PivotUst)
         if(ask>PivotAlt)
            PivotOk=true;

   KontrolTrueFalse();

   if(PivotOk)
      OrderOpenFonction();
}

//+------------------------------------------------------------------+
//| Main Trading Functions                                           |
//+------------------------------------------------------------------+

//+------------------------------------------------------------------+
//| Close Order                                                      |
//+------------------------------------------------------------------+
void CloseOrder()
{
   string AlertCloseSell="Symbol :"+symbol+ "  Magic :"+PositionComment+"  Sell Pozisyonları Kapatıldı fiyat :"+DoubleToString(LastPositionSellTp);
   string AlertCloseBuy="Symbol :"+symbol+ "  Magic :"+PositionComment+"  Buy Pozisyonları Kapatıldı fiyat :"+DoubleToString(LastPositionBuyTp);

   if(OrderSell1Sended||OrderSell2Sended||OrderSell3Sended||OrderSell4Sended||OrderSell5Sended||OrderSell6Sended||OrderSell7Sended||OrderSell8Sended||OrderSell9Sended||OrderSell10Sended||OrderSell11Sended||OrderSell12Sended||OrderSell13Sended||OrderSell14Sended)
      if(TotalSell==0)
      {
         Print("Closed Sell Tp Gerçek islem  :"+DoubleToString(SellTpLevel));
         CloseAllSell();
         SendNotification(AlertCloseSell);
      }

   if(OrderBuy1Sended||OrderBuy2Sended||OrderBuy3Sended||OrderBuy4Sended||OrderBuy5Sended||OrderBuy6Sended||OrderBuy7Sended||OrderBuy8Sended||OrderBuy9Sended||OrderBuy10Sended||OrderBuy11Sended||OrderBuy12Sended||OrderBuy13Sended||OrderBuy14Sended)
      if(TotalBuy==0)
      {
         Print("Closed Buy Tp Gerçek islem  :"+DoubleToString(BuyTpLevel));
         CloseAllBuy();
         SendNotification(AlertCloseBuy);
      }

   if(ask<=SellTpLevel)
      if(SellTpLevel!=0)
      {
         Print("Closed Sell Tp Sanal islem  :"+DoubleToString(SellTpLevel));
         if(OrderSell3Ok==true)
            SendNotification(AlertCloseSell);
         CloseAllSell();
      }

   if(bid>=BuyTpLevel)
      if(BuyTpLevel!=0)
      {
         Print("Closed Buy Tp  Sanal islem :"+DoubleToString(BuyTpLevel));
         if(OrderBuy3Ok==true)
            SendNotification(AlertCloseBuy);
         CloseAllBuy();
      }

   if(OrderTimeOk==false)
   {
      if(TotalBuy==0)
         CloseAllBuy();
      if(TotalSell==0)
         CloseAllSell();
   }
}

//+------------------------------------------------------------------+
//| Calculate Line                                                   |
//+------------------------------------------------------------------+
void CalculateLine()
{
   string AlertBuy3="Symbol :"+symbol+ "  Magic :"+PositionComment+"  3 Nolu Buy Açıldı Fiyat "+DoubleToString(ask);
   string AlertBuy4="Symbol :"+symbol+ "  Magic :"+PositionComment+"  4 Nolu Buy Açıldı Fiyat "+DoubleToString(ask);
   string AlertBuy5="Symbol :"+symbol+ "  Magic :"+PositionComment+"  5 Nolu Buy Açıldı Fiyat "+DoubleToString(ask);

   string AlertSell3="Symbol :"+symbol+ "  Magic :"+PositionComment+"  3 Nolu Sell Açıldı Fiyat "+DoubleToString(bid);
   string AlertSell4="Symbol :"+symbol+ "  Magic :"+PositionComment+"  4 Nolu Sell Açıldı Fiyat "+DoubleToString(bid);
   string AlertSell5="Symbol :"+symbol+ "  Magic :"+PositionComment+"  5 Nolu Sell Açıldı Fiyat "+DoubleToString(bid);

   if(OrderTimeOk)
   {
      if(OrderBuy1Ok==false)
      {
         OrderBuy1Ok=true;
         BuyTpLevel=NormalizeDouble((ask+(tp1*_Point)),digit);
         BuySlLevel=NormalizeDouble((ask-(sl1*_Point)),digit);
         BuyTp();
      }

      if(OrderSell1Ok==false)
      {
         OrderSell1Ok=true;
         SellTpLevel=NormalizeDouble((bid-(tp1*_Point)),digit);
         SellSlLevel=NormalizeDouble((bid+(sl1*_Point)),digit);
         SellTp();
      }
   }

   // Buy levels 2-14
   if(OrderBuy2Ok==false && ask<=BuyPositionsOpenLevel2)
   {
      OrderBuy2Ok=true;
      BuyTpLevel=NormalizeDouble(ask+(tp2*_Point),digit);
      BuySlLevel=NormalizeDouble((ask-(sl2*_Point)),digit);
      BuyTp();
   }

   if(OrderBuy3Ok==false && ask<=BuyPositionsOpenLevel3)
   {
      OrderBuy3Ok=true;
      BuyTpLevel=NormalizeDouble(ask+(tp3*_Point),digit);
      BuySlLevel=NormalizeDouble((ask-(sl3*_Point)),digit);
      BuyTp();
      if(Alert3) SendNotification(AlertBuy3);
   }

   // Sell levels 2-14
   if(OrderSell2Ok==false && bid>=SellPositionsOpenLevel2)
   {
      OrderSell2Ok=true;
      SellTpLevel=NormalizeDouble(bid-(tp2*_Point),digit);
      SellSlLevel=NormalizeDouble(bid+(sl2*_Point),digit);
      SellTp();
   }

   if(OrderSell3Ok==false && bid>=SellPositionsOpenLevel3)
   {
      OrderSell3Ok=true;
      SellTpLevel=NormalizeDouble(bid-(tp3*_Point),digit);
      SellSlLevel=NormalizeDouble((bid+(sl3*_Point)),digit);
      SellTp();
      if(Alert3) SendNotification(AlertSell3);
   }
}

//+------------------------------------------------------------------+
//| Find Order Level                                                 |
//+------------------------------------------------------------------+
void FindOrderLevel()
{
   if(reflevelbuy==0)
   {
      reflevelbuy=ask;
      BuyPositionsOpenLevel1=(reflevelbuy);
      BuyPositionsOpenLevel2=(reflevelbuy-NewPositionAddLevel2Point);
      BuyPositionsOpenLevel3=(reflevelbuy-NewPositionAddLevel3Point);
      BuyPositionsOpenLevel4=(reflevelbuy-NewPositionAddLevel4Point);
      BuyPositionsOpenLevel5=(reflevelbuy-NewPositionAddLevel5Point);
      BuyPositionsOpenLevel6=(reflevelbuy-NewPositionAddLevel6Point);
      BuyPositionsOpenLevel7=(reflevelbuy-NewPositionAddLevel7Point);
      BuyPositionsOpenLevel8=(reflevelbuy-NewPositionAddLevel8Point);
      BuyPositionsOpenLevel9=(reflevelbuy-NewPositionAddLevel9Point);
      BuyPositionsOpenLevel10=(reflevelbuy-NewPositionAddLevel10Point);
      BuyPositionsOpenLevel11=(reflevelbuy-NewPositionAddLevel11Point);
      BuyPositionsOpenLevel12=(reflevelbuy-NewPositionAddLevel12Point);
      BuyPositionsOpenLevel13=(reflevelbuy-NewPositionAddLevel13Point);
      BuyPositionsOpenLevel14=(reflevelbuy-NewPositionAddLevel14Point);
      CreateBuyLines();
      BuyTp();
   }

   if(reflevelsell==0)
   {
      reflevelsell=bid;
      SellPositionsOpenLevel1=(reflevelsell);
      SellPositionsOpenLevel2=(reflevelsell+NewPositionAddLevel2Point);
      SellPositionsOpenLevel3=(reflevelsell+NewPositionAddLevel3Point);
      SellPositionsOpenLevel4=(reflevelsell+NewPositionAddLevel4Point);
      SellPositionsOpenLevel5=(reflevelsell+NewPositionAddLevel5Point);
      SellPositionsOpenLevel6=(reflevelsell+NewPositionAddLevel6Point);
      SellPositionsOpenLevel7=(reflevelsell+NewPositionAddLevel7Point);
      SellPositionsOpenLevel8=(reflevelsell+NewPositionAddLevel8Point);
      SellPositionsOpenLevel9=(reflevelsell+NewPositionAddLevel9Point);
      SellPositionsOpenLevel10=(reflevelsell+NewPositionAddLevel10Point);
      SellPositionsOpenLevel11=(reflevelsell+NewPositionAddLevel11Point);
      SellPositionsOpenLevel12=(reflevelsell+NewPositionAddLevel12Point);
      SellPositionsOpenLevel13=(reflevelsell+NewPositionAddLevel13Point);
      SellPositionsOpenLevel14=(reflevelsell+NewPositionAddLevel14Point);
      CreateSellLines();
      SellTp();
   }
}

//+------------------------------------------------------------------+
//| Order Open Function                                              |
//+------------------------------------------------------------------+
void OrderOpenFonction()
{
   // Buy Orders
   if(SendOrder1 && OrderBuy1Ok && OrderBuy1Sended==false)
   {
      if(OrderSend(NULL,OP_BUY,LotSize1,ask,0,ask-sl1point,ask+tp1point,PositionComment,0,0,clrNONE))
         OrderBuy1Sended=true;
   }

   if(SendOrder2 && OrderBuy2Ok && OrderBuy2Sended==false)
   {
      if(OrderSend(NULL,OP_BUY,LotSize2,ask,0,ask-sl2point,ask+tp2point,PositionComment,0,0,clrNONE))
         OrderBuy2Sended=true;
   }

   // Sell Orders
   if(SendOrder1 && OrderSell1Ok && OrderSell1Sended==false)
   {
      if(OrderSend(NULL,OP_SELL,LotSize1,bid,0,bid+sl1point,bid-tp1point,PositionComment,0,0,clrNONE))
         OrderSell1Sended=true;
   }

   if(SendOrder2 && OrderSell2Ok && OrderSell2Sended==false)
   {
      if(OrderSend(NULL,OP_SELL,LotSize2,bid,0,bid+sl2point,bid-tp2point,PositionComment,0,0,clrNONE))
         OrderSell2Sended=true;
   }
}

//+------------------------------------------------------------------+
//| TP Functions                                                     |
//+------------------------------------------------------------------+
void BuyTp()
{
   ObjectDelete(0,"tpbuy");
   ObjectCreate(0,"tpbuy",OBJ_TREND,0,Time[50],BuyTpLevel,(Time[1]+(50*PeriodSeconds())),BuyTpLevel);
   ObjectSetInteger(0,"tpbuy",OBJPROP_RAY,false);
   ObjectSetInteger(0,"tpbuy",OBJPROP_COLOR,clrGreenYellow);
   ObjectSetInteger(0,"tpbuy",OBJPROP_STYLE,STYLE_DOT);
   ObjectSetInteger(0,"tpbuy",OBJPROP_WIDTH,3);
}

void SellTp()
{
   ObjectDelete(0,"tpsell");
   ObjectCreate(0,"tpsell",OBJ_TREND,0,Time[50],SellTpLevel,(Time[1]+(50*PeriodSeconds())),SellTpLevel);
   ObjectSetInteger(0,"tpsell",OBJPROP_RAY,false);
   ObjectSetInteger(0,"tpsell",OBJPROP_STYLE,STYLE_DOT);
   ObjectSetInteger(0,"tpsell",OBJPROP_COLOR,clrRosyBrown);
   ObjectSetInteger(0,"tpsell",OBJPROP_WIDTH,3);
}

//+------------------------------------------------------------------+
//| Create Lines Functions                                           |
//+------------------------------------------------------------------+
void CreateBuyLines()
{
   for(int i=1; i<=14; i++)
   {
      double level = 0;
      switch(i)
      {
         case 1: level = BuyPositionsOpenLevel1; break;
         case 2: level = BuyPositionsOpenLevel2; break;
         case 3: level = BuyPositionsOpenLevel3; break;
         case 4: level = BuyPositionsOpenLevel4; break;
         case 5: level = BuyPositionsOpenLevel5; break;
         case 6: level = BuyPositionsOpenLevel6; break;
         case 7: level = BuyPositionsOpenLevel7; break;
         case 8: level = BuyPositionsOpenLevel8; break;
         case 9: level = BuyPositionsOpenLevel9; break;
         case 10: level = BuyPositionsOpenLevel10; break;
         case 11: level = BuyPositionsOpenLevel11; break;
         case 12: level = BuyPositionsOpenLevel12; break;
         case 13: level = BuyPositionsOpenLevel13; break;
         case 14: level = BuyPositionsOpenLevel14; break;
      }
      
      string objName = "objecbuy" + IntegerToString(i);
      ObjectCreate(0,objName,OBJ_TREND,0,Time[1],level,(Time[1]+(50*PeriodSeconds())),level);
      ObjectSetInteger(0,objName,OBJPROP_RAY,false);
      ObjectSetInteger(0,objName,OBJPROP_COLOR,clrGreen);
      ObjectSetInteger(0,objName,OBJPROP_WIDTH,1);
   }
   Total++;
}

void CreateSellLines()
{
   for(int i=1; i<=14; i++)
   {
      double level = 0;
      switch(i)
      {
         case 1: level = SellPositionsOpenLevel1; break;
         case 2: level = SellPositionsOpenLevel2; break;
         case 3: level = SellPositionsOpenLevel3; break;
         case 4: level = SellPositionsOpenLevel4; break;
         case 5: level = SellPositionsOpenLevel5; break;
         case 6: level = SellPositionsOpenLevel6; break;
         case 7: level = SellPositionsOpenLevel7; break;
         case 8: level = SellPositionsOpenLevel8; break;
         case 9: level = SellPositionsOpenLevel9; break;
         case 10: level = SellPositionsOpenLevel10; break;
         case 11: level = SellPositionsOpenLevel11; break;
         case 12: level = SellPositionsOpenLevel12; break;
         case 13: level = SellPositionsOpenLevel13; break;
         case 14: level = SellPositionsOpenLevel14; break;
      }
      
      string objName = "objecsell" + IntegerToString(i);
      ObjectCreate(0,objName,OBJ_TREND,0,Time[1],level,(Time[1]+(50*PeriodSeconds())),level);
      ObjectSetInteger(0,objName,OBJPROP_RAY,false);
      ObjectSetInteger(0,objName,OBJPROP_COLOR,clrRed);
      ObjectSetInteger(0,objName,OBJPROP_WIDTH,1);
   }
   Total++;
} 