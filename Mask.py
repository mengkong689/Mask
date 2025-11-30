import discord
from discord.ext import commands
import asyncio
import secrets
import time

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Temporary access codes stored in memory
access_codes = {}  # code: expire_timestamp


# ------------------------------
# Helper: Check if user has valid code
# ------------------------------
def has_valid_code(code: str):
    if code not in access_codes:
        return False
    if time.time() > access_codes[code]:
        del access_codes[code]
        return False
    return True


# ------------------------------
# !generatecode (Owner Only)
# ------------------------------
@bot.command()
@commands.is_owner()
async def generatecode(ctx, expires_in_minutes: int = 5):
    code = secrets.token_hex(4)
    expire_time = time.time() + (expires_in_minutes * 60)
    access_codes[code] = expire_time

    await ctx.send(
        f"✅ **Access Code Generated**\n"
        f"**Code:** `{code}`\n"
        f"Expires in: **{expires_in_minutes} minutes**"
    )


# ------------------------------
# Protected Command Helper
# ------------------------------
async def require_code(ctx, code: str):
    if not has_valid_code(code):
        await ctx.send("❌ Invalid or expired access code.")
        return False
    return True


# ------------------------------
# !createchannel (Requires Code)
# ------------------------------
@bot.command()
async def createchannel(ctx, channel_name: str, access_code: str):
    if not await require_code(ctx, access_code):
        return

    guild = ctx.guild
    await guild.create_text_channel(channel_name)
    await ctx.send(f"✅ Created channel **#{channel_name}**")


# ------------------------------
# !announce (Requires Code)
# ------------------------------
@bot.command()
async def announce(ctx, channel: discord.TextChannel, *, message_and_code: str):
    """Usage: !announce #channel message_here | code"""
    if "|" not in message_and_code:
        return await ctx.send("❌ Use format: `!announce #channel message | code`")

    message, access_code = [part.strip() for part in message_and_code.split("|", 1)]

    if not await require_code(ctx, access_code):
        return

    await channel.send(f"📢 **Announcement:**\n{message}")
    await ctx.send("✅ Announcement sent!")


# ------------------------------
# !addrole (Requires Code)
# ------------------------------
@bot.command()
async def addrole(ctx, member: discord.Member, role: discord.Role, access_code: str):
    if not await require_code(ctx, access_code):
        return

    await member.add_roles(role)
    await ctx.send(f"✅ Added role **{role.name}** to **{member.name}**")


# ------------------------------
# Bot Start
# ------------------------------
bot.run("MTA3MzE5MjA3MzY4OTMwMTAxNA.GwENak.1yxC5OwXnqgBjqt6FZDr0xPBz-WqIygd0dZUYw")
