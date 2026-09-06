"""Thin data-access layer around mongoer.
 
All Mongo-specific query shapes live here, and only here. If the
collection name or document shape ever changes, this is the one file
that needs to change -- nothing else in the app imports mongoer.
"""
from backend import mongoer
 
 
class ServerRepository:
    COLLECTION = "servers"
 
    def get(self, server_id: str) -> dict | None:
        """Return the saved doc for a server, or None if nothing has
        been saved for it yet."""
        docs = mongoer.find(self.COLLECTION, {"server_id": server_id})
        return docs[0] if docs else None
 
    def save(self, server_id: str, players: dict) -> None:
        mongoer.insert(
            self.COLLECTION,
            {"server_id": server_id, "players": players},
        )
 
    def delete(self, server_id: str) -> None:
        mongoer.delete(self.COLLECTION, {"server_id": server_id})
 