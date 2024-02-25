from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import SMA, EMA
from surmount.logging import log
from surmount.data import Asset

class TradingStrategy(Strategy):
    def __init__(self):
        # Assets to track: diversified across equity ETFs and various assets for trend following
        # Adding a put option asset as a hedge against tail risk for equity ETFs
        self.equity_etfs = ["SPY", "QQQ"]
        self.trend_assets = ["GLD", "TLT", "USO"]  # Gold, Bonds, Oil
        self.hedge_asset = "SPY_PUT"  # Simplified representation of put option for SPY
        self.tickers = self.equity_etfs + self.trend_assets + [self.hedge_asset]
    
    @property
    def interval(self):
        # Daily interval for long-term trend analysis
        return "1day"
    
    @property
    def assets(self):
        return self.tickers
    
    def run(self, data):
        allocation_dict = {}
        trend_signal = False
        hedge_signal = False
        
        # Trend following strategy based on EMA crossover for multiple assets
        for asset in self.trend_assets:
            short_ema = EMA(ticker=asset, data=data["ohlcv"], length=50)
            long_ema = EMA(ticker=asset, data=data["ohlcv"], length=200)

            if short_ema and long_ema and short_ema[-1] > long_ema[-1]:
                trend_signal = True
                break  # If any asset shows a positive trend, we take a position in equity ETFs

        # Simple hedging strategy: buy puts if the EMA for SPY shows a downtrend
        spy_ema = EMA(ticker="SPY", data=data["ohlcv"], length=50)
        spy_long_ema = EMA(ticker="SPY", data=data["ohlcv"], length=200)

        if spy_ema and spy_long_ema and spy_ema[-1] < spy_long_ema[-1]:
            hedge_signal = True
        
        # Equity ETF allocation based on trend signal, evenly split if trend is positive
        if trend_signal:
            equity_allocation = 1.0 / len(self.equity_etfs)
            for etf in self.equity_etfs:
                allocation_dict[etf] = equity_allocation
        else:
            for etf in self.equity_etfs:
                allocation_dict[etf] = 0.0
        
        # Allocate a small portion to hedge asset if hedge signal is true
        allocation_dict[self.hedge_asset] = 0.1 if hedge_signal else 0.0
        
        # Reallocate remaining to cash or equivalent if both signals are False
        if not trend_signal and not hedge_signal:
            allocation_dict["CASH"] = 1.0 - sum(allocation_dict.values())
        else:
            allocation_dict["CASH"] = max(0, 1.0 - sum(allocation_dict.values()))

        return TargetAllocation(allocation_dict)