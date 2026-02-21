import json 

def importFichier(fichier) :

    coordonnee = []

    contenu = fichier.getvalue().decode("utf-8")

    if fichier.name.endswith(".txt") :

        for ligne in contenu.split("\n"):
            if ligne.strip():
                x,y = ligne.strip().split(",")
                coordonnee.append([float(x), float(y)])

    
    elif fichier.name.endswith(".json") :
        data = json.loads(contenu)
        for p in data : 
            coordonnee.append([float(p[0]), float(p[1])])

    
    return coordonnee
