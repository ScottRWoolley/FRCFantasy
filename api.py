"""The incoming API. This is intentionally NOT a cog -- it's not
reacting to Discord commands, it's reacting to HTTP requests, so it
gets its own small module.
 
It only needs two things it doesn't own itself: the running bot (to
actually send messages) and the StateManager (to figure out who cares
and what to say). Both get handed in via create_app().
"""
from aiohttp import web
 
 
async def handle_post(request: web.Request) -> web.Response:
    bot = request.app["bot"]
    state_manager = request.app["state_manager"]
 
    try:
        payload = await request.json()
    except ValueError:
        return web.json_response({"error": "invalid json"}, status=400)
 
    for guild in bot.guilds:
        server_id = str(guild.id)
        state = state_manager.get(server_id)  # cached lookup only -- a
        if state is None:                      # server that's never run
            continue                           # a command has nothing to notify
        if state.notify_channel_id is None:
            continue
 
        message = state.build_response(payload)
        if message is None:
            continue
 
        channel = bot.get_channel(state.notify_channel_id)
        if channel is not None:
            await channel.send(message)
 
    return web.json_response({"status": "ok"})
 
 
def create_app(bot, state_manager) -> web.Application:
    app = web.Application()
    app["bot"] = bot
    app["state_manager"] = state_manager
    app.router.add_post("/events", handle_post)
    return app