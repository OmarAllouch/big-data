import utils
import time


c, db = utils.connect()

# 2.2
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

start = time.time()
no_damage = list(db.pokemons.aggregate(pipeline_no_damage))
end = time.time()

print(f'2.2 - SQL execution time: ~307ms')
print(f'2.2 - MongoDB execution time: {int((end - start) * 1000)}ms')
utils.close(c)
