import discord, os, pathlib
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv(dotenv_path=pathlib.Path("./.env"))

TOKEN = os.getenv("TOKEN")

class Foox(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("f!"),
                         status=discord.Status.idle,
                         activity=discord.Activity(type=discord.ActivityType.watching, name="The Foox Den"),
                         intents=discord.Intents.all()
        )
    
    async def setup_hook(self):
        for filename in os.listdir("./bot/extensions"):
            if filename.endswith(".py"):
                extension = f"bot.extensions.{filename[:-3]}"
                await self.load_extension(extension)
        await self.load_extension("jishaku")
        await bot.tree.sync()

    async def is_owner(self, user:discord.User):
        if user.id == 766508994390523926:
            return True
        
        return await super().is_owner(user)
    
    async def on_ready(self):
        channel = await self.fetch_channel(878421905756004383)
        await channel.send('Bot Has Started')
        print(f'Logged In As {self.user}')
    
    async def close(self):
        channel = await self.fetch_channel(878421905756004383)
        await channel.send("Bot Has Stopped.")
        print(f"Logging Out...")
        await super().close()

bot = Foox()
bot.run(TOKEN)