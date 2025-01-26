import os
import json
import logging
from kiteconnect import KiteConnect

logging.basicConfig(level=logging.INFO)

class ZerodhaConnector:
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token = None
        self.kite = None
        self.token_file = "config.json"
        self.logger = logging.getLogger("ZerodhaConnector")

    def connect(self):
        """Establishes connection with Zerodha API"""
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file) as f:
                    config = json.load(f)
                    self.access_token = config.get('access_token')
            
            if self.access_token:
                self.kite = KiteConnect(api_key=self.api_key)
                self.kite.set_access_token(self.access_token)
                self.logger.info("Connected using existing access token")
                return True
                
        except Exception as e:
            self.logger.error(f"Connection error: {str(e)}")
            return self.manual_connect()

    def manual_connect(self):
        """Handles manual authentication flow"""
        try:
            self.kite = KiteConnect(api_key=self.api_key)
            print(f"Please visit this URL to authorize: {self.kite.login_url()}")
            request_token = input("Enter the generated request token: ").strip()
            session = self.kite.generate_session(request_token, self.secret_key)
            
            with open(self.token_file, 'w') as f:
                json.dump({'access_token': session['access_token']}, f)
                
            self.kite.set_access_token(session['access_token'])
            self.logger.info("New access token generated and saved")
            return True
            
        except Exception as e:
            self.logger.error(f"Manual connection failed: {str(e)}")
            return False
