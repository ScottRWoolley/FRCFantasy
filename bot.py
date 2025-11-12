import discord
from discord.ext import commands
import random
import json
import asyncio
from backend import send
import math

class Bot:
    def __init__(self, ctx):
        self.serverid = ctx.guild.id
        self.ctx = ctx
        self.AUCTIONTIME = 10
        
    
    async def setup(self):
        await self.ctx.send("use ?helpplease for a list of commands")
        with open("bible.json", "r") as f:
            data = json.load(f)

        if str(self.serverid) in data.keys():
            self.players = data[str(self.serverid)]
        
        # would probably be a lot better to make a player class but too late now
        self.players = {
            member.name: []
            for member in self.ctx.guild.members if not member.bot
        }
        self.teampool = {
            member.name: []
            for member in self.ctx.guild.members if not member.bot
        }
        self.MAXPOOLTEAMS = 5
        self.auctioned = False
    
    async def setmaxpool(self, num):
        self.MAXPOOLTEAMS = num
        await self.ctx.send(f"ok it's at {num} now")
    
    async def poolteams(self, ctx):
        author = ctx.author.name
        pooledteams = sum(self.teampool.values(), [])
        authorpooledteams = self.teampool[author]

        message = f'''here are the current teams in the pool:\n{", ".join(pooledteams)}
you personally have contributed:{", ".join(authorpooledteams)}\nyou can contribute {self.MAXPOOLTEAMS-len(authorpooledteams)} more teams'''

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
        if self.auctioned:
            return
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
                text += f"{player} - {self.money[player]}: {", ".join(list(map(lambda x: x[3:], teams)))}\n"
            await self.ctx.send(text)
            await self.line()
        
        await self.ctx.send("The auction has ended!")
        
        with open("bible.json", "r") as f:
            data = json.load(f)

        data[str(self.serverid)] = self.players
        print(data)

        with open("bible.json", "w") as f:
            json.dump(data, f)
        self.auctioned = True
    
    async def auction_team(self, team):
        self.bid_history = [{"buyer": "", "price": 0}]

        m = await self.ctx.send(f"{team}: current price: {self.bid_history[0]["price"]}; current buyer: {self.bid_history[0]["buyer"]}")
        self.countdown_message = await self.ctx.send(f"Time left to bid: {self.AUCTIONTIME}")

        self.current_countdown = asyncio.create_task(self.countdown())
        while not await self.current_countdown:
            await m.edit(content=f"{team}: current price: {self.bid_history[0]["price"]}; current buyer: {self.bid_history[0]["buyer"]}")
            self.current_countdown = asyncio.create_task(self.countdown())
        
        if buyer := self.bid_history[0]["buyer"]:
            self.money[buyer] -= self.bid_history[0]["price"]
            await self.ctx.send(f"sold! team {team} for {self.bid_history[0]["price"]} to {buyer}")
            self.players[buyer].append("frc"+team)

            if loser := self.bid_history[1]["buyer"]:
                if loser != buyer:
                    self.money[loser] -= math.floor(self.bid_history[1]["price"]/2)
                    await self.ctx.send(f'''{loser} it's called first robotics competition not second robotics competition
looks like you'll have to pay {math.floor(self.bid_history[1]["price"]/2)} scootbucks''')
        else:
            await self.ctx.send(f"oof no one wanted {team}")
        await self.line()

    async def countdown(self):
        seconds = self.AUCTIONTIME
        try:
            while seconds > 0:
                await asyncio.sleep(1)
                seconds -= 1
                await self.countdown_message.edit(content=f"Time left to bid: {seconds}")
            await self.countdown_message.edit(content="Time expired")
            return True
        except asyncio.CancelledError:
            return False
        finally:
            self.current_countdown = False
    
    async def bid(self, ctx, num):
        await ctx.message.delete()
        if self.money[ctx.author.name] >= num and (
            num > self.bid_history[0]["price"]
              or (
                self.bid_history[0]["price"] == 5
                and num >= self.bid_history[0]["price"]
                and not self.bid_history[0]["buyer"]
                )
            ):
            self.bid_history.insert(0, {"buyer": ctx.author.name, "price": num})
            if self.current_countdown:
                self.current_countdown.cancel()
    
    async def line(self):
        await self.ctx.send("---------------------------------------")
    
    async def get_score(self):
        scores = send.score(str(self.serverid))
        text = ""
        for player, teams in scores.items():
            text += f"{player}:\n"
            for team, score in teams.items():
                text += f"Team {team[3:]}: {score}\n"
            text += f"{player} total: {sum(teams.values())}\n"
            text += "----------\n"
        await self.ctx.send(text)
    
    async def reset(self):
        with open("bible.json", "r") as f:
            data = json.load(f)

        if str(self.serverid) in data.keys():
            del data[str(self.serverid)]
        
        with open("bible.json", "w") as f:
            json.dump(data, f)
        
        self.players = {
            member.name: []
            for member in self.ctx.guild.members if not member.bot
        }
        await self.ctx.send("reset done")
        self.auctioned = False
    
    async def help(self):
        message = '''use ?setup to setup the bot. if there was an existing auction result the bot will pull that
?maxpool [num]: set the max amount of teams each player can pool for the auction
?poolteams: get a list of all teams in the pool
?pool [team_num]: pool a team
?unpool [team_num]: unpool a team you have pooled
?auction: start the auction
?b [num] or ?bid [num]: place a bid
?score: see the scores
?reset: reset the auction results'''
        await self.ctx.send(message)