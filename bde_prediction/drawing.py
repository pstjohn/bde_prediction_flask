from flask import Markup

from rdkit import Chem
from rdkit.Chem import rdDepictor
from rdkit.Chem.Draw import rdMolDraw2D

def draw_bde(smiles, bond_index, figsize=(300, 300)):
    
    mol = Chem.MolFromSmiles(smiles)
    bond_index = int(bond_index)

    if bond_index >= mol.GetNumBonds():

        molH = Chem.AddHs(mol)
        bond = molH.GetBondWithIdx(bond_index)

        start_atom = mol.GetAtomWithIdx(bond.GetBeginAtomIdx())
        mol = Chem.AddHs(mol, onlyOnAtoms=[start_atom.GetIdx()])
        bond_index = mol.GetNumBonds() - 1

    if not mol.GetNumConformers():
        rdDepictor.Compute2DCoords(mol)

    drawer = rdMolDraw2D.MolDraw2DSVG(*figsize)
    drawer.SetFontSize(.6)
    drawer.DrawMolecule(mol, highlightAtoms=[], highlightBonds=[bond_index,])

    drawer.FinishDrawing()
    svg = drawer.GetDrawingText()

    svg = svg.replace('svg:', '').replace(':svg', '')
    
    return Markup(svg)


def draw_mol_outlier(smiles, missing_atoms, missing_bonds, figsize=(300, 300)):
    
    mol = Chem.MolFromSmiles(smiles)
    missing_bonds_adjusted = []
    for bond_index in missing_bonds:

        if bond_index >= mol.GetNumBonds():

            molH = Chem.AddHs(mol)
            bond = molH.GetBondWithIdx(int(bond_index))

            start_atom = mol.GetAtomWithIdx(bond.GetBeginAtomIdx())
            mol = Chem.AddHs(mol, onlyOnAtoms=[start_atom.GetIdx()])
            bond_index = mol.GetNumBonds() - 1

        missing_bonds_adjusted += [int(bond_index)]

    if not mol.GetNumConformers():
        rdDepictor.Compute2DCoords(mol)

    drawer = rdMolDraw2D.MolDraw2DSVG(*figsize)
    drawer.SetFontSize(.6)
    drawer.DrawMolecule(
        mol, 
        highlightAtoms=[int(index) for index in missing_atoms],
        highlightBonds=missing_bonds_adjusted)

    drawer.FinishDrawing()
    svg = drawer.GetDrawingText()

    svg = svg.replace('svg:', '').replace(':svg', '')

    return Markup(svg)


def draw_mol(smiles, figsize=(300, 300)):
    
    mol = Chem.MolFromSmiles(smiles)
    rdDepictor.Compute2DCoords(mol)

    drawer = rdMolDraw2D.MolDraw2DSVG(*figsize)
    drawer.SetFontSize(.6)
    drawer.DrawMolecule(mol)

    drawer.FinishDrawing()
    svg = drawer.GetDrawingText()

    svg = svg.replace('svg:', '').replace(':svg', '')
    
    return Markup(svg)
