from tabulate import tabulate

class TradingDashboard:
    def __init__(self, trader):
        self.trader = trader
        
    def display(self):
        print("\n" * 50)  # Clear console
        print("=== TRADING DASHBOARD ===")
        
        # Capital Summary
        print(f"\nInitial Capital: {self.trader.initial_capital}")
        print(f"Current Balance: {self.trader.current_balance}")
        
        # Positions Summary
        headers = ["Symbol", "Direction", "Qty", "Entry", "Current", "P/L"]
        rows = []
        for pos in self.trader.open_positions:
            current_price = self.trader.kite.quote(pos['symbol'])['last_price']
            pl = current_price - pos['entry_price']
            direction = f"\033[92m{pos['direction']}\033[0m" if pos['direction'] == 'LONG' else f"\033[91m{pos['direction']}\033[0m"
            rows.append([
                pos['symbol'],
                direction,
                pos['quantity'],
                pos['entry_price'],
                current_price,
                f"{pl:.2f} ({pl/pos['entry_price']*100:.2f}%)"
            ])
            
        print(tabulate(rows, headers=headers))