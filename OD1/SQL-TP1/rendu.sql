-- 1.1
SELECT p.id as "Rang", psn.name as "Nom", p.height as "Taille", p.weight as "Poids"
FROM pokemon p
JOIN pokemon_species_names psn ON p.species_id = psn.pokemon_species_id
AND psn.local_language_id IN (SELECT local_language_id FROM language_names WHERE name = "Français");


-- 1.2
CREATE VIEW "pokemon_view"
AS
	SELECT p.id as "Rang", psn.name as "Nom", p.height as "Taille", p.weight as "Poids"
	FROM pokemon p
	JOIN pokemon_species_names psn ON p.species_id = psn.pokemon_species_id
		AND psn.local_language_id IN (SELECT local_language_id FROM language_names WHERE name = "Français");

CREATE VIEW pokemon_type_view
AS
	SELECT pt.pokemon_id AS "Rang", tn.name AS "Type"
	FROM pokemon_types pt
	JOIN type_names tn ON pt.type_id = tn.type_id
	JOIN language_names ln ON tn.local_language_id IN (SELECT local_language_id FROM language_names WHERE name = "Français");

	
-- 1.3
SELECT DISTINCT Nom
FROM pokemon_view p, pokemon_type_view pt
WHERE p.Rang = pt.Rang AND pt.Type = "Feu" AND p.Rang BETWEEN 1 AND 151;

SELECT DISTINCT Nom
FROM pokemon_view p, pokemon_type_view pt
WHERE p.Rang = pt.Rang AND pt.Type = "Feu" AND p.Rang BETWEEN 1 AND 151 AND p.Taille < 100;


-- 2.1
CREATE VIEW pokemon_fr
AS
	SELECT p.id, p.species_id, psn.name AS name
	FROM pokemon p
	JOIN pokemon_species_names psn ON p.species_id = psn.pokemon_species_id AND psn.local_language_id = 5; -- 5 = Francais

-- Dépendances fonctionnelles :
-- 		{id} -> {species_id, name}
-- 		{species_id} -> {name}
--
-- La vue "pokemon_fr" est :
-- En 1NF car tous les attributs sont atomiques.
-- En 2NF car elle est en 1NF, et "species_id" et "name" sont pleinement dépendents de "id".
-- En 3NF car elle est en 2NF, et ne contient pas de dépendances transitives.


-- 2.2
CREATE VIEW location_areas_fr
AS
	SELECT la.id, la.location_id,
		   CASE
			   WHEN l.name IS NOT NULL AND la.name IS NOT NULL THEN l.name || ' - ' || la.name
			   WHEN la.name IS NOT NULL THEN la.name
			   ELSE l.name
		   END AS name
	FROM location_areas la
	LEFT JOIN locations l ON la.location_id = l.id;

-- Dépendances fonctionnelles pour la vue "location_areas_fr":
--     {id} -> {location_id, name}
--     {location_id} -> {name}
-- 
-- La vue "location_areas_fr" est :
-- En 1NF car tous les attributs sont atomiques.
-- En 2NF car elle est en 1NF, et ne contient pas de dépendances partielles.
-- En 3NF car elle est en 2NF, et ne contient pas de dépendances transitives.


-- 3.1
SELECT pokemon.identifier AS Pokemon_Name, regions.identifier AS Region_Name,
    COUNT(DISTINCT encounters.location_area_id) * 100 / total_locations.Total_Region_Locations AS Occupancy_Ratio
FROM encounters
JOIN locations ON encounters.location_area_id = locations.id
JOIN regions ON regions.id = locations.region_id
JOIN pokemon ON pokemon.id = encounters.pokemon_id
JOIN 
    (
        SELECT region_id, COUNT(*) AS Total_Region_Locations
        FROM locations
        WHERE region_id IS NOT NULL
        GROUP BY region_id
    ) AS total_locations ON regions.id = total_locations.region_id
GROUP BY pokemon.identifier, regions.identifier, total_locations.Total_Region_Locations;
-- 201ms


