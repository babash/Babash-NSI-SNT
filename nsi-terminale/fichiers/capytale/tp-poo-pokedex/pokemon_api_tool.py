import requests

def get_pokemon_stats(pokemon_name, max_attemps=5):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}"
    response = requests.get(url)
    attemps = 1
    while response.status_code != 200 and attemps < max_attemps:
        response = requests.get(url)
        attemps += 1
    if response.status_code == 200 :
        data = response.json()
        return data
    if response.status_code != 200:
        print(f"Error retrieving data for {pokemon_name}: {response.status_code}")
        return None

def get_all_pokemon_names():
    url = "https://pokeapi.co/api/v2/pokemon?limit=100000"  # Adjust limit as needed
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        pokemon_list = data["results"]
        pokemon_names = [pokemon["name"] for pokemon in pokemon_list]
        return pokemon_names
    else:
        print(f"Error retrieving names: {response.status_code}")
        return None

def get_all_pokemon_data():
    pokemon_data = {}
    pokemon_names = get_all_pokemon_names()
    for pokemon_name in pokemon_names:
        current_pokemon_data = get_pokemon_stats(pokemon_name)
        if current_pokemon_data:
            pokemon_data[pokemon_name] = current_pokemon_data
    return pokemon_names, pokemon_data


def Pokemon_from_data(pokemon_data):
    stats = {}
    for stat in pokemon_data['stats']:
        stats[stat['stat']['name']] = stat['base_stat']
    return Pokemon(pokemon_data['name'],
                    pokemon_data['pid'],
                    pokemon_data['height'],
                    pokemon_data['weight'],
                    stats,
                    pokemon_data['sprites']['front_default'],
                    pokemon_data['cries']['latest'])

def generate_pokemon_json():
    import json
    with open('pokemon_data.json', 'w') as json_file:
        json.dump(pokemon_data, json_file)
    with open('pokemon_names.json', 'w') as json_file:
        json.dump(pokemon_names, json_file)
    pokemon_names, pokemon_data = get_all_pokemon_data()

print(f"Retrieved data for {len(pokemon_data)}/{len(pokemon_names)} Pokémon.")
