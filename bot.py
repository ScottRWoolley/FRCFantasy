import discord
from discord.ext import commands
import random
import asyncio

class Bot:
    async def __init__(self, ctx):
        self.serverid = ctx.guild.id
        self.ctx = ctx
        # would probably be a lot better to make a player class but too late now
        self.players = {
            member.name: []
            for member in ctx.guild.members if not member.bot
        }
        self.teampool = {
            member.name: []
            for member in ctx.guild.members if not member.bot
        }
        await ctx.send("use ?maxpool [num] to set the maximum amount of teams one person can put in the auction pool")
    
    async def setmaxpool(self, num):
        self.MAXPOOLTEAMS = num
        await self.ctx.send(f"ok it's at {num} now")
    
    async def poolteams(self, ctx):
        author = ctx.author.name
        pooledteams = sum(self.teampool.values, [])
        authorpooledteams = self.teampool[author]

        message = f'''here are the current teams in the pool:\n{", ".join(pooledteams)}
            you personally have contributed:{", ".join(authorpooledteams)}\nyou can contribute {self.MAXPOOLTEAMS-len(authorpooledteams)} more teams
            use ?pool [team_num] to add it to the pool'''

        await self.ctx.send(message)
    
    async def addtopool(self, ctx, team_num):
        author = ctx.author.name
        if len(self.teampool[author]) >= self.MAXPOOLTEAMS:
            await self.ctx.send("you cant do that")
        else:
            self.teampool[author].append(team_num)
            await self.ctx.send("added")
    
    async def auction(self):
        pooledteams = sum(self.teampool.values, [])
        random.seed()
        random.shuffle(pooledteams)

        self.money = {
            member.name: 100
            for member in self.ctx.guild.members if not member.bot
        }

        for team in pooledteams:
            await self.auction_team(team)
            text = "current team rosters:\n"
            for player, teams in self.players.items():
                text += f"{player}: {sum(teams, [])}\n"
            await self.ctx.send(text)
    
    async def auction_team(self, team):
        await self.ctx.send(f"now auctioning: {team}")
        self.current_bid = 5
        self.current_buyer = ""
        await self.ctx.send(f"current price: {self.current_bid}")

        self.current_countdown = asyncio.create_task(self.countdown())
        while not await self.current_countdown:
            await self.ctx.send(f"current price: {self.current_bid}; current buyer: {self.current_buyer}")
            self.current_countdown = asyncio.create_task(self.countdown())
        
        if self.current_buyer:
            buyer = self.current_buyer
            await self.ctx.send(f"sold! team {team} for {self.current_bid} to {buyer}")
            self.money[buyer] -= self.current_bid
            await self.ctx.send(f"{buyer}, you now have {self.money[buyer]} scootbucks left")
            self.players[buyer].append(team)
        else:
            await self.ctx.send(f"oof no one wanted {team}")

    async def countdown(self):
        seconds = 15
        message = await self.ctx.send(f"Time left to bid: {seconds}")
        try:
            while seconds > 0:
                await asyncio.sleep(1)
                seconds -= 1
                await message.edit(content=f"Time left to bid: {seconds}")
            await message.edit(content="Time expired")
            return True
        except asyncio.CancelledError:
            return False
        finally:
            self.current_countdown = False
    
    async def bid(self, ctx, num):
        if self.money[ctx.author.name] >= num:
            self.current_bid = num
            self.current_buyer = ctx.author.name
            if self.current_countdown:
                self.current_countdown.cancel()