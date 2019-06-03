from bde.fragment import fragment_iterator
import pickle
import warnings

import pandas as pd
from keras.models import load_model

from preprocessor_utils import ConcatGraphSequence
from nfp import custom_layers
from drawing import draw_bde

with open('model_files/preprocessor.p', 'rb') as f:
    preprocessor = pickle.load(f)

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    model = load_model(
        'model_files/best_model.hdf5', custom_objects=custom_layers)


def check_input(smiles):
    """ Check the given SMILES to ensure it's present in the model's
    preprocessor dictionary.

    Returns:
    (is_outlier, missing_atom, missing_bond)

    """

    iinput = preprocessor.predict((smiles,))[0]

    missing_bond = np.array(
        list(set(iinput['bond_indices'][iinput['bond'] == 1])))
    missing_atom = np.arange(iinput['n_atom'])[iinput['atom'] == 1]
    
    is_outlier = (missing_bond.size != 0) | (missing_atom.size != 0)
    
    return is_outlier, missing_atom, missing_bond


def predict_bdes(smiles):

    # Break bonds and get corresponding bond indexes where predictions are
    # valid
    frag_df = pd.DataFrame(fragment_iterator(smiles))
    frag_df = frag_df[(frag_df[
        ['delta_assigned_stereo', 'delta_unassigned_stereo']
    ] == 0).all(1)].drop(
        ['delta_assigned_stereo', 'delta_unassigned_stereo'], 1)

    inputs = preprocessor.predict((smiles,))

    pred = model.predict_generator(
        ConcatGraphSequence(inputs, batch_size=1, shuffle=False), verbose=0)

    bde_df = pd.DataFrame(inputs[0]['bond_indices'], columns=['bond_index'])
    bde_df['bde_pred'] = pred
    bde_df = bde_df.groupby('bond_index').mean().reset_index()

    pred_df = frag_df.merge(bde_df, on=['bond_index'], how='left')
    pred_df = pred_df.sort_values('bde_pred').drop_duplicates(
        ['fragment1', 'fragment2']).reset_index()
    pred_df['svg'] = pred_df.apply(
        lambda x: draw_bde(x.molecule, x.bond_index), 1)

    return pred_df
