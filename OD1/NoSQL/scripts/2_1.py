import utils
import time


c, db = utils.connect()

# 2.1 - SQL execution time: 201ms
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

start_time = time.time()
geographical_distribution = list(db.pokedex.aggregate(pipeline_geographical_distribution))
end_time = time.time()
print('SQL execution time: ~200ms')
print('MongoDB execution time:', round((end_time - start_time) * 1000), 'ms')

utils.close(c)
