//+------------------------------------------------------------------+
//|                                     FXMind_Signal_Copier.mq5     |
//|                        Copyright 2026, FXMind Quant Technologies |
//|                                       https://fxmind.quant       |
//+------------------------------------------------------------------+
#property copyright "FXMind Quant Technologies"
#property link      "https://fxmind.quant"
#property version   "1.00"
#property strict

#include <Trade\Trade.mqh>
CTrade trade;

//--- Expert Inputs
input group "=== Connection Settings ==="
input string   InpServerUrl       = "http://localhost:8000/api/v1"; // FXMind API Base URL
input string   InpSymbol          = "GBPUSD";                       // Target Symbol
input int      InpPollIntervalSec = 15;                             // Signal Poll Interval (Seconds)

input group "=== Risk Management ==="
input double   InpLotSize         = 0.01;                           // Micro Lot Size ($100 Capital Base)
input ulong    InpMagicNumber     = 108821;                         // EA Magic Number
input int      InpSlippage        = 20;                             // Maximum Slippage (Points)

//--- Internal State Variables
int      lastExecutedSignalId = -1;
datetime lastCheckTime        = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   trade.SetExpertMagicNumber(InpMagicNumber);
   trade.SetDeviationInPoints(InpSlippage);
   trade.SetTypeFilling(ORDER_FILLING_IOC);

   Print("=================================================");
   Print("🚀 FXMind Automated Signal Copier Initialized");
   Print("   Server URL  : ", InpServerUrl);
   Print("   Symbol      : ", InpSymbol);
   Print("   Fixed Lots  : ", InpLotSize, " (Micro Lot Protection)");
   Print("=================================================");

   EventSetTimer(InpPollIntervalSec);
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   EventKillTimer();
   Print("🛑 FXMind Copier Deactivated.");
}

//+------------------------------------------------------------------+
//| Timer function: Polls FXMind Signal API                          |
//+------------------------------------------------------------------+
void OnTimer()
{
   string url = InpServerUrl + "/analysis/" + InpSymbol;
   string headers = "Accept: application/json\r\n";
   char postData[];
   char resultData[];
   string resultHeaders;

   ResetLastError();
   int res = WebRequest("GET", url, headers, 3000, postData, resultData, resultHeaders);

   if(res == 200)
   {
      string responseJson = CharArrayToString(resultData);
      ProcessSignalJson(responseJson);
   }
   else if(res == -1)
   {
      int err = GetLastError();
      if(err == 4060) // ERR_WEBREQUEST_NOT_ALLOWED
      {
         Print("⚠️ WebRequest not allowed! Add '", InpServerUrl, "' in MT5 -> Tools -> Options -> Expert Advisors -> Allow WebRequest.");
      }
   }
}

//+------------------------------------------------------------------+
//| Simple JSON Parser & Order Execution Handler                     |
//+------------------------------------------------------------------+
void ProcessSignalJson(string json)
{
   // 1. Check if status is ACTIVE
   int statusPos = StringFind(json, "\"status\":\"ACTIVE\"");
   if(statusPos < 0) return;

   // 2. Extract Signal ID
   int idPos = StringFind(json, "\"id\":");
   int sigId = 0;
   if(idPos > 0)
   {
      string idSub = StringSubstr(json, idPos + 5, 10);
      sigId = (int)StringToInteger(idSub);
   }

   // Avoid duplicate execution
   if(sigId > 0 && sigId == lastExecutedSignalId) return;

   // 3. Extract Direction
   string direction = "LONG";
   if(StringFind(json, "\"direction\":\"SHORT\"") > 0 || StringFind(json, "\"direction\":\"SELL\"") > 0)
      direction = "SHORT";

   // 4. Extract SL & TP
   double sl = ExtractDouble(json, "\"stop_loss\":");
   double tp = ExtractDouble(json, "\"take_profit\":");

   if(sl <= 0 || tp <= 0) return;

   // 5. Execute Order
   bool success = false;
   if(direction == "LONG")
   {
      double ask = SymbolInfoDouble(InpSymbol, SYMBOL_ASK);
      success = trade.Buy(InpLotSize, InpSymbol, ask, sl, tp, "FXMind AI Long");
   }
   else
   {
      double bid = SymbolInfoDouble(InpSymbol, SYMBOL_BID);
      success = trade.Sell(InpLotSize, InpSymbol, bid, sl, tp, "FXMind AI Short");
   }

   if(success)
   {
      lastExecutedSignalId = sigId;
      Print("✅ [FXMind Auto-Trade] Executed ", direction, " ", InpLotSize, " lots on ", InpSymbol, " | SL: ", sl, " | TP: ", tp);
   }
   else
   {
      Print("❌ Order send failed: ", trade.ResultRetcodeDescription());
   }
}

//+------------------------------------------------------------------+
//| Utility to parse numeric values from JSON                        |
//+------------------------------------------------------------------+
double ExtractDouble(string json, string key)
{
   int pos = StringFind(json, key);
   if(pos < 0) return 0.0;
   int start = pos + StringLen(key);
   string sub = StringSubstr(json, start, 20);
   int end = StringFind(sub, ",");
   if(end < 0) end = StringFind(sub, "}");
   if(end > 0) sub = StringSubstr(sub, 0, end);
   return StringToDouble(sub);
}
//+------------------------------------------------------------------+
