from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
import os
from backend import scoring, send
import requests
import json

app = FastAPI()
client = MongoClient(os.environ['MongoClient'], 1678)
db = client.Fantasy

class Update(BaseModel):
    message_type: str | None = None
    message_data: dict | None = None

@app.post("/tbawebhook")
async def get_updates(request: Update):
    update = request.model_dump()
    alliances = update["message_data"]["match"]["alliances"]
    teams = []
    teams.extend(alliances[color]["team_keys"] for color in ["red", "blue"])
    teams = sum(teams, [])
    send.send_score_updates(teams, update["message_data"]["match"])