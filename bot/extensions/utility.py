import discord, pymongo, random
from pymongo import MongoClient
from discord.ext import commands

class Utility(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot
        self.cluster = MongoClient("mongodb+srv://VegitoTy:59894179@cluster0.rlky3md.mongodb.net/?retryWrites=true&w=majority")
        self.db = self.cluster["foox"]
        self.drawing = self.db["drawing"]

    @commands.command(name='Userinfo', aliases=['whois', 'ui', 'UI'], description=f"Shows The Info Of A User\nUsage:- f!Ui [User]")
    async def _ui(self, ctx:commands.Context, user:discord.User=None):
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
            drawing_data = self.drawing.find_one({})
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
            drawing_data = self.drawing.find_one({})
            if drawing_data == None:
                self.drawing.insert_one({"list": args})
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
            
            self.drawing.update_one(drawing_data, {"list": unique_list})

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
            drawing_data = self.drawing.find_one({})
            if drawing_data == None:
                return await ctx.send("There is no drawing data available.")
            
            drawing_list:list = drawing_data["list"]

            updated_drawing_list = [item for item in drawing_list if item not in args]
            missing = [item for item in args if item not in updated_drawing_list]

            self.drawing.update_one(drawing_data, {"list": updated_drawing_list})

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
            drawing_data = self.drawing.find_one({})
            if drawing_data == None:
                return await ctx.send("There is no drawing data available.")
            
            drawing_list:list = drawing_data["list"]
            message = f"Here are all the words that are in the list:\n"
            for word in drawing_list:
                message = f"{message}, {word}"
            message = message.replace(',', '', 1)

            await ctx.send(message)

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(
        Utility(bot)
    )