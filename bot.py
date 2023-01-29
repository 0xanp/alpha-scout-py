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

EXAMPLES = "for example\nhttps://twitter.com/ChunkyChihuahuas\nor\nhttps://mobile.twitter.com/GrumpyGremplins\n\nIf you know the estimated launch date, you can add it after the twitter link, like \nhttps://mobile.twitter.com/PuffyPandas September 14, 2023\nor\nhttps://twitter.com/OrangeOttersXYZ Q3 2023"

@client.event
async def on_message(message):
    if message.author.bot:
        return
    handler = MessageHandler()
    print(message.content)
    result = await handler.handle(message.content, message_username(message))
    if result == MessageHandler.STATUS['BAD_TWITTER_LINK']:
        await message.channel.send(f":x: Invalid Format: Please enter the project Twitter link (i.e. it should start with https://www.twitter.com/)\n{EXAMPLES}")
    elif result == MessageHandler.STATUS['DB_SUCCESS']:
        await message.channel.send(":white_check_mark: Thank You! Successfully Saved")
    elif result == MessageHandler.STATUS['DUPLICATE_RECORD']:
        await message.channel.send(":x: That NFT project has already been added")
    elif result == MessageHandler.STATUS['DB_SAVING_ERROR']:
        await message.channel.send(":x: ERROR saving to the database, please contact an admin")

client.run(os.environ.get('DISCORD_BOT_TOKEN'))