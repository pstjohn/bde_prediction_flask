from flask import Flask, render_template, request, redirect, Markup, flash
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

import urllib.parse

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

from prediction import predict_bdes, check_input
from drawing import draw_mol_outlier

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
    can_smiles = canonicalize_smiles(smiles)

    is_outlier, missing_atom, missing_bond = check_input(can_smiles)
    if is_outlier:
        svg = draw_mol_outlier(can_smiles, missing_atom, missing_bond)
        return render_template(
            "outlier.html", form=form, smiles=can_smiles, mol_svg=svg)

