import logging
from datetime import datetime

class TradeExecuter:
    def __init__(self, kite, config):
        self.kite = kite
        self.initial_capital = config['initial_capital']
        self.current_balance = config['initial_capital']
        self.max_positions = config['max_positions']
        self.risk_per_trade = config['risk_per_trade']
        self.reward_ratio = config['reward_ratio']
        self.open_positions = []
        self.closed_positions = []
        self.logger = logging.getLogger("Trader")

    def calculate_position_size(self):
        """Calculate position size based on current balance"""
        return self.current_balance / self.max_positions

    def execute_trade(self, signal):
        """Execute trade based on signal"""
        if len(self.open_positions) >= self.max_positions:
            self.logger.warning("Max open positions reached")
            return False

        try:
            symbol = signal['symbol']
            ltp = self.kite.ltp(f"NSE:{symbol}")[f"NSE:{symbol}"]["last_price"]
            position_size = self.calculate_position_size()
            quantity = int(position_size // ltp)

            if quantity < 1:
                self.logger.warning(f"Insufficient capital for {symbol}")
                return False

            if signal['signal'] == 'BULLISH':
                order_id = self.kite.place_order(
                    variety="regular",
                    exchange="NSE",
                    tradingsymbol=symbol,
                    transaction_type="BUY",
                    quantity=quantity,
                    product="MIS",
                    order_type="MARKET"
                )
                self.open_positions.append({
                    'symbol': symbol,
                    'entry_time': datetime.now(),
                    'entry_price': ltp,
                    'quantity': quantity,
                    'stop_loss': ltp * (1 - self.risk_per_trade),
                    'target': ltp * (1 + self.risk_per_trade * self.reward_ratio),
                    'direction': 'LONG',
                    'status': 'OPEN'
                })
                self.current_balance -= position_size
                
            elif signal['signal'] == 'BEARISH':
                order_id = self.kite.place_order(
                    variety="regular",
                    exchange="NSE",
                    tradingsymbol=symbol,
                    transaction_type="SELL",
                    quantity=quantity,
                    product="MIS",
                    order_type="MARKET"
                )
                self.open_positions.append({
                    'symbol': symbol,
                    'entry_time': datetime.now(),
                    'entry_price': ltp,
                    'quantity': quantity,
                    'stop_loss': ltp * (1 + self.risk_per_trade),
                    'target': ltp * (1 - self.risk_per_trade * self.reward_ratio),
                    'direction': 'SHORT',
                    'status': 'OPEN'
                })
                self.current_balance -= position_size

            self.logger.info(f"Executed {signal['signal']} trade for {symbol}")
            return True

        except Exception as e:
            self.logger.error(f"Trade execution failed: {str(e)}")
            return False

    def update_trailing_sl(self):
        """Update trailing stop losses"""
        for position in self.open_positions:
            if position['status'] != 'OPEN':
                continue
                
            ltp = self.kite.ltp(f"NSE:{position['symbol']}")[f"NSE:{position['symbol']}"]["last_price"]
            
            if position['direction'] == 'LONG':
                new_sl = ltp * (1 - self.risk_per_trade)
                if new_sl > position['stop_loss']:
                    position['stop_loss'] = new_sl
                    
            elif position['direction'] == 'SHORT':
                new_sl = ltp * (1 + self.risk_per_trade)
                if new_sl < position['stop_loss']:
                    position['stop_loss'] = new_sl
