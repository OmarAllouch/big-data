import utils


c, db = utils.connect()

pokemons = db.pokedex.update_many({'ndex': {'$exists': True}}, {'$set': {'type': 'pokemon'}})
print(f"Updated {pokemons.modified_count} documents")
locations = db.pokedex.update_many({'ndex': {'$exists': False}}, {'$set': {'type': 'location'}})
print(f"Updated {locations.modified_count} documents")

utils.close(c)