-- 3.2
SELECT pokemon.identifier AS Pokemon_Name, regions.identifier AS Region_Name,
    COUNT(DISTINCT encounters.location_area_id) * 100 / total_locations.Total_Region_Locations AS Etalement
FROM encounters
CROSS JOIN 
    (
        SELECT region_id, COUNT(*) AS Total_Region_Locations
        FROM locations
        WHERE region_id IS NOT NULL
        GROUP BY region_id
    ) AS total_locations
CROSS JOIN pokemon
CROSS JOIN regions
CROSS JOIN locations
WHERE encounters.location_area_id = locations.id
  AND locations.region_id = regions.id
  AND pokemon.id = encounters.pokemon_id
  AND regions.id = total_locations.region_id
GROUP BY pokemon.identifier, regions.identifier, total_locations.Total_Region_Locations;
-- 271ms
-- Après plusieurs essaies, le temps d'éxecution dépend de l'ordre des CROSS JOIN.
-- Dans ce cas, le temps est un peu plus grand, mais il peut être pire.


-- 3.3
-- EXPLAIN QUERY PLAN
SELECT moves.identifier, pokemon.identifier
FROM moves
JOIN type_efficacy ON type_efficacy.damage_type_id = moves.type_id
JOIN pokemon_types ON pokemon_types.type_id = type_efficacy.target_type_id
JOIN pokemon ON pokemon.id = pokemon_types.pokemon_id AND pokemon.id BETWEEN 1 AND 151
GROUP BY moves.identifier, pokemon.identifier;
-- ~370ms


-- 3.4
SELECT moves.identifier, pokemon.identifier
FROM moves
CROSS JOIN type_efficacy
CROSS JOIN pokemon_types
CROSS JOIN pokemon
WHERE type_efficacy.damage_type_id = moves.type_id
	AND pokemon.id = pokemon_types.pokemon_id AND pokemon.id BETWEEN 1 AND 151
	AND pokemon_types.type_id = type_efficacy.target_type_id
GROUP BY moves.identifier, pokemon.identifier;
-- ~1100ms

SELECT moves.identifier, pokemon.identifier
FROM moves
CROSS JOIN pokemon_types
CROSS JOIN pokemon
CROSS JOIN type_efficacy
WHERE type_efficacy.damage_type_id = moves.type_id
	AND pokemon.id = pokemon_types.pokemon_id AND pokemon.id BETWEEN 1 AND 151
	AND pokemon_types.type_id = type_efficacy.target_type_id
GROUP BY moves.identifier, pokemon.identifier;
-- ~690ms

SELECT moves.identifier, pokemon.identifier
FROM moves
CROSS JOIN pokemon_types
CROSS JOIN pokemon
CROSS JOIN type_efficacy
WHERE type_efficacy.damage_type_id = moves.type_id
	AND pokemon.id = pokemon_types.pokemon_id AND pokemon.id BETWEEN 1 AND 151
	AND pokemon_types.type_id = type_efficacy.target_type_id
GROUP BY moves.identifier, pokemon.identifier;
-- ~690ms

SELECT moves.identifier, pokemon.identifier
FROM moves
CROSS JOIN pokemon_types
CROSS JOIN pokemon
CROSS JOIN type_efficacy
WHERE type_efficacy.damage_type_id = moves.type_id
	AND pokemon.id = pokemon_types.pokemon_id
	AND pokemon.id BETWEEN 1 AND 151
	AND pokemon_types.type_id = type_efficacy.target_type_id
GROUP BY moves.identifier, pokemon.identifier;
-- ~520ms

-- Si on execute les CROSS JOIN qui réduisent le plus la quantité de donnée (comme pokemon_types),
-- cela va accélerer l'execution de la requête.
-- Et alors, si on considère ce critère, on peut les classer sans éxecution.


