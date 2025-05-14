from core.bybit_handler import BybitHandler

class SignalDetector:
    def __init__(self):
        self.api = BybitHandler()

    def check_signal(self, symbol="BTCUSDT"):
        price = self.api.get_price(symbol)
        if price < 60000:
            return f"Сигнал: цена {symbol} упала ниже 60k! Сейчас: {price}"
        return None
