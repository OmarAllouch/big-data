import time
from pymongo import MongoClient
from os import listdir
from json import load


def connect():
    c = MongoClient()
    db = c.pokedex_db
    return c, db


def close(c):
    c.close()


def print_pokemons(pokemons):
    total = 0
    for pokemon in pokemons:
        # Print in JSON format
        print(pokemon)
        print()
        total += 1
    print(f"\nTotal: {total}")


def object_to_array(obj):
    return [str(value) for values in obj.values() for value in values]


def check_ndex():
    ndexes = set()
    for filename in listdir("json"):
        with open(f"json/{filename}") as f:
            doc = load(f)
            # Check if `ndex` is in the document
            if "ndex" not in doc:
                continue
            ndex = doc["ndex"]
            if ndex in ndexes:
                print(f"Duplicate ndex: {ndex}")
            ndexes.add(ndex)

    print(f"Total unique ndexes: {len(ndexes)}")


c, db = connect()

# 1.1 --------------------
# >>> python3 load.py
# Les documents sont insérés dans la collection `pokedex` de la base de données `pokedex_db`.
# Le meilleur choix d'une clé primaire pour accéder à un document sera `ndex` qui est un identifiant unique pour chaque pokémon.
# J'ai fait un petit script pour m'assurer qu'il n'y a pas de doublons. (voir la fonction `check_ndex`)

# 1.2 --------------------
pokemons = db.pokedex.find({
    'type1': 'Fire',
    'weight-kg': {'$lt': 100}
})

print_pokemons(pokemons)


# 1.3 --------------------
pokemons = db.pokedex.update_many({'ndex': {'$exists': True}}, {'$set': {'type': 'pokemon'}})
print(f"Updated {pokemons.modified_count} documents")
locations = db.pokedex.update_many({'ndex': {'$exists': False}}, {'$set': {'type': 'location'}})
print(f"Updated {locations.modified_count} documents")
# Le critère de distinction entre un Pokémon et une localité est que les Pokémon ont un `ndex` et les localités n'en ont pas.


# 1.4 --------------------
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

print_pokemons(pokemons)

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


# 2.1 --------------------
pipeline_geographical_distribution = [
    {
        '$match': {
            'type': 'location',
            'region': {
                '$exists': True
            }
        }
    }, {
        '$project': {
            'region': 1,
            'encounters': {
                '$objectToArray': '$encounters'
            }
        }
    }, {
        '$unwind': {
            'path': '$encounters'
        }
    }, {
        '$project': {
            'region': 1,
            'encounter_list': '$encounters.v'
        }
    }, {
        '$unwind': {
            'path': '$encounter_list'
        }
    }, {
        '$lookup': {
            'from': 'pokedex',
            'let': {
                'region': '$region'
            },
            'pipeline': [
                {
                    '$match': {
                        '$expr': {
                            '$eq': [
                                '$region', '$$region'
                            ]
                        }
                    }
                }, {
                    '$group': {
                        '_id': '$region',
                        'total_locations': {
                            '$sum': 1
                        }
                    }
                }
            ],
            'as': 'region_info'
        }
    }, {
        '$addFields': {
            'total_locations_for_region': {
                '$arrayElemAt': [
                    '$region_info.total_locations', 0
                ]
            }
        }
    }, {
        '$group': {
            '_id': {
                'region': '$region',
                'pokemon': '$encounter_list'
            },
            'total_locations_for_region': {
                '$first': '$total_locations_for_region'
            },
            'count': {
                '$sum': 1
            }
        }
    }, {
        '$addFields': {
            'occupancy_ratio': {
                '$multiply': [
                    {
                        '$divide': [
                            '$count', '$total_locations_for_region'
                        ]
                    }, 100
                ]
            }
        }
    }, {
        '$project': {
            '_id': 0,
            'region': '$_id.region',
            'pokemon': '$_id.pokemon',
            'occupancy_ratio': 1
        }
    }
]
# La logique de la requête est la suivante:
# - On commence par filtrer les documents de type `location` qui ont un champ `region`.
# - On effectue des transformations sur le champ `encounters`, pour que chaque document soit une region et un pokémon.
# - On ajoute un champ `total_locations_for_region` qui contient le nombre total de localités pour la région.
# - On groupe les documents par région et par pokémon pour obtenir le nombre de localités où chaque pokémon apparaît.
# - On ajoute un champ `occupancy_ratio` qui contient le ratio d'occupation de chaque pokémon pour chaque région.

