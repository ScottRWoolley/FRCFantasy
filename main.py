import asyncio
 
import discord
from aiohttp import web
from discord.ext import commands
 
from env_vars import DISCORD_TOKEN, COMMAND_CHAR
from state_manager import StateManager
from repository import ServerRepository
from api import create_app
 
EXTENSIONS = [
    "cogs.server_cog",
]
 
API_HOST = "0.0.0.0"
API_PORT = 8080
 
 
async def main():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
 
    bot = commands.Bot(command_prefix=COMMAND_CHAR, intents=intents)
    bot.state_manager = StateManager(ServerRepository())
 
    @bot.event
    async def on_ready():
        guild_members = {
            str(g.id): [m.name for m in g.members if not m.bot]
            for g in bot.guilds
        }
        bot.state_manager.warm_cache(guild_members)
        print(f"Bot logged in as {bot.user}, warmed {len(guild_members)} guild(s)")
 
    for ext in EXTENSIONS:
        await bot.load_extension(ext)
 
    # Start the HTTP API on the same event loop the bot runs on. This
    # doesn't block -- site.start() just registers the listener with
    # the loop and returns, so bot.start() below runs concurrently
    # with incoming POSTs being handled.
    app = create_app(bot, bot.state_manager)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, API_HOST, API_PORT)
    await site.start()
    print(f"API listening on http://{API_HOST}:{API_PORT}")
 
    async with bot:
        await bot.start(DISCORD_TOKEN)
 
 
if __name__ == "__main__":
    asyncio.run(main())