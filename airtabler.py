import os
from airtable import Airtable
from dotenv import load_dotenv

load_dotenv()

airtable_api_key = os.environ.get('AIRTABLE_API_KEY')
airtable_base = os.environ.get('AIRTABLE_BASE')
airtable_table_name = os.environ.get('AIRTABLE_TABLE_NAME')
airtable = Airtable(airtable_base, airtable_table_name, airtable_api_key)

class Airtabler:

    async def create_record(self, twitter_link: str, launch_date: str, author: str) -> dict:
        print("createRecord")
        records = airtable.insert({"Twitter Link": twitter_link, "Author": author, "Launch Date": launch_date})
        return records

    def find_record(self, twitter_link: str) -> dict:
        return airtable.search("Twitter Link", twitter_link.lower())