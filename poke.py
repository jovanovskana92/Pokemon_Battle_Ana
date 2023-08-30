import requests
from flask import Flask, request, jsonify, render_template
from flasgger import Swagger
from models import Pokemon
from pydantic import ValidationError
import random

app = Flask(__name__)
swagger = Swagger(app)


def fetch_moves_changes():
    url1 = "https://pokeapi.co/api/v2/pokemon/pikachu"
    response = requests.get(url1)
    data = response.json()

    urls = [stat['stat']['url'] for stat in data["stats"]]
    urls_d_a = [urls[2], urls[1]]  # Using Defense and Attack move URLs

    changes = {}
    for u in urls_d_a:
        responseMove = requests.get(u)
        response_move = responseMove.json()

        for move in response_move['affecting_moves']['increase']:
            move_name = move['move']['name']
            change_value = move['change']
            changes[move_name] = change_value
        for move in response_move['affecting_moves']['decrease']:
            move_name = move['move']['name']
            change_value = move['change']
            changes[move_name] = change_value

    return changes


class PokemonBattle:
    def __init__(self, pokemon1_name, pokemon2_name):
        self.pokemon1 = self.get_pokemon_data(pokemon1_name)
        self.pokemon2 = self.get_pokemon_data(pokemon2_name)

    def get_pokemon_data(self, name):
        try:
            response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name.lower()}")
            response.raise_for_status()
            data = response.json()
            id = data['id']
            stats = {stat['stat']['name']: stat['base_stat'] for stat in data['stats']}
            return Pokemon(name=data['name'], id=id, stats=stats)
            # Use the Pokemon class from models.py
            # return {'name': data['name'], 'pokemon ID': id, 'stats': stats}
        except requests.exceptions.HTTPError as error_msg:
            if response.status_code == 404:
                raise ValueError("Pokemon not found")
            else:
                ValueError(error_msg)
        except ValidationError:
            raise ValueError("Invalid Pokemon data")
        except requests.exceptions.RequestException:
            raise ValueError("Error fetching Pokemon data from PokeAPI")


    def simulate_battle(self, changes, battle_info):
        hp_pokemon1 = self.pokemon1.stats.get("hp")
        hp_pokemon2 = self.pokemon2.stats.get("hp")

        while hp_pokemon1 > 0 and hp_pokemon2 > 0:
            random_move_pokemon1 = random.choice(list(changes.keys()))
            random_move_pokemon2 = random.choice(list(changes.keys()))

            move_value_pokemon1 = changes[random_move_pokemon1]
            move_value_pokemon2 = changes[random_move_pokemon2]

            hp_pokemon1 = max(0, hp_pokemon1 - move_value_pokemon2)
            hp_pokemon2 = max(0, hp_pokemon2 - move_value_pokemon1)

            battle_info.append({
                f'{self.pokemon1.name}_move': {
                    'move_name': random_move_pokemon1,
                    'hp_after_move': hp_pokemon1
                },
                f'{self.pokemon2.name}_move': {
                    'move_name': random_move_pokemon2,
                    'hp_after_move': hp_pokemon2
                }
            })

        if hp_pokemon1 <= 0:
            winner_name = self.pokemon2.name
            remaining_hp = hp_pokemon2
        else:
            winner_name = self.pokemon1.name
            remaining_hp = hp_pokemon1
        return f"{winner_name} is winner with {remaining_hp} remaining HP."


@app.route('/battle', methods=['POST'])
def start_battle():
    """
    Start a battle between two Pokemons
    ---
    parameters:
      - name: pokemon1
        in: formData
        type: string
        required: true
        description: Name of the first Pokemon
      - name: pokemon2
        in: formData
        type: string
        required: true
        description: Name of the second Pokemon
    responses:
      200:
        description: Battle result
      500:
        description: Internal server error
    """
    try:
        data = request.form
        pokemon1_name = data['pokemon1']
        pokemon2_name = data['pokemon2']

        battle = PokemonBattle(pokemon1_name, pokemon2_name)
        changes = fetch_moves_changes()
        battle_info = []
        winner = battle.simulate_battle(changes=changes, battle_info=battle_info)

        # Convert Pokemon objects to dictionaries
        pokemon1_dict = {
            'name': battle.pokemon1.name,
            'id': battle.pokemon1.id,
            'stats': battle.pokemon1.stats
        }
        pokemon2_dict = {
            'name': battle.pokemon2.name,
            'id': battle.pokemon2.id,
            'stats': battle.pokemon2.stats
        }
        # response_data = {
        #     "pokemon1": pokemon1_dict,
        #     "pokemon2": pokemon2_dict,
        #     "winner": winner
        # }
        # return jsonify(battle_info, response_data), 200
        return render_template('battle_results.html', winner=winner, battle_info=battle_info, pokemon1=pokemon1_dict,
                               pokemon2=pokemon2_dict)
    except (ValueError, Exception) as e:
        return jsonify({"error": str(e)}), 500


@app.route('/', methods=['GET'])  # Display HTML from to initiate battles
def home():
    return render_template('battle_form.html')


if __name__ == '__main__':
    app.run(debug=True, port=5001)