import unittest
from unittest.mock import MagicMock, patch
from airtabler import Airtabler
from message_handler import MessageHandler
from google_sheets_reader import GoogleSheetReader
import faker
import asyncio

class TestAirtabler(unittest.TestCase):
    airtabler = Airtabler()
    TWITTER_LINK_RECORD = "https://twitter.com/a_new_nft_project44"

    async def test_create_record(self):
        print("\nTESTING create_record...")
        twitter_link = self.TWITTER_LINK_RECORD
        launch_date = "March 2023"
        author = "mintyMcMintable#9999"
        records = await self.airtabler.create_record(twitter_link, launch_date, author)
        record = records['fields']
        self.assertEqual(record["Twitter Link"], twitter_link)
        self.assertEqual(record["Launch Date"], launch_date)
        self.assertEqual(record["Author"], author)
        print("PASSED")

    async def test_find_record(self):
        print("\nTESTING find_record...")
        twitter_link = self.TWITTER_LINK_RECORD
        records = await self.airtabler.find_record(twitter_link)
        self.assertGreater(len(records), 0)
        self.assertEqual(records[0]['fields']["Twitter Link"], twitter_link)
        print("PASSED")

class TestGoogleSheetReader(unittest.TestCase):
    async def test_read_data(self):
        print("\nTESTING google_sheets_reader...")
        reader = GoogleSheetReader()
        data = await reader.read_data()
        self.assertFalse("https://twitter.com/LonelyPopNFT" in data) # should not match since we called .lower()
        self.assertTrue("https://twitter.com/lonelypopnft" in data)
        self.assertTrue("https://twitter.com/metapeeps" in data)
        print("PASSED")