-- 3.5
ANALYZE;
-- La table `sqlite_stat1` dans SQLite contient des statistiques sur la distribution des clés dans les index.
-- SQLite pourrait utiliser les statistiques contenues dans la table `sqlite_stat1` pour optimiser l'ordre des JOIN.
-- Prenons l'exemple de l'étalement des pokémons :
-- Par exemple, si SQLite estime que la table locations est plus sélective que la table encounters,
-- il pourrait choisir de la joindre en premier pour réduire la taille de l'ensemble de résultats intermédiaire
-- dès le début de l'exécution de la requête.


-- 4.1
SELECT Nom
FROM pokemon_view AS P,
     pokemon_type_view AS PT
WHERE P.Rang = PT.Rang AND
      Type = 'Feu';
-- Le nombre de rows a changé, il y a plus qui sont retournés cette fois.
-- Puisque les tables n'ont pas de clés primaires ou étrangères, les lignes ne sont pas uniques.
-- Alors, les requêtes peuvent retourner plus de lignes que prévu.
-- C'est pour cela que le nombre de lignes retournées a changé.


-- 4.2
SELECT pokemon.identifier AS Pokemon_Name, regions.identifier AS Region_Name,
    COUNT(DISTINCT encounters.location_area_id) * 100 / total_locations.Total_Region_Locations AS Occupancy_Ratio
FROM encounters
JOIN locations ON encounters.location_area_id = locations.id
JOIN regions ON regions.id = locations.region_id
JOIN pokemon ON pokemon.id = encounters.pokemon_id
JOIN 
    (
        SELECT region_id, COUNT(*) AS Total_Region_Locations
        FROM locations
        WHERE region_id IS NOT NULL
        GROUP BY region_id
    ) AS total_locations ON regions.id = total_locations.region_id
GROUP BY pokemon.identifier, regions.identifier, total_locations.Total_Region_Locations;
-- Même temps d'éxecution qu'avant. (200ms)

SELECT pokemon.identifier AS Pokemon_Name, regions.identifier AS Region_Name,
    COUNT(DISTINCT encounters.location_area_id) * 100 / total_locations.Total_Region_Locations AS Etalement
FROM encounters
CROSS JOIN 
    (
        SELECT region_id, COUNT(*) AS Total_Region_Locations
        FROM locations
        WHERE region_id IS NOT NULL
        GROUP BY region_id
    ) AS total_locations
CROSS JOIN pokemon
CROSS JOIN regions
CROSS JOIN locations
WHERE encounters.location_area_id = locations.id
  AND locations.region_id = regions.id
  AND pokemon.id = encounters.pokemon_id
  AND regions.id = total_locations.region_id
GROUP BY pokemon.identifier, regions.identifier, total_locations.Total_Region_Locations;
-- Celle ci est devenu plus lente. (793ms)

-- Ce que je pense :
-- L'absence de clés primaires ou étrangères peut résulter en des produits cartésiens pour les CROSS JOIN.
-- Cela peut augmenter la taille de l'ensemble de résultats intermédiaire et ralentir l'exécution de la requête.
-- Alors que les JOINs normaux ne produisent pas de produits cartésiens, même si les tables n'ont pas de clés primaires ou étrangères.

-- 4.3
SELECT *
FROM pokemon_species p1
WHERE EXISTS (
    SELECT 1
    FROM pokemon_species p2
    WHERE p1.id = p2.evolves_from_species_id
        AND substr(p1.identifier, 1, 3) = substr(p2.identifier, 1, 3)
)
ORDER BY p1.identifier;
-- 107ms

-- 4.4
CREATE INDEX ix_pokemon_species_names_name ON pokemon_species_names(name);

SELECT *
FROM pokemon_species p1
WHERE EXISTS (
    SELECT 1
    FROM pokemon_species p2
    WHERE p1.id = p2.evolves_from_species_id
        AND substr(p1.identifier, 1, 3) = substr(p2.identifier, 1, 3)
)
ORDER BY p1.identifier;
-- 105ms

-- C'est normal dans mon cas, la requête que j'éxecute n'utilise pas l'attribut "name" ni "pokemon_species_names".
-- Alors un ajout d'un tel index n'aura aucun effet.
-- Par contre, si on ajoute un index sur "identifier" de "pokemon_species", le temps d'éxecution doit être plus petit.
