import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta

class NiftySmallCapScanner:
    def __init__(self, kite, symbols_file):
        self.kite = kite
        self.symbols = self._load_symbols(symbols_file)
        self.logger = logging.getLogger("Scanner")
        
    def _load_symbols(self, file_path):
        """Load symbols from CSV file"""
        try:
            df = pd.read_csv(file_path)
            return df['tradingsymbol'].tolist()
        except Exception as e:
            self.logger.error(f"Error loading symbols: {str(e)}")
            return []

    def _get_historical_data(self, symbol):
        """Fetch 5-minute historical data"""
        try:
            to_date = datetime.now()
            from_date = to_date - timedelta(days=7)
            return self.kite.historical_data(
                instrument_token=self.kite.ltp(f"NSE:{symbol}")[f"NSE:{symbol}"]["instrument_token"],
                from_date=from_date,
                to_date=to_date,
                interval="5minute"
            )
        except Exception as e:
            self.logger.error(f"Data fetch error for {symbol}: {str(e)}")
            return []

    def scan(self):
        """Main scanning logic"""
        signals = []
        for symbol in self.symbols:
            try:
                data = self._get_historical_data(symbol)
                if not data:
                    continue
                    
                df = pd.DataFrame(data)
                df['ma20'] = df['close'].rolling(20).mean()
                df['ma50'] = df['close'].rolling(50).mean()
                df['ma_deviation'] = ((df['close'] - df['ma50']) / df['ma50']) * 100
                df['volume_roc'] = ((df['volume'] - df['volume'].shift(14)) / df['volume'].shift(14)) * 100
                
                last_row = df.iloc[-1]
                
                if last_row['ma_deviation'] > 1.5 and last_row['volume_roc'] > 25:
                    signals.append({'symbol': symbol, 'signal': 'BULLISH'})
                elif last_row['ma_deviation'] < -1.5 and last_row['volume_roc'] > 25:
                    signals.append({'symbol': symbol, 'signal': 'BEARISH'})
                    
            except Exception as e:
                self.logger.error(f"Scan error for {symbol}: {str(e)}")
                
        return signals
