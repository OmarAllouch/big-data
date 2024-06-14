import utils
import time


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


# The result is a list of documents, each containing the name of the region,
# a list of pokemons, for each pokemon has the name and the occupancy ratio.
def find_pokemon_distribution(docs):
    distribution = {}
    for doc in docs:
        if 'region' not in doc:
            continue
        region = doc['region']
        encounters = doc['encounters']
        pokemon_names = utils.object_to_array(encounters)
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


c, db = utils.connect()

start = time.time()
distribution = find_pokemon_distribution(list(db.pokedex.find()))
end = time.time()
print(f'Execution time: {round((end - start) * 1000)}ms')
# for region in distribution:
#     print(region)
#     for pokemon_name, occupancy_ratio in distribution[region].items():
#         print(f'\t{pokemon_name}: {occupancy_ratio * 100}%')

start = time.time()
immune_pokemons = find_type_efficacy_0(list(db.pokedex.find()))
end = time.time()
print(f'Execution time: {round((end - start) * 1000)}ms')
# for pokemon_name in immune_pokemons:
#     print(f'{pokemon_name} is immune to:')
#     for type_name in immune_pokemons[pokemon_name]:
#         print(f'\t{type_name}')

utils.close(c)
