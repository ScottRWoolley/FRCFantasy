from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
import os

app = FastAPI()
print(os.environ['MongoClient'])
client = MongoClient(os.environ['MongoClient'], 1678)
db = client.Testing
teams_to_update = []
class Update(BaseModel):
    message_type: str | None = None
    message_data: dict | None = None

@app.post("/tbawebhook")
async def get_updates(request: Update):
    global teams_to_update
    update = request.model_dump()
    try:
        alliances = update["message_data"]["match"]["alliances"]
        teams = []
        teams.extend(alliances[color]["teams"] for color in ["red", "blue"])
        teams = sum(teams, [])
    except:
        print(update)
        print("error")
    teams_to_update.extend(teams)
    db["testing"].insert_one(update)

@app.get("/get_updates")
async def test_get():
    global teams_to_update
    t = teams_to_update
    teams_to_update = []
    return t