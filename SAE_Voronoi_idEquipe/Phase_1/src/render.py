import matplotlib.pyplot as plt




def dessiner_diagramme(diagram):
    dessin , axe  = plt.subplots(figsize=(8, 8))
    
    # Dessiner les sommets
    for x, y in diagram["sommet"]:
        axe.plot(x, y, 'ro')
    
    # Dessiner les arêtes
    for (x1, y1), (x2, y2) in diagram["aretes"]:
        axe.plot([x1, x2], [y1, y2], 'b-')
    
    axe.set_title("Diagramme de Voronoï")
    axe.set_xlabel("X")
    axe.set_ylabel("Y")
    
    return dessin
