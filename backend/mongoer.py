from pymongo import MongoClient
import os

client = MongoClient(os.environ['MongoClient'], 1678)
db = client.Fantasy
bible = db["bible"]

def find(collection, query={}):
    return list(db[collection].find(query))

def insert(collection, data):
    try:
        if isinstance(data, list) and data:
            db[collection].insert_many(data)
        elif data and isinstance(data, dict):
            db[collection].insert_one(data)
    except Exception as err:
        print(f"Unable to insert some documents into collection {collection}: {err}")

def update_document(collection: str, new_data: dict, query: dict, many: bool = False, upsert: bool = False):
        """Updates one document that matches 'query' with 'new_data', uses upsert"""
        if not many:
            return db[collection].update_one(query, {"$set": new_data}, upsert)
        else:
            return db[collection].update_many(query, {"$set": new_data}, upsert)

def delete(collection, query):
    db[collection].delete_many(query)