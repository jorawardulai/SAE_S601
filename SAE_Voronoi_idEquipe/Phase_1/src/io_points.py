import json 

def importFichier(filepath) :

    coordonnee = []

    if filepath.endswith(".txt") :

        with open(filepath, 'r') as fichier :
            for ligne in fichier :
                if ligne.strip():
                    x,y = ligne.strip().split(",")
                    coordonnee.append([float(x), float(y)])

    elif filepath.endswith(".json") :
        with open(filepath, "r") as fichier :
            data = json.load(fichier):

            for p in data : 
                coordonnee.append([float(p[0]), float(p[1])])

    
    return coordonnee
