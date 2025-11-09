import discord
from discord.ext import commands
import random
import json
import asyncio
from backend import send

class Bot:
    def __init__(self, ctx):
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
        self.MAXPOOLTEAMS = 5
    
    async def setup(self):
        await self.ctx.send("use ?maxpool [num] to set the maximum amount of teams one person can put in the auction pool (default 5)")
    
    async def setmaxpool(self, num):
        self.MAXPOOLTEAMS = num
        await self.ctx.send(f"ok it's at {num} now")
    
    async def poolteams(self, ctx):
        author = ctx.author.name
        pooledteams = sum(self.teampool.values(), [])
        authorpooledteams = self.teampool[author]

        message = f'''here are the current teams in the pool:\n{", ".join(pooledteams)}
you personally have contributed:{", ".join(authorpooledteams)}\nyou can contribute {self.MAXPOOLTEAMS-len(authorpooledteams)} more teams
use ?pool [team_num] to add it to the pool'''

        await self.ctx.send(message)
    
    async def addtopool(self, ctx, team_num):
        author = ctx.author.name
        if len(self.teampool[author]) >= self.MAXPOOLTEAMS or team_num in sum(self.teampool.values(), []):
            await self.ctx.send("you cant do that")
        else:
            self.teampool[author].append(team_num)
            await self.ctx.send(f"added\nyou can contribute {self.MAXPOOLTEAMS-len(self.teampool[author])} more teams")
    
    async def unpool(self, ctx, team_num):
        author = ctx.author.name
        if team_num not in self.teampool[author]:
            await self.ctx.send("you cant do that")
        else:
            self.teampool[author].remove(team_num)
            await self.ctx.send("removed")
    
    async def auction(self):
        pooledteams = sum(self.teampool.values(), [])
        random.seed()
        random.shuffle(pooledteams)

        self.money = {
            member.name: 100
            for member in self.ctx.guild.members if not member.bot
        }

        for team in pooledteams:
            await self.auction_team(team)
            text = "team rosters:\n"
            for player, teams in self.players.items():
                text += f"{player}: {", ".join(list(map(lambda x: x[3:], teams)))}\n"
            await self.ctx.send(text)
            await self.line()
        
        await self.ctx.send("The auction has ended!")
        
        with open("bible.json", "r") as f:
            data = json.load(f)

        data[self.serverid] = self.players
        
        with open("bible.json", "w") as f:
            json.dump(data, f)
    
    async def auction_team(self, team):
        await self.ctx.send(f"now auctioning: {team}")
        self.current_bid = 5
        self.current_buyer = ""
        await self.ctx.send(f"current price: {self.current_bid}")

        self.current_countdown = asyncio.create_task(self.countdown())
        while not await self.current_countdown:
            await self.ctx.send(f"{team}: current price: {self.current_bid}; current buyer: {self.current_buyer}")
            self.current_countdown = asyncio.create_task(self.countdown())
        
        if self.current_buyer:
            buyer = self.current_buyer
            await self.ctx.send(f"sold! team {team} for {self.current_bid} to {buyer}")
            self.money[buyer] -= self.current_bid
            await self.ctx.send(f"{buyer}, you now have {self.money[buyer]} scootbucks left")
            self.players[buyer].append("frc"+team)
        else:
            await self.ctx.send(f"oof no one wanted {team}")
        await self.line()

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
        if self.money[ctx.author.name] >= num and (num > self.current_bid or (self.current_bid == 5 and num >= self.current_bid)):
            self.current_bid = num
            self.current_buyer = ctx.author.name
            if self.current_countdown:
                self.current_countdown.cancel()
    
    async def line(self):
        await self.ctx.send("---------------------------------------")
    
    async def get_score(self):
        scores = send.score(self.serverid)
        text = ""
        for player, teams in scores.items():
            text += f"{player}:\n"
            for team, score in teams.items():
                text += f"Team {team[3:]}: {score}\n"
            text += f"{player} total: {sum(teams.values())}\n"
            text += "----------\n"
        await self.ctx.send(text)