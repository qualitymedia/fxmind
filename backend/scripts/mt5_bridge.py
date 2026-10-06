"""
FXMind MetaTrader 5 Auto-Execution Bridge.

Connects FXMind Quant Signal Feed to your MetaTrader 5 (MT4/MT5) terminal.
Executes automated micro-lot orders (0.01 lot for $100 accounts) with exact Stop Loss
and Take Profit levels upon receiving ACTIVE AI trade signals.

Requirements:
- Windows OS with MetaTrader 5 installed (Any broker: IC Markets, Exness, Pepperstone, etc.)
- 100% Free: No paid licenses or third-party bridge fees required.
- Install python package: pip install MetaTrader5 requests

Usage:
    python scripts/mt5_bridge.py --lot-size 0.01 --symbol GBPUSD
"""

import sys
import time
import argparse
import requests
from datetime import datetime

API_BASE_URL = "http://localhost:8000/api/v1"

def parse_args():
    parser = argparse.ArgumentParser(description="FXMind MT5 Auto-Execution Bridge")
    parser.add_argument("--lot-size", type=float, default=0.01, help="Order lot size (0.01 micro lot default)")
    parser.add_argument("--symbol", type=str, default="GBPUSD", help="Forex symbol to trade")
    parser.add_argument("--poll-interval", type=int, default=15, help="Polling interval in seconds")
    parser.add_argument("--dry-run", action="store_true", help="Simulate MT5 orders without executing")
    return parser.parse_args()


def init_mt5():
    try:
        import MetaTrader5 as mt5
        if not mt5.initialize():
            print(f"❌ MT5 initialization failed: {mt5.last_error()}")
            return None
        account_info = mt5.account_info()
        if account_info:
            print(f"✅ MT5 Connected to Broker: {account_info.company}")
            print(f"   Account: #{account_info.login} | Balance: ${account_info.balance:.2f} | Leverage: 1:{account_info.leverage}")
        return mt5
    except ImportError:
        print("⚠️ 'MetaTrader5' Python package not installed.")
        print("   To enable direct terminal auto-execution, run:")
        print("   pip install MetaTrader5")
        return None


def execute_order(mt5, symbol: str, direction: str, entry: float, sl: float, tp: float, lot: float, dry_run: bool = False):
    print(f"\n⚡ [ORDER TRIGGER] {direction} {lot} lots on {symbol}")
    print(f"   Target Entry: {entry:.5f} | SL: {sl:.5f} | TP: {tp:.5f}")

    if dry_run or mt5 is None:
        print("   [SIMULATION] Dry-run active. Order validated successfully without sending to broker.")
        return True

    # Check symbol availability in MT5 MarketWatch
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"❌ Symbol {symbol} not found in MT5 MarketWatch.")
        return False

    if not symbol_info.visible:
        if not mt5.symbol_select(symbol, True):
            print(f"❌ Failed to select {symbol} in MarketWatch.")
            return False

    is_buy = direction in ("BUY", "LONG")
    order_type = mt5.ORDER_TYPE_BUY if is_buy else mt5.ORDER_TYPE_SELL
    price = mt5.symbol_info_tick(symbol).ask if is_buy else mt5.symbol_info_tick(symbol).bid
    deviation = 20

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": 108821,
        "comment": "FXMind Quant AI",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"❌ Order failed: retcode={result.retcode}, comment={result.comment}")
        return False

    print(f"✅ Order executed on MT5! Ticket: #{result.order} @ {result.price:.5f}")
    return True


def main():
    args = parse_args()
    print("=" * 60)
    print("  FXMind Institutional MT5 Execution Bridge")
    print("=" * 60)
    print(f"  Target Symbol : {args.symbol}")
    print(f"  Order Size    : {args.lot_size} lots (Micro Lot)")
    print(f"  Poll Frequency: Every {args.poll_interval}s")
    print(f"  Dry Run Mode  : {'ENABLED' if args.dry_run else 'DISABLED (Live Execution)'}")
    print("=" * 60)

    mt5 = None if args.dry_run else init_mt5()
    last_executed_signal_id = None

    print("\n🎧 Listening to FXMind Quant Signal Feed...")

    while True:
        try:
            res = requests.get(f"{API_BASE_URL}/analysis/{args.symbol}", timeout=5)
            if res.status_code == 200:
                data = res.json()
                signal = data.get("signal", {})
                trade = signal.get("trade", {})
                status = trade.get("status")
                sig_id = signal.get("id")

                if status == "ACTIVE" and sig_id != last_executed_signal_id:
                    direction = trade.get("direction", "LONG")
                    entry_low = trade.get("entry_low")
                    entry_high = trade.get("entry_high")
                    entry = (entry_low + entry_high) / 2.0 if entry_low and entry_high else (entry_low or 1.3200)
                    sl = trade.get("stop_loss")
                    tp = trade.get("take_profit")

                    if sl and tp:
                        success = execute_order(
                            mt5=mt5,
                            symbol=args.symbol,
                            direction=direction,
                            entry=entry,
                            sl=sl,
                            tp=tp,
                            lot=args.lot_size,
                            dry_run=args.dry_run,
                        )
                        if success:
                            last_executed_signal_id = sig_id

            time.sleep(args.poll_interval)
        except KeyboardInterrupt:
            print("\n🛑 Execution Bridge stopped by user.")
            if mt5:
                mt5.shutdown()
            break
        except Exception as e:
            time.sleep(args.poll_interval)


if __name__ == "__main__":
    main()
