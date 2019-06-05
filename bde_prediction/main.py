from flask import Flask, render_template, request, redirect, Markup, flash
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

import urllib.parse

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
app.config['DEBUG'] = True

from prediction import predict_bdes, check_input
from neighbors import find_neighbor_bonds
from drawing import draw_mol_outlier

from bde.fragment import canonicalize_smiles

class ReusableForm(Form):
    name = TextField('SMILES:', validators=[validators.required()])

def quote(x):
    return urllib.parse.quote(x, safe='')

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

        bde_df = predict_bdes(can_smiles)
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

        bde_df = predict_bdes(can_smiles)
        bde_row = bde_df.set_index('bond_index').loc[bond_index]

        neighbor_df = find_neighbor_bonds(can_smiles, bond_index)
        return render_template(
            "neighbor.html", form=form, smiles=can_smiles, bde_row=bde_row,
            neighbor_df=neighbor_df)

if __name__ == '__main__':
    app.run()
