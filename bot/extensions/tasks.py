import time, pathlib, os, certifi
from dotenv import load_dotenv
from pymongo import MongoClient
from discord.ext import commands, tasks

load_dotenv(dotenv_path=pathlib.Path("./.env"))

MONGODB = os.getenv("MONGODB")

class Tasks(commands.Cog):

    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
        self.cluster = MongoClient(MONGODB, tlsCAFile=certifi.where())
        self.db = self.cluster["foox"]
        self.bans = self.db["bans"]
        self.tickets = self.db["tickets"]

    @tasks.loop(seconds=10.0)
    async def _unban(self):
        cursor = self.bans.find({})
        for document in cursor:
            time_to_unban = document["time_to_unban"]
            if time.time() <= time_to_unban:
                guild_id = document["guild_id"]
                guild = await self.bot.fetch_guild(guild_id)
                async for entry in guild.bans():
                    user = entry.user
                    if user.id == document["_id"]:
                        try:
                            await guild.unban(user, reason="Ban Duration Ended")
                        except:
                            pass
                self.bans.delete_one(document)

    @_unban.before_loop
    async def _before_unban(self):
        await self.bot.wait_until_ready()

    @tasks.loop(seconds=10.0)
    async def _ticket_check(self):
        cursor = self.tickets.find({})
        for document in cursor:
            if document["user_left"] or document["status"] == "CLOSED":
                continue

            guild_id = document["guild_id"]
            channel_id = document["channel_id"]
            user_id = document["user_id"]
            
            guild = await self.bot.fetch_guild(guild_id)
            channel = await guild.fetch_channel(channel_id)
            user = await guild.fetch_member(user_id)

            if user == None:
                await channel.send("The user who opened this ticket has left.")
                self.tickets.update_one(document, {"$set": {"user_left": True}})
    
    @_ticket_check.before_loop
    async def _before_ticket_check(self):
        await self.bot.wait_until_ready()

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(
        Tasks(bot)
    )