import matplotlib.pyplot as plt




def dessiner_diagramme(diagramme):
    dessin , axe  = plt.subplots(figsize=(8, 8))
    
    # Dessiner les sommets
    for x, y in diagramme["sommets"]:
        axe.plot(x, y, 'ro')
    
    # Dessiner les arêtes
    for (x1, y1), (x2, y2) in diagramme["aretes"]:
        axe.plot([x1, x2], [y1, y2], 'b-')
    
    if len(diagramme["sommets"]) > 0:
        x_coords = [p[0] for p in diagramme["sommets"]]
        y_coords = [p[1] for p in diagramme["sommets"]]
        
        marge = 3 # On laisse 3 unités de marge autour de tes points
        
        axe.set_xlim(min(x_coords) - marge, max(x_coords) + marge)
        axe.set_ylim(min(y_coords) - marge, max(y_coords) + marge)

    
    axe.set_xticks([])
    axe.set_yticks([])
    
    
    return dessin
