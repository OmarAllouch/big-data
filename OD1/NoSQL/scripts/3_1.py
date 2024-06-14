import sqlite3
from cassandra.cluster import Cluster


def copy_data_to_cassandra(sqlite_db, cassandra_keyspace, cassandra_table):
    # Connect to the SQLite database
    sqlite_conn = sqlite3.connect(sqlite_db)
    sqlite_cursor = sqlite_conn.cursor()

    # Query to fetch relevant data from SQLite
    sqlite_query = """
    SELECT id, name, type1, type2
    FROM pokemon;
    """

    # Execute the query
    sqlite_cursor.execute(sqlite_query)
    pokemons = sqlite_cursor.fetchall()

    # Connect to Cassandra
    cluster = Cluster(['127.0.0.1'])  # Update with your Cassandra cluster address
    session = cluster.connect(cassandra_keyspace)

    # Prepare the insert statement for Cassandra
    insert_query = session.prepare(f"""
    INSERT INTO {cassandra_table} (pokemon_id, name, type1, type2)
    VALUES (?, ?, ?, ?);
    """)

    # Insert each Pokémon into the Cassandra table
    for pokemon in pokemons:
        pokemon_id, name, type1, type2 = pokemon
        session.execute(insert_query, (pokemon_id, name, type1, type2))

    # Close the connections
    sqlite_conn.close()
    cluster.shutdown()


# Usage
copy_data_to_cassandra('pokedex.sqlite', 'mykeyspace', 'pokemontypes')