start_time = time.time()
geographical_distribution = list(db.pokedex.aggregate(pipeline_geographical_distribution))
end_time = time.time()
print('SQL execution time: ~200ms')
print('MongoDB execution time:', round((end_time - start_time) * 1000), 'ms')
# ~200ms vs ~5400ms
# Le temps d'exécution de la requête SQL est beaucoup plus rapide que celui de MongoDB,
# malgré le fait que MongoDB a très peu de documents à traiter.
# Je dirais que cela est dû au fait que la requête MongoDB reparcourt plusieurs fois la collection pour chaque étape.
# Ce n'est pas peut être pas la meilleure approche pour cette requête.
# Mais il me semble qu'écrire une requête NoSQL en adoptant une logique SQL n'est pas la meilleure approche.

# 2.2 --------------------
# On utilise 100 au lieu de 0 => même logique
pipeline_no_damage = [
    {
        '$match': {
            'type': 'pokemon',
            'efficacy': {
                '$exists': True,
                '$ne': None
            }
        }
    }, {
        '$addFields': {
            'zero_efficacy_types': {
                '$reduce': {
                    'input': {
                        '$objectToArray': '$efficacy'
                    },
                    'initialValue': [],
                    'in': {
                        '$cond': [
                            {
                                '$eq': [
                                    '$$this.v', 100
                                ]
                            }, {
                                '$concatArrays': [
                                    '$$value', [
                                        '$$this.k'
                                    ]
                                ]
                            }, '$$value'
                        ]
                    }
                }
            }
        }
    }, {
        '$lookup': {
            'from': 'pokedex',
            'let': {
                'types': '$zero_efficacy_types'
            },
            'pipeline': [
                {
                    '$match': {
                        'type': 'pokemon',
                        '$expr': {
                            '$in': [
                                '$type1', '$$types'
                            ]
                        }
                    }
                }, {
                    '$project': {
                        'name': 1
                    }
                }
            ],
            'as': 'immune_pokemons'
        }
    }, {
        '$project': {
            'name': 1,
            'immune_pokemons': '$immune_pokemons.name'
        }
    }
]
# La logique de la requête est la suivante:
# - On commence par filtrer les documents de type `pokemon` qui ont un champ `efficacy`.
# - On ajoute un champ `zero_efficacy_types` qui contient la liste des types pour lesquels le pokémon est immunisé.
# - On fait une jointure avec la collection `pokedex` pour obtenir les noms des pokémons qui sont immunisés.

start = time.time()
no_damage = list(db.pokemons.aggregate(pipeline_no_damage))
end = time.time()

print(f'2.2 - SQL execution time: ~307ms')
print(f'2.2 - MongoDB execution time: {int((end - start) * 1000)}ms')
# ~307ms vs ~2ms
# Cette fois le temps d'exécution de la requête SQL est plus long que celui de MongoDB.
# Cela est dû à :
# - Le nombre de documents est plus petit
# - La requête MongoDB est plus simple et plus directe (la structure des données elle-même est plus simple)

# 2.3 --------------------


def get_locations_by_region(docs, region):
    locations = []
    for doc in docs:
        if 'type' not in doc or doc['type'] != 'location':
            continue
        if 'region' not in doc or doc['region'] != region:
            continue
        locations.append(doc)
    return locations


