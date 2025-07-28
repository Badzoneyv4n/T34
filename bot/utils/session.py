# bot/core/session.py

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

ALL_SESSIONS = []

@dataclass
class TradeResult:
    """
    Represents the result of a trade.
    """
    entry_time: datetime
    level: int
    amount: float
    order_id: Optional[str]
    result: str  # 'win' or 'loss'
    profit: float

@dataclass
class SignalSession:
    """
    Represents a trading signal session.
    """
    pair: str
    expiration: int  # in seconds
    direction: str  # 'call' or 'put'
    entry_time:  datetime  # in LOCAL time
    martingale_levels: List[datetime]  # as HH:MM strings in local time
    initial_amount: float
    trades: List[TradeResult] = field(default_factory=list)
    total_profit: float = 0.0

    def add_trade_result(self, trade: TradeResult):

        # Prevent adding the same trade multiple times
        if any(t.order_id == trade.order_id for t in self.trades if t.order_id is not None):
            print(f"[SignalSession] Trade {trade.order_id} already exists in session for pair {self.pair}. Not adding again.")
            return  # Already added

        self.trades.append(trade)
        self.total_profit += trade.profit