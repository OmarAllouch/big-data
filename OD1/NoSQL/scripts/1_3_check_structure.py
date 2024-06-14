import utils


c, db = utils.connect()

pokemons = db.pokedex.find({
    'type': 'pokemon',
    '$or': [
        {'name': {'$exists': False}},
        {'forme': {'$exists': False}},
        {'type1': {'$exists': False}},
        {'type2': {'$exists': False}},
        {'generation': {'$exists': False}},
    ]
})

utils.print_pokemons(pokemons)

# Check if the weight in lbs is consistent with the weight in kg
pokemons = db.pokedex.find({
    'type': 'pokemon',
    'weight-kg': {'$exists': True},
    'weight-lbs': {'$exists': True}
})
for pokemon in pokemons:
    weight_kg = pokemon['weight-kg']
    weight_lbs = pokemon['weight-lbs']
    if round(weight_kg * 2.20462, 1) != weight_lbs:
        print(f"{weight_lbs}, {round(weight_kg * 2.20462, 1)}")
        print(
            f"Poids incohérent pour {pokemon['name']}: {weight_kg} kg =/= {weight_lbs} lbs")

utils.close(c)
