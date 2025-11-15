from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
import os
from backend import scoring, send
import requests
import json

app = FastAPI()
client = MongoClient(os.environ['MongoClient'], 1678)
db = client.Testing

class Update(BaseModel):
    message_type: str | None = None
    message_data: dict | None = None

@app.post("/tbawebhook")
async def get_updates(request: Update):
    update = request.model_dump()
    try:
        alliances = update["message_data"]["match"]["alliances"]
        teams = []
        teams.extend(alliances[color]["teams"] for color in ["red", "blue"])
        teams = sum(teams, [])
    except:
        print(update)
        print("error")
        return
    
    send.send_score_updates(teams, update["message_data"]["match"])