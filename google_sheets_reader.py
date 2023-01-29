import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json
from dotenv import load_dotenv

load_dotenv()

SHEET_NAME = "Master ML Alpha Calendar"

class GoogleSheetReader:
    def __init__(self):
        if not os.environ.get('GOOGLE_SHEET_MIDNIGHT_LABS_ID'):
            raise ValueError("No env variable GOOGLE_SHEET_MIDNIGHT_LABS_ID")
        self.spreadsheet_id = os.environ.get('GOOGLE_SHEET_MIDNIGHT_LABS_ID')

    def read_data(self):
        credentials = Credentials.from_authorized_user_info(info=json.loads(os.environ.get('GOOGLE_SHEET_CREDENTIALS')), scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
        sheets_service = build('sheets', 'v4', credentials=credentials)
        result = sheets_service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=f'{SHEET_NAME}!D:D').execute()
        values = result.get('values', [])
        return [x[0].strip().lower() for x in values]
