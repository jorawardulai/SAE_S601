import json 

def importFichier(fichier) :

    coordonnee = [] #creation d'un tableau qui va contenir les coordonnee x et y

    contenu = fichier.getvalue().decode("utf-8") # on recupere le contenu du fichier et convertion en string

    if fichier.name.endswith(".txt") :

        for ligne in contenu.split("\n"):
            if ligne.strip(): #si la ligne n'est pas vide
                valeurs = ligne.strip().split(",") #on separe les donnees par des virgule et enleve les espace inutile
                x = valeurs[0] #la premiere valeur est x et la deuxieme est y
                y = valeurs[1]
                coordonnee.append([float(x), float(y)]) #on ajouter les coordonee que l'on met en float dans le tabelau

    
    elif fichier.name.endswith(".json") : #meme chose pour les fichiers json
        data = json.loads(contenu)
        for p in data : 
            coordonnee.append([float(p[0]), float(p[1])])

    
    return coordonnee
