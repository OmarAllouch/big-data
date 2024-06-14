import utils


c, db = utils.connect()

pokemons = db.pokedex.find({
    'type1': 'Fire',
    'weight-kg': {'$lt': 100}
})

utils.print_pokemons(pokemons)

utils.close(c)
