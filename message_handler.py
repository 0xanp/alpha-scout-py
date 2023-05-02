import re
from google_sheets_reader import GoogleSheetReader
from airtabler import Airtabler, AirtablerExisting
import os

class MessageHandler:
    STATUS = {
        'NONE': 'NONE',
        'BAD_TWITTER_LINK': 'BAD_TWITTER_LINK',
        'DUPLICATE_RECORD': 'DUPLICATE_RECORD',
        'NOT_FROM_NFT_LIST': 'NOT_FROM_NFT_LIST',
        'DB_SUCCESS': 'DB_SUCCESS',
        'DB_SAVING_ERROR': 'DB_SAVING_ERROR'
    }

    def __init__(self):
        self.status = MessageHandler.STATUS['NONE']

    def twitter_handle_match(self, message: str) -> str:
        match = re.search(r"twitter\.com\/(?P<twitter_handle>[a-zA-Z0-9_]+)", message)
        if match:
            return match.group("twitter_handle")

    def url_match(self, url: str) -> str:
        match = re.search(r'(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)', url)
        if match:
            return match.group(0)

    def parse_launch_date(self, message: str, twitter_handle: str = None) -> str:
        if not twitter_handle:
            twitter_handle = self.twitter_handle_match(message)
        url = self.url_match(message)
        if not url:
            raise ValueError(f"There is not URL in this message: '{message}'")
        launch_date = message.replace(url, "")
        launch_date = re.sub(r"^[^a-z\d]*|[^a-z\d]*$", "", launch_date, flags=re.IGNORECASE)
        return launch_date
    
    def is_twitter_status(self, message: str) -> bool:
        pattern = r"^(https://twitter.com/|https://mobile.twitter.com/)(\w+)/status/*"
        match = re.search(pattern, message)
        return bool(match)

    def tweet_status_id_match(self, message):
        return message.split('/')[-1].split('?')[0]

    async def is_notable(self, twitter_link):
        reader = GoogleSheetReader()
        lower_case_twitter = twitter_link.lower()
        sheet_entries = await reader.read_notable_data()
        if sheet_entries and lower_case_twitter in sheet_entries:
            return True
        return False

    async def handle(self, message: str, author: str):
        # first we run the message through the new project flow
        twitter_handle = self.twitter_handle_match(message)
        if not twitter_handle:
            return MessageHandler.STATUS["BAD_TWITTER_LINK"]

        twitter_link = f"https://twitter.com/{twitter_handle.lower()}"
        launch_date = self.parse_launch_date(message, twitter_handle)
        
        # if found duplicate in new project flow but the message is a status, we switch to existing project flow
        if await self.does_record_exist(twitter_link) and self.is_twitter_status(message):
            print("is duplicate but is also a status")
            if not await self.is_notable(twitter_link):
                return MessageHandler.STATUS["NOT_FROM_NFT_LIST"]

            status_id = self.tweet_status_id_match(message)
            #print(status_id)
            announcement = f"{twitter_link}/status/{status_id}"
            #print(announcement)
            if await self.does_record_exist_existing(announcement):
                print("record existed")
                return MessageHandler.STATUS["DUPLICATE_RECORD"]
            airtabler_existing = AirtablerExisting()

            try:
                print("insde try catch of handle existing")
                records = await airtabler_existing.create_record(twitter_link, announcement, author, launch_date)
                print("record created for exisitng table")
                if records and len(records) > 0:
                    return MessageHandler.STATUS["DB_SUCCESS"]
            except Exception as err:
                if "NODE_ENV" not in os.environ or os.environ["NODE_ENV"] != "test":
                    print("error saving to DB")
                    print(err)
                return MessageHandler.STATUS["DB_SAVING_ERROR"]
        
            # if the project is notable we run it through the exisiting project flow immediately
        elif await self.is_notable(twitter_link):
            #print("inside is notable")
            status_id = self.tweet_status_id_match(message)
            #print(status_id)
            announcement = f"{twitter_link}/status/{status_id}"
            #print(announcement)
            if await self.does_record_exist_existing(announcement):
                print("record existed")
                return MessageHandler.STATUS["DUPLICATE_RECORD"]
            airtabler_existing = AirtablerExisting()

            try:
                #print("insde try catch of handle existing")
                records = await airtabler_existing.create_record(twitter_link, announcement, author, launch_date)
                #print("record created for exisitng table")
                if records and len(records) > 0:
                    return MessageHandler.STATUS["DB_SUCCESS"]
            except Exception as err:
                if "NODE_ENV" not in os.environ or os.environ["NODE_ENV"] != "test":
                    print("error saving to DB")
                    print(err)
                return MessageHandler.STATUS["DB_SAVING_ERROR"]
        
        # if it's just a duplicate handle entry then we reject
        elif await self.does_record_exist(twitter_link) and not self.is_twitter_status(message):
            return MessageHandler.STATUS["DUPLICATE_RECORD"]
        
        else:
            # if it's unique new entry, we create new record in new project flow
            airtabler = Airtabler()
            try:
                records = await airtabler.create_record(twitter_link, launch_date, author)
                if records and len(records) > 0:
                    return MessageHandler.STATUS["DB_SUCCESS"]
            except Exception as err:
                if "NODE_ENV" not in os.environ or os.environ["NODE_ENV"] != "test":
                    print("error saving to DB")
                    print(err)
                return MessageHandler.STATUS["DB_SAVING_ERROR"]

    async def does_record_exist(self, twitter_link:str) -> bool:
        airtabler = Airtabler()
        records = await airtabler.find_record(twitter_link)
        if records and len(records) > 0:
            return True
        reader = GoogleSheetReader()
        sheet_entries = await reader.read_data()
        if sheet_entries and twitter_link.lower() in sheet_entries:
            return True
        return False

    async def does_record_exist_existing(self, announcement: str) -> bool:
        airtabler_existing = AirtablerExisting()
        announcement_records = await airtabler_existing.find_announcement_record(announcement)
        if announcement_records and len(announcement_records) > 0:
            return True
        return False
