import discord
from discord.ext import commands
import secrets
import time
import asyncio
from dotenv import TOKEN

PREFIX = "$"   # <<< Change your prefix here

bot = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())

# ---------------------------------------------------------
# Access Code Storage
# ---------------------------------------------------------
access_codes = {}  
# Format:
# access_codes[code] = {
#      "expires": timestamp,
#      "used": False
# }

# ---------------------------------------------------------
# Bot Ready Event
# ---------------------------------------------------------
@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

# ---------------------------------------------------------
# Command: Generate Access Code (owner only)
# ---------------------------------------------------------
@bot.command()
@commands.is_owner()
async def gen_code(ctx, expire_seconds: int = 300):
    """
    Generate an admin access code that expires in X seconds.
    """
    code = secrets.token_hex(4)  # short code
    expire_time = time.time() + expire_seconds

    access_codes[code] = {
        "expires": expire_time,
        "used": False
    }

    await ctx.send(f"✅ **Access Code Generated**\n```\n{code}\n```\nExpires in **{expire_seconds}s**")

# ---------------------------------------------------------
# Command: Use Access Code
# ---------------------------------------------------------
@bot.command()
async def use_code(ctx, code: str):
    """
    Users can redeem an access code to unlock admin commands temporarily.
    """

    if code not in access_codes:
        return await ctx.send("❌ Invalid code.")

    data = access_codes[code]

    if data["used"]:
        return await ctx.send("❌ Code already used.")

    if time.time() > data["expires"]:
        return await ctx.send("❌ Code expired.")

    # Code valid → allow admin permission
    data["used"] = True
    role = discord.utils.get(ctx.guild.roles, name="TempAdmin")

    if role is None:
        role = await ctx.guild.create_role(name="TempAdmin", permissions=discord.Permissions(administrator=True))

    await ctx.author.add_roles(role)
    await ctx.send(f"✅ Code accepted! **{ctx.author}** now has **TempAdmin** role.")

# ---------------------------------------------------------
# Safe Commands
# ---------------------------------------------------------
@bot.command()
async def ping(ctx):
    start = time.perf_counter()
    await ctx.trigger_typing()
    end = time.perf_counter()
    latency = round((end - start) * 1000)
    await ctx.send(f"Pong! `{latency}ms`")

@bot.command()
async def clear(ctx, amount: int = 10):
    if not ctx.author.guild_permissions.manage_messages:
        return await ctx.send("❌ You don't have permission to clear messages.")

    deleted = await ctx.channel.purge(limit=amount)
    await ctx.send(f"🧹 Deleted `{len(deleted)}` messages.", delete_after=3)

@bot.command()
async def info(ctx, member: discord.Member = None):
    member = member or ctx.author

    embed = discord.Embed(title=f"{member.name}'s Info", color=discord.Color.blue())
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Status", value=member.status)
    embed.add_field(name="Top Role", value=member.top_role)
    embed.add_field(name="Joined", value=member.joined_at)

    await ctx.send(embed=embed)

@bot.command()
async def invite(ctx):
    await ctx.send("🔗 Invite the bot:\nhttps://discord.com/oauth2/authorize?client_id=YOUR_ID&permissions=8&scope=bot")

# ---------------------------------------------------------
# Run Bot
# ---------------------------------------------------------
bot.run("TOKEN")
