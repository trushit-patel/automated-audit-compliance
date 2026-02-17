import json
from pymongo import MongoClient

# 1. Connect to Atlas
client = MongoClient("mongodb+srv://pateltrushit1710:ES2zTQ2wbxsAFoO4@maincluster.7rpl7ai.mongodb.net/")
db = client["audit_db"]
collection = db["transactions"]

# 2. Load JSON file (array of docs)
with open("transaction.json", "r", encoding="utf-8") as f:
    data = json.load(f)  # this will be a list of dicts

# 3. Bulk insert
result = collection.insert_many(data)
print(f"Inserted {len(result.inserted_ids)} documents")
