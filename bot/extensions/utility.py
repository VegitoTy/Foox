import discord
import random, asyncio, pathlib, os, certifi
from dotenv import load_dotenv
from pymongo import MongoClient
from discord.ext import commands

load_dotenv(dotenv_path=pathlib.Path("./.env"))

MONGODB = os.getenv("MONGODB")

class Utility(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot
        self.cluster = MongoClient(MONGODB, tlsCAFile=certifi.where())
        self.db = self.cluster["foox"]
        self.utility = self.db["utility"]

    @commands.command(name='Userinfo', aliases=['whois', 'ui', 'UI'], description=f"Shows The Info Of A User\nUsage:- f!Ui [User]")
    async def _ui(self, ctx:commands.Context, user:discord.User=None):
        async with ctx.typing():
            await asyncio.sleep(2)
            if not user:
                user = ctx.author
            
            member = await ctx.guild.query_members(user_ids=[user.id])
            if len(member) == 0:
                created_at = user.created_at
                embed = discord.Embed(colour=0x3498db, timestamp=ctx.message.created_at)
                embed.set_author(name=f'User Info - {user}')
                embed.set_thumbnail(url=user.avatar.url)
                embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.display_avatar.url)
                embed.add_field(name='ID: ', value=user.id, inline=False)
                embed.add_field(name='Name: ',value=user.name,inline=False)
                embed.add_field(name='Created at:',value=discord.utils.format_dt(dt=created_at),inline=False)
            else:
                member:discord.Member = member[0]
                created_at = member.created_at
                joined_at = member.joined_at
                rlist = []
                ignored_roles = 0
                for role in member.roles:
                    if len(rlist) >= 15:
                        ignored_roles += 1
                    if role.name != "@everyone" and len(rlist) < 15:
                        rlist.append(role.mention)
                e = ""
                for role in rlist:
                    e += f"{role}, "     
                embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)
                embed.set_author(name=f'User Info - {member}')
                embed.set_thumbnail(url=member.avatar.url)
                embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.display_avatar.url)
                embed.add_field(name='ID: ',value=member.id,inline=False)
                embed.add_field(name='Name:',value=member.name,inline=False)
                embed.add_field(name='Created at:',value=discord.utils.format_dt(created_at),inline=False)
                embed.add_field(name='Joined at:',value=discord.utils.format_dt(joined_at),inline=False)
                if ignored_roles == 0:
                    embed.add_field(name=f'Roles: {len(member.roles)}', value=f'{e[:-2]}',inline=False)
                else:
                    embed.add_field(name=f'Roles: {len(member.roles)}', value=f'{e[:-2]} And {ignored_roles} more roles..',inline=False)
                embed.add_field(name='Top Role:',value=member.top_role.mention,inline=False)
            await ctx.send(f'Info about {user}', embed=embed)
    
    @commands.group(name='DrawingChallenge', aliases=['drawingchallenge', 'DC', 'dc'], description=f"Sends two random topics for a drawing challenge\nUsage:- f!dc", invoke_without_command=True, case_insensitive=True)
    async def _dc(self, ctx:commands.Context):
        async with ctx.typing():
            drawing_data = self.utility.find_one({"_id":"drawing"})
            if drawing_data == None:
                return await ctx.send("There is no drawing data available")
            
            drawing_list = drawing_data["list"]

            first_choice = random.choice(drawing_list)
            second_choice = random.choice(drawing_list)

            while first_choice == second_choice:
                second_choice = random.choice(drawing_list)

            await ctx.send(f"Here are the two topics: {first_choice} and {second_choice}")

    @_dc.command(name='add', description=f"Adds Words To The Drawing List\nUsage:- f!Dc add word1 word2...")
    @commands.has_permissions(administrator=True)
    async def _dc_add(self, ctx:commands.Context, *args):
        async with ctx.typing():
            args = list(args)

            drawing_data = self.utility.find_one({"_id":"drawing"})
            if drawing_data == None:
                self.utility.insert_one({"_id": "drawing", "list": args})
                return await ctx.send("Added")
            
            drawing_list:list = drawing_data["list"]
            unique_list = []
            merged_list = drawing_list + args
            duplicates = []

            for item in merged_list:
                if item in unique_list:
                    duplicates.append(item)
                else:
                    unique_list.append(item)
            
            self.utility.replace_one(drawing_data, {"_id": "drawing", "list": unique_list})

            if duplicates == []:
                return await ctx.send("Added.")
            
            message = f"Added. The following word(s) were not added as they were already in the list:"
            for duplicate in duplicates:
                message = f"{message}\n{duplicate}"

            await ctx.send(message)

    @_dc.command(name='remove', description=f"Remove Words From The Drawing List\nUsage:- f!Dc remove word1 word2...")
    @commands.has_permissions(administrator=True)
    async def _dc_remove(self, ctx:commands.Context, *args):
        async with ctx.typing():
            args = list(args)

            drawing_data = self.utility.find_one({"_id": "drawing"})
            if drawing_data == None:
                return await ctx.send("There is no drawing data available.")
            
            drawing_list:list = drawing_data["list"]

            missing = [item for item in args if item not in drawing_list]
            updated_drawing_list = [item for item in drawing_list if item not in args]

            self.utility.replace_one(drawing_data, {"_id": "drawing", "list": updated_drawing_list})

            if missing == []:
                return await ctx.send("Done!")
            
            message = f"Removed. The following word(s) were not in the list already:"
            for miss in missing:
                message = f"{message}\n{miss}"
            
            await ctx.send(message)
    
    @_dc.command(name='list', description=f"Shows the drawing list\nUsage:- f!Dc list")
    @commands.has_permissions(administrator=True)
    async def _dc_list(self, ctx:commands.Context):
        async with ctx.typing():
            drawing_data = self.utility.find_one({"_id": "drawing"})
            if drawing_data == None:
                return await ctx.send("There is no drawing data available.")
            
            drawing_list:list = drawing_data["list"]
            message = f"Here are all the words that are in the list:\n"
            for word in drawing_list:
                message = f"{message}, {word}"
            message = message.replace(',', '', 1)

            await ctx.send(message)
    
    @commands.command(name='Emoji', aliases=['emoji'], description=f"Sends a random emoji\nUsage:- f!Emoji")
    async def _emoji(self, ctx:commands.Context):
        async with ctx.typing():
            random_emoji = random.choice(ctx.guild.emojis)

            await ctx.send(random_emoji)

    @commands.group(name='Cookie', aliases=['cookie', 'ck'], description=f"Sends the Foox Cookie Emoji\nUsage:- f!Cookie", invoke_without_command=True, case_insensitive=True)
    async def _cookie(self, ctx:commands.Context):
        async with ctx.typing():
            emoji_data = self.utility.find_one({"_id": "pat"})
            emoji = emoji_data["pat"]

            await ctx.send(emoji)
    
    @_cookie.command(name='update', description=f"Updates the cookie emoji\nUsage:- f!Cookie update")
    @commands.has_permissions(administrator=True)
    async def _cookie_update(self, ctx:commands.Context, emoji:discord.Emoji):
        async with ctx.typing():
            emoji_data = self.utility.find_one_and_replace({"_id": "pat"}, {"_id": "pat", "pat": str(emoji)})
            prev_emoji = emoji_data["pat"]

            await ctx.send(f"Replaced {prev_emoji} with {emoji}")
    
    @commands.group(name='Screm', aliases=['screm'], description=f"Sends the Foox Screm Emoji\nUsage:- f!Screm", invoke_without_command=True, case_insensitive=True)
    async def _screm(self, ctx:commands.Context):
        async with ctx.typing():
            emoji_data = self.utility.find_one({"_id": "screm"})
            emoji = emoji_data["screm"]

            await ctx.send(emoji)
    
    @_screm.command(name='update', description=f"Updates the screm emoji\nUsage:- f!Screm update")
    @commands.has_permissions(administrator=True)
    async def _screm_update(self, ctx:commands.Context, emoji:discord.Emoji):
        async with ctx.typing():
            emoji_data = self.utility.find_one_and_replace({"_id": "screm"}, {"_id": "screm", "screm": str(emoji)})
            prev_emoji = emoji_data["screm"]

            await ctx.send(f"Replaced {prev_emoji} with {emoji}")

    @commands.group(name='Site', aliases=['site'], description=f"Sends a link to the Foox website\nUsage:- f!Site", invoke_without_command=True, case_insensitive=True)
    async def _site(self, ctx:commands.Context):
        async with ctx.typing():
            site_data = self.utility.find_one({"_id": "site"})
            site = site_data["site"]

            await ctx.send(site)
    
    @_site.command(name="update", description=f"Updates the link to the Foox website\nUsage:- f!Site update")
    @commands.has_permissions(administrator=True)
    async def _site_update(self, ctx:commands.Context, link:str):
        async with ctx.typing():
            site_data = self.utility.find_one_and_replace({"_id": "site"}, {"_id": "site", "site": link})
            prev_site = site_data["site"]

            await ctx.send(f"Replaced `{prev_site}` with `{link}`")
    
    @commands.group(name='Shop', aliases=['shop'], description=f"Sends a link to the Foox Shop\nUsage:- f!Shop", invoke_without_command=True, case_insensitive=True)
    async def _shop(self, ctx:commands.Context):
        async with ctx.typing():
            shop_data = self.utility.find_one({"_id": "shop"})
            shop = shop_data["shop"]

            await ctx.send(shop)
    
    @_shop.command(name="update", description=f"Updates the link to the Foox Shop\nUsage:- f!Shop update")
    @commands.has_permissions(administrator=True)
    async def _shop_update(self, ctx:commands.Context, link:str):
        async with ctx.typing():
            shop_data = self.utility.find_one_and_replace({"_id": "shop"}, {"_id": "shop", "shop": link})
            prev_site = shop_data["shop"]

            await ctx.send(f"Replaced `{prev_site}` with `{link}`")

    @commands.group(name='Patreon', aliases=['patreon', 'pt'], description=f"Sends a link to the Foox Patreon\nUsage:- f!Patreon", invoke_without_command=True, case_insensitive=True)
    async def _patreon(self, ctx:commands.Context):
        async with ctx.typing():
            patreon_data = self.utility.find_one({"_id": "patreon"})
            patreon = patreon_data["patreon"]

            await ctx.send(patreon)

    @_patreon.command(name="update", description=f"Updates the link to the Foox Patreon\nUsage:- f!Patreon update")
    @commands.has_permissions(administrator=True)
    async def _patreon_update(self, ctx:commands.Context, link:str):
        async with ctx.typing():
            patreon_data = self.utility.find_one_and_replace({"_id": "patreon"}, {"_id": "patreon", "patreon": link})
            prev_site = patreon_data["patreon"]

            await ctx.send(f"Replaced `{prev_site}` with `{link}`")
    
    @commands.group(name='Youtube', aliases=['youtube', 'YT', 'Yt', 'yt'], description=f"Sends a link to the Foox Youtube\nUsage:- f!Youtube", invoke_without_command=True, case_insensitive=True)
    async def _youtube(self, ctx:commands.Context):
        async with ctx.typing():
            youtube_data = self.utility.find_one({"_id": "youtube"})
            youtube = youtube_data["youtube"]

            await ctx.send(youtube)

    @_youtube.command(name="update", description=f"Updates the link to the Foox Youtube\nUsage:- f!Youtube update")
    @commands.has_permissions(administrator=True)
    async def _youtube_update(self, ctx:commands.Context, link:str):
        async with ctx.typing():
            youtube_data = self.utility.find_one_and_replace({"_id": "youtube"}, {"_id": "youtube", "youtube": link})
            prev_site = youtube_data["youtube"]

            await ctx.send(f"Replaced `{prev_site}` with `{link}`")
    
    @commands.group(name='Twitter', aliases=['twitter', 'TwT', 'Twt', 'twt'], description=f"Sends a link to the Foox twitter\nUsage:- f!Twitter", invoke_without_command=True, case_insensitive=True)
    async def _twitter(self, ctx:commands.Context):
        async with ctx.typing():
            twitter_data = self.utility.find_one({"_id": "twitter"})
            twitter = twitter_data["twitter"]

            await ctx.send(twitter)

    @_twitter.command(name="update", description=f"Updates the link to the Foox Twitter\nUsage:- f!Twitter update")
    @commands.has_permissions(administrator=True)
    async def _twitter_update(self, ctx:commands.Context, link:str):
        async with ctx.typing():
            twitter_data = self.utility.find_one_and_replace({"_id": "twitter"}, {"_id": "twitter", "twitter": link})
            prev_site = twitter_data["twitter"]

            await ctx.send(f"Replaced `{prev_site}` with `{link}`")
    
    @commands.group(name='Kofi', aliases=['kofi'], description=f"Sends a link to the Foox Ko-Fi page\nUsage:- f!Kofi", invoke_without_command=True, case_insensitive=True)
    async def _kofi(self, ctx:commands.Context):
        async with ctx.typing():
            kofi_data = self.utility.find_one({"_id": "kofi"})
            kofi = kofi_data["kofi"]

            await ctx.send(kofi)

    @_kofi.command(name="update", description=f"Updates the link to the Foox Ko-Fi page\nUsage:- f!Kofi update")
    @commands.has_permissions(administrator=True)
    async def _kofi_update(self, ctx:commands.Context, link:str):
        async with ctx.typing():
            kofi_data = self.utility.find_one_and_replace({"_id": "kofi"}, {"_id": "kofi", "kofi": link})
            prev_site = kofi_data["kofi"]

            await ctx.send(f"Replaced `{prev_site}` with `{link}`")

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(
        Utility(bot)
    )