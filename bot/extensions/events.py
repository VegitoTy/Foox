import discord, datetime
from discord.ext import commands

class Events(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener("on_member_join")
    async def _welcome_message(self, member:discord.Member):
        channel = await self.bot.fetch_channel(878419521558437948)
        await channel.send(f"Welcome {member.mention}! Please be sure to check out <#878413758563770419> and make yourself colorful with <#878430024263434310> ! Then tell everyone a little about yourself in <#878414893232033802>")

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(
        Events(bot)
    )