import time, pathlib, os
from dotenv import load_dotenv
from pymongo import MongoClient
from discord.ext import commands, tasks

load_dotenv(dotenv_path=pathlib.Path("./.env"))

MONGODB = os.getenv("MONGODB")

class Tasks(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot
        self.cluster = MongoClient(MONGODB)
        self.db = self.cluster["foox"]
        self.bans = self.db["bans"]

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

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(
        Tasks(bot)
    )