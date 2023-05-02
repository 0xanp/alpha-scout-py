import os
from airtable import Airtable
from dotenv import load_dotenv

load_dotenv()

# new projects airtable credentials
airtable_api_key = os.environ.get('AIRTABLE_API_KEY')
airtable_base = os.environ.get('AIRTABLE_BASE')
airtable_table_name = os.environ.get('AIRTABLE_TABLE_NAME')
# exisiting projects airtable credentials
exisiting_airtable_api_key = os.environ.get('EXISTING_AIRTABLE_API_KEY')
exisiting_airtable_base = os.environ.get('EXISTING_AIRTABLE_BASE')
exisiting_airtable_table_name = os.environ.get('EXISTING_AIRTABLE_TABLE_NAME')
airtabler_existing = Airtable(exisiting_airtable_base, exisiting_airtable_table_name, exisiting_airtable_api_key)
airtable = Airtable(airtable_base, airtable_table_name, airtable_api_key)

class Airtabler:
    async def create_record(self, twitter_link: str, launch_date: str, author: str) -> list:
        print("createRecord")
        records = airtable.insert({"Twitter Link": twitter_link, "Author": author, "Launch Date": launch_date})
        return records

    async def find_record(self, twitter_link: str) -> dict:
        return airtable.search("Twitter Link", twitter_link)

class AirtablerExisting:

    async def create_record(self, twitter_profile: str, announcement: str, author: str, scout_comment: str) -> dict:
        print("createRecord")
        records = airtabler_existing.insert({"Twitter Profile": twitter_profile,"Announcement": announcement, "Author": author, "Scout Comment": scout_comment})
        return records

    async def find_announcement_record(self, announcement: str) -> dict:
        return airtabler_existing.search("Announcement", announcement)