def get_total_locations_per_region(docs):
    region_locations = {}
    for doc in docs:
        if 'type' not in doc or doc['type'] != 'location':
            continue
        if 'region' not in doc:
            continue
        region = doc['region']
        if region not in region_locations:
            region_locations[region] = 0
        region_locations[region] += 1
    return region_locations


def find_pokemon_distribution(docs):
    distribution = {}
    for doc in docs:
        if 'region' not in doc:
            continue
        region = doc['region']
        encounters = doc['encounters']
        pokemon_names = object_to_array(encounters)
        for pokemon_name in pokemon_names:
            if region not in distribution:
                distribution[region] = {}
            if pokemon_name not in distribution[region]:
                distribution[region][pokemon_name] = 0
            distribution[region][pokemon_name] += 1

    region_locations = get_total_locations_per_region(docs)

    for region in distribution:
        for pokemon_name in distribution[region]:
            distribution[region][pokemon_name] = round(
                distribution[region][pokemon_name] / region_locations[region], 2)

    return distribution


def find_type_efficacy_0(docs):
    immune_to = {}
    for doc in docs:
        if 'efficacy' not in doc:
            continue

        pokemon_name = doc['name']
        efficacy = doc['efficacy']

        if any(type_efficacy == 100 for type_efficacy in efficacy.values()):
            immune_to[pokemon_name] = [type_name for type_name,
                                       type_efficacy in efficacy.items() if type_efficacy == 100]

    # For each pokemon, we have a list of types that the pokemon cannot deal damage to.
    # Expand that list by adding all the pokemons that fall into any of the types in the list.
    immune_pokemons = {}
    for doc in docs:
        if 'efficacy' not in doc:
            continue

        pokemon_name = doc['name']
        type1 = doc['type1']

        # If type1 is in any of the immune_pokemons lists, add the pokemon to the list.
        for immune_pokemon_name in immune_to:
            if type1 in immune_to[immune_pokemon_name]:
                if immune_pokemon_name not in immune_pokemons:
                    immune_pokemons[immune_pokemon_name] = []
                immune_pokemons[immune_pokemon_name].append(pokemon_name)

    return immune_pokemons


start = time.time()
distribution = find_pokemon_distribution(list(db.pokedex.find()))
end = time.time()
print(f'Execution time: {round((end - start) * 1000)}ms')  # 14ms
for region in distribution:
    print(region)
    for pokemon_name, occupancy_ratio in distribution[region].items():
        print(f'\t{pokemon_name}: {occupancy_ratio * 100}%')

start = time.time()
immune_pokemons = find_type_efficacy_0(list(db.pokedex.find()))
end = time.time()
print(f'Execution time: {round((end - start) * 1000)}ms')  # 114ms
for pokemon_name in immune_pokemons:
    print(f'{pokemon_name} is immune to:')
    for type_name in immune_pokemons[pokemon_name]:
        print(f'\t{type_name}')

# La première fonction est plus rapide que la pipeline équivalente, mais la deuxième est plus lente.
# La logique de la requête 2.1 est simplifiée dans le code Python ce qui la rend plus rapide.
# La requête 2.2 est presque la même que la pipeline MongoDB,
# alors le temps d'exécution revient à l'optimisation de la requête par MongoDB.

# 2.4 --------------------
# Pour implémenter la recherche par mot-clé avec BigTable, on peut utiliser un index inversé.
# L'index inversé contient les mots-clés comme clés et les identifiants des documents comme valeurs.
# Pour chaque mot-clé, on peut stocker les identifiants des documents qui contiennent ce mot-clé.
# Lorsqu'on veut effectuer une recherche par mot-clé, on récupère les identifiants des documents qui contiennent le mot-clé,
# puis on récupère les documents correspondants.

close(c)

# 3.1 --------------------
# CQL :
# CREATE TABLE pokemontypes (
#     pokemon_id INT,
#     name TEXT,
#     type TEXT,
#     height DOUBLE,
#     weight DOUBLE,
#     PRIMARY KEY (pokemon_id),
# );
