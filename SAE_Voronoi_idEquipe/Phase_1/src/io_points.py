import json 

def importFichier(filepath) :

    coordonnee = []

    with open(filepath, 'r') as fichier :
        for ligne in fichier :
            if ligne.strip():
                x,y = ligne.strip().split(",")
                coordonnee.append([float(x), float(y)])
    
    return coordonnee
