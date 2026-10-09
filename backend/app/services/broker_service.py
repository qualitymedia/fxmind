"""
Broker Auto-Execution Service (Direct API).

Enables users to connect any Forex Broker (MT5) account directly via API.
Zero Python or code required by the user — they simply input their Account Login,
Password, and Broker Server via the Web UI or API.

Features:
- Auto AI Trading on ACTIVE signals (enabled by default upon connection)
- User 1-click manual toggle (Auto vs Manual mode)
- Intelligent symbol detection (handles broker suffixes like GBPUSD.m, GBPUSDpro, etc.)
- Dynamic Filling Mode detection via order_check (resolves 10030 unsupported filling mode)
- Accurate error mapping (e.g. 10018 Market Closed, 10027 Algo Trading Disabled)
"""

from __future__ import annotations

import os
import json
import logging
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger("broker_service")

CONFIG_FILE = Path("data/broker_config.json")

# Friendly MT5 return code translations
RETCODE_MESSAGES = {
    10004: "Requote — price moved while sending order.",
    10008: "Order placed successfully.",
    10009: "Order executed and filled successfully.",
    10014: "Invalid trade volume (lot size).",
    10015: "Invalid order price.",
    10016: "Invalid stop loss or take profit level.",
    10018: "Market is currently closed (Forex markets trade Sun 22:00 UTC - Fri 22:00 UTC).",
    10019: "Insufficient margin/funds to execute this order.",
    10021: "No quote available for symbol right now.",
    10027: "Algo Trading is turned off in your MetaTrader 5 application toolbar.",
    10030: "Unsupported filling mode for this broker symbol.",
}


