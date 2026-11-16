import networkx as nx
import matplotlib.pyplot as plt

def visualiser_graphe(dictionnaire_graphe):
    """
    Fonction utilitaire pour tracer le graphe depuis le dictionnaire
    Utilise networkx et matplotlib (installés sur Capytale)
    """
    # 1. Création de l'objet Graphe
    G = nx.Graph()

    # 2. Ajout des arêtes depuis le dictionnaire
    for personne, amis in dictionnaire_graphe.items():
        for ami in amis:
            G.add_edge(personne, ami)

    # 3. Paramètres de dessin (Esthétique)
    plt.figure(figsize=(8, 6)) # Taille de l'image
    pos = nx.spring_layout(G, seed=42) # Disposition "élastique" (seed fixe pour que le dessin ne bouge pas)

    # 4. Dessin
    nx.draw(G, pos,
            with_labels=True,
            node_color='lightblue',
            node_size=2500,
            font_size=10,
            font_weight='bold',
            edge_color='gray',
            width=2)

    plt.title("Visualisation du Réseau Social")
    plt.show()

