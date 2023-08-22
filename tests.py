import pytest
from poke import app
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


def test_successful_battle_response(client):
    data = {
        'pokemon1': 'pikachu',
        'pokemon2': 'eevee'
    }

    response = client.post('/battle', data=data)
    assert response.status_code == 200

    expected_response = {
        "pokemon1": {
            "id": 25,
            "name": "pikachu",
            "stats": {
                "attack": 55,
                "defense": 40,
                "hp": 35,
                "special-attack": 50,
                "special-defense": 50,
                "speed": 90
            }
        },
        "pokemon2": {
            "id": 133,
            "name": "eevee",
            "stats": {
                "attack": 55,
                "defense": 50,
                "hp": 55,
                "special-attack": 45,
                "special-defense": 65,
                "speed": 55
            }
        },
        "winner": "eevee"
    }

    assert response.json == expected_response
