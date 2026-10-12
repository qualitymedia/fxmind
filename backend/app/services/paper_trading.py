"""
Paper Trading Simulation Engine.

Executes simulated paper trades from ACTIVE ML signals.
Tracks open positions tick-by-tick against live market prices,
determines outcomes (TARGET_HIT, STOP_HIT, EXPIRED),
computes P&L in pips and USD, and writes outcomes back to the database.

All closed trades are persisted to DB — they survive server restarts.
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Optional
from pymongo.asynchronous.database import AsyncDatabase

from app.api.v1.logs import add_system_log
from app.models.base import from_mongo
from app.models.signal import Signal
from app.services.signal_service import update_signal_outcome


class PaperTradingEngine:
    """In-memory + DB paper trading simulator."""

    def __init__(self, initial_capital: float = 100.0):
        self.initial_capital = initial_capital
        self.current_equity = initial_capital
        self.open_positions: list[dict] = []
        self.closed_positions: list[dict] = []  # In-memory cache of recent closed trades
        self._pos_counter: int = 1

    @staticmethod
    def _scrap_trade_value(value: float, cap: float = 1.5) -> float:
        """Keep paper-trading outcomes intentionally small and easy to spot as a simulation."""
        if value == 0:
            return 0.0
        sign = 1 if value >= 0 else -1
        limited = min(abs(value), cap)
        return round(sign * limited, 2)

    def calculate_lot_size(self, stop_loss: float, entry_price: float, risk_pct: float = 0.03) -> float:
        """Calculate position lot size based on 3% account risk on $100 capital & SL distance."""
        sl_pips = abs(entry_price - stop_loss) * 10000.0
        if sl_pips <= 0:
            sl_pips = 20.0  # default 20 pips if invalid
        
        risk_amount = self.current_equity * risk_pct  # e.g. $3.00 on $100 account
        # 1.0 Lot GBPUSD = $10.00 / pip -> 0.05 Lot = $0.50 / pip
        raw_lots = risk_amount / (sl_pips * 10.0)
        # For a $100 account, clamp between 0.02 and 0.10 lots for realistic and safe sizing
        clamped_lots = round(max(0.02, min(0.10, raw_lots)), 2)
        return clamped_lots

    def open_trade(self, signal_dict: dict, db_signal_id: Optional[int] = None) -> Optional[dict]:
        """Open a paper position from an ACTIVE AI signal."""
        trade = signal_dict.get("trade", {})
        status = trade.get("status")
        direction = trade.get("direction")

        if status != "ACTIVE" or direction not in ("LONG", "SHORT"):
            return None

        # Allow multiple valid trades when each signal is a distinct profitable setup.
        # Only prevent exact duplicate signal re-entry, not legitimate multi-entry trading.
        symbol = signal_dict.get("symbol", "GBPUSD")

        sig_id = db_signal_id or signal_dict.get("id")
        if sig_id and any(p.get("signal_id") == sig_id for p in self.open_positions):
            return None

        entry_low = trade.get("entry_low")
        entry_high = trade.get("entry_high")
        stop_loss = trade.get("stop_loss")
        take_profit = trade.get("take_profit")

        if not stop_loss or not take_profit:
            return None

        # Validate TP/SL direction is correct
        if entry_low and entry_high:
            entry_price = round((entry_low + entry_high) / 2.0, 5)
        elif entry_low:
            entry_price = round(entry_low, 5)
        else:
            entry_price = round(stop_loss + 0.0020 if direction == "LONG" else stop_loss - 0.0020, 5)

        # Sanity check: TP must be further from entry than SL in the correct direction
        if direction == "LONG":
            if take_profit <= entry_price:
                add_system_log("PAPER_TRADING", f"Skipping LONG trade: TP ({take_profit:.5f}) <= entry ({entry_price:.5f})", "WARNING")
                return None
            if stop_loss >= entry_price:
                add_system_log("PAPER_TRADING", f"Skipping LONG trade: SL ({stop_loss:.5f}) >= entry ({entry_price:.5f})", "WARNING")
                return None
        else:  # SHORT
            if take_profit >= entry_price:
                add_system_log("PAPER_TRADING", f"Skipping SHORT trade: TP ({take_profit:.5f}) >= entry ({entry_price:.5f})", "WARNING")
                return None
            if stop_loss <= entry_price:
                add_system_log("PAPER_TRADING", f"Skipping SHORT trade: SL ({stop_loss:.5f}) <= entry ({entry_price:.5f})", "WARNING")
                return None

        sig_id = db_signal_id or signal_dict.get("id") or self._pos_counter
        lot_size = self.calculate_lot_size(stop_loss, entry_price)
        pip_value_usd = lot_size * 10.0  # $0.50/pip on 0.05 lot

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=6)

        pos = {
            "position_id": f"PAPER-{self._pos_counter}",
            "signal_id": sig_id,
            "symbol": symbol,
            "direction": direction,
            "strategy_type": trade.get("strategy_type", "TREND_FOLLOWING"),
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "lot_size": lot_size,
            "pip_value_usd": pip_value_usd,
            "risk_reward": trade.get("risk_reward", 2.0),
            "opened_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
            "duration_hours": 6,
            "status": "OPEN",
            "current_price": entry_price,
            "unrealized_pnl_pips": 0.0,
            "unrealized_pnl_usd": 0.0,
            "model_confidence": signal_dict.get("confidence", 0.0),
            "trade_mode": "SCRAP",
            "is_scrap_trade": True,
        }

        self._pos_counter += 1
        self.open_positions.append(pos)

        add_system_log(
            "PAPER_TRADING",
            f"Opened {direction} on {symbol} @ {entry_price:.5f} ({lot_size} Lots, TP: {take_profit:.5f}, SL: {stop_loss:.5f}, 6h Expiry)",
            "SUCCESS",
        )
        return pos

    async def check_and_close_positions(
        self,
        current_price: float,
        high: Optional[float] = None,
        low: Optional[float] = None,
        db: Optional[AsyncDatabase] = None,
    ) -> list[dict]:
        """
        Evaluate open paper trades against current live price.
        Closes trades that hit TP, SL, or max holding duration.
        All closures are persisted to DB immediately.
        """
        high = high or current_price
        low = low or current_price

        closed_this_tick = []
        still_open = []

        now = datetime.now(timezone.utc)

        for pos in self.open_positions:
            pos["current_price"] = current_price
            direction = pos["direction"]
            entry = pos["entry_price"]
            tp = pos["take_profit"]
            sl = pos["stop_loss"]
            pip_val = pos.get("pip_value_usd", 0.50)

            # Compute current unrealized P&L in pips and USD
            if direction == "LONG":
                pnl_pips = (current_price - entry) * 10000.0
            else:
                pnl_pips = (entry - current_price) * 10000.0

            pos["unrealized_pnl_pips"] = round(pnl_pips, 1)
            pos["unrealized_pnl_usd"] = round(pnl_pips * pip_val, 2)

            # Real-time expiration check: 6 hours from open time
            opened_at = datetime.fromisoformat(pos["opened_at"])
            if opened_at.tzinfo is None:
                opened_at = opened_at.replace(tzinfo=timezone.utc)
            else:
                opened_at = opened_at.astimezone(timezone.utc)
            elapsed_secs = (now - opened_at).total_seconds()
            is_expired = elapsed_secs >= 6 * 3600  # 6 hours

            outcome = None
            final_pnl_pips = 0.0

            if direction == "LONG":
                if high >= tp:
                    outcome = "TARGET_HIT"
                    final_pnl_pips = (tp - entry) * 10000.0
                elif low <= sl:
                    outcome = "STOP_HIT"
                    final_pnl_pips = (sl - entry) * 10000.0
                elif is_expired:
                    outcome = "EXPIRED"
                    final_pnl_pips = (current_price - entry) * 10000.0
            else:  # SHORT
                if low <= tp:
                    outcome = "TARGET_HIT"
                    final_pnl_pips = (entry - tp) * 10000.0
                elif high >= sl:
                    outcome = "STOP_HIT"
                    final_pnl_pips = (entry - sl) * 10000.0
                elif is_expired:
                    outcome = "EXPIRED"
                    final_pnl_pips = (entry - current_price) * 10000.0

            if outcome:
                if db is None or not pos.get("signal_id"):
                    add_system_log(
                        "PAPER_TRADING",
                        f"Cannot persist close for {pos.get('position_id')}; keeping it open until MongoDB is available.",
                        "ERROR",
                    )
                    still_open.append(pos)
                    continue

                try:
                    updated_signal = await update_signal_outcome(
                        signal_id=pos["signal_id"],
                        outcome=outcome,
                        pnl=final_pnl_pips,
                        db=db,
                    )
                    if updated_signal is None:
                        raise RuntimeError(
                            f"Signal ID={pos['signal_id']} was not found while saving its outcome."
                        )
                except Exception as exc:
                    add_system_log(
                        "PAPER_TRADING",
                        f"MongoDB outcome persistence failed for {pos.get('position_id')}: {exc}. "
                        "The position remains open for retry.",
                        "ERROR",
                    )
                    still_open.append(pos)
                    continue

                closed_at = datetime.now(timezone.utc).isoformat()
                capped_pips = self._scrap_trade_value(final_pnl_pips, cap=1.5)
                realized_pnl = round(capped_pips * 0.1, 2)

                pos["status"] = outcome
                pos["closed_at"] = closed_at
                pos["pnl_pips"] = round(capped_pips, 1)
                pos["realized_pnl"] = realized_pnl
                pos["trade_mode"] = "SCRAP"
                pos["is_scrap_trade"] = True
                self.current_equity += realized_pnl

                self.closed_positions.append(pos)
                closed_this_tick.append(pos)

                # Dispatch Telegram alert
                try:
                    from app.services.telegram_service import telegram_service
                    await telegram_service.send_trade_closed_alert(pos)
                except Exception as tg_err:
                    print(f"[PAPER TRADING] Telegram close alert error: {tg_err}")

                add_system_log(
                    "PAPER_TRADING",
                    f"CLOSED {direction} #{pos['position_id']} @ {current_price:.5f}. "
                    f"Outcome: {outcome}, PnL: {final_pnl_pips:+.1f} pips (${realized_pnl:+.2f}). "
                    f"Equity: ${self.current_equity:.2f}",
                    "SUCCESS" if final_pnl_pips > 0 else "WARNING",
                )
            else:
                still_open.append(pos)

        self.open_positions = still_open
        return closed_this_tick

    def get_open_positions(self) -> list[dict]:
        """Return all active paper positions."""
        return self.open_positions

    def _position_from_signal_document(self, document: dict) -> Optional[dict]:
        """Rebuild an open paper position from its durable signal document."""
        signal = from_mongo(Signal, document)
        if (
            signal is None
            or signal.status != "ACTIVE"
            or signal.outcome is not None
            or signal.direction not in ("LONG", "SHORT")
            or signal.stop_loss is None
            or signal.take_profit is None
            or (signal.entry_low is None and signal.entry_high is None)
        ):
            return None

        if signal.entry_low is not None and signal.entry_high is not None:
            entry_price = round((signal.entry_low + signal.entry_high) / 2.0, 5)
        else:
            entry_price = round(signal.entry_low or signal.entry_high or 0.0, 5)

        opened_at = signal.paper_opened_at or signal.timestamp
        if opened_at.tzinfo is None:
            opened_at = opened_at.replace(tzinfo=timezone.utc)
        else:
            opened_at = opened_at.astimezone(timezone.utc)

        lot_size = self.calculate_lot_size(signal.stop_loss, entry_price)
        expires_at = opened_at + timedelta(hours=6)
        return {
            "position_id": f"PAPER-{signal.id}",
            "signal_id": signal.id,
            "symbol": signal.symbol,
            "direction": signal.direction,
            "strategy_type": signal.strategy_type or "TREND_FOLLOWING",
            "entry_price": entry_price,
            "stop_loss": signal.stop_loss,
            "take_profit": signal.take_profit,
            "lot_size": lot_size,
            "pip_value_usd": lot_size * 10.0,
            "risk_reward": signal.risk_reward,
            "opened_at": opened_at.isoformat(),
            "expires_at": expires_at.isoformat(),
            "duration_hours": 6,
            "status": "OPEN",
            "current_price": entry_price,
            "unrealized_pnl_pips": 0.0,
            "unrealized_pnl_usd": 0.0,
            "model_confidence": signal.confidence,
            "trade_mode": "SCRAP",
            "is_scrap_trade": True,
        }

    async def restore_open_positions(self, db: AsyncDatabase) -> int:
        """Restore unfinished paper positions after a process restart."""
        cursor = db[Signal.collection].find(
            {
                "status": "ACTIVE",
                "outcome": None,
                "direction": {"$in": ["LONG", "SHORT"]},
                "stop_loss": {"$ne": None},
                "take_profit": {"$ne": None},
            }
        ).sort("timestamp", 1)
        documents = await cursor.to_list(length=None)
        positions = [
            position
            for document in documents
            if (position := self._position_from_signal_document(document)) is not None
        ]
        self.open_positions = positions
        add_system_log(
            "PAPER_TRADING",
            f"Restored {len(positions)} open paper position(s) from MongoDB.",
            "INFO",
        )
        return len(positions)

    async def get_open_positions_from_db(self, db: AsyncDatabase) -> list[dict]:
        """Return open positions from durable signals, including after a restart."""
        cursor = db[Signal.collection].find(
            {
                "status": "ACTIVE",
                "outcome": None,
                "direction": {"$in": ["LONG", "SHORT"]},
                "stop_loss": {"$ne": None},
                "take_profit": {"$ne": None},
            }
        ).sort("timestamp", 1)
        documents = await cursor.to_list(length=None)
        cached = {
            position.get("signal_id"): position for position in self.open_positions
        }
        positions = []
        for document in documents:
            position = self._position_from_signal_document(document)
            if position is not None:
                position.update(
                    {
                        key: cached[position["signal_id"]][key]
                        for key in ("current_price", "unrealized_pnl_pips", "unrealized_pnl_usd")
                        if position["signal_id"] in cached
                    }
                )
                positions.append(position)
        return positions

    async def get_history_from_db(self, db: AsyncDatabase, limit: int = 50) -> list[dict]:
        """
        Query closed trade history directly from the DB.
        Returns signals that have an outcome set (TARGET_HIT, STOP_HIT, EXPIRED).
        """
        cursor = (
            db[Signal.collection]
            .find({"outcome": {"$in": ["TARGET_HIT", "STOP_HIT", "EXPIRED"]}})
            .sort("outcome_timestamp", -1)
            .limit(limit)
        )
        signals = [
            signal
            for document in await cursor.to_list(length=limit)
            if (signal := from_mongo(Signal, document)) is not None
        ]

        history = []
        for s in signals:
            if s.entry_low is None and s.entry_high is None:
                continue  # Skip NO_TRADE signals
            
            entry_price = ((s.entry_low or 0) + (s.entry_high or 0)) / 2.0 if s.entry_low and s.entry_high else (s.entry_low or s.entry_high or 0)
            pnl_pips = s.outcome_pnl or 0.0
            realized_pnl = round(pnl_pips * 0.50, 2)  # $0.50/pip default (0.05 lot on $100)

            capped_pips = self._scrap_trade_value(pnl_pips, cap=1.5)
            realized_pnl = round(capped_pips * 0.1, 2)

            history.append({
                "position_id": f"DB-{s.id}",
                "signal_id": s.id,
                "symbol": s.symbol,
                "direction": s.direction or "LONG",
                "strategy_type": s.strategy_type,
                "entry_price": round(entry_price, 5),
                "stop_loss": s.stop_loss,
                "take_profit": s.take_profit,
                "risk_reward": s.risk_reward,
                "opened_at": s.timestamp.isoformat() if s.timestamp else None,
                "closed_at": s.outcome_timestamp.isoformat() if s.outcome_timestamp else None,
                "status": s.outcome,
                "pnl_pips": round(capped_pips, 1),
                "realized_pnl": realized_pnl,
                "trade_mode": "SCRAP",
                "is_scrap_trade": True,
                "model_confidence": s.confidence,
                "regime": s.regime,
                "session": s.session_name,
            })
        return history

    async def get_summary_from_db(self, db: AsyncDatabase) -> dict:
        """Calculate paper-trading totals from durable closed and open signals."""
        pipeline = [
            {
                "$match": {
                    "outcome": {"$in": ["TARGET_HIT", "STOP_HIT", "EXPIRED"]},
                    "$or": [
                        {"entry_low": {"$ne": None}},
                        {"entry_high": {"$ne": None}},
                    ],
                }
            },
            {
                "$project": {
                    "paper_pnl": {
                        "$max": [
                            -1.5,
                            {
                                "$min": [
                                    1.5,
                                    {"$ifNull": ["$outcome_pnl", 0.0]},
                                ]
                            },
                        ]
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_trades": {"$sum": 1},
                    "wins": {
                        "$sum": {"$cond": [{"$gt": ["$paper_pnl", 0]}, 1, 0]}
                    },
                    "gross_profit": {
                        "$sum": {
                            "$cond": [{"$gt": ["$paper_pnl", 0]}, "$paper_pnl", 0]
                        }
                    },
                    "gross_loss": {
                        "$sum": {
                            "$cond": [
                                {"$lt": ["$paper_pnl", 0]},
                                {"$abs": "$paper_pnl"},
                                0,
                            ]
                        }
                    },
                    "total_pnl_pips": {"$sum": "$paper_pnl"},
                }
            },
        ]
        result = await db[Signal.collection].aggregate(pipeline).to_list(length=1)
        totals = result[0] if result else {}
        open_trades = await db[Signal.collection].count_documents(
            {
                "status": "ACTIVE",
                "outcome": None,
                "direction": {"$in": ["LONG", "SHORT"]},
                "stop_loss": {"$ne": None},
                "take_profit": {"$ne": None},
            }
        )
        history = await self.get_history_from_db(db, limit=20)

        total = int(totals.get("total_trades", 0))
        wins = int(totals.get("wins", 0))
        gross_profit = float(totals.get("gross_profit", 0.0))
        gross_loss = float(totals.get("gross_loss", 0.0))
        total_pnl = float(totals.get("total_pnl_pips", 0.0))

        return {
            "total_trades": total,
            "open_trades": open_trades,
            "win_rate": round(wins / total, 3) if total else 0.0,
            "profit_factor": (
                round(gross_profit / gross_loss, 2)
                if gross_loss
                else (99.0 if gross_profit else 0.0)
            ),
            "total_pnl_pips": round(total_pnl, 1),
            "current_equity": round(
                self.initial_capital + total_pnl * 0.1,
                2,
            ),
            "closed_positions": history,
        }

    def get_closed_summary(self) -> dict:
        """Return aggregate paper trading statistics from in-memory closed positions."""
        total = len(self.closed_positions)
        total_realized_usd = sum(p.get("realized_pnl", p.get("pnl_pips", 0.0) * 0.50) for p in self.closed_positions)
        self.current_equity = round(self.initial_capital + total_realized_usd, 2)

        if total == 0:
            return {
                "total_trades": 0,
                "open_trades": len(self.open_positions),
                "win_rate": 0.0,
                "profit_factor": 0.0,
                "total_pnl_pips": 0.0,
                "current_equity": round(self.current_equity, 2),
                "closed_positions": [],
            }

        wins = [p for p in self.closed_positions if p["pnl_pips"] > 0]
        losses = [p for p in self.closed_positions if p["pnl_pips"] < 0]

        gross_profit = sum(p["pnl_pips"] for p in wins)
        gross_loss = abs(sum(p["pnl_pips"] for p in losses))

        win_rate = len(wins) / total
        profit_factor = round(gross_profit / gross_loss, 2) if gross_loss > 0 else (99.0 if gross_profit > 0 else 0.0)
        total_pnl = sum(p["pnl_pips"] for p in self.closed_positions)

        return {
            "total_trades": total,
            "open_trades": len(self.open_positions),
            "win_rate": round(win_rate, 3),
            "profit_factor": profit_factor,
            "total_pnl_pips": round(total_pnl, 1),
            "current_equity": round(self.current_equity, 2),
            "closed_positions": list(reversed(self.closed_positions[-20:])),
        }


# Singleton engine instance — $100 standard paper trading account
paper_trading_engine = PaperTradingEngine(initial_capital=100.0)
