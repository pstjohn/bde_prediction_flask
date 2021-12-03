import urllib.parse
from os import environ

from alfabet.drawing import draw_mol_outlier
from alfabet.fragment import canonicalize_smiles
from alfabet.neighbors import find_neighbor_bonds
from alfabet.prediction import predict_bdes, check_input
from flask import Flask, render_template, request, flash, jsonify, send_from_directory
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from wtforms import Form, StringField, validators

# App config.

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
app.config['DEBUG'] = False

try:
    # Need try->if instead of .get because environment gets garbled by gunicorn and 
    #   rewrites the variable to an empty string, which will return instead of '/'
    if environ['APP_ROOT']:
        APPLICATION_ROOT = '/bde'  # Prevent unnecessary backslash from trickling down
    app.config["APPLICATION_ROOT"] = APPLICATION_ROOT

    app.config.update(APPLICATION_ROOT=APPLICATION_ROOT)


    def simple(env, resp):
        resp('200 OK', [('Content-Type', 'text/plain')])
        return [b'HTTP exchange successful, but an internal redirect error occurred.']


    app.wsgi_app = DispatcherMiddleware(simple, {APPLICATION_ROOT: app.wsgi_app})

except Exception:
    pass


class ReusableForm(Form):
    name = StringField('SMILES:', validators=[validators.DataRequired()])


def quote(x):
    return urllib.parse.quote(x, safe='')


@app.route('/client/<path:path>')
def send_client(path):
    return send_from_directory('static/client', path)


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route("/", methods=['GET', 'POST'])
def index():
    form = ReusableForm(request.form)
    return render_template('index.html', form=form)


@app.route("/result", methods=['GET', 'POST'])
def result():
    form = ReusableForm(request.form)
    smiles = request.args['name']

    try:
        can_smiles = canonicalize_smiles(smiles)
        if not can_smiles:
            raise Exception
    except Exception:
        flash('Error: "{}" SMILES string invalid. Please enter a valid SMILES '
              'without quotes.'.format(smiles))
        return render_template('index.html', form=form)

    is_outlier, missing_atom, missing_bond = check_input(can_smiles)
    if is_outlier:
        svg = draw_mol_outlier(can_smiles, missing_atom, missing_bond)
        return render_template(
            "outlier.html", form=form, smiles=can_smiles, mol_svg=svg)

    else:

        bde_df = predict_bdes(can_smiles, draw=True)
        bde_df = bde_df.drop_duplicates(['fragment1', 'fragment2']).reset_index(drop=True)
        bde_df['smiles_link'] = bde_df.molecule.apply(quote)
        return render_template(
            "result.html", form=form, smiles=can_smiles, df=bde_df)


@app.route("/neighbor", methods=['GET', 'POST'])
def neighbor():
    form = ReusableForm(request.form)
    smiles = request.args['name']
    bond_index = int(request.args['bond_index'])

    try:
        can_smiles = canonicalize_smiles(smiles)
        if not can_smiles:
            raise Exception
    except Exception:
        flash('Error: "{}" SMILES string invalid. Please enter a valid SMILES '
              'without quotes.'.format(smiles))
        return render_template('index.html', form=form)

    is_outlier, missing_atom, missing_bond = check_input(can_smiles)
    if is_outlier:
        svg = draw_mol_outlier(can_smiles, missing_atom, missing_bond)
        return render_template(
            "outlier.html", form=form, smiles=can_smiles, mol_svg=svg)

    else:

        bde_df = predict_bdes(can_smiles, draw=True)
        bde_row = bde_df.set_index('bond_index').loc[bond_index]

        neighbor_df = find_neighbor_bonds(can_smiles, bond_index, draw=True)
        return render_template(
            "neighbor.html", form=form, smiles=can_smiles, bde_row=bde_row,
            neighbor_df=neighbor_df)


@app.route("/api/<string:smiles>", methods=['GET'])
def api(smiles):
    try:
        can_smiles = canonicalize_smiles(smiles)
        if not can_smiles:
            raise Exception
    except Exception:
        return jsonify({'status': 'invalid smiles'})

    is_outlier, missing_atom, missing_bond = check_input(can_smiles)
    if is_outlier:
        return jsonify({'status': 'outlier',
                        'missing atoms': missing_atom.tolist(),
                        'missing bond': missing_bond.tolist()})

    bde_df = predict_bdes(can_smiles, draw=False)
    return jsonify({'status': 'ok',
                    'results': bde_df.to_dict(orient='records')})


@app.route("/api/neighbors/<string:smiles>/<int:bond_index>", methods=['GET'])
def neighbors_api(smiles, bond_index):
    try:
        can_smiles = canonicalize_smiles(smiles)
        if not can_smiles:
            raise Exception
    except Exception:
        return jsonify({'status': 'invalid smiles'})

    is_outlier, missing_atom, missing_bond = check_input(can_smiles)
    if is_outlier:
        return jsonify({'status': 'outlier',
                        'missing atoms': missing_atom.tolist(),
                        'missing bond': missing_bond.tolist()})

    neighbor_df = find_neighbor_bonds(
        can_smiles, bond_index, draw=False).drop(['rid', 'bdfe'], 1)

    return jsonify({'status': 'ok',
                    'results': neighbor_df.to_dict(orient='records')})


if __name__ == '__main__':
    app.run()
