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
# /generatecode (Owner Only)
# ------------------------------
@bot.slash_command(description="Generate a temporary access code.")
@commands.is_owner()
async def generatecode(ctx, expires_in_minutes: int = 5):
    code = secrets.token_hex(4)
    expire_time = time.time() + (expires_in_minutes * 60)
    access_codes[code] = expire_time

    await ctx.respond(
        f"✅ **Access Code Generated**\n"
        f"**Code:** `{code}`\n"
        f"Expires in: **{expires_in_minutes} minutes**"
    )


# ------------------------------
# Protected Command Template
# ------------------------------
async def require_code(ctx, code: str):
    if not has_valid_code(code):
        await ctx.respond("❌ Invalid or expired access code.")
        return False
    return True


# ------------------------------
# /createchannel (Requires Code)
# ------------------------------
@bot.slash_command(description="Create a new text channel (requires valid access code)")
async def createchannel(ctx, channel_name: str, access_code: str):
    if not await require_code(ctx, access_code):
        return

    guild = ctx.guild
    await guild.create_text_channel(channel_name)
    await ctx.respond(f"✅ Created channel **#{channel_name}**")


# ------------------------------
# /announce (Requires Code)
# ------------------------------
@bot.slash_command(description="Send announcement message to a channel.")
async def announce(ctx, channel: discord.TextChannel, message: str, access_code: str):
    if not await require_code(ctx, access_code):
        return

    await channel.send(f"📢 **Announcement:**\n{message}")
    await ctx.respond("✅ Announcement sent!")


# ------------------------------
# /addrole (Requires Code)
# ------------------------------
@bot.slash_command(description="Give a role to a user.")
async def addrole(ctx, member: discord.Member, role: discord.Role, access_code: str):
    if not await require_code(ctx, access_code):
        return

    await member.add_roles(role)
    await ctx.respond(f"✅ Added role **{role.name}** to **{member.name}**")


# ------------------------------
# Bot Start
# ------------------------------
bot.run("YOUR_BOT_TOKEN")
