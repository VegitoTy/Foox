import discord, pymongo, time
from discord.ext import commands, tasks
from pymongo import MongoClient


class Tasks(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot
        self.cluster = MongoClient("mongodb+srv://VegitoTy:59894179@cluster0.rlky3md.mongodb.net/?retryWrites=true&w=majority")
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