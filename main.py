# https://discord.com/api/oauth2/authorize?client_id=1179233488117964810&permissions=274877982720&redirect_uri=https%3A%2F%2Femmetts.dev&response_type=code&scope=guilds%20guilds.join%20bot%20messages.read%20dm_channels.read

import os
import discord
from customGPT import generate_reply
from replit import db
import threading
from bottle import route, run, template

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

client = discord.Client(intents=intents)

isBusy = False


async def update_presence():
    # Build the party status
    party_status = f"</>"
    activity = discord.Game(name=party_status)
    await client.change_presence(activity=activity)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await update_presence()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    global isBusy
    if isBusy:  # IF ALREADY BUSY, STOP BOT
        return

    authorID = str(message.author.id)
    
    if isinstance(message.channel, discord.DMChannel): 
        threadID = db.get(authorID, "NIL")
        if "delete-all" in message.content.lower():  # IF USER REQUESTS DELETION, DELETE DB
            del db[authorID]
            print(f"Deleted conversation thread with {message.author.name} - {authorID}")
            async with message.channel.typing():
                await message.channel.send(f"All messages deleted for user {message.author.name}")
            return
        else:
            isBusy = True
            async with message.channel.typing():
                response = generate_reply(message.content, threadID, authorID)
                await message.channel.send(response)
            isBusy = False

    elif message.guild is not None and client.user in message.mentions:
        threadID = db.get(authorID, "NIL")
        if "delete-all" in message.content.lower():
            del db[authorID]
            print(f"Deleted conversation thread with {message.author.name} - {authorID}")
            async with message.channel.typing():
                await message.channel.send(f"All messages deleted for user {message.author.name}")
            return
        else:
            isBusy = True
            async with message.channel.typing():
                response = generate_reply(message.content, threadID, authorID)
                await message.channel.send(response)
            isBusy = False


def startup_Codie():
    token = os.getenv("TOKEN") or ""
    if token == "":
        raise Exception("Please add your token to the Secrets pane.")
    client.run(token)


# Bottle web server setup
@route('/')
def home():
    return "Discord bot is running!"


def run_bottle():
    run(host='0.0.0.0', port=8080)


# Starting the Bottle server in a separate thread
bottle_thread = threading.Thread(target=run_bottle)
bottle_thread.start()
startup_Codie()