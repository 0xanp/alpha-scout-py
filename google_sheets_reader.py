import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

class GoogleSheetReader:
    def __init__(self):
        if not os.environ.get('GOOGLE_SHEET_URL'):
            raise ValueError("No env variable for google sheets")
        self.spreadsheet_url= os.environ.get('GOOGLE_SHEET_URL')
    async def read_data(self):
        df = pd.read_excel(self.spreadsheet_url, usecols="D")
        # every twitter links to lowercase for comparison
        df = df.astype(str).apply(lambda x: x.str.lower())
        return [url[0] for url in df.values.tolist()]
