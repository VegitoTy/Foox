import discord, asyncio
from discord.ext import commands

class ReasonModal(discord.ui.Modal, title="Close"):
    answer = discord.ui.TextInput(label = "Reason", style = discord.TextStyle.paragraph, placeholder="Reason for closing the ticket. Eg:- Resolved", required=True)

    async def on_submit(self, interaction:discord.Interaction):
        channel = interaction.guild.get_channel(1124607726530609214)
        embed = discord.Embed(title="Ticket Closed", colour=0xADD8E6)
        embed.add_field(name=f"Opened By", value=f"{user.mention}", inline=True)
        embed.add_field(name=f"Closed By", value=f"{interaction.user.mention}", inline=True)
        embed.add_field(name=f"Reason", value=f"{self.answer}", inline=True)
        await channel.send(embed=embed)

        await interaction.response.send_message("Closing..")
        await asyncio.sleep(1)
        await interaction.channel.delete()

class CloseTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Close", custom_id="close", style=discord.ButtonStyle.red)
    async def _close(self, interaction:discord.Interaction, button:discord.ui.Button):
        channel = interaction.guild.get_channel(1124607726530609214)
        embed = discord.Embed(title="Ticket Closed", colour=0xADD8E6)
        embed.add_field(name=f"Opened By", value=f"{user.mention}", inline=True)
        embed.add_field(name=f"Closed By", value=f"{interaction.user.mention}", inline=True)
        embed.add_field(name=f"Reason", value=f"No reason given", inline=True)
        embed.set_thumbnail(url=user.avatar.url)
        await channel.send(embed=embed)

        await interaction.response.send_message("Closing..")
        await asyncio.sleep(1)
        await interaction.channel.delete()

class InTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Close", custom_id="close_ticket", style=discord.ButtonStyle.red, emoji="🔒")
    async def _close_ticket(self, interaction:discord.Interaction, button:discord.ui.Button):
        view = CloseTicket()
        await interaction.response.send_message(f"{interaction.user.mention} Are you sure you want to close this ticket?", view=view)

    @discord.ui.button(label="Close With Reason", custom_id="close_with_reason", style=discord.ButtonStyle.red, emoji="🔐")
    async def _close_with_reason(self, interaction:discord.Interaction, button:discord.ui.Button):
        await interaction.response.send_modal(ReasonModal())
    
    @discord.ui.button(label="Save Ticket", custom_id="save_ticket", style=discord.ButtonStyle.blurple, emoji="🗒️")
    async def _save_ticket(self, interaction:discord.Interaction, button:discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("You do not have the required permissions to do that", ephemeral=True)

        await interaction.channel.set_permissions(target=user, overwrite=None)

        await interaction.response.send_message(f"Ticket Saved. Requested By {interaction.user.mention}")

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Open A Ticket", custom_id="ticket", style=discord.ButtonStyle.green, emoji="<:FooxGun:1015872747072663592>")
    async def _ticket(self, interaction:discord.Interaction, button:discord.ui.Button):
        global user

        user = interaction.user

        view = InTicketView()

        tickets_cg = discord.utils.get(interaction.guild.categories, id=1124373765879496785)

        ticket:discord.TextChannel = await tickets_cg.create_text_channel(f"ticket-{interaction.user.name}")

        await ticket.set_permissions(interaction.user, read_messages=True, send_messages=True)
        await ticket.set_permissions(interaction.guild.default_role, view_channel=False)

        await interaction.response.send_message(f"Opened A Ticket! {ticket.mention}", ephemeral=True)

        embed = discord.Embed(title="Foox Den Support", description=f"Hi {interaction.user.mention}!\nSomeone will be here to help you with your query soon.\nMeanwhile describe your issue and wait for a response.", colour=interaction.user.colour)
        embed.set_thumbnail(url=interaction.guild.icon.url)
        await ticket.send("<@&879161719358906470>", embed=embed, view=view)

class Tickets(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name='Tickets', aliases=["tickets", "Tk", "tk"], description=f"Shows the drawing list\nUsage:- f!Dc list")
    @commands.has_permissions(administrator=True)
    async def _tickets(self, ctx:commands.Context):
        view = TicketView()
        embed = discord.Embed(title="Tickets", description="Open a ticket by using the button below!", color=0xADD8E6)
        embed.set_thumbnail(url=ctx.guild.icon.url)

        await ctx.send(embed=embed, view=view)

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(
        Tickets(bot)
    )