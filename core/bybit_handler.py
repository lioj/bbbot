from pybit.unified_trading import HTTP
from config.settings import BYBIT_API_KEY, BYBIT_API_SECRET

def round_value(value, precision):
    return float(f"{value:.{precision}f}")

class BybitHandler:
    def __init__(self):
        self.session = HTTP(
            api_key=BYBIT_API_KEY,
            api_secret=BYBIT_API_SECRET,
            testnet=False
        )
        self.update_current_prices()
        self.precision_cache = {}  # кэшируем точности

    def update_current_prices(self):
        tickers = self.session.get_tickers(category="spot")
        self.coin2price = {}
        for item in tickers['result']['list']:
            self.coin2price[item["symbol"]] = float(item["lastPrice"])
    
    def get_avg_price(self, symbol):
        cursor = None
        cost = 0
        size = 0
        side = ""
        while side != "Sell" and cursor != "":
            try:
                res = self.session.get_order_history(
                    category="spot",
                    symbol=symbol,
                    orderStatus="Filled",
                    limit=10,
                    cursor=cursor
                )
                cursor = res["result"]["nextPageCursor"]
                for item in res["result"]["list"]:
                    side = item["side"]
                    if side == "Sell":
                        break
                    avg_price = float(item["avgPrice"])
                    qty = float(item["qty"])
                    cost += avg_price * qty
                    size += qty
            except Exception as e:
                print(f"Error fetching order history for {symbol}: {e}")
                return 0
        return cost / size if size > 0 else 0

    def get_open_positions(self):
        try:
            result = self.session.get_wallet_balance(accountType="UNIFIED")
            coins = result["result"]["list"][0]["coin"]
            positions = []
            for coin in coins:
                symbol = coin["coin"]
                if symbol != "USDT":
                    size = float(coin["walletBalance"])
                    symbol_full = f"{symbol}USDT"
                    price = self.coin2price.get(symbol_full, 0)
                    amount = size * price
                    if amount > 1:
                        positions.append({"symbol": symbol, "size": size, "price": price, "amount": amount})
            return positions
        except Exception as e:
            print(f"Error fetching wallet balances: {e}")
            return []
    
    def get_open_sell_orders(self):
        try:
            res = self.session.get_open_orders(category="spot")
            sell_orders = set()
            for item in res["result"]["list"]:
                if item["side"] == "Sell":
                    sell_orders.add(item["symbol"])
            return sell_orders
        except Exception as e:
            print(f"Error fetching open orders: {e}")
            return set()

    def get_symbol_precisions(self, symbol):
        if symbol in self.precision_cache:
            return self.precision_cache[symbol]
        try:
            res = self.session.get_instruments_info(category="spot", symbol=symbol)
            info = res["result"]["list"][0]
            qty_step = info["lotSizeFilter"]["basePrecision"]
            price_tick = info["priceFilter"]["tickSize"]

            # Вычисляем количество знаков после запятой
            qty_precision = len(qty_step.split('.')[-1].rstrip('0')) if '.' in qty_step else 0
            price_precision = len(price_tick.split('.')[-1].rstrip('0')) if '.' in price_tick else 0
           
            self.precision_cache[symbol] = (qty_precision, price_precision)
            return qty_precision, price_precision
        except Exception as e:
            print(f"Failed to fetch precision for {symbol}: {e}")
            return 6, 6  # дефолт
    
    def get_sell_order_recomendations(self):
        positions = self.get_open_positions()
        open_sells = self.get_open_sell_orders()
        res=[]
        for pos in positions:
            symbol = pos["symbol"]
            full_symbol = f"{symbol}USDT"
            if full_symbol not in open_sells:
                avg_price = self.get_avg_price(full_symbol)
                if avg_price > 0:
                    price = avg_price * 1.02  # на 2% выше
                    qty=pos["size"]
                    qty_precision, price_precision = self.get_symbol_precisions(full_symbol)
                    qty = round_value(qty, qty_precision)
                    price = round_value(price, price_precision)
                    res.append([full_symbol, price, qty])
        return res
