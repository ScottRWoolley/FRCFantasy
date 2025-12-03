import discord
from discord.ext import commands
import random
import asyncio
from backend import send
import math
from pymongo import MongoClient
from backend import mongoer
import time
import os

PUNISHMENT = 4 # Divide losing bid by how much
CCHAR = os.getenv("COMMAND_CHAR") # ? or !

class Bot:
    def __init__(self, ctx):
        self.serverid = str(ctx.guild.id)
        self.ctx = ctx
        self.AUCTIONTIME = 10
        self.bidtimer = time.time()
        
    
    async def setup(self):
        await self.ctx.send(f"use {CCHAR}helpplease for a list of commands\nif you want to set up a webhook for match updates, use {CCHAR}webhook [url]")
        data = mongoer.find("bible", {"server_id": self.serverid})

        if len(data) > 0:
            self.players = data[0]["players"]
            self.auctioned = True
            self.teampool = {
                member.name: []
                for member in self.ctx.guild.members if not member.bot
            }
        else:
            # would probably be a lot better to make a player class but too late now
            self.players = {
                member.name: []
                for member in self.ctx.guild.members if not member.bot
            }
            self.teampool = {
                member.name: []
                for member in self.ctx.guild.members if not member.bot
            }
            self.auctioned = False
        print(self.teampool)
        self.MAXPOOLTEAMS = 5
    
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

        mongoer.insert(
            "bible",
            {
                "server_id": self.serverid,
                "players": self.players
            }
        )

        teams = set(sum(self.players.values(), []))

        mongo_all_teams = mongoer.find("all_teams")
        if not mongo_all_teams:
            mongoer.insert("all_teams", {"data": []})
            mongo_all_teams = mongoer.find("all_teams")
        team_data = mongo_all_teams[0]["data"]
        team_data = set(team_data)
        all_teams = team_data | teams
        mongoer.update_document("all_teams", query={"_id": mongo_all_teams[0]["_id"]}, new_data={"data": list(all_teams)})

        unadded_teams = list(teams.difference(team_data))
        score_update = dict().fromkeys(unadded_teams, 0)

        scores = mongoer.find("scores")
        if not scores:
            mongoer.insert("scores", score_update)
        else:
            mongoer.update_document("scores", query={"_id": scores[0]["_id"]}, new_data=score_update)

        self.auctioned = True
    
    async def auction_team(self, team):
        self.bid_history = [{"buyer": "", "price": 0}]

        m = await self.ctx.send(self.gen_auction_message(team, self.bid_history, self.AUCTIONTIME))

        self.current_countdown = asyncio.create_task(self.countdown(team, m))
        while not await self.current_countdown:
            self.current_countdown = asyncio.create_task(self.countdown(team, m))
        
        if buyer := self.bid_history[0]["buyer"]:
            self.money[buyer] -= self.bid_history[0]["price"]
            await self.ctx.send(f"sold! team {team} for {self.bid_history[0]["price"]} to {buyer}")
            self.players[buyer].append("frc"+team)

            if loser := next((b["buyer"] for b in self.bid_history if b["buyer"] != buyer), None):
                self.money[loser] -= math.floor(self.bid_history[1]["price"]/PUNISHMENT)
                await self.ctx.send(f'''{loser} it's called first robotics competition not second robotics competition
looks like you'll have to pay {math.floor(self.bid_history[1]["price"]/PUNISHMENT)} scootbucks''')
        else:
            await self.ctx.send(f"oof no one wanted {team}")
        await self.line()
    
    def gen_auction_message(self, team, bid_history, time):
        text = f"{team}: current price: {bid_history[0]["price"]}; current buyer: {bid_history[0]["buyer"]}\n"
        if time > 0:
            text += f"Time left to bid: {time}"
        else:
            text += f"Time expired"
        return text

    async def countdown(self, team, message):
        seconds = self.AUCTIONTIME
        try:
            while seconds > 0:
                await asyncio.sleep(1)
                seconds -= 1
                await message.edit(content=self.gen_auction_message(team, self.bid_history, seconds))
            await message.edit(content=self.gen_auction_message(team, self.bid_history, seconds))
            return True
        except asyncio.CancelledError:
            await message.edit(content=self.gen_auction_message(team, self.bid_history, seconds))
            return False
        finally:
            self.current_countdown = False
    
    async def bid(self, ctx, num):
        await ctx.message.delete()
        current_time = time.time()
        if current_time - self.bidtimer < 2:
            return
        if len(self.players[ctx.author.name]) >= self.MAXPOOLTEAMS:
            return
        if self.money[ctx.author.name] >= num and (num > self.bid_history[0]["price"]):
            self.bid_history.insert(0, {"buyer": ctx.author.name, "price": num})

            if self.current_countdown:
                self.current_countdown.cancel()

        self.bidtimer = time.time()
    
    async def line(self):
        await self.ctx.send("---------------------------------------")
    
    async def get_score(self):
        scores = send.score(self.serverid)
        text = ""
        for player, teams in scores.items():
            text += f"{player}:\n"
            for team, score in teams.items():
                text += f"Team {team[3:]}: {score}\n"
            text += f"{player} total: {round(sum(teams.values()), 2)}\n"
            text += "----------\n"
        await self.ctx.send(text)
    
    async def reset(self):
        
        mongoer.delete("bible", {"server_id": self.serverid})
        
        self.players = {
            member.name: []
            for member in self.ctx.guild.members if not member.bot
        }
        await self.ctx.send("reset done")
        self.auctioned = False
    
    async def help(self):
        message = f'''use {CCHAR}setup to setup the bot. if there was an existing auction result the bot will pull that
{CCHAR}maxpool [num]: set the max amount of teams each player can pool for the auction
{CCHAR}poolteams: get a list of all teams in the pool
{CCHAR}pool [team_num]: pool a team
{CCHAR}unpool [team_num]: unpool a team you have pooled
{CCHAR}auction: start the auction
{CCHAR}b [num] or ?bid [num]: place a bid
{CCHAR}score: see the scores
{CCHAR}reset: reset the auction results
{CCHAR}roster: see team roster
{CCHAR}webhook [url] use this to set up match updates'''

        await self.ctx.send(message)
    
    async def roster(self):
        text = "team rosters:\n"
        for player, teams in self.players.items():
            text += f"{player}: {", ".join(list(map(lambda x: x[3:], teams)))}\n"
        await self.ctx.send(text)
