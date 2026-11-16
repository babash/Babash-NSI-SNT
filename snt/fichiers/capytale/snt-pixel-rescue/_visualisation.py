from ipythonblocks import BlockGrid


def dessiner(mat):
    nb_lignes = len(mat)
    nb_colonnes = len(mat[0])
    grille = BlockGrid(nb_colonnes, nb_lignes, block_size=30)
    for ligne in range(nb_lignes):
        for colonne in range(nb_colonnes):
            grille[ligne, colonne] = mat[ligne][colonne]
    return grille
