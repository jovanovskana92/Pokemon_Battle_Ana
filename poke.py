import requests
from flask import Flask, request, jsonify, render_template
from flasgger import Swagger
from models import Pokemon

app = Flask(__name__)
swagger = Swagger(app)


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
            return Pokemon(data['name'], id, stats)
            # Use the Pokemon class from models.py
            # return {'name': data['name'], 'pokemon ID': id, 'stats': stats}
        except requests.exceptions.HTTPError as error_msg:
            if response.status_code == 404:
                raise ValueError("Pokemon not found")
            else:
                ValueError(error_msg)

    def simulate_battle(self):
        pokemon1_total_stat = sum(self.pokemon1.stats.values())
        pokemon2_total_stat = sum(self.pokemon2.stats.values())

        if pokemon1_total_stat > pokemon2_total_stat:
            return self.pokemon1.name
        elif pokemon2_total_stat > pokemon1_total_stat:
            return self.pokemon2.name
        else:
            return "It's a tie!"


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
        winner = battle.simulate_battle()

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
        response_data = {
            "pokemon1": pokemon1_dict,
            "pokemon2": pokemon2_dict,
            "winner": winner
        }
        return jsonify(response_data), 200
        # return render_template('battle_results.html', winner=winner, pokemon1=pokemon1_dict, pokemon2=pokemon2_dict)
        # We can render the template battle_results and comment response_data to have the results displayed beautifully

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/', methods=['GET'])  # Display HTML from to initiate battles
def home():
    return render_template('battle_form.html')


if __name__ == '__main__':
    app.run(debug=True, port=5001)