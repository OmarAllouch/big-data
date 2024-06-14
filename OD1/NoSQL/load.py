from os import listdir
from json import load
from pymongo import MongoClient

c = MongoClient()
db = c.pokedex_db

db.pokedex.delete_many({})

for filename in listdir("json"):
    with open(f"json/{filename}") as f:
        print(f"Processing {filename}")

        doc = load(f)
        db.pokedex.insert_one(doc)

print(f"Inserted {db.pokedex.count_documents({})} documents")
