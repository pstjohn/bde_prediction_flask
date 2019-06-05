import pandas as pd
import numpy as np
import joblib

from nfp import GraphModel
from preprocessor_utils import ConcatGraphSequence

from drawing import draw_bde
from prediction import preprocessor, model, predict_bdes

embedding_model = GraphModel(model.inputs, [model.layers[-3].input])
bond_embed_df = pd.read_csv('model_files/20190604_bonds_for_neighbors.csv.gz')
nbrs_pipe = joblib.load('model_files/20190604_bond_embedding_nbrs.p.z')

def pipe_kneighbors(pipe, X):
    Xt = pipe.steps[0][-1].transform(X)
    return pipe.steps[-1][-1].kneighbors(Xt)

def find_neighbor_bonds(smiles, bond_index):

    inputs = preprocessor.predict((smiles,))
    embeddings = embedding_model.predict_generator(
        ConcatGraphSequence(inputs, batch_size=128, shuffle=False), verbose=0)

    distances, indices = pipe_kneighbors(
    nbrs_pipe, embeddings[inputs[0]['bond_indices'] == bond_index])

    neighbor_df = bond_embed_df.dropna().iloc[indices.flatten()]
    neighbor_df['distance'] = distances.flatten()
    neighbor_df = neighbor_df.drop_duplicates(
        ['molecule', 'fragment1', 'fragment2']).sort_values('distance')
    neighbor_df['svg'] = neighbor_df.apply(
        lambda x: draw_bde(x.molecule, x.bond_index, figsize=(200,200)), 1)

    return neighbor_df
