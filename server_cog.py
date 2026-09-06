"""A Cog is just a class that groups related commands together and
gets loaded into the bot as a unit. The pattern for every cog you add
later is the same four pieces:
 
  1. __init__(self, bot) stores whatever shared objects it needs
     (here, the StateManager -- see main.py for how it gets passed in)
  2. a small helper (_state below) that turns "this ctx" into "the
     right ServerState for this guild"
  3. @commands.command() methods that call one thing on the state and
     ctx.send() the result -- no game/business logic lives in the cog
  4. an async setup(bot) function at the bottom, which is what
     bot.load_extension() actually calls
 
This cog only has the basics: initialize a server's state and manage
the player list. No auction logic at all.
"""
import discord
from discord.ext import commands
 
 
def member_names(guild: discord.Guild) -> list[str]:
    return [m.name for m in guild.members if not m.bot]
 
 
class ServerCog(commands.Cog):
    def __init__(self, bot: commands.Bot, state_manager):
        self.bot = bot
        self.state_manager = state_manager
 
    def _state(self, ctx: commands.Context):
        return self.state_manager.get_or_create(str(ctx.guild.id), member_names(ctx.guild))
 
    @commands.command()
    @commands.guild_only()
    async def setup(self, ctx: commands.Context):
        """Explicitly (re)load this server's state -- useful if you
        want setup to be a visible, deliberate step rather than
        purely automatic on first command."""
        state = self._state(ctx)
        await ctx.send(f"server ready, tracking {len(state.players)} player(s)")
 
    @commands.command()
    @commands.guild_only()
    async def addplayer(self, ctx: commands.Context, name: str):
        state = self._state(ctx)
        await ctx.send(state.add_player(name))
        self.state_manager.save(str(ctx.guild.id))
 
    @commands.command()
    @commands.guild_only()
    async def removeplayer(self, ctx: commands.Context, name: str):
        state = self._state(ctx)
        await ctx.send(state.remove_player(name))
        self.state_manager.save(str(ctx.guild.id))
 
    @commands.command()
    @commands.guild_only()
    async def players(self, ctx: commands.Context):
        state = self._state(ctx)
        await ctx.send(state.list_players())
 
    @commands.command()
    @commands.guild_only()
    async def setchannel(self, ctx: commands.Context):
        """Point this server's API-driven notifications at whatever
        channel this command is run in."""
        state = self._state(ctx)
        state.notify_channel_id = ctx.channel.id
        await ctx.send(f"ok, I'll post API updates in {ctx.channel.mention}")
        # NOTE: notify_channel_id isn't persisted to the DB by
        # StateManager.save() below -- it only saves `players`. If you
        # want this to survive a restart, extend ServerRepository /
        # StateManager to save and reload it too.
 
    @commands.command()
    @commands.guild_only()
    async def reset(self, ctx: commands.Context):
        self.state_manager.reset(str(ctx.guild.id), member_names(ctx.guild))
        await ctx.send("reset done")
 
 
async def setup(bot: commands.Bot):
    # bot.state_manager is set once in main.py before cogs are loaded,
    # so every cog can pull the same shared instance off the bot.
    await bot.add_cog(ServerCog(bot, bot.state_manager))
 