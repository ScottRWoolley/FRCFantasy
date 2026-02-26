import os
from dotenv import load_dotenv

load_dotenv()

TBA_KEY=os.getenv("TBA_KEY")
DISCORD_TOKEN=os.getenv("DISCORD_TOKEN")
MONGOCLIENT=os.getenv("MongoClient")
COMMAND_CHAR=os.getenv("COMMAND_CHAR")