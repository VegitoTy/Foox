import discord
from discord.ext import commands

error_emote = "❌"

class error_handler(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot
    
    @commands.Cog.listener('on_command_error')
    async def errorhandler(self, ctx:commands.Context, exception):
        sus = False
        
        exception = exception.__cause__ or exception

        if isinstance(exception, commands.NotOwner):
            description = f"> You are not the owner of this bot."
        elif isinstance(exception, commands.CommandInvokeError):
          description = f"> Something went wrong during invocation of command `{ctx.command}`."
          sus = True
        elif isinstance(exception, commands.CommandOnCooldown):
            description = f"> This command is on cooldown. Retry in `{exception.retry_after:.2f}` seconds."
        elif isinstance(exception, commands.errors.CheckFailure):
            description = f"> You do not have the right permissions to use this command"
        elif isinstance(exception, commands.errors.MissingRequiredArgument):
            args = ""
            for arg in exception.args:
                args = args + f"`{arg[:-40]}`, "
            args = args[:-2]
            description = f"> Missing required argument(s): {args}"
        elif isinstance(exception, commands.MemberNotFound):
            description = f"> Member Not Found"
        elif isinstance(exception, commands.UserNotFound):
            description = f"> User Not Found"
        elif isinstance(exception, TypeError):
            description = "> Invalid option type"
            sus = True
        elif isinstance(exception, commands.CommandNotFound):
            return
        else:
            description = f"! There was a error with this command\n{exception}"
            sus = True

        embed = discord.Embed(title=f"{error_emote} Error", description=description, color=0x3498db)

        if sus == True:
            raise exception

        try:
            await ctx.reply(embed=embed)
        except Exception as e:
            await ctx.send(embed=embed)
            raise e
            
async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(
        error_handler(bot)
    )