class TestMessageHandler(unittest.TestCase):
    handler = MessageHandler()
    DUPLICATE_TWITTER_LINK = "https://twitter.com/a_new_nft_project44"

    async def test_does_record_exist(self):
        print("\nTESTING does_record_exist...")
        exists = await self.handler.does_record_exist(self.DUPLICATE_TWITTER_LINK)
        self.assertTrue(exists)

        exists = await self.handler.does_record_exist("https://twitter.com/LonelyPopNFT")
        self.assertTrue(exists)
        print("PASSED")

    async def test_handle(self):
        author = 'mcMinty'
        print("\nTESTING DB status...")
        # BAD_TWITTER_LINK
        result = await self.handler.handle("moonbirds 2022", author)
        self.assertEqual(result, MessageHandler.STATUS['BAD_TWITTER_LINK'])

        # DUPLICATE_RECORD
        result = await self.handler.handle(f"{self.DUPLICATE_TWITTER_LINK} 2022", author)
        self.assertEqual(result, MessageHandler.STATUS['DUPLICATE_RECORD'])

        # DB_SUCCESS
        f = faker.Faker()
        twitter_link = "https://twitter.com/" + "-".join(f.words(6))
        print(twitter_link)
        result =  await self.handler.handle(f"{twitter_link} 2022", author)
        self.assertEqual(result, MessageHandler.STATUS['DB_SUCCESS'])

        # DB_SAVING_ERROR
        with patch.object(Airtabler, 'create_record', MagicMock(side_effect=Exception("intentionally generated TEST Error"))):
            twitter_link = "https://twitter.com/" + "-".join(f.words(6))
            result = await self.handler.handle(f"{twitter_link} 2022", author)
            self.assertEqual(result, MessageHandler.STATUS['DB_SAVING_ERROR'])
        print("PASSED")

    def test_twitter_handle_match(self):
        print("\nTESTING twitter_handle_match...")
        
        # upper and lowercase
        print("Upper and Lowercase")
        message = "https://twitter.com/MoonbirdsXYZ"
        self.assertEqual(self.handler.twitter_handle_match(message), "MoonbirdsXYZ")
        print("PASSED")

        # numbers and underscores
        print("Numbers and Underscores")
        message = "https://twitter.com/_Boonbirds99"
        self.assertEqual(self.handler.twitter_handle_match(message), "_Boonbirds99")
        print("PASSED")

        # http not https
        print("http not https")
        message = "http://twitter.com/MoonbirdsXYZ"
        self.assertEqual(self.handler.twitter_handle_match(message), "MoonbirdsXYZ")
        print("PASSED")
        
        # has no protocol https
        print("has no protocol https")
        message = "twitter.com/MoonbirdsXYZ"
        self.assertEqual(self.handler.twitter_handle_match(message), "MoonbirdsXYZ")
        print("PASSED")
        
        # has mobile/www subdomain
        print("has mobile or www subdomain")
        message = "mobile.twitter.com/MoonbirdsXYZ"
        self.assertEqual(self.handler.twitter_handle_match(message), "MoonbirdsXYZ")
        message = "www.twitter.com/MoonbirdsXYZ"
        self.assertEqual(self.handler.twitter_handle_match(message), "MoonbirdsXYZ")
        print("PASSED")

        # has comma, period or bar delimiter
        print("has comma, period or bar delimiter")
        message = "https://twitter.com/_GoeyGeese1,April 5, 2023"
        self.assertEqual(self.handler.twitter_handle_match(message), "_GoeyGeese1")
        message = "https://twitter.com/_GoeyGeese1.April 5, 2023"
        self.assertEqual(self.handler.twitter_handle_match(message), "_GoeyGeese1")
        message = "https://twitter.com/_GoeyGeese1|April 5, 2023"
        self.assertEqual(self.handler.twitter_handle_match(message), "_GoeyGeese1")
        print("PASSED")
        
        # has query string
        print("has query string")
        message = "https://mobile.twitter.com/Moonbirds55_?t=yUnZi2HaVMlwaSGs_Dyzxw&s=09,2023"
        self.assertEqual(self.handler.twitter_handle_match(message), "Moonbirds55_")
        print("PASSED")

        # receives garbage
        print("receives garbage")
        message = "twat.com/NoNadaNothing"
        self.assertIsNone(self.handler.twitter_handle_match(message))
        message = "twitter.com"
        self.assertIsNone(self.handler.twitter_handle_match(message))
        message = "twitter.com/"
        self.assertIsNone(self.handler.twitter_handle_match(message))
        message = "twitter.com/"
        self.assertIsNone(self.handler.twitter_handle_match(message))
        message = "twitter.com/!!!"
        self.assertIsNone(self.handler.twitter_handle_match(message))
        print("PASSED")

    def test_url_match(self):
        print("\nTESTING url_match...")
        # with date ending
        print("with date ending")
        url = "https://mobile.twitter.com/Moonbirds55_ April 5, 2023"
        self.assertEqual(self.handler.url_match(url), "https://mobile.twitter.com/Moonbirds55_")
        print("PASSED")

        # with query string and comma delimiter
        print("with query string and comma delimiter")
        url = "https://twitter.com/Moonbirds55_?t=yUnZi2HaVMlwaSGs_Dyzxw&s=09,April 5, 2023"
        self.assertEqual(self.handler.url_match(url), "https://twitter.com/Moonbirds55_?t=yUnZi2HaVMlwaSGs_Dyzxw&s=09")
        print("PASSED")

        # period will be included in url
        print("period delimiter will be included in url (unexpected!)")
        url = "https://www.twitter.com/Moonbirds55_?t=yUnZi2HaVMlwaSGs_Dyzxw&s=09.April 5, 2023"
        self.assertEqual(self.handler.url_match(url), "https://www.twitter.com/Moonbirds55_?t=yUnZi2HaVMlwaSGs_Dyzxw&s=09.April")
        print("PASSED")

    def test_parse_launch_date(self):
        print("\nTESTING parse_launch_date...")

        # space delimited
        print("space delimited")
        message = "https://twitter.com/_GoeyGeese1 2023"
        self.assertEqual(self.handler.parse_launch_date(message), "2023")
        print("PASSED")

        # space delimited with date and comma
        print("space delimited with date and comma")
        message = "https://twitter.com/_GoeyGeese1 April 5, 2023"
        self.assertEqual(self.handler.parse_launch_date(message), "April 5, 2023")
        print("PASSED")

        # comma delimited
        print("comma delimited")
        message = "https://twitter.com/_GoeyGeese1,2023"
        self.assertEqual(self.handler.parse_launch_date(message), "2023")
        print("PASSED")
        
        # url with query string and comma delimited
        print("url with query string and comma delimited")
        message = "https://mobile.twitter.com/Moonbirds55_?t=yUnZi2HaVMlwaSGs_Dyzxw&s=09,April 5, 2023"
        self.assertEqual(self.handler.parse_launch_date(message), "April 5, 2023")
        print("PASSED")

        # period delimited
        print("period delimited (unexpected!)")
        message = "https://mobile.twitter.com/Moonbirds55_?t=yUnZi2HaVMlwaSGs_Dyzxw&s=09.April 5, 2023"
        self.assertEqual(self.handler.parse_launch_date(message), "5, 2023")
        print("PASSED")

async def main():
    print("Testing Alpha Scout Bot...")
    # Testing airtabler
    airtabler_tester = TestAirtabler()
    await airtabler_tester.test_create_record()
    await airtabler_tester.test_find_record()
    # Testing google_sheets_reader
    google_sheets_reader_tester = TestGoogleSheetReader()
    await google_sheets_reader_tester.test_read_data()
    # Testing message_handler
    message_handler_tester = TestMessageHandler()
    await message_handler_tester.test_handle()
    await message_handler_tester.test_does_record_exist()
    message_handler_tester.test_url_match()
    message_handler_tester.test_parse_launch_date()
    message_handler_tester.test_twitter_handle_match()
    print("\nDone Testing Alpha Scout Bot!")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
