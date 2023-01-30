import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

class GoogleSheetReader:
    def __init__(self):
        if not os.environ.get('GOOGLE_SHEET_MIDNIGHT_LABS_SHEET_ID') and not os.environ.get('GOOGLE_SHEET_MIDNIGHT_LABS_GID'):
            raise ValueError("No env variable for google sheets")
        self.spreadsheet_url= os.environ.get('GOOGLE_SHEET_URL')
    async def read_data(self):
        df = pd.read_excel(self.spreadsheet_url, usecols="D")
        return df.values.tolist()
