import discord
from discord.ext import commands
from message_handler import MessageHandler
import os
from dotenv import load_dotenv

load_dotenv()
client = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@client.event
async def on_ready():
    print("The bot is ready")

def message_username(message: discord.Message) -> str:
    return message.author.name + "#" + message.author.discriminator

EXAMPLES_PROFILE = "for example\nhttps://twitter.com/ChunkyChihuahuas\nor\nhttps://mobile.twitter.com/GrumpyGremplins\n\nIf you know the estimated launch date, you can add it after the twitter link, like \nhttps://mobile.twitter.com/PuffyPandas September 14, 2023\nor\nhttps://twitter.com/OrangeOttersXYZ Q3 2023 \n You can also submit a twitter status link of an announcement of an existing project from this list https://docs.google.com/spreadsheets/d/1gu1ZY7HCZH87RwqNOvjgJI3xog7qwhN_A43JzyQF1Pc/edit?usp=sharing"
EXAMPLES_ANNOUNCEMENT = "for example\nhttps://twitter.com/prometheansxyz/status/1619087210250371072?s=20&t=F-HswS5r0Rlck4V395TPvg\nor\nhttps://mobile.twitter.com/jollyswap/status/1605958314390474754?s=20&t=F-HswS5r0Rlck4V395TPvg"

@client.event
async def on_message(message):
    if message.author.bot:
        return
    handler = MessageHandler()
    result = await handler.handle(message.content, message_username(message))
    if result == MessageHandler.STATUS['BAD_TWITTER_LINK']:
        await message.reply(f":x: Invalid Format: Please enter the project Twitter handle link or project Twitter status link (i.e. it should start with https://www.twitter.com/)\n{EXAMPLES_PROFILE}")
    elif result == MessageHandler.STATUS['DB_SUCCESS']:
        await message.reply(":white_check_mark: Thank You! Successfully Saved")
    elif result == MessageHandler.STATUS['DUPLICATE_RECORD']:
        await message.reply(":x: That NFT project has already been added")
    elif result == MessageHandler.STATUS['DB_SAVING_ERROR']:
        await message.reply(":x: ERROR saving to the database, please contact an admin")
    elif result == MessageHandler.STATUS['NOTABLE_BUT_NO_ANNOUNCEMENT']:
        await message.reply(f":x: You entered a twitter profile from the notable list (https://docs.google.com/spreadsheets/d/1gu1ZY7HCZH87RwqNOvjgJI3xog7qwhN_A43JzyQF1Pc/edit?usp=sharing), but no twitter link to a new announcement was found. \nPlease enter an announcement of that profile using the following format {EXAMPLES_ANNOUNCEMENT}")

client.run(os.environ.get('DISCORD_BOT_TOKEN'))