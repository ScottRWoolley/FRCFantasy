"""Plain data + logic for one server. No discord imports here on
purpose -- this class doesn't know it's being driven by a Discord
command or an incoming webhook. That's what keeps it easy to test and
reuse from either place.
"""
from dataclasses import dataclass, field
 
 
@dataclass
class ServerState:
    server_id: str
    players: dict = field(default_factory=dict)       # player_name -> arbitrary data
    notify_channel_id: int | None = None               # where API-driven messages go
 
    @classmethod
    def new(cls, server_id: str, member_names: list[str]) -> "ServerState":
        return cls(server_id=server_id, players={m: [] for m in member_names})
 
    @classmethod
    def from_saved(cls, server_id: str, member_names: list[str], saved_players: dict) -> "ServerState":
        state = cls.new(server_id, member_names)
        state.players.update(saved_players)
        return state
 
    # ---- player management ----
    def add_player(self, name: str) -> str:
        if name in self.players:
            return f"{name} is already tracked"
        self.players[name] = []
        return f"added {name}"
 
    def remove_player(self, name: str) -> str:
        if name not in self.players:
            return f"{name} isn't tracked"
        del self.players[name]
        return f"removed {name}"
 
    def list_players(self) -> str:
        if not self.players:
            return "no players yet"
        return "\n".join(self.players.keys())
 
    # ---- API integration ----
    def build_response(self, payload: dict) -> str | None:
        """Look at an incoming API payload and decide whether/how this
        server cares. Return None to mean "nothing to say" -- the
        caller will skip messaging this server entirely.
 
        This is a placeholder for whatever your actual matching logic
        is (e.g. "does this update mention a team one of our players
        owns"). Replace the body, keep the signature.
        """
        subject = payload.get("subject")
        if subject is None:
            return None
 
        owners = [name for name, items in self.players.items() if subject in items]
        if not owners:
            return None
 
        return f"Update on {subject}: {payload.get('message', '')} (relevant to {', '.join(owners)})"