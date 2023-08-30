import pytest
from poke import app, PokemonBattle
from unittest.mock import Mock, patch


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Battle' in response.data


@patch('poke.requests.get')
def test_start_battle_error(mock_get, client):
    mock_response = Mock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    data = {
        'pokemon1': 'invalidpokemon',
        'pokemon2': 'pikachu'
    }
    response = client.post('/battle', data=data)
    assert response.status_code == 500
    assert b'error' in response.data


def test_simulate_battle():
    # Sample changes dictionary for testing
    changes = {
        "move1": 10,
        "move2": 15,
        "move3": 20,
    }

    # Create a PokemonBattle instance
    battle = PokemonBattle("pikachu", "eevee")

    # Call simulate_battle with the sample changes
    battle_info = []
    winner = battle.simulate_battle(changes=changes, battle_info=battle_info)

    # Split the winner_and_hp string to get the winner's name
    winner_name = winner.split(" is winner ")[0]

    # Assert the winner's name
    assert winner_name in ["pikachu", "eevee"]
