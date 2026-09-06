"""Owns one ServerState per guild, in memory, loaded lazily from the
repository the first time a guild needs it.
 
Every cog shares this same manager instance. That's the whole trick
for keeping things modular: cogs don't talk to Mongo, and they don't
hold state themselves -- they just ask the manager for "the state for
this guild" and call methods on what comes back.
"""
from state import ServerState
from repository import ServerRepository
 
 
class StateManager:
    def __init__(self, repo: ServerRepository):
        self.repo = repo
        self._states: dict[str, ServerState] = {}
 
    def get(self, server_id: str) -> ServerState | None:
        """Cached lookup only -- no DB hit, no creation. Use this when
        you want to check "has this guild been set up yet" without a
        side effect."""
        return self._states.get(server_id)
 
    def get_or_create(self, server_id: str, member_names: list[str]) -> ServerState:
        if server_id in self._states:
            return self._states[server_id]
 
        saved = self.repo.get(server_id)
        state = (
            ServerState.from_saved(server_id, member_names, saved["players"])
            if saved
            else ServerState.new(server_id, member_names)
        )
        self._states[server_id] = state
        return state
 
    def save(self, server_id: str) -> None:
        state = self._states[server_id]
        self.repo.save(server_id, state.players)
 
    def reset(self, server_id: str, member_names: list[str]) -> ServerState:
        self.repo.delete(server_id)
        state = ServerState.new(server_id, member_names)
        self._states[server_id] = state
        return state
 
    def warm_cache(self, guild_members: dict[str, list[str]]) -> None:
        """Optional: call from on_ready to eagerly load every guild's
        state at startup instead of waiting for the first command per
        guild."""
        for server_id, members in guild_members.items():
            self.get_or_create(server_id, members)
 