import json
from Connectors.zerodha_connector import ZerodhaConnector
from Scanners.nifty_smallcap import NiftySmallCapScanner
from Trader.trade_executer import TradeExecuter
from Display.trading_dashboard import TradingDashboard
import time

def main():
    # Load configuration
    with open('config.json') as f:
        config = json.load(f)
    
    # Initialize components
    connector = ZerodhaConnector(config['api_key'], config['secret_key'])
    if connector.connect():
        scanner = NiftySmallCapScanner(connector.kite)
        trader = TradeExecuter(connector.kite, config['initial_capital'])
        dashboard = TradingDashboard(trader)
        
        while True:
            signals = scanner.scan()
            for signal in signals:
                trader.execute_trade(signal)
                
            dashboard.display()
            time.sleep(300)  # 5 minute interval

if __name__ == "__main__":
    main()