class BrokerExecutionService:
    def __init__(self):
        self.login: Optional[int] = None
        self.password: Optional[str] = None
        self.server: Optional[str] = None
        self.is_connected: bool = False
        self.account_info: dict = {}
        # Auto-trading ON by default — AI executes trades automatically on ACTIVE signals
        self.auto_trading_enabled: bool = True
        self._load_saved_config()

    def _load_saved_config(self) -> None:
        """Load saved credentials from data/broker_config.json."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.login = data.get("login")
                    self.password = data.get("password")
                    self.server = data.get("server")
            except Exception as e:
                logger.warning(f"Could not load broker config: {e}")

    def save_config(self, login: int, password: str, server: str) -> None:
        """Persist broker credentials locally."""
        self.login = int(login)
        self.password = password
        self.server = server.strip()

        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "login": self.login,
                "password": self.password,
                "server": self.server
            }, f, indent=2)

    def connect(self, login: int, password: str, server: str) -> dict:
        """Connect directly to MetaTrader broker account."""
        self.save_config(login, password, server)

        try:
            import MetaTrader5 as mt5

            # Initialize MT5 with credentials
            initialized = mt5.initialize(
                login=self.login,
                password=self.password,
                server=self.server
            )

            if not initialized:
                if not mt5.initialize():
                    err = mt5.last_error()
                    return {
                        "success": False,
                        "connected": False,
                        "error": f"MT5 connection failed: {err}. Ensure MetaTrader 5 is running on this PC and credentials match your broker.",
                    }

            info = mt5.account_info()
            if info:
                self.is_connected = True
                self.account_info = {
                    "login": info.login,
                    "server": info.server,
                    "company": info.company,
                    "balance": round(float(info.balance), 2),
                    "equity": round(float(info.equity), 2),
                    "currency": info.currency,
                    "leverage": info.leverage,
                }
                logger.info(f"[BrokerService] Connected to #{info.login} ({info.company}) Balance: ${info.balance:.2f}")
                return {
                    "success": True,
                    "connected": True,
                    "account": self.account_info,
                    "auto_trading": self.auto_trading_enabled,
                }
            else:
                return {
                    "success": False,
                    "connected": False,
                    "error": "MT5 terminal initialized, but could not retrieve account information. Verify account login and password.",
                }
        except ImportError:
            return {
                "success": False,
                "connected": False,
                "error": "MetaTrader5 Python package not available.",
            }
        except Exception as e:
            return {
                "success": False,
                "connected": False,
                "error": str(e),
            }

    def get_status(self) -> dict:
        """Check live connection status and refresh balance."""
        auto_connected = False
        try:
            import MetaTrader5 as mt5
            if mt5.initialize():
                info = mt5.account_info()
                if info:
                    auto_connected = not self.is_connected
                    self.is_connected = True
                    self.account_info = {
                        "login": info.login,
                        "server": info.server,
                        "company": info.company,
                        "balance": round(float(info.balance), 2),
                        "equity": round(float(info.equity), 2),
                        "currency": info.currency,
                        "leverage": info.leverage,
                    }
                    return {
                        "connected": True,
                        "auto_connected": auto_connected,
                        "account": self.account_info,
                        "auto_trading": self.auto_trading_enabled,
                    }
        except Exception:
            pass

        return {
            "connected": self.is_connected,
            "auto_connected": False,
            "account": self.account_info if self.is_connected else None,
            "configured_login": self.login,
            "configured_server": self.server,
            "auto_trading": self.auto_trading_enabled,
        }

    def _resolve_symbol(self, symbol: str, mt5) -> str:
        """Find matching symbol in MT5 (handles suffixes like GBPUSD.m, GBPUSDpro, GBPUSDraw)."""
        s_info = mt5.symbol_info(symbol)
        if s_info is not None:
            return symbol

        all_symbols = mt5.symbols_get()
        if all_symbols:
            for s in all_symbols:
                if s.name.upper() == symbol.upper():
                    return s.name
            for s in all_symbols:
                if s.name.upper().startswith(symbol.upper()):
                    return s.name
        return symbol

    def _determine_valid_filling_mode(self, symbol: str, is_buy: bool, volume: float, mt5) -> int:
        """
        Use order_check to determine the exact supported filling mode for this broker & symbol.
        Returns the first filling mode that passes broker validation without code 10030.
        """
        tick = mt5.symbol_info_tick(symbol)
        price = (tick.ask if is_buy else tick.bid) if tick else 1.0
        order_type = mt5.ORDER_TYPE_BUY if is_buy else mt5.ORDER_TYPE_SELL

        # Candidate filling modes based on symbol flags
        candidates = []
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info:
            flags = getattr(symbol_info, "filling_mode", 0)
            if flags & 1:  # SYMBOL_FILLING_FOK
                candidates.append(mt5.ORDER_FILLING_FOK)
            if flags & 2:  # SYMBOL_FILLING_IOC
                candidates.append(mt5.ORDER_FILLING_IOC)
            if flags & 4:  # SYMBOL_FILLING_BOC
                candidates.append(getattr(mt5, "ORDER_FILLING_BOC", 3))

        for fallback in [mt5.ORDER_FILLING_FOK, mt5.ORDER_FILLING_IOC, mt5.ORDER_FILLING_RETURN]:
            if fallback not in candidates:
                candidates.append(fallback)

        # Test each candidate using mt5.order_check
        for mode in candidates:
            test_req = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": float(volume),
                "type": order_type,
                "price": float(price),
                "deviation": 20,
                "magic": 108821,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mode,
            }
            check_res = mt5.order_check(test_req)
            if check_res is not None and check_res.retcode != 10030:
                logger.info(f"[BrokerService] Selected filling mode {mode} for {symbol} (check retcode: {check_res.retcode})")
                return mode

        return candidates[0] if candidates else mt5.ORDER_FILLING_FOK

    def execute_order(
        self,
        symbol: str = "GBPUSD",
        direction: str = "LONG",
        lot_size: float = 0.01,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        source: str = "manual",
    ) -> dict:
        """Send a direct execution order to the connected broker."""
        try:
            import MetaTrader5 as mt5

            if not mt5.initialize():
                return {"success": False, "error": "MT5 terminal is not running or not initialized."}

            actual_symbol = self._resolve_symbol(symbol, mt5)
            symbol_info = mt5.symbol_info(actual_symbol)
            if symbol_info is None:
                return {
                    "success": False,
                    "error": f"Symbol '{symbol}' not found in broker MarketWatch.",
                }

            if not symbol_info.visible:
                mt5.symbol_select(actual_symbol, True)

            is_buy = direction.upper() in ("BUY", "LONG")
            order_type = mt5.ORDER_TYPE_BUY if is_buy else mt5.ORDER_TYPE_SELL

            # 1. Determine verified filling mode for this broker
            filling_mode = self._determine_valid_filling_mode(actual_symbol, is_buy, lot_size, mt5)

            # 2. Get fresh live price
            tick = mt5.symbol_info_tick(actual_symbol)
            if tick is None or (is_buy and tick.ask <= 0) or (not is_buy and tick.bid <= 0):
                return {
                    "success": False,
                    "error": f"No live price quote available for {actual_symbol}. Market may be closed.",
                }

            price = tick.ask if is_buy else tick.bid

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": actual_symbol,
                "volume": float(lot_size),
                "type": order_type,
                "price": float(price),
                "sl": float(stop_loss) if stop_loss else 0.0,
                "tp": float(take_profit) if take_profit else 0.0,
                "deviation": 20,
                "magic": 108821,
                "comment": f"FXMind {'AI' if source == 'auto' else 'Manual'}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": filling_mode,
            }

            result = mt5.order_send(request)
            if result is None:
                err_code, err_msg = mt5.last_error()
                return {"success": False, "error": f"Order failed: {err_msg} (code {err_code})"}

            # Success
            if result.retcode in (mt5.TRADE_RETCODE_DONE, getattr(mt5, "TRADE_RETCODE_PLACED", 10008)):
                logger.info(
                    f"[BrokerService] [{source.upper()}] Order filled! "
                    f"Ticket: #{result.order} @ {result.price:.5f} filling={filling_mode}"
                )
                return {
                    "success": True,
                    "order_ticket": result.order,
                    "price": result.price,
                    "volume": result.volume,
                    "symbol": actual_symbol,
                    "direction": direction,
                    "source": source,
                }

            # Map error retcode to human-friendly explanation
            friendly_err = RETCODE_MESSAGES.get(result.retcode, result.comment or f"Broker error code {result.retcode}")
            return {
                "success": False,
                "retcode": result.retcode,
                "error": f"{friendly_err} (code {result.retcode})",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── Auto-Trading Control ─────────────────────────────────────────────────

    def enable_auto_trading(self) -> dict:
        """Turn on AI auto-execution (default ON)."""
        self.auto_trading_enabled = True
        logger.info("[BrokerService] Auto-trading ENABLED.")
        return {
            "success": True,
            "auto_trading": True,
            "message": "AI Auto-Trading is now ACTIVE. Trades will execute automatically on ACTIVE signals.",
        }

    def disable_auto_trading(self) -> dict:
        """Turn off AI auto-execution — user controls all trades manually."""
        self.auto_trading_enabled = False
        logger.info("[BrokerService] Auto-trading DISABLED.")
        return {
            "success": True,
            "auto_trading": False,
            "message": "AI Auto-Trading is now OFF. Trades will only be executed when you click Execute manually.",
        }

    def get_auto_trading_status(self) -> dict:
        return {
            "auto_trading": self.auto_trading_enabled,
            "broker_connected": self.is_connected or bool(self.account_info),
        }

    def calculate_dynamic_lot_size(
        self,
        stop_loss: Optional[float] = None,
        entry_price: Optional[float] = None,
        risk_pct: float = 0.01,
        trade_type: Optional[str] = None,
        is_scrap_trade: bool = False,
    ) -> float:
        """Calculate risk-managed lot size based on connected MT5 account equity and trade type."""
        equity = 3000.0
        if self.account_info and isinstance(self.account_info.get("equity"), (int, float)):
            equity = float(self.account_info["equity"])

        sl_pips = 20.0
        if stop_loss and entry_price:
            computed_pips = abs(entry_price - stop_loss) * 10000.0
            if computed_pips > 0:
                sl_pips = computed_pips

        trade_name = str(trade_type or "").upper()
        if is_scrap_trade or "SCRAP" in trade_name:
            effective_risk_pct = min(risk_pct, 0.003)
            lower_bound = 0.01
            upper_bound = 0.25
        else:
            effective_risk_pct = min(max(risk_pct, 0.003), 0.02)
            lower_bound = 0.05
            upper_bound = 2.0

        risk_amount = equity * effective_risk_pct
        computed_lots = risk_amount / (sl_pips * 10.0)
        clamped_lots = round(max(lower_bound, min(upper_bound, computed_lots)), 2)
        return clamped_lots

    def auto_execute_signal(self, signal: dict) -> dict:
        """Called by live pipeline when an ACTIVE signal fires and auto-trading is ON."""
        if not self.auto_trading_enabled:
            return {"skipped": True, "reason": "Auto-trading is disabled by user."}

        trade = signal.get("trade", {})
        if trade.get("status") != "ACTIVE":
            return {"skipped": True, "reason": "Signal is not ACTIVE."}

        direction = signal.get("bias", "NEUTRAL").upper()
        if direction not in ("BULLISH", "BEARISH"):
            return {"skipped": True, "reason": f"Non-directional bias: {direction}"}

        direction_str = "BUY" if direction == "BULLISH" else "SELL"
        symbol = signal.get("symbol", "GBPUSD")
        sl = trade.get("stop_loss")
        tp = trade.get("take_profit")
        entry_low = trade.get("entry_low")
        entry_high = trade.get("entry_high")
        trade_type = trade.get("strategy_type") or signal.get("strategy_type") or "TREND_FOLLOWING"
        is_scrap = bool(signal.get("is_scrap_trade") or trade.get("is_scrap_trade") or "SCRAP" in str(trade_type).upper())

        entry_price = ((entry_low or 0) + (entry_high or 0)) / 2.0 if entry_low and entry_high else (entry_low or entry_high or None)
        auto_lot_size = self.calculate_dynamic_lot_size(
            stop_loss=sl,
            entry_price=entry_price,
            risk_pct=0.01,
            trade_type=trade_type,
            is_scrap_trade=is_scrap,
        )

        result = self.execute_order(
            symbol=symbol,
            direction=direction_str,
            lot_size=auto_lot_size,
            stop_loss=sl,
            take_profit=tp,
            source="auto",
        )
        if result.get("success"):
            logger.info(f"[BrokerService] AI auto-trade executed: {direction_str} {symbol} ({auto_lot_size} Lots) @ {result.get('price')}")
        else:
            logger.warning(f"[BrokerService] AI auto-trade failed: {result.get('error')}")
        return result

    def check_and_close_open_positions(
        self,
        current_price: Optional[float] = None,
        high: Optional[float] = None,
        low: Optional[float] = None,
    ) -> dict:
        """Close any open MT5 positions that hit their TP or SL during the current tick."""
        try:
            import MetaTrader5 as mt5
            if not mt5.initialize():
                return {"closed": 0, "positions_checked": 0, "error": "MT5 not initialized"}

            positions = mt5.positions_get() or []
            close_count = 0
            checked = 0
            closed_tickets = []

            for pos in positions:
                checked += 1
                if pos.tp is None or pos.sl is None:
                    continue

                is_buy = pos.type == getattr(mt5, "ORDER_TYPE_BUY", 0)
                price = current_price
                if price is None:
                    tick = mt5.symbol_info_tick(pos.symbol)
                    if tick is None:
                        continue
                    price = (tick.ask + tick.bid) / 2.0

                if is_buy:
                    hit_tp = (high is not None and high >= pos.tp) or (price is not None and price >= pos.tp)
                    hit_sl = (low is not None and low <= pos.sl) or (price is not None and price <= pos.sl)
                else:
                    hit_tp = (low is not None and low <= pos.tp) or (price is not None and price <= pos.tp)
                    hit_sl = (high is not None and high >= pos.sl) or (price is not None and price >= pos.sl)

                if not (hit_tp or hit_sl):
                    continue

                close_method = getattr(mt5, "Close", None)
                if callable(close_method):
                    result = close_method(pos.ticket)
                else:
                    close_type = mt5.ORDER_TYPE_SELL if is_buy else mt5.ORDER_TYPE_BUY
                    request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": pos.symbol,
                        "volume": float(pos.volume),
                        "type": close_type,
                        "price": float(price or pos.price_current),
                        "deviation": 20,
                        "magic": 108821,
                        "comment": "Auto close on TP/SL",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_FOK,
                        "position_ticket": pos.ticket,
                    }
                    result = mt5.order_send(request)

                if result is not None:
                    close_count += 1
                    closed_tickets.append({"ticket": pos.ticket, "symbol": pos.symbol, "reason": "TP" if hit_tp else "SL"})

            return {
                "closed": close_count,
                "positions_checked": checked,
                "closed_tickets": closed_tickets,
            }
        except Exception as e:
            logger.warning(f"[BrokerService] Position close scan failed: {e}")
            return {"closed": 0, "positions_checked": 0, "error": str(e)}

    def get_open_positions(self) -> dict:
        """Fetch all currently open positions from MT5."""
        try:
            import MetaTrader5 as mt5
            if not mt5.initialize():
                return {"positions": [], "error": "MT5 not initialized"}
            positions = mt5.positions_get()
            if positions is None:
                return {"positions": []}
            result = []
            for p in positions:
                result.append({
                    "ticket": p.ticket,
                    "symbol": p.symbol,
                    "type": "BUY" if p.type == 0 else "SELL",
                    "volume": p.volume,
                    "open_price": round(p.price_open, 5),
                    "current_price": round(p.price_current, 5),
                    "stop_loss": round(p.sl, 5) if p.sl else None,
                    "take_profit": round(p.tp, 5) if p.tp else None,
                    "profit": round(p.profit, 2),
                    "swap": round(p.swap, 2),
                    "open_time": p.time,
                    "comment": p.comment,
                    "magic": p.magic,
                    "is_ai": p.magic == 108821,
                })
            return {"positions": result, "count": len(result)}
        except Exception as e:
            return {"positions": [], "error": str(e)}

    def get_trade_history(self, limit: int = 50) -> dict:
        """Fetch recent closed deals from MT5 history."""
        try:
            import MetaTrader5 as mt5
            from datetime import datetime, timedelta
            if not mt5.initialize():
                return {"trades": [], "error": "MT5 not initialized"}
            # Last 30 days of history
            date_from = datetime.now() - timedelta(days=30)
            deals = mt5.history_deals_get(date_from, datetime.now())
            if deals is None:
                return {"trades": []}
            result = []
            for d in list(deals)[-limit:][::-1]:  # newest first
                if d.type not in (0, 1):  # only BUY/SELL deals, skip balance/credit
                    continue
                result.append({
                    "ticket": d.ticket,
                    "order": d.order,
                    "symbol": d.symbol,
                    "type": "BUY" if d.type == 0 else "SELL",
                    "volume": d.volume,
                    "price": round(d.price, 5),
                    "profit": round(d.profit, 2),
                    "commission": round(d.commission, 2),
                    "swap": round(d.swap, 2),
                    "time": d.time,
                    "comment": d.comment,
                    "is_ai": d.magic == 108821,
                    "magic": d.magic,
                })
            total_profit = sum(t["profit"] for t in result)
            ai_trades = [t for t in result if t["is_ai"]]
            wins = [t for t in ai_trades if t["profit"] > 0]
            return {
                "trades": result,
                "count": len(result),
                "ai_trade_count": len(ai_trades),
                "total_profit": round(total_profit, 2),
                "ai_wins": len(wins),
                "ai_win_rate": round(len(wins) / len(ai_trades) * 100, 1) if ai_trades else 0,
            }
        except Exception as e:
            return {"trades": [], "error": str(e)}

    def disconnect(self) -> dict:
        """Disconnect and clear local broker session."""
        try:
            import MetaTrader5 as mt5
            mt5.shutdown()
        except Exception:
            pass
        self.is_connected = False
        self.account_info = {}
        return {"success": True, "message": "Broker disconnected."}


broker_service = BrokerExecutionService()
