from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, EMA, SMA
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the single asset to trade, adjust accordingly.
        self.asset = "AAPL" 

    @property
    def assets(self):
        # Inform Surmount of the assets this strategy will consider.
        return [self.asset]

    @property
    def interval(self):
        # Set the data interval for analysis. 
        # "1day" means the strategy will use daily candlestick data.
        return "1day"

    def run(self, data):
        # Initialize allocation to 0% for the asset.
        allocation = {self.asset: 0.0}
        
        # Ensure there is enough data for EMA(50), RSI(14), and SMA(20) calculations.
        if len(data["ohlcv"]) < 50:
            log("Not enough data to perform analysis.")
            return TargetAllocation(allocation)

        # Calculate technical indicators for the asset.
        ema50 = EMA(self.asset, data["ohlcv"], 50)[-1]
        rsi14 = RSI(self.asset, data["ohlcv"], 14)[-1]
        sma20 = SMA(self.asset, data["ohlcv"], 20)[-1]
        current_price = data["ohlcv"][-1][self.asset]["close"]

        # Check trading conditions.
        if current_price > ema50 and rsi14 < 70 and current_price > sma20:
            # All conditions met, allocate 100% to the asset.
            allocation[self.asset] = 1.0
            log(f"Conditions met for {self.asset}. Allocating 100%.")
        else:
            log(f"Conditions not met for {self.asset}. Allocation remains at {allocation[self.asset]*100}%.")

        return TargetAllocation(allocation)