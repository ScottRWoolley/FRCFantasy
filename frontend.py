import discord
from discord.ext import commands
from bot import Bot
import json

def main():

    file = open('token.txt','r')
    content = file.read()
    file.close()

    TOKEN = content

    intents = discord.Intents.default()
    intents.message_content = True
    intents.voice_states = True
    intents.members = True

    bot = commands.Bot(command_prefix="?", intents=intents)
    client = discord.Client(intents=intents)

    with open("team_keys.json", "r") as f:
        valid_teams = json.load(f)

    runningGames = {}

    def get_server_id(ctx):
        server_id = ctx.guild.id
        return server_id

    @bot.event
    async def on_ready():
        print(f'Bot logged in as {bot.user}')
    
    @bot.command()
    async def setup(ctx):
        if ctx.guild:
            server_id = get_server_id(ctx)

            runningGames[server_id] = Bot(ctx)
            await runningGames[server_id].setup()

    @bot.command()
    async def maxpool(ctx, val):
        if ctx.guild:
            server_id = get_server_id(ctx)
            try:
                val = int(val)
                await runningGames[server_id].setmaxpool(val)
            except:
                pass
    
    @bot.command()
    async def bid(ctx, val):
        if ctx.guild:
            server_id = get_server_id(ctx)
            try:
                val = int(val)
                await runningGames[server_id].bid(ctx, val)
            except:
                pass

    @bot.command()
    async def poolteams(ctx):
        if ctx.guild:
            server_id = get_server_id(ctx)

            await runningGames[server_id].poolteams(ctx)
    
    @bot.command()
    async def pool(ctx, team_num):
        if ctx.guild and team_num in valid_teams:
            server_id = get_server_id(ctx)

            await runningGames[server_id].addtopool(ctx, team_num)
    
    @bot.command()
    async def unpool(ctx, team_num):
        if ctx.guild and team_num in valid_teams:
            server_id = get_server_id(ctx)

            await runningGames[server_id].unpool(ctx, team_num)

    @bot.command()
    async def auction(ctx):
        if ctx.guild:
            server_id = get_server_id(ctx)

            await runningGames[server_id].auction()

    bot.run(TOKEN)
    
if __name__ == '__main__':
    main()