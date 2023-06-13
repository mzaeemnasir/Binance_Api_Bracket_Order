from binance.client import Client
from binance.enums import *
import requests

class Binance: 
    # Constructor
    def __init__(self, api_key, api_secret):
        try:
            self.client = Client(api_key=api_key, api_secret=api_secret, testnet= True) # Testnet is True for testing purposes
            print("Binance API initialized successfully & your Bot is Successfully Connected") 
            self.client.API_URL = 'https://testnet.binance.vision/api'                
        except Exception as e:
            print(e)
            exit()
    
    # Get the balance of a particular asset futures_account_balance
    def get_balance(self, asset):
        try:
            balances = self.client.futures_account_balance()
            for balance in balances:
                if balance['asset'] == asset:
                    return float(balance['balance'])
            return 0
        except Exception as e:
            print(e)
            return 0
    
    # Get Position of a particular symbol
    def get_position(self, symbol):
        try:
            positions = self.client.futures_position_information()
            for position in positions:
                if position['symbol'] == symbol:
                    return float(position['positionAmt'])
            return 0
        except Exception as e:
            print(e)
            return 0
    
    # Checking if there is an open order for a particular symbol
    def check_open_order(self, symbol):
        try:
            orders = self.client.futures_get_open_orders(symbol=symbol)
            if len(orders) > 0:
                print(f"Open Order: {orders[0].get('orderId')} for {symbol}")
            return len(orders) > 0 # True if there is an open order 
        except Exception as e:
            print(e)
            return False
    
    # Get the price of a particular symbol
    def get_price(self, symbol):
        return float(self.client.get_symbol_ticker(symbol=symbol)['price'])
    
    def get_tick_size(self, symbol):
        try:
            size =  float(self.client.get_symbol_info(symbol=symbol)['filters'][0]['tickSize'])
        except Exception as e:
            print(e)
            return None
            
        # count the number of decimal places
        print(size)
        count = 0
        while size < 1:
            size *= 10
            count += 1
        return count
    
    
    def delete_pending_orders(self, symbol):
        print("Deleting pending orders")
        try:
            orders = self.client.futures_get_open_orders(symbol=symbol)
            for order in orders:
                
                self.client.futures_cancel_order(symbol=symbol, orderId=order.get('orderId'))
        except Exception as e:
            print(e)
            return False
        
        
    # Placing a market order (Braket order with stop loss and take profit)
    def place_bracket_order(self, symbol, quantity, side, takeProfit, stopLoss):
        side =  side.upper()
        side2 = "SELL" if side == "BUY" else "BUY"            

        
        # Check if there is an open Position
        position = self.get_position(symbol)
        if position != 0:
            print(f"Position: {position} for {symbol}")
            return None
        
        # If There is no Position open deleting pending orders
        self.delete_pending_orders(symbol)
        
        
        if take_profit is not None:
            take_profit = round(take_profit/100, tick_size)
            
        if stop_loss is not None:
            stop_loss = round(stop_loss/100, tick_size)
        
        # Ticker Size
        tick_size = self.get_tick_size(symbol)
        if tick_size is None:
            return None
        
        # Ticker price
        ticker_price = round(self.get_price(symbol), tick_size)
        
        # 1% stop loss
        stop_loss = round(ticker_price - (ticker_price * 0.01), tick_size)
        
        # 1.5% take profit
        take_profit = round(ticker_price + (ticker_price * 0.015),tick_size)
        print(tick_size,ticker_price, stop_loss, take_profit)
        
        """What is Bracket Order?
        
        A bracket order is a special type of order where you can place a market order, 
        along with a take profit order and a stop loss order.
        
        """
        
        
        try:
            self.client.futures_leverage_bracket( # Setting the leverage to 1
                symbol=symbol,
                leverage=1,
                )
            
            # Market Order
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type=FUTURE_ORDER_TYPE_MARKET,
                quantity=quantity,
                )
            
            # Stop Loss and Take Profit
            
            # Stop Loss
            self.client.futures_create_order(
                symbol=symbol,
                side=side2,
                type=FUTURE_ORDER_TYPE_STOP_MARKET,
                quantity=quantity,
                stopPrice=stop_loss,
                timeInForce='GTC')
            
            # Take Profit
            self.client.futures_create_order(
                symbol=symbol,
                side=side2,
                type=FUTURE_ORDER_TYPE_TAKE_PROFIT_MARKET,
                quantity=quantity,
                stopPrice=take_profit,
                timeInForce='GTC')
            
            msg = f"```Successfully Placed and Order Here is the Summary of the Order \n \n {order}```"
            
            return order
        except Exception as e:
            print(e)
            return None   