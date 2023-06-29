import discord, datetime
from discord.ext import commands


class Events(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener("on_member_join")
    async def _welcome_message(self, member:discord.Member):
        embed = discord.Embed(title=f"Welcome {member.name}!", description=f"You are the {member.guild.member_count}th member in this server!", timestamp=datetime.datetime.utcnow())
        try:
            embed.set_image(url=member.avatar.url)
        except:
            pass
        channel = await self.bot.fetch_channel(878419521558437948)
        await channel.send(f"Hi {member.mention}!", embed=embed)

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(
        Events(bot)
    )