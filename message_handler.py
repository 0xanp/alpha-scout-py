import re
from typing import Optional
from google_sheets_reader import GoogleSheetReader
from airtabler import Airtabler
import os

class MessageHandler:
    STATUS = {
        'NONE': 'NONE',
        'BAD_TWITTER_LINK': 'BAD_TWITTER_LINK',
        'DUPLICATE_RECORD': 'DUPLICATE_RECORD',
        'DB_SUCCESS': 'DB_SUCCESS',
        'DB_SAVING_ERROR': 'DB_SAVING_ERROR'
    }

    def __init__(self):
        self.status = MessageHandler.STATUS['NONE']

    def twitterHandleMatch(self, message: str) -> str:
        match = re.search(r"twitter\.com\/(?P<twitterHandle>[a-zA-Z0-9_]+)", message)
        if match:
            return match.group("twitterHandle")

    def urlMatch(self, url: str) -> str:
        match = re.search(r'(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)', url)
        if match:
            return match.group(0)

    def parseLaunchDate(self, message: str, twitterHandle: str = None) -> str:
        if not twitterHandle:
            twitterHandle = self.twitterHandleMatch(message)
        url = self.urlMatch(message)
        if not url:
            raise ValueError(f"There is not URL in this message: '{message}'")
        launchDate = message.replace(url, "")
        launchDate = re.sub(r"^[^a-z\d]*|[^a-z\d]*$", "", launchDate, flags=re.IGNORECASE)
        return launchDate

    async def handle(self, message: str, author: str):
        twitterHandle = self.twitterHandleMatch(message)
        if not twitterHandle:
            self.status = MessageHandler.STATUS["BAD_TWITTER_LINK"]
            return self.status
        twitterLink = f"https://twitter.com/{twitterHandle}"
        launchDate = self.parseLaunchDate(message, twitterHandle)

        if not twitterLink:
            self.status = MessageHandler.STATUS["BAD_TWITTER_LINK"]
            return self.status

        if await self.doesRecordExist(twitterLink):
            self.status = MessageHandler.STATUS["DUPLICATE_RECORD"]
            return self.status   
        airtabler = Airtabler()
        try:
            records = await airtabler.createRecord(twitterLink, launchDate, author)
            if records and len(records) > 0:
                return MessageHandler.STATUS["DB_SUCCESS"]
        except Exception as err:
            if "NODE_ENV" not in os.environ or os.environ["NODE_ENV"] != "test":
                print("error saving to DB")
                print(err)
            return MessageHandler.STATUS["DB_SAVING_ERROR"]

    async def doesRecordExist(self, twitterLink:str) -> bool:
        airtabler = Airtabler()
        records = await airtabler.find_record(twitterLink)
        if records and len(records) > 0:
            return True
        reader = GoogleSheetReader()
        lowerCaseTwitter = twitterLink.lower()
        sheetEntries = await reader.readData()
        if sheetEntries and lowerCaseTwitter in sheetEntries:
            return True
        return False
