import pytest
from bde_flask import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_index(client):
    rv = client.get('/')
    assert b'Machine learning predictions' in rv.data

def test_result(client):
    rv = client.get('/result?name=c1ccccc1')
    assert b'Bond 1' in rv.data

def test_neighbors(client):
    rv = client.get('/neighbor?name=c1ccccc1&bond_index=6')
    assert b'c1ccccc1' in rv.data

def test_out_of_scope(client):
    rv = client.get('/result?name=C%5BC%5D')
    assert b'Molecule out of scope' in rv.data

def test_invalid(client):
    rv = client.get('/result?name=')
    assert b'Please enter a valid SMILES without quotes' in rv.data

def test_api(client):
    data = client.get('/api/CCO').get_json()
    assert data['status'] == 'ok'

    data = client.get('/api/B').get_json()
    assert data['status'] == 'outlier'

    data = client.get('/api/X').get_json()
    assert data['status'] == 'invalid smiles'

    data = client.get('/api/neighbors/CCO/5').get_json()
    assert data['status'] == 'ok'

    data = client.get('/api/neighbors/B/1').get_json()
    assert data['status'] == 'outlier'

    data = client.get('/api/neighbors/X/1').get_json()
    assert data['status'] == 'invalid smiles'
