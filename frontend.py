import discord
from discord.ext import commands
from bot import Bot
import json
import os
from backend import scoring, send
import utils
from pymongo import MongoClient
from backend import mongoer
from env_vars import *

def main():


    TOKEN = DISCORD_TOKEN

    intents = discord.Intents.default()
    intents.message_content = True
    intents.voice_states = True
    intents.members = True

    bot = commands.Bot(COMMAND_CHAR, intents=intents)
    client = discord.Client(intents=intents)

    with open("jsons/team_keys.json", "r") as f:
        valid_teams = json.load(f)

    runningGames = {}

    def get_server_id(ctx):
        server_id = ctx.guild.id
        return str(server_id)

    @bot.event
    async def on_ready():
        print(f'Bot logged in as {bot.user}')
    
    @bot.event
    async def on_message(message):
        await bot.process_commands(message)
        if message.author == bot.user:
            return

        if isinstance(message.channel, discord.DMChannel) and message.reference:
            for server, game in runningGames.items():
                if message.reference.message_id in game.stored_dms:
                    message_ref = await message.channel.fetch_message(message.reference.message_id)
                    await game.parse_message(message, message_ref)
    
    @bot.command()
    async def dm(ctx):
        if ctx.guild:
            await runningGames[get_server_id(ctx)].send_dm(ctx)

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
    async def b(ctx, val):
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
    
    @bot.command()
    async def score(ctx):
        if ctx.guild:
            server_id = get_server_id(ctx)

            await runningGames[server_id].get_score()

    @bot.command()
    async def reset(ctx):
        if ctx.guild:
            server_id = get_server_id(ctx)

            await runningGames[server_id].reset()
    
    @bot.command()
    async def helpplease(ctx):
        if ctx.guild:
            server_id = get_server_id(ctx)

            await runningGames[server_id].help()
    
    @bot.command()
    async def recalc(ctx):
        scoring.calc_all_teams()
        await ctx.send("recalculated")
    
    @bot.command()
    async def roster(ctx):
        if ctx.guild:
            server_id = get_server_id(ctx)

            await runningGames[server_id].roster()
    
    @bot.command()
    async def webhook(ctx, webhook_url):
        if ctx.guild:
            server_id = get_server_id(ctx)

            webhooks = mongoer.find("webhook_urls")
            if not webhooks:
                mongoer.insert("webhook_urls", {server_id: webhook_url})
            else:
                mongoer.update_document("webhook_urls", query={"_id": webhooks[0]["_id"]}, new_data={server_id: webhook_url})

            if send.send_webhook("test test", webhook_url):
                await ctx.send("you are now breathing manually")
            else:
                await ctx.send("hmm something went wrong")

    bot.run(TOKEN)
    
if __name__ == '__main__':
